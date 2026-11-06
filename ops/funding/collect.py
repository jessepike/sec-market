"""Weekly funding-rounds and investor-portfolio collector (startup discovery lane).

Separate from the daily collector and from contracts/market.json: it never
touches the 74-supplier roster. Stdlib only, no model calls, no secrets.

What it does each run:
  1. Reads the Return on Security archive, takes up to MAX_POSTS weekly
     "Security, Funded" posts it has not processed, and parses the Funding
     section into rounds (company, country, amount, stage, lead investor).
  2. Confirms each round against the primary source the post links to
     (the company's own announcement, a wire release or an SEC Form D).
     A round is published only when that page names the company and states
     the amount (or, for an undisclosed amount, the round). Anything else is
     kept as "held" with its reason and never shown.
  3. Reads five cyber-specialist investor portfolio pages and records each
     company the first week it appears. The first read of a page is the
     baseline and marks nothing as new.
  4. Writes web/src/data/funding/feed.json only when its content changed:
     no per-run timestamps, so a week with nothing new produces no commit.
     A source that cannot be read is retried next week, never recorded.

Facts only: no ranking, no labels, no interpretation (D-76). Descriptions from
the newsletter are not republished; the page shows the facts and links to the
primary source, crediting where the round was found.
"""
from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FEED = ROOT / "web" / "src" / "data" / "funding" / "feed.json"

UA = "Mozilla/5.0 (compatible; SecurityMarketPulse/1.0; +https://securitymarketpulse.com)"
# SEC asks automated clients to name themselves and a contact address.
SEC_UA = "SecurityMarketPulse research jp@jessepike.dev"

ROS_BASE = "https://www.returnonsecurity.com"
ROS_ARCHIVE = ROS_BASE + "/archive"
MAX_POSTS = 2          # newest unprocessed posts per run
MAX_TRIES = 3         # weekly attempts to read a round's source before holding it
MAX_FETCHES = 50       # hard cap on HTTP requests per run
FETCH_PAUSE = 1.0      # seconds between requests
MAX_BYTES = 3_000_000

PORTFOLIOS = [
    {"id": "syn", "name": "SYN Ventures", "url": "https://www.synventures.com/portfolio-companies/",
     "pattern": r"https://www\.synventures\.com/portfolio/([a-z0-9-]+)/"},
    {"id": "forgepoint", "name": "Forgepoint Capital", "url": "https://forgepointcap.com/companies/",
     "pattern": r"https://forgepointcap\.com/companies/([a-z0-9-]+)/(?!case-study)",
     # The list is paginated: /companies/page/2/ and so on.
     "pages": r"https://forgepointcap\.com/companies/page/(\d+)/", "maxPages": 10},
    {"id": "team8", "name": "Team8", "url": "https://team8.vc/cybersecurity/",
     "pattern": r"https://team8\.vc/portfolio/([a-z0-9-]+)/"},
    {"id": "cyberstarts", "name": "Cyberstarts", "url": "https://www.cyberstarts.com/portfolio",
     "pattern": r'href="/companies/([a-z0-9-]+)"'},
    {"id": "yl", "name": "YL Ventures", "url": "https://www.ylventures.com/portfolio/",
     # Each YL card is the company's site followed by its LinkedIn page.
     "pattern": r'href="https?://(?:www\.)?([a-z0-9-]+(?:\.[a-z0-9-]+)+)/?"[^>]*>\s*(?:<[^a][^>]*>\s*)*</a>\s*(?:<[^>]+>\s*)*<a[^>]+href="https://www\.linkedin\.com/company/'},
]
MIN_PORTFOLIO_RATIO = 0.6  # a read with far fewer names than last time is treated as broken
MAX_NEW_RATIO = 0.25       # a read where over a quarter of the names are new is treated as a layout change

ITEM = re.compile(
    r"^(?P<name>.+?) \((?P<cc>[A-Z]{2})\) · (?P<deal>.+?) \| (?P<rest>.+)$"
)
AMOUNT = re.compile(r"^\$(?P<num>[\d.,]+)(?P<unit>[KMB])\s+(?P<stage>.+)$")
UNDISCLOSED = re.compile(r"^Undisclosed amount in an? (?P<stage>.+)$", re.I)
LEAD = re.compile(r",\s*(?:led by|from)\s+(?P<lead>.+?)\s*\((?:more|SEC Filing)\)\s*$")


class Budget:
    def __init__(self, limit: int):
        self.left = limit
        self.used = 0

    def take(self) -> None:
        if self.left <= 0:
            raise RuntimeError("fetch budget spent")
        self.left -= 1
        self.used += 1


def fetch(url: str, budget: Budget) -> str:
    budget.take()
    host = urllib.parse.urlparse(url).hostname or ""
    ua = SEC_UA if host.endswith("sec.gov") else UA
    req = urllib.request.Request(url, headers={"User-Agent": ua, "Accept": "text/html,application/xhtml+xml,application/xml,*/*"})
    time.sleep(FETCH_PAUSE)
    with urllib.request.urlopen(req, timeout=30) as r:
        body = r.read(MAX_BYTES)
    return body.decode("utf-8", "replace")


def text_of(fragment: str) -> str:
    s = re.sub(r"(?is)<(script|style|noscript).*?</\1>", " ", fragment)
    s = re.sub(r"(?s)<[^>]+>", " ", s)
    s = html.unescape(s).replace("\xa0", " ")
    return re.sub(r"\s+", " ", s).strip()


def hrefs(fragment: str) -> list[str]:
    return [html.unescape(h) for h in re.findall(r'(?i)<a\b[^>]*\bhref="([^"]+)"', fragment)]


# ---------------------------------------------------------------- Return on Security

def post_links(archive_html: str) -> list[tuple[int, str]]:
    found = {}
    for href in hrefs(archive_html):
        m = re.search(r"/p/security-funded-(\d+)\b", href)
        if m:
            found[int(m.group(1))] = ROS_BASE + "/p/security-funded-" + m.group(1)
    return sorted(found.items(), reverse=True)


def funding_section(post_html: str) -> str:
    """The HTML between the Funding heading and the M&A heading."""
    start = None
    for m in re.finditer(r"(?is)<h[1-4][^>]*>(.*?)</h[1-4]>", post_html):
        label = text_of(m.group(1)).lower()
        if start is None and label.endswith("funding") and "market" not in label:
            start = m.end()
        elif start is not None and ("mergers" in label or "acquisitions" in label):
            return post_html[start:m.start()]
    return post_html[start:] if start is not None else ""


def parse_week(post_html: str) -> str | None:
    m = re.search(r"during the week of ([A-Z][a-z]+) (\d{1,2})(?:st|nd|rd|th)?, (\d{4})", text_of(post_html))
    if not m:
        return None
    try:
        return dt.datetime.strptime(f"{m.group(1)} {m.group(2)} {m.group(3)}", "%B %d %Y").date().isoformat()
    except ValueError:
        return None


def parse_published(post_html: str) -> str | None:
    m = re.search(r"\b([A-Z][a-z]{2}) (\d{1,2}), (\d{4})\b", text_of(post_html))
    if not m:
        return None
    try:
        return dt.datetime.strptime(" ".join(m.groups()), "%b %d %Y").date().isoformat()
    except ValueError:
        return None


def amount_usd(num: str, unit: str) -> int:
    value = float(num.replace(",", ""))
    return int(round(value * {"K": 1e3, "M": 1e6, "B": 1e9}[unit]))


def parse_rounds(section_html: str) -> list[dict]:
    rounds = []
    blocks = re.split(r"(?i)</li>|</p>", section_html)
    for block in blocks:
        t = text_of(block)
        m = ITEM.match(t)
        if not m:
            continue
        links = [h for h in hrefs(block) if h.startswith("http")]
        if len(links) < 2:
            continue
        deals = parse_deals(m.group("deal"))
        if not deals:
            continue
        lead_m = LEAD.search(t)
        lead = lead_m.group("lead").strip() if lead_m else None
        if lead and lead.lower().startswith("investors undisclosed"):
            lead = None
        for amount, stage in deals:
            rounds.append({
                "company": m.group("name").strip(),
                "country": m.group("cc"),
                "amountUsd": amount,
                "stage": normalize_stage(stage),
                "lead": lead,
                "companyUrl": links[0],
                "sourceUrl": links[-1],
            })
    return rounds


def parse_deals(deal: str) -> list[tuple[int | None, str]]:
    """"$28.0M Series A and $6.0M Seed" -> two deals. Emoji and other decoration are dropped."""
    clean = re.sub(r"[^\x20-\x7e]+", " ", deal)
    clean = re.sub(r"\s+", " ", clean).strip()
    out = []
    for part in re.split(r"\s+and\s+(?=\$)", clean):
        part = part.strip()
        a = AMOUNT.match(part)
        u = UNDISCLOSED.match(part)
        if a:
            out.append((amount_usd(a.group("num"), a.group("unit")), a.group("stage").strip()))
        elif u:
            out.append((None, u.group("stage").strip()))
        else:
            return []
    return out


def normalize_stage(stage: str) -> str:
    s = stage.strip().rstrip(".")
    s = re.sub(r"(?i)^venture round$", "Venture round", s)
    return s[:1].upper() + s[1:]


# ---------------------------------------------------------------- confirmation

def page_text(raw: str) -> str:
    """Lower-case visible text with single spaces; keeps $, digits and punctuation."""
    return re.sub(r"\s+", " ", text_of(raw).lower()).strip()


def amount_pattern(usd: int) -> re.Pattern:
    """Dollar-stated forms of one amount, never matching inside a larger number.

    $40M, $40 million, $40.0 million, US$40m, $40,000,000. Bare numbers without a
    dollar sign do not count: "40 million users" or a year must not confirm.
    """
    forms = [re.escape(f"{usd:,}")]
    for unit, div, words in (("m", 1e6, r"(?:million|mn|m)"), ("b", 1e9, r"(?:billion|bn|b)"), ("k", 1e3, r"(?:thousand|k)")):
        v = usd / div
        if v >= 1 and abs(v * 1000 - round(v * 1000)) < 1e-6:
            n = f"{v:.3f}".rstrip("0").rstrip(".")
            num = re.escape(n) + (r"(?:\.0+)?" if "." not in n else r"0*")
            forms.append(num + r"\s?" + words + r"(?![a-z0-9])")
    body = "|".join(forms)
    return re.compile(r"(?:us)?\$\s?(?<![\d.,])(?:" + body + r")(?![\d,]*\d)")


SUFFIXES = {"inc", "ltd", "llc", "technologies", "technology", "labs", "corp", "co", "gmbh", "ai", "security", "systems"}
NEAR = 250  # characters: a shortened name must sit this close to the amount


def name_forms(company: str) -> tuple[list[str], list[str]]:
    """(full forms, shortened forms). Full: the name as listed and without a "(formerly ...)" note.
    Shortened: the name without a trailing company-type word, accepted only next to the amount."""
    base = re.sub(r"\s*\(.*?\)\s*", " ", company).strip().lower()
    full = list(dict.fromkeys([company.lower().strip(), base]))
    words = base.split()
    short = []
    while len(words) > 1 and words[-1] in SUFFIXES:
        words = words[:-1]
        short.append(" ".join(words))
    return [f for f in full if len(f) >= 3], [w for w in short if len(w) >= 3]


def _find(form: str, text: str) -> list[int]:
    return [m.start() for m in re.finditer(r"(?<![a-z0-9])" + re.escape(form) + r"(?![a-z0-9])", text)]


# After a shortened name, the next word must not continue a different name
# ("Ultra Mobile raises" is not Ultra Security).
SHORT_NEXT = r"(?:[^a-z0-9 ]|$| (?:raises|raised|secures|secured|announces|announced|closes|closed|has|today|lands|gets|emerges|launches|completes|completed|is|was|and|with|in|to|of|a|an|the|led|from)\b)"


def _find_short(form: str, text: str) -> list[int]:
    return [m.start() for m in re.finditer(r"(?<![a-z0-9])" + re.escape(form) + r"(?![a-z0-9])(?=" + SHORT_NEXT + ")", text)]


def confirm(round_: dict, raw: str) -> tuple[bool, str]:
    text = page_text(raw)
    full, short = name_forms(round_["company"])
    full_hits = [i for f in full for i in _find(f, text)]
    short_hits = [i for f in short for i in _find_short(f, text)]
    if not full_hits and not short_hits:
        return False, "source does not name the company"
    if round_["amountUsd"] is None:
        # A round with no amount in the funding list is not published: the
        # source may state one we did not read, and a blank figure misleads.
        return False, "no amount in the funding list"
    amounts = [m.start() for m in amount_pattern(round_["amountUsd"]).finditer(text)]
    if not amounts:
        return False, "source does not state the amount"
    if full_hits:
        return True, "company and amount stated on the source"
    if any(abs(a - n) <= NEAR for a in amounts for n in short_hits):
        return True, "company and amount stated together on the source"
    return False, "source names the company only in short form, away from the amount"


def form_d_sold(raw: str) -> int | None:
    """Total amount sold from a Form D, as XML or as SEC's rendered page."""
    m = re.search(r"<totalAmountSold>\s*\$?([\d,]+)", raw, re.I)
    if not m:
        m = re.search(r"total amount sold\s*\$?\s*([\d,]+)", page_text(raw))
    if not m:
        return None
    digits = m.group(1).replace(",", "")
    return int(digits) if digits.isdigit() else None


def confirm_form_d(round_: dict, raw: str) -> tuple[bool, str]:
    full, short = name_forms(round_["company"])
    text = page_text(raw)
    if not any(_find(f, text) for f in full + short):
        return False, "Form D issuer name does not match"
    if round_["amountUsd"] is None:
        return False, "no amount in the funding list"
    sold = form_d_sold(raw)
    if sold is None:
        return False, "Form D total amount sold not found"
    if sold == round_["amountUsd"]:
        return True, "total amount sold in the company's SEC Form D"
    return False, "Form D total amount sold differs"


# ---------------------------------------------------------------- portfolios

def portfolio_names(page_html: str, pattern: str) -> list[str]:
    skip = {"www", "page", "linkedin.com", "ylventures.com", "twitter.com", "facebook.com"}
    names = sorted({m.group(1).lower() for m in re.finditer(pattern, page_html)} - skip)
    return names


# ---------------------------------------------------------------- run

def load_feed() -> dict:
    if FEED.exists():
        feed = json.loads(FEED.read_text())
    else:
        feed = {"schemaVersion": 1, "rounds": [], "held": [], "postsProcessed": [], "portfolios": {}, "retries": {}}
    # Older files carried per-run fields that changed every week; they are not content.
    feed.pop("runs", None)
    feed.pop("checkedAt", None)
    for state in feed["portfolios"].values():
        for company in state["companies"].values():
            company.pop("lastSeen", None)
    return feed


def round_id(r: dict) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", r["company"].lower()).strip("-")
    return f"{slug}:{r['weekOf']}:{r['stage'].lower().replace(' ', '-')}"


def round_key(r: dict) -> tuple:
    """The same company, round and amount listed again in a later week is one round."""
    return (re.sub(r"[^a-z0-9]+", "", r["company"].lower()), r["stage"].lower(), r["amountUsd"])


def content(feed: dict) -> str:
    return json.dumps(feed, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def run(today: str, dry: bool) -> tuple[dict, list[str]]:
    feed = load_feed()
    before_text = content(feed)
    budget = Budget(MAX_FETCHES)
    log: list[str] = []
    errors: list[str] = []

    # 1-2. Return on Security
    done = set(feed["postsProcessed"])
    known = {round_key(r) for r in feed["rounds"] + feed["held"]}
    try:
        posts = [p for p in post_links(fetch(ROS_ARCHIVE, budget)) if p[0] not in done][:MAX_POSTS]
    except Exception as e:  # noqa: BLE001 - a source failure is recorded, never fatal
        posts = []
        errors.append(f"archive: {type(e).__name__}: {e}")
    for number, url in sorted(posts):
        try:
            post = fetch(url, budget)
        except Exception as e:  # noqa: BLE001
            errors.append(f"post {number}: {type(e).__name__}: {e}")
            continue
        week = parse_week(post)
        section = funding_section(post)
        parsed = parse_rounds(section)
        if os.environ.get("FUNDING_DEBUG"):
            print(f"DEBUG post {number} section {len(section)} chars:\n{section[:4000]}")
        if not week or not parsed:
            errors.append(f"post {number}: could not read week or rounds (week={week}, rounds={len(parsed)})")
            continue
        log.append(f"post {number}: week of {week}, {len(parsed)} rounds")
        complete = True
        for r in parsed:
            r.update({"weekOf": week, "foundVia": {"name": "Return on Security", "issue": number, "url": url}})
            r["id"] = round_id(r)
            if round_key(r) in known:
                continue
            is_form_d = "sec.gov" in (urllib.parse.urlparse(r["sourceUrl"]).hostname or "")
            try:
                body = fetch(r["sourceUrl"], budget)
            except Exception as e:  # noqa: BLE001
                if budget.left <= 0 and isinstance(e, RuntimeError):
                    complete = False
                    errors.append(f"post {number}: fetch budget spent; the rest waits for next week")
                    break
                # A failed read is retried on later runs; after MAX_TRIES it is held, never published.
                tries = feed.setdefault("retries", {})
                tries[r["id"]] = tries.get(r["id"], 0) + 1
                errors.append(f"post {number}: {r['company']} source unreadable ({type(e).__name__}), try {tries[r['id']]}")
                if tries[r["id"]] < MAX_TRIES:
                    complete = False
                    continue
                ok, why = False, f"source unreadable on {MAX_TRIES} weekly tries"
                r.update({"sourceKind": "sec-form-d" if is_form_d else "announcement", "checkedAt": today, "confirmation": why})
                feed["held"].append(r)
                known.add(round_key(r))
                tries.pop(r["id"], None)
                log.append(f"  HELD      {r['company']} {r['stage']} {r['amountUsd']} - {why}")
                continue
            feed.get("retries", {}).pop(r["id"], None)
            ok, why = (confirm_form_d if is_form_d else confirm)(r, body)
            r["sourceKind"] = "sec-form-d" if is_form_d else "announcement"
            r["checkedAt"] = today
            r["confirmation"] = why
            (feed["rounds"] if ok else feed["held"]).append(r)
            known.add(round_key(r))
            log.append(f"  {'CONFIRMED' if ok else 'HELD     '} {r['company']} {r['stage']} {r['amountUsd']} - {why}")
        if complete:
            feed["postsProcessed"] = sorted(set(feed["postsProcessed"]) | {number})

    # 3. Portfolios
    for p in PORTFOLIOS:
        if budget.left <= 0:
            errors.append(f"portfolio {p['id']}: fetch budget spent")
            continue
        state = feed["portfolios"].setdefault(p["id"], {"name": p["name"], "url": p["url"], "companies": {}, "baselineAt": None})
        try:
            first = fetch(p["url"], budget)
            names = set(portfolio_names(first, p["pattern"]))
            if p.get("pages"):
                last = max([int(n) for n in re.findall(p["pages"], first)] or [1])
                for n in range(2, min(last, p["maxPages"]) + 1):
                    names |= set(portfolio_names(fetch(p["url"] + f"page/{n}/", budget), p["pattern"]))
            names = sorted(names)
        except Exception as e:  # noqa: BLE001
            errors.append(f"portfolio {p['id']}: {type(e).__name__}: {e}")
            continue
        if os.environ.get("FUNDING_DEBUG"):
            print(f"DEBUG portfolio {p['id']}: {names}")
        before = state["companies"]
        if not names:
            errors.append(f"portfolio {p['id']}: no names found")
            continue
        if before and len(names) < MIN_PORTFOLIO_RATIO * len(before):
            errors.append(f"portfolio {p['id']}: read {len(names)} names, last time {len(before)}; kept last read")
            continue
        baseline = state["baselineAt"] is None
        new = [n for n in names if n not in before]
        if not baseline and len(new) > MAX_NEW_RATIO * len(before):
            # A page redesign that renames every link would otherwise list the whole portfolio as new.
            errors.append(f"portfolio {p['id']}: {len(new)} new of {len(before)}; looks like a layout change, kept last read")
            continue
        for n in new:
            before[n] = {"firstSeen": today, "baseline": baseline}
        if baseline:
            state["baselineAt"] = today
        log.append(f"portfolio {p['id']}: {len(names)} names, {0 if baseline else len(new)} new{' (baseline)' if baseline else ''}")

    feed["rounds"].sort(key=lambda r: (r["weekOf"], r.get("amountUsd") or 0, r["company"]), reverse=True)
    feed["held"].sort(key=lambda r: (r["weekOf"], r["company"]), reverse=True)
    changed = content(feed) != before_text
    if changed:
        feed["updatedAt"] = today
    for line in log + [f"ERROR {e}" for e in errors]:
        print(line)
    print(f"fetches used: {budget.used} of {MAX_FETCHES}; feed {'changed' if changed else 'unchanged'}")
    if not dry and changed:
        FEED.parent.mkdir(parents=True, exist_ok=True)
        FEED.write_text(content(feed))
    return feed, errors


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--today", default=dt.datetime.now(dt.timezone.utc).date().isoformat())
    args = ap.parse_args(argv)
    _, errors = run(args.today, args.dry_run)
    # Fail the job when the funding list or most portfolio pages could not be read, so an outage alerts.
    broken = any(e.startswith(("archive:", "post ")) and "could not read" in e or e.startswith("archive:") for e in errors)
    portfolio_errors = sum(e.startswith("portfolio ") for e in errors)
    return 1 if broken or portfolio_errors >= 3 else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
