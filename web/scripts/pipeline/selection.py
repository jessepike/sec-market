"""Bound daily semantic work without asserting historical discovery completeness."""
from datetime import timedelta

from contracts import instant


def select_documents(found, history, policy, now):
    """Return current/delta work first and retain every deferred URL for audit.

    lastmod is only a scheduling hint, never evidence of a fact's effective date.
    A successful semantic check records the index signature and check time. Changed
    index signatures are revisited immediately; unchanged documents rotate through
    the audit queue after the current window. Unknown dates never become current.
    """
    items = set(found["items"])
    modified = found.get("itemModified", {})
    cutoff = (instant(now) - timedelta(days=policy["currentWindowDays"])).date().isoformat()
    current, audit = [], []
    for url in sorted(items):
        stamp = modified.get(url, "")
        old = history.get(url)
        changed = old is not None and old.get("modified", "") != stamp
        recent = cutoff <= stamp[:10] <= now[:10] if stamp else False
        due = old is None or old.get("checkedAt", "")[:10] < cutoff
        if changed or (recent and due):
            current.append(url)
        elif due:
            audit.append(url)
    current.sort(key=lambda u: (modified.get(u, ""), u), reverse=True)
    # Oldest successful audit first. New, undated pages use stable URL order.
    audit.sort(key=lambda u: (history.get(u, {}).get("checkedAt", ""), u))
    maximum = policy["maxDocumentsPerSource"]
    selected = current[:maximum]
    selected += audit[:min(policy["maxAuditDocumentsPerSource"], maximum - len(selected))]
    return selected, sorted(items - set(selected))
