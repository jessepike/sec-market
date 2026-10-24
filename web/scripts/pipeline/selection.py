"""Bound daily semantic work without asserting historical discovery completeness."""
from datetime import timedelta
import re
from urllib.parse import unquote, urlsplit

from contracts import instant


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
    """
    items = set(found["items"])
    modified = found.get("itemModified", {})
    cutoff = (instant(now) - timedelta(days=policy["currentWindowDays"])).date().isoformat()
    current, audit, audit_order = [], [], {}
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
        elif due:
            audit.append(url)
    current.sort(key=lambda u: (entity_url_priority(u, supplier), modified.get(u, ""), u), reverse=True)
    # Oldest successful audit first. New, undated pages use stable URL order.
    audit.sort(key=lambda u: (not entity_url_priority(u, supplier), audit_order[u], u))
    maximum = policy["maxDocumentsPerSource"]
    selected = current[:maximum]
    selected += audit[:min(policy["maxAuditDocumentsPerSource"], maximum - len(selected))]
    # Retained inventory also includes unchanged, not-yet-due successes. Those
    # remain in the engine's inventory object without becoming pending again.
    return selected, sorted((set(current) | set(audit)) - set(selected))
