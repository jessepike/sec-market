"""Pure Cyera finite-list evidence. Calendar dates never establish event times."""
import csv
import io
import json
import re
from datetime import datetime, timedelta, timezone
from urllib.parse import unquote

from contracts import digest, instant, require
from discovery import IndexMarkup, IndexNode
from prnewswire_press_list import _walk, _active
from q4_press_list import _object, _constant

VERSION = 'cyera-press-list-finite-html-v1'
SOURCE = 'cyera:official:1'
INDEX = 'https://www.cyera.com/newsroom/press-releases'
COLLECTION = '694bb73db5c685fb23d95442'
CSV_FIELDS = ['rowIndex', 'sourceId', 'url', 'title', 'dateLiteral', 'calendarDay', 'timezone',
              'cmsCollectionId', 'cmsItemId', 'currentWindow', 'knownSeed']


class _Markup(IndexMarkup):
    def handle_starttag(self, tag, attrs):
        require(tag != 'base', 'CYERA_LIST_BASE_FORBIDDEN')
        self.count = getattr(self, 'count', 0) + 1
        require(self.count <= 50_000, 'CYERA_LIST_NODE_BOUND')
        require(len(attrs) == len(dict(attrs)), 'CYERA_LIST_DUPLICATE_ATTRIBUTES')
        super().handle_starttag(tag, attrs)

    def handle_startendtag(self, tag, attrs):
        require(tag in self.VOID or tag in {'path', 'circle', 'rect', 'polygon', 'line', 'polyline', 'ellipse', 'use'}
                and any(n.tag == 'svg' for n in self.stack), 'CYERA_LIST_SELF_CLOSING_CONTEXT')
        super().handle_startendtag(tag, attrs)


def _one(nodes, label):
    require(len(nodes) == 1, 'CYERA_LIST_' + label + '_AMBIGUOUS')
    node = nodes[0]
    while node.parent:
        require(node.closed and _active(node), 'CYERA_LIST_' + label + '_INACTIVE_OR_UNCLOSED')
        node = node.parent
    return nodes[0]


def _text(node):
    require(all(n.closed and _active(n) for n in _walk(node)), 'CYERA_LIST_INERT_OR_UNCLOSED_TEXT')
    return ' '.join(node.text.split())


def inventory_csv(stream):
    out = io.StringIO(newline='')
    writer = csv.DictWriter(out, fieldnames=CSV_FIELDS)
    writer.writeheader()
    for row in stream['records']:
        writer.writerow({k: (row[k] if k in row else row['url'] in stream['currentWindowItems'] if k == 'currentWindow'
                             else row['url'] in stream['knownSeedUrls']) for k in CSV_FIELDS})
    return out.getvalue().encode('utf-8')


def parse_press_list(raw, source_id, as_of, window_days=30, seed_urls=()):
    require(source_id == SOURCE and type(raw) is bytes and 0 < len(raw) <= 2_000_000, 'CYERA_LIST_SOURCE_OR_BYTES')
    require(type(window_days) is int and window_days == 30, 'CYERA_LIST_WINDOW')
    require(isinstance(seed_urls, (list, tuple)) and len(set(seed_urls)) == len(seed_urls), 'CYERA_LIST_SEEDS')
    markup = _Markup(raw.decode('utf-8', errors='strict'))
    nodes = list(_walk(markup.root))
    canonical = _one([n for n in nodes if n.tag == 'link' and 'canonical' in n.attrs.get('rel', '').split()], 'CANONICAL')
    require(canonical.attrs.get('href') == INDEX, 'CYERA_LIST_CANONICAL_DIFFERS')
    heading = _one([n for n in nodes if n.tag == 'h1'], 'HEADING')
    require(_text(heading) == 'Cyera press releases', 'CYERA_LIST_HEADING_DIFFERS')
    wrapper = _one([n for n in nodes if n.tag == 'div' and {'card_list-wrapper', 'w-dyn-list'} <= n.classes], 'WRAPPER')
    require(all(n.closed and _active(n) for n in _walk(wrapper)), 'CYERA_LIST_INACTIVE_OR_UNCLOSED_SUBTREE')
    listing = _one([n for n in nodes if n.tag == 'div' and {'card_list', 'w-dyn-items'} <= n.classes], 'LIST')
    require(listing.parent is wrapper, 'CYERA_LIST_PATH_DIFFERS')
    cards = [n for n in nodes if n.tag == 'div' and {'card_item', 'w-dyn-item'} <= n.classes]
    require(cards and all(n.parent is listing for n in cards) and
            all(c in cards if isinstance(c, IndexNode) else not c.strip() for c in listing.children), 'CYERA_LIST_CARD_INVENTORY')
    # Continuations in or immediately beside this CMS list are unsupported evidence.
    scope = list(_walk(wrapper.parent))
    require(not any({'w-pagination-wrapper', 'w-pagination-next', 'w-pagination-previous'} & n.classes or
                    any(re.search(r'pagination|loadmore|load-more|fs-cmsload|fs-list|data-page|data-next', k, re.I)
                        for k in n.attrs) or
                    n.tag == 'link' and {'next', 'prev'} & set(n.attrs.get('rel', '').lower().split())
                    for n in scope + [n for n in nodes if n.tag == 'link']), 'CYERA_LIST_CONTINUATION_UNPROVED')
    day = instant(as_of).astimezone(timezone.utc).date()
    cutoff = day - timedelta(days=window_days)
    rows, urls, ids, previous = [], set(), set(), None
    for index, card in enumerate(cards):
        _one([card], 'CARD')
        descendants = list(_walk(card))
        link = _one([n for n in descendants if n.tag == 'a' and {'card_item-link', 'w-inline-block'} <= n.classes], 'LINK')
        date = _one([n for n in descendants if n.tag == 'div' and 'card_date' in n.classes], 'DATE')
        title = _one([n for n in descendants if n.tag == 'h3'], 'TITLE')
        require(date.inside(link) and title.inside(link), 'CYERA_LIST_CARD_PATH_DIFFERS')
        href = link.attrs.get('href')
        require(isinstance(href, str) and re.fullmatch(r'(?:https://www\.cyera\.com)?/press-releases/[a-z0-9]+(?:-[a-z0-9]+)*', href),
                'CYERA_LIST_DETAIL_URL_INVALID')
        url = href if href.startswith('https://') else 'https://www.cyera.com' + href
        cms = json.loads(unquote(link.attrs.get('data-wf-cms-context', '')), object_pairs_hook=_object, parse_constant=_constant)
        require(type(cms) is list and len(cms) == 1 and type(cms[0]) is dict and
                set(cms[0]) == {'collectionId', 'itemId'} and cms[0]['collectionId'] == COLLECTION and
                isinstance(cms[0]['itemId'], str) and re.fullmatch('[a-f0-9]{24}', cms[0]['itemId']), 'CYERA_LIST_CMS_IDENTITY')
        literal, headline = _text(date), _text(title)
        require(headline and re.fullmatch(r'[A-Z][a-z]{2} \d{1,2}, \d{4}', literal), 'CYERA_LIST_DATE_OR_TITLE_INVALID')
        stamp = datetime.strptime(literal, '%b %d, %Y').date()
        require(previous is None or stamp <= previous, 'CYERA_LIST_UNORDERED_DATE')
        require(url not in urls and cms[0]['itemId'] not in ids, 'CYERA_LIST_DUPLICATE_IDENTITY')
        previous = stamp; urls.add(url); ids.add(cms[0]['itemId'])
        rows.append({'rowIndex': index, 'sourceId': source_id, 'url': url, 'title': headline, 'dateLiteral': literal,
                     'calendarDay': stamp.isoformat(), 'timezone': None, 'cmsCollectionId': COLLECTION, 'cmsItemId': cms[0]['itemId']})
    current = [r['url'] for r in rows if cutoff.isoformat() <= r['calendarDay'] <= day.isoformat()]
    older = [r['url'] for r in rows if r['calendarDay'] < cutoff.isoformat()]
    future = [r['url'] for r in rows if r['calendarDay'] > day.isoformat()]
    boundary = [r['url'] for r in rows if r['calendarDay'] in (cutoff.isoformat(), day.isoformat())]
    membership = {url: url in urls for url in seed_urls}
    return {'parserVersion': VERSION, 'sourceId': source_id, 'asOf': as_of, 'windowStart': cutoff.isoformat(),
            'windowEnd': day.isoformat(), 'timezone': None, 'records': rows, 'recordsSha256': digest(rows),
            'items': sorted(urls), 'itemsSha256': digest(sorted(urls)), 'knownSeedUrls': list(seed_urls),
            'knownSeedMembership': membership, 'knownSeedMembershipSha256': digest([r['url'] for r in rows if r['url'] in seed_urls]),
            'currentWindowItems': current, 'historicalItems': older, 'undeterminedWindowItems': future,
            'boundaryAmbiguousItems': boundary, 'sourceDateAnomalies': [{'url': url, 'reason': 'FUTURE_PUBLICATION_CALENDAR_UNRESOLVED'} for url in future],
            'olderBoundaryPresent': bool(older), 'dailyWindowComplete': bool(older) and not future and not boundary,
            'currentWindowQuiet': bool(older) and not current and not future and not boundary}
