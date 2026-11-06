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
  4. Writes web/src/data/funding/feed.json, sorted and stable, so a run with
     nothing new produces no diff.

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

def amount_variants(usd: int) -> list[str]:
    out = {f"{usd:,}", str(usd)}
    for unit, div in (("million", 1e6), ("billion", 1e9), ("thousand", 1e3)):
        v = usd / div
        if v >= 1 and abs(v * 10 - round(v * 10)) < 1e-6:
            short = f"{v:.1f}".rstrip("0").rstrip(".")
            for n in {short, f"{v:.1f}"}:
                out.update({f"${n} {unit}", f"${n}{unit[0].upper()}", f"${n} {unit[0].upper()}", f"{n} {unit}",
                            f"${n}{unit[0]}", f"${n}{'mn' if unit == 'million' else unit[0]}"})
    return sorted(out, key=len, reverse=True)


def norm(s: str) -> str:
    return re.sub(r"[^a-z0-9$.,]+", " ", s.lower()).strip()


SUFFIXES = {"inc", "ltd", "llc", "technologies", "technology", "labs", "corp", "co", "gmbh", "ai", "security", "systems"}


def name_variants(company: str) -> list[str]:
    """The name as listed, without a "(formerly ...)" note, and without a trailing company-type word."""
    base = re.sub(r"\s*\(.*?\)\s*", " ", company).strip()
    out = [norm(company), norm(base)]
    words = norm(base).split()
    while len(words) > 1 and words[-1] in SUFFIXES:
        words = words[:-1]
        out.append(" ".join(words))
    return [v for v in dict.fromkeys(out) if len(v) >= 3]


def names_company(round_: dict, page: str) -> bool:
    return any(re.search(r"(?<![a-z0-9])" + re.escape(v) + r"(?![a-z0-9])", page) for v in name_variants(round_["company"]))


def confirm(round_: dict, page_text: str) -> tuple[bool, str]:
    page = norm(page_text)
    if not names_company(round_, page):
        return False, "source does not name the company"
    if round_["amountUsd"] is None:
        # A round with no amount in the funding list is not published: the
        # source may state one we did not read, and a blank figure misleads.
        return False, "no amount in the funding list"
    flat = page.replace(" ", "")
    for v in amount_variants(round_["amountUsd"]):
        nv = norm(v)
        if nv in page or nv.replace(" ", "") in flat:
            return True, "company and amount stated on the source"
    return False, "source does not state the amount"


def confirm_form_d(round_: dict, xml_text: str) -> tuple[bool, str]:
    t = text_of(xml_text)
    if not names_company(round_, norm(t)):
        return False, "Form D issuer name does not match"
    if round_["amountUsd"] is None:
        return True, "Form D filed by the company"
    digits = f"{round_['amountUsd']:,}"
    plain = str(round_["amountUsd"])
    if digits in t or plain in t.replace(",", ""):
        return True, "amount stated in the company's SEC Form D"
    return False, "Form D does not state the amount"


# ---------------------------------------------------------------- portfolios

def portfolio_names(page_html: str, pattern: str) -> list[str]:
    skip = {"www", "page", "linkedin.com", "ylventures.com", "twitter.com", "facebook.com"}
    names = sorted({m.group(1).lower() for m in re.finditer(pattern, page_html)} - skip)
    return names


# ---------------------------------------------------------------- run

def load_feed() -> dict:
    if FEED.exists():
        return json.loads(FEED.read_text())
    return {"schemaVersion": 1, "rounds": [], "held": [], "postsProcessed": [], "portfolios": {}, "runs": []}


def round_id(r: dict) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", r["company"].lower()).strip("-")
    return f"{slug}:{r['weekOf']}:{r['stage'].lower().replace(' ', '-')}"


def run(today: str, dry: bool) -> dict:
    feed = load_feed()
    budget = Budget(MAX_FETCHES)
    log: list[str] = []
    errors: list[str] = []

    # 1-2. Return on Security
    done = set(feed["postsProcessed"])
    known_ids = {r["id"] for r in feed["rounds"]} | {h["id"] for h in feed["held"]}
    try:
        posts = [p for p in post_links(fetch(ROS_ARCHIVE, budget)) if p[0] not in done][:MAX_POSTS]
    except Exception as e:  # noqa: BLE001 - a source failure is recorded, never fatal
        posts, _ = [], errors.append(f"archive: {type(e).__name__}: {e}")
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
        for r in parsed:
            r.update({"weekOf": week, "foundVia": {"name": "Return on Security", "issue": number, "url": url}})
            r["id"] = round_id(r)
            if r["id"] in known_ids:
                continue
            try:
                body = fetch(r["sourceUrl"], budget)
                is_form_d = "sec.gov" in (urllib.parse.urlparse(r["sourceUrl"]).hostname or "")
                ok, why = (confirm_form_d if is_form_d else confirm)(r, body)
                r["sourceKind"] = "sec-form-d" if is_form_d else "announcement"
            except Exception as e:  # noqa: BLE001
                ok, why = False, f"source unreadable: {type(e).__name__}"
            r["checkedAt"] = today
            r["confirmation"] = why
            (feed["rounds"] if ok else feed["held"]).append(r)
            known_ids.add(r["id"])
            log.append(f"  {'CONFIRMED' if ok else 'HELD     '} {r['company']} {r['stage']} {r['amountUsd']} - {why}")
        feed["postsProcessed"] = sorted(set(feed["postsProcessed"]) | {number})

    # 3. Portfolios
    for p in PORTFOLIOS:
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
        if before and len(names) < MIN_PORTFOLIO_RATIO * len(before):
            errors.append(f"portfolio {p['id']}: read {len(names)} names, last time {len(before)}; kept last read")
            continue
        if not names:
            errors.append(f"portfolio {p['id']}: no names found")
            continue
        baseline = state["baselineAt"] is None
        new = [n for n in names if n not in before]
        for n in new:
            before[n] = {"firstSeen": today, "baseline": baseline, "lastSeen": today}
        for n in names:
            before[n]["lastSeen"] = today
        if baseline:
            state["baselineAt"] = today
        log.append(f"portfolio {p['id']}: {len(names)} names, {0 if baseline else len(new)} new{' (baseline)' if baseline else ''}")

    feed["rounds"].sort(key=lambda r: (r["weekOf"], r.get("amountUsd") or 0, r["company"]), reverse=True)
    feed["held"].sort(key=lambda r: (r["weekOf"], r["company"]), reverse=True)
    feed["runs"] = (feed["runs"] + [{"date": today, "fetches": budget.used, "errors": errors}])[-12:]
    feed["checkedAt"] = today
    for line in log + [f"ERROR {e}" for e in errors]:
        print(line)
    print(f"fetches used: {budget.used} of {MAX_FETCHES}")
    if not dry:
        FEED.parent.mkdir(parents=True, exist_ok=True)
        FEED.write_text(json.dumps(feed, indent=2, sort_keys=True, ensure_ascii=False) + "\n")
    return feed


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--today", default=dt.datetime.now(dt.timezone.utc).date().isoformat())
    args = ap.parse_args(argv)
    feed = run(args.today, args.dry_run)
    # Fail the job only when nothing at all could be read, so an outage alerts.
    last = feed["runs"][-1]
    return 1 if last["fetches"] > 0 and len(last["errors"]) >= 1 + len(PORTFOLIOS) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
