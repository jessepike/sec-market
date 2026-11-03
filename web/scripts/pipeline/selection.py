"""Bound daily semantic work without asserting historical discovery completeness."""
from datetime import date, timedelta
import re
from urllib.parse import unquote, urlsplit

from contracts import digest, instant


def date_partitions(items, modified, policy, now):
    """Index signatures classify work only; they never establish a fact date."""
    cutoff = (instant(now) - timedelta(days=policy['currentWindowDays'])).date()
    current, historical, unknown = set(), set(), set()
    for url in items:
        stamp = modified.get(url, '')
        try:
            day = __import__('datetime').date.fromisoformat(stamp[:10])
            if day > instant(now).date():
                raise ValueError('Future scheduling hint')
            (current if day >= cutoff else historical).add(url)
        except (ValueError, TypeError):
            unknown.add(url)
    return current, historical, unknown


def windowed(policy):
    """History-window behaviour exists only for policies that declare it (policy-versioned)."""
    return 'historyWindowDays' in policy


def known_day(stamp, now):
    """A usable scheduling date, or None. Future and malformed stamps are unknown."""
    try:
        day = date.fromisoformat((stamp or '')[:10])
    except (ValueError, TypeError):
        return None
    return None if day > instant(now).date() else day


def outside_history_window(stamp, policy, now):
    """True only for a known date older than the history window. Undated is never outside."""
    if not windowed(policy):
        return False
    day = known_day(stamp, now)
    return day is not None and day < (instant(now) - timedelta(days=policy['historyWindowDays'])).date()


NOT_ABOUT_RULE = 'not-about-supplier-v1'
NOT_ABOUT_OUTCOME = 'not_about_supplier'
LEGAL = {'inc', 'incorporated', 'corp', 'corporation', 'llc', 'ltd', 'limited', 'plc'}
TRAILING_GENERIC = {'security', 'cybersecurity', 'systems', 'software', 'solutions', 'technology',
                    'technologies', 'networks', 'network', 'holdings', 'group', 'global', 'international'}


def name_forms(name):
    """Word tuples a company may be written as: the name, each parenthetical part, minus legal suffixes."""
    forms = set()
    pieces = [re.sub(r'\([^)]*\)?', ' ', name), *re.findall(r'\(([^)]*)\)?', name)]
    for piece in pieces:
        words = re.findall(r'[a-z0-9]+', piece.lower())
        while words and words[-1] in LEGAL:
            words.pop()
        if words:
            forms.add(tuple(words))
            trimmed = list(words)
            while len(trimmed) > 1 and trimmed[-1] in TRAILING_GENERIC:
                trimmed.pop()
                forms.add(tuple(trimmed))
    return forms


def mentions_supplier(text, supplier):
    """Case-insensitive whole-word mention of the name or an alias, tolerant of punctuation and spacing.

    Errs toward "mentioned": a wrong yes only costs a model call, a wrong no would
    drop a document. Segment suppliers are never excluded, because their documents
    legitimately name the parent company or a product instead of the segment.
    """
    if supplier.get('kind') == 'segment':
        return True
    lowered = text.lower()
    for name in [supplier['name'], *supplier.get('aliases', [])]:
        if not name:
            continue
        if re.search(r'\b' + re.escape(name.lower()) + r'\b', lowered):
            return True
        for words in name_forms(name):
            if re.search(r'(?<![a-z0-9])' + r'[\W_]*'.join(map(re.escape, words)) + r'(?![a-z0-9])', lowered):
                return True
    return False


def entity_url_priority(url, supplier):
    """Exact registered slugs are a work-order hint, never entity evidence."""
    if not supplier:
        return False
    legal = {'inc', 'incorporated', 'corp', 'corporation', 'llc', 'ltd', 'limited', 'plc'}
    generic = {'security', 'cybersecurity', 'systems', 'software', 'solutions', 'technology',
               'technologies', 'networks', 'network', 'holdings', 'group', 'global', 'international'}
    path = tuple(re.findall(r'[a-z0-9]+', unquote(urlsplit(url).path).lower()))
    for name in [supplier['name'], *supplier.get('aliases', [])]:
        words = re.findall(r'[a-z0-9]+', name.lower())
        while words and words[-1] in legal:
            words.pop()
        if not words or len(''.join(words)) < 5 or (len(words) == 1 and words[0] in generic):
            continue
        phrase = tuple(words)
        if any(path[i:i + len(phrase)] == phrase for i in range(len(path) - len(phrase) + 1)):
            return True
        if len(words) > 1 and ''.join(words) in path:
            return True
    return False


def select_documents(found, history, policy, now, supplier=None):
    """Return current/delta work first and retain every deferred URL for audit.

    lastmod is only a scheduling hint, never evidence of a fact's effective date.
    A successful semantic check records the index signature and check time. Changed
    index signatures are revisited immediately; unchanged documents rotate through
    the audit queue after the current window. Unknown dates never become current.

    Policies that declare historyWindowDays also archive never-reviewed documents
    whose known date is older than that window. Archived URLs are returned with the
    deferred ones, so they stay in the retained queue, but they are never selected.
    Undated documents stay eligible and sort after dated ones. Policies that also
    declare maxFetchAuditDocumentsPerSource add extra audit slots for documents
    that can be settled by a fetch alone; which ones is rotated daily.
    """
    items = set(found["items"])
    modified = found.get("itemModified", {})
    cutoff = (instant(now) - timedelta(days=policy["currentWindowDays"])).date().isoformat()
    history_window = windowed(policy)
    current, audit, archived, audit_order = [], [], [], {}
    revalidation = set(found.get('requiredRevalidation', []))
    for url in sorted(items):
        stamp = modified.get(url, "")
        old = history.get(url)
        changed = old is not None and old.get("modified", "") != stamp
        recent = cutoff <= stamp[:10] <= now[:10] if stamp else False
        # Invalid or future cursor times cannot suppress unresolved work.
        try:
            checked = instant(old["checkedAt"]) if old else None
            valid_check = checked is not None and checked <= instant(now)
        except (KeyError, TypeError, ValueError):
            valid_check = False
        due = not valid_check or old["checkedAt"][:10] < cutoff
        audit_order[url] = old["checkedAt"] if valid_check else ""
        if url in revalidation or changed or (recent and due):
            current.append(url)
        elif due and outside_history_window(stamp, policy, now):
            # An already reviewed document is not re-audited once it is outside the window.
            if not valid_check:
                archived.append(url)
        elif due:
            audit.append(url)
    current.sort(key=lambda u: (entity_url_priority(u, supplier), modified.get(u, ""), u), reverse=True)
    maximum = policy["maxDocumentsPerSource"]
    if not history_window:
        # Oldest successful audit first. New, undated pages use stable URL order.
        audit.sort(key=lambda u: (not entity_url_priority(u, supplier), audit_order[u], u))
        selected = current[:maximum]
        selected += audit[:min(policy["maxAuditDocumentsPerSource"], maximum - len(selected))]
        return selected, sorted((set(current) | set(audit)) - set(selected))
    # Dated documents first, undated last; oldest successful audit first inside each.
    audit.sort(key=lambda u: (not entity_url_priority(u, supplier), known_day(modified.get(u), now) is None, audit_order[u], u))
    selected = current[:maximum]
    selected += audit[:min(policy["maxAuditDocumentsPerSource"], maximum - len(selected))]
    extra = policy.get("maxFetchAuditDocumentsPerSource", 0)
    if extra:
        # Documents that passed the name check but wait for model budget must not
        # hold the front of the queue forever, so the extra slots rotate daily.
        taken = set(selected)
        rest = [u for u in audit if u not in taken]
        rest.sort(key=lambda u: (not entity_url_priority(u, supplier), known_day(modified.get(u), now) is None,
                                 digest({'day': now[:10], 'url': u})))
        selected += rest[:extra]
    return selected, sorted((set(current) | set(audit) | set(archived)) - set(selected))
