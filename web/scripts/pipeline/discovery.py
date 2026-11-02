"""Source discovery with explicit pagination completeness, never empty=success."""
import json
import gzip
import io
import re
import zlib
from datetime import date, datetime, timedelta, timezone
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from urllib.parse import urljoin, urlsplit

from contracts import digest, require, instant, utcnow
from regulatory import SEC_FILING_FORMS
from q4_press_list import VERSION as Q4_LEGACY_PROFILE, NULL_OVERRIDE_VERSION as Q4_CURRENT_PROFILE


MAX_DISCOVERY_BYTES = 32_000_000
ORCA_HTML_MODE = "orca-news-pagination-v1"
PING_HTML_MODE = "ping-release-pagination-v1"
PING_HTML_MODE_V2 = "ping-release-pagination-v2"
PING_HTML_MODE_V3 = "ping-release-pagination-v3"
PING_INDEX = "https://press.pingidentity.com/news-releases"
DELINEA_HTML_MODE = 'delinea-news-pagination-v1'
DELINEA_HTML_MODE_V2 = 'delinea-news-pagination-v2'
DELINEA_HTML_MODE_V3 = 'delinea-news-pagination-v3'
DELINEA_HTML_MODE_V4 = 'delinea-news-pagination-v4'
DELINEA_HTML_MODE_V5 = 'delinea-news-pagination-v5'
DELINEA_INDEX = 'https://delinea.com/news'
SONATYPE_HTML_MODE = 'sonatype-press-pagination-v1'
SONATYPE_HTML_MODE_V2 = 'sonatype-press-pagination-v2'
SONATYPE_HTML_MODE_V3 = 'sonatype-press-pagination-v3'
SONATYPE_HTML_MODE_V4 = 'sonatype-press-pagination-v4'
SONATYPE_HTML_MODE_V5 = 'sonatype-press-pagination-v5'
SONATYPE_INDEX = 'https://www.sonatype.com/press-releases'
SONATYPE_V5_PUBLISHER_LEAD_URL = (
    'https://www.sonatype.com/press-releases/resources/state-of-the-software-supply-chain-2022/'
    'establishment-and-expansion-of-software-supply-chain-regulation-standards')


def ping_index_number(url):
    require(isinstance(url, str) and not any(ord(c) <= 32 or ord(c) == 127 for c in url), 'Unsafe Ping index URL text')
    parsed = urlsplit(url)
    require(parsed.scheme == 'https' and parsed.netloc == 'press.pingidentity.com' and
            parsed.path == '/news-releases' and not parsed.fragment, 'Unsafe Ping index destination')
    require(not parsed.query or re.fullmatch(r'o=(0|[1-9]\d*)', parsed.query), 'Unknown Ping index query')
    offset = int(parsed.query[2:]) if parsed.query else 0
    require(offset % 10 == 0, 'Ping offset must follow observed ten-item pages')
    return offset // 10 + 1


def ping_article_date(path, mode):
    """Return an explicitly encoded valid V2/V3 Ping route date, if present."""
    if not isinstance(path, str):
        return None
    if mode not in (PING_HTML_MODE_V2, PING_HTML_MODE_V3):
        return None
    compact = re.fullmatch(r'/(\d{6}-\d{2})-[A-Za-z0-9_,-]+', path)
    if compact:
        try:
            return datetime.strptime(compact.group(1), '%Y%m-%d').date().isoformat()
        except ValueError:
            return None
    if mode == PING_HTML_MODE_V3:
        dated = re.fullmatch(r'/(\d{4})-(\d{1,2})-(\d{1,2})-([A-Za-z0-9_,-]+)', path)
        if dated:
            try:
                return date(int(dated.group(1)), int(dated.group(2)), int(dated.group(3))).isoformat()
            except ValueError:
                return None
    return None


def _v3_literal_article_href(href):
    """Reject route syntax that URL resolution could normalize before V3 checks."""
    require(isinstance(href, str) and href and
            not any(ord(char) <= 32 or ord(char) == 127 for char in href) and
            '%' not in href and '\\' not in href,
            'Unsafe V3 literal article URL')
    parsed = urlsplit(href)
    require(not (parsed.netloc and not parsed.scheme), 'Unsafe V3 protocol-relative article URL')
    segments = parsed.path.split('/')
    if parsed.path.startswith('/'):
        segments = segments[1:]
    require(bool(segments) and all(segment and segment not in ('.', '..') for segment in segments),
            'Unsafe V3 literal article path')


def ping_index(source, url, body, highest_page, as_of):
    require(source['kind'] == 'html_index' and source['id'] == 'ping-identity:official:1' and
            source['supplierId'] == 'ping-identity' and source['family'] == 'official_announcements' and
            source['allowedHosts'] == ['press.pingidentity.com'] and source['url'] == PING_INDEX and
            type(source['maxPages']) is int and 1 <= source['maxPages'] <= 60 and
            source.get('htmlCompleteness') in (PING_HTML_MODE, PING_HTML_MODE_V2, PING_HTML_MODE_V3),
            'Ping HTML mode requires its exact supplier/source binding')
    current = ping_index_number(url)
    nodes = list(IndexMarkup(body.decode('utf8', errors='strict')).root.walk())
    def one(values, label):
        require(len(values) == 1 and values[0].closed, 'Missing or ambiguous Ping ' + label)
        return values[0]
    canonical = one([n for n in nodes if n.tag == 'link' and 'canonical' in n.attrs.get('rel','').split()], 'canonical link')
    require(canonical.attrs.get('href') == PING_INDEX, 'Unexpected Ping canonical index')
    require(not any(n.tag == 'link' and {'next', 'prev'} & set(n.attrs.get('rel','').lower().split()) for n in nodes),
            'Unqualified Ping head pagination signal')
    region = one([n for n in nodes if n.tag == 'div' and 'wd_newsfeed_releases' in n.classes], 'release region')
    listing = one([n for n in nodes if n.tag == 'ul' and 'wd_item_list' in n.classes and n.inside(region)], 'card list')
    cards = [n for n in listing.walk() if n.tag == 'li' and 'wd_item' in n.classes]
    require(bool(cards), 'Ping has no qualified static cards')
    require(all(c in cards if isinstance(c, IndexNode) else not c.strip() for c in listing.children), 'Unknown Ping card-list content')
    dates, ordered_dates = {}, []
    for card in cards:
        require(card.closed and card.parent is listing, 'Invalid Ping card structure')
        descendants = list(card.walk())
        title = one([n for n in descendants if 'wd_title' in n.classes], 'card title')
        link = one([n for n in title.walk() if n.tag == 'a'], 'title link')
        require(link.text.strip() and link.attrs.get('href'), 'Empty Ping title link')
        require(not any(ord(c) <= 32 or ord(c) == 127 for c in link.attrs['href']), 'Control or whitespace in Ping article URL')
        if source['htmlCompleteness'] == PING_HTML_MODE_V3:
            _v3_literal_article_href(link.attrs['href'])
        target = urljoin(url, link.attrs['href']); parsed = urlsplit(target)
        path_ok = bool(re.fullmatch(r'/\d{4}-\d{2}-\d{2}-[A-Za-z0-9_,-]+', parsed.path))
        compact_day = None
        if source['htmlCompleteness'] in (PING_HTML_MODE_V2, PING_HTML_MODE_V3):
            compact_route = re.fullmatch(r'/\d{6}-\d{2}-[A-Za-z0-9_,-]+', parsed.path)
            v3_dated_route = (source['htmlCompleteness'] == PING_HTML_MODE_V3 and
                              re.fullmatch(r'/\d{4}-\d{1,2}-\d{1,2}-[A-Za-z0-9_,-]+', parsed.path))
            if compact_route or v3_dated_route:
                compact_day = ping_article_date(parsed.path, source['htmlCompleteness'])
                path_ok = compact_day is not None
        require(parsed.scheme == 'https' and parsed.netloc == 'press.pingidentity.com' and not parsed.query and not parsed.fragment
                and path_ok, 'Unsafe Ping article path')
        stamp = one([n for n in descendants if 'wd_date' in n.classes], 'card date').text.strip()
        require(re.fullmatch(r'[A-Z][a-z]{2} \d{2}, \d{4}', stamp), 'Malformed Ping card date')
        day = datetime.strptime(stamp, '%b %d, %Y').date().isoformat()
        require(compact_day is None or compact_day == day, 'Ping compact article date differs from card date')
        require(day <= instant(as_of).astimezone(timezone.utc).date().isoformat(), 'Future Ping card date')
        require(target not in dates, 'Duplicate Ping card URL')
        dates[target] = day; ordered_dates.append(day)
    require(ordered_dates == sorted(ordered_dates, reverse=True), 'Ping card dates out of order')
    paging = one([n for n in nodes if n.tag == 'ul' and 'wd_page_links' in n.classes and n.inside(region)], 'pagination')
    controls = [n for n in paging.children if isinstance(n, IndexNode)]
    require(all(n.tag == 'li' and n.closed and 'wd_page_link' in n.classes for n in controls), 'Unknown Ping pagination control')
    require(all(isinstance(n, IndexNode) or not n.strip() for n in paging.children), 'Unknown Ping pagination text')
    active = one([n for n in controls if 'wd_page_active' in n.classes], 'active page')
    marker = one([n for n in active.walk() if n.tag == 'span' and n.attrs.get('aria-current') == 'page'], 'active marker')
    require(marker.text.strip() == str(current) and not any(n.tag == 'a' for n in active.walk()), 'Ping active page mismatch')
    numbered, next_urls, previous, sequence, disabled_next = {}, [], [], [], False
    for control in controls:
        roles = control.classes - {'wd_page_link'}
        require(len(roles) == 1 and roles <= {'wd_page_active','wd_page_prev','wd_page_next','wd_page_start','wd_page_mid1','wd_page_mid2','wd_page_end','wd_page_skip1','wd_page_skip2'}, 'Unknown Ping page role')
        role = next(iter(roles)); children = [n for n in control.children if isinstance(n, IndexNode)]
        child = one(children, 'page control child')
        require(child.tag in ('a','span') and not any(n.tag in ('a','button','form','select') for n in child.walk() if n is not child), 'Unknown Ping page control')
        if role.startswith('wd_page_skip'):
            require(child.tag == 'span' and child.text.strip() == '…', 'Invalid Ping ellipsis'); sequence.append(None); continue
        if role == 'wd_page_active':
            sequence.append(current); continue
        if role == 'wd_page_prev' and current == 1:
            require(child.tag == 'span' and child.text.strip() == '«', 'Invalid Ping disabled previous'); previous.append(None); continue
        if role == 'wd_page_next' and child.tag == 'span':
            require(not disabled_next and not child.attrs.get('href') and child.text.strip() == '»', 'Invalid Ping disabled next')
            disabled_next = True; continue
        require(child.tag == 'a' and child.attrs.get('href'), 'Unproved Ping disabled control')
        target = _index_target(url, child.attrs['href']); number = ping_index_number(target)
        if role == 'wd_page_next':
            require(number == current + 1 and child.text.strip() == '»', 'Ping next loop or gap'); next_urls.append(target)
        elif role == 'wd_page_prev':
            require(number == current - 1 and child.text.strip() == '«', 'Ping previous mismatch'); previous.append(target)
        else:
            if role == 'wd_page_start':
                require(current > 1 and number == 1, 'Invalid Ping start page')
            require(child.text.strip() == str(number) and number not in numbered and number != current, 'Ping numbered page mismatch or duplicate')
            numbered[number] = target; sequence.append(number)
    require(len(previous) == 1 and len(next_urls) <= 1, 'Missing or duplicate Ping directional control')
    require(sequence and sequence[0] == 1 and sequence[-1] is not None, 'Incomplete Ping advertised page sequence')
    for i, number in enumerate(sequence):
        if number is None:
            require(0 < i < len(sequence)-1 and sequence[i-1] is not None and sequence[i+1] is not None and sequence[i+1] > sequence[i-1]+1, 'Invalid Ping advertised gap')
        elif i and sequence[i-1] is not None:
            require(number == sequence[i-1]+1, 'Ping missing sequential page control')
    highest_page = max(highest_page, *numbered, current)
    if next_urls:
        require(not disabled_next and numbered.get(current+1) == next_urls[0] and len(cards) == 10, 'Conflicting Ping next/numbered controls or page size')
    if disabled_next:
        require(not next_urls and current == highest_page and sequence[-1] == current and len(cards) <= 10,
                'Unproved Ping terminal page')
    return {'items': set(dates), 'dates': dates, 'highestPage': highest_page,
            'currentPage': current, 'terminalProved': disabled_next,
            'next': next_urls[0] if next_urls else None, 'lastDate': ordered_dates[-1], 'firstDate': ordered_dates[0]}


def decoded_discovery_body(body):
    """A bounded parsing view; callers retain the original archived object."""
    if body.startswith(b"\x1f\x8b"):
        try:
            with gzip.GzipFile(fileobj=io.BytesIO(body)) as compressed:
                body = compressed.read(MAX_DISCOVERY_BYTES + 1)
        except (OSError, EOFError, zlib.error) as exc:
            raise ValueError("Invalid compressed discovery body") from exc
    require(len(body) <= MAX_DISCOVERY_BYTES, "Decoded discovery body exceeds byte budget")
    return body


class IndexNode:
    def __init__(self, tag, attrs=(), parent=None):
        self.tag, self.attrs, self.parent = tag, {key: '' if value is None else value for key, value in attrs}, parent
        self.children = []
        self.closed = False

    @property
    def classes(self):
        return set(self.attrs.get("class", "").split())

    def walk(self):
        if self.tag in ("script", "style", "template", "noscript"):
            return
        yield self
        for child in self.children:
            if isinstance(child, IndexNode):
                yield from child.walk()

    @property
    def text(self):
        if self.tag in ("script", "style", "template", "noscript"):
            return ""
        return " ".join(c.text if isinstance(c, IndexNode) else c for c in self.children)

    def inside(self, ancestor):
        parent = self.parent
        while parent:
            if parent is ancestor:
                return True
            parent = parent.parent
        return False


class IndexMarkup(HTMLParser):
    """Only structural HTML is inspected; scripts and templates never supply cards."""
    VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}

    def __init__(self, html):
        super().__init__(convert_charrefs=True)
        self.root = IndexNode("document")
        self.stack = [self.root]
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        require(len(self.stack) <= 256, "Discovery markup nesting exceeds bound")
        node = IndexNode(tag, attrs, self.stack[-1])
        self.stack[-1].children.append(node)
        if tag not in self.VOID:
            self.stack.append(node)
        else:
            node.closed = True

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in self.VOID:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        for index in range(len(self.stack)-1, 0, -1):
            if self.stack[index].tag == tag:
                self.stack[index].closed = True
                del self.stack[index:]
                break

    def handle_data(self, data):
        self.stack[-1].children.append(data)


def _index_one(values, label):
    require(len(values) == 1 and values[0].closed, 'Missing or ambiguous ' + label)
    return values[0]


def _index_target(base, href):
    require(isinstance(href, str) and href and not any(ord(c) <= 32 or ord(c) == 127 for c in href)
            and '%' not in href and '\\' not in href and
            not any(part in ('.', '..') for part in urlsplit(href).path.split('/')),
            'Unsafe HTML index literal URL')
    return urljoin(base, href)


def html_index_number(url, mode):
    """Strict request/continuation grammar for the two observed archive roots."""
    delinea = mode in (DELINEA_HTML_MODE, DELINEA_HTML_MODE_V2, DELINEA_HTML_MODE_V3,
                       DELINEA_HTML_MODE_V4, DELINEA_HTML_MODE_V5)
    root = DELINEA_INDEX if delinea else SONATYPE_INDEX
    require(mode in (DELINEA_HTML_MODE, DELINEA_HTML_MODE_V2, DELINEA_HTML_MODE_V3, DELINEA_HTML_MODE_V4,
                     DELINEA_HTML_MODE_V5, SONATYPE_HTML_MODE, SONATYPE_HTML_MODE_V2,
                     SONATYPE_HTML_MODE_V3, SONATYPE_HTML_MODE_V4, SONATYPE_HTML_MODE_V5),
            'Unknown HTML index mode')
    require(isinstance(url, str) and not any(ord(c) <= 32 or ord(c) == 127 for c in url), 'Unsafe HTML index URL text')
    parsed, expected = urlsplit(url), urlsplit(root)
    require(parsed.scheme == 'https' and parsed.netloc == expected.netloc and not parsed.fragment,
            'Unsafe HTML index destination')
    if delinea:
        require(not parsed.query, 'Unknown Delinea index query')
        match = re.fullmatch(r'/news(?:/page/([1-9]\d*))?', parsed.path)
        require(match is not None and (not match[1] or int(match[1]) >= 2), 'Unknown Delinea index path')
        return int(match[1] or 1)
    require(parsed.path == expected.path and (not parsed.query or re.fullmatch(r'page=[1-9]\d*', parsed.query)),
            'Unknown Sonatype index query or path')
    return int(parsed.query[5:]) if parsed.query else 1


def _html_archive(source, url, body, mode):
    delinea = mode in (DELINEA_HTML_MODE, DELINEA_HTML_MODE_V2, DELINEA_HTML_MODE_V3,
                       DELINEA_HTML_MODE_V4, DELINEA_HTML_MODE_V5)
    supplier = 'delinea' if delinea else 'sonatype'
    root = DELINEA_INDEX if delinea else SONATYPE_INDEX
    host = urlsplit(root).netloc
    require(source['kind'] == 'html_index' and source['id'] == supplier + ':official:1' and
            source['supplierId'] == supplier and source['family'] == 'official_announcements' and
            source['allowedHosts'] == [host] and source['url'] == root and type(source['maxPages']) is int and
            1 <= source['maxPages'] <= 60 and source.get('htmlCompleteness') == mode,
            'HTML archive requires its exact supplier/source binding')
    current = html_index_number(url, mode)
    nodes = list(IndexMarkup(body.decode('utf8', errors='strict')).root.walk())
    canonical = _index_one([n for n in nodes if n.tag == 'link' and 'canonical' in n.attrs.get('rel', '').split()], supplier + ' canonical')
    head = _index_one([n for n in nodes if n.tag == 'head'], supplier + ' head')
    require(canonical.inside(head) and canonical.attrs.get('href') == root, 'HTML archive canonical differs')
    require(all(n.inside(head) for n in nodes if n.tag == 'link' and
                {'next', 'prev'} & set(n.attrs.get('rel', '').lower().split())), 'HTML pagination link outside head')
    return current, nodes


def _archive_article_url(base, href, mode):
    if mode in (DELINEA_HTML_MODE_V3, SONATYPE_HTML_MODE_V3, DELINEA_HTML_MODE_V4,
                SONATYPE_HTML_MODE_V4, DELINEA_HTML_MODE_V5, SONATYPE_HTML_MODE_V5):
        _v3_literal_article_href(href)
    target = _index_target(base, href)
    parsed = urlsplit(target)
    delinea = mode in (DELINEA_HTML_MODE, DELINEA_HTML_MODE_V2, DELINEA_HTML_MODE_V3,
                       DELINEA_HTML_MODE_V4, DELINEA_HTML_MODE_V5)
    root = urlsplit(DELINEA_INDEX if delinea else SONATYPE_INDEX)
    prefix = '/news/' if delinea else '/press-releases/'
    path_match = bool(re.fullmatch(re.escape(prefix) + r'[a-z0-9]+(?:-[a-z0-9]+)*', parsed.path))
    if mode == DELINEA_HTML_MODE_V2:
        path_match = bool(re.fullmatch(re.escape(prefix) + r'[a-z0-9]+(?:-[a-z0-9]+)*-?', parsed.path))
    if mode in (DELINEA_HTML_MODE_V3, DELINEA_HTML_MODE_V4, DELINEA_HTML_MODE_V5):
        reserved = {'page', 'pages', 'news', 'press-releases'}
        direct = re.fullmatch(re.escape(prefix) + r'([a-z0-9]+(?:-[a-z0-9]+)*-?)', parsed.path)
        historical = re.fullmatch(r'/news/about-us/news/press-releases/[0-9]{4}/([a-z0-9]+(?:-[a-z0-9]+)*)', parsed.path)
        direct_slug = direct.group(1).rstrip('-') if direct else ''
        historical_slug = historical.group(1) if historical else ''
        path_match = bool((direct and direct_slug not in reserved and not direct_slug.isdigit()) or
                          (historical and historical_slug not in reserved and not historical_slug.isdigit()))
        if mode in (DELINEA_HTML_MODE_V4, DELINEA_HTML_MODE_V5):
            dated_company_blog = re.fullmatch(
                r'/news/company/blog/([0-9]{4})/([0-9]{2})/([0-9]{2})/([a-z0-9]+(?:-[a-z0-9]+)*)',
                parsed.path)
            if dated_company_blog:
                try:
                    date(*(int(part) for part in dated_company_blog.groups()[:3]))
                    blog_slug = dated_company_blog.group(4)
                    path_match = blog_slug not in reserved and not blog_slug.isdigit()
                except ValueError:
                    path_match = False
    if mode == SONATYPE_HTML_MODE_V2 and parsed.path == (
            '/press-releases/sonatype-introduces-cutting-edge-ai/ml-component-detection'):
        path_match = True
    if mode in (SONATYPE_HTML_MODE_V3, SONATYPE_HTML_MODE_V4, SONATYPE_HTML_MODE_V5):
        final_slug = r'[a-z0-9]+(?:-[a-z0-9]+)*' + ('-?' if mode in (SONATYPE_HTML_MODE_V4, SONATYPE_HTML_MODE_V5) else '')
        direct = re.fullmatch(r'/press-releases/(' + final_slug + r')', parsed.path)
        nested = re.fullmatch(r'/press-releases/([a-z0-9]+(?:-[a-z0-9]+)*)/(' + final_slug + r')', parsed.path)
        segments = (direct.groups() if direct else nested.groups() if nested else ())
        reserved = {'page', 'pages', 'news', 'press-releases'}
        checked_segments = tuple(segment.rstrip('-') for segment in segments) if mode in (SONATYPE_HTML_MODE_V4, SONATYPE_HTML_MODE_V5) else segments
        path_match = bool(checked_segments) and all(segment not in reserved and not segment.isdigit()
                                                    for segment in checked_segments)
    if mode == SONATYPE_HTML_MODE_V5 and parsed.path == urlsplit(SONATYPE_V5_PUBLISHER_LEAD_URL).path:
        path_match = True
    require(parsed.scheme == 'https' and parsed.netloc == root.netloc and not parsed.query and not parsed.fragment
            and path_match, 'Unsafe HTML archive article path')
    return target


def delinea_index(source, url, body, highest_page, as_of):
    mode = source.get('htmlCompleteness')
    current, nodes = _html_archive(source, url, body, mode)
    instant(as_of)
    region = _index_one([n for n in nodes if n.tag == 'section' and 'blog-index' in n.classes], 'Delinea cards')
    cards = [n for n in nodes if n.tag == 'article' and 'blog-index__post' in n.classes]
    require(0 < len(cards) <= 12 and all(n.closed and n.parent is region for n in cards), 'Invalid Delinea card inventory')
    items = set()
    for card in cards:
        title = _index_one([n for n in card.walk() if n.tag == 'h2' and 'blog-index__post-title' in n.classes], 'Delinea title')
        link = _index_one([n for n in title.walk() if n.tag == 'a' and 'blog-index__post-title-link' in n.classes], 'Delinea title link')
        require(link.text.strip(), 'Empty Delinea title')
        target = _archive_article_url(url, link.attrs.get('href'), mode)
        image = _index_one([n for n in card.walk() if n.tag == 'a' and 'blog-index__post-image-wrapper' in n.classes], 'Delinea image link')
        require(_archive_article_url(url, image.attrs.get('href'), mode) == target and target not in items,
                'Duplicate or conflicting Delinea article')
        items.add(target)
    paging = _index_one([n for n in nodes if n.tag == 'nav' and 'blog-pagination' in n.classes], 'Delinea pagination')
    require(paging.attrs.get('role') == 'navigation' and paging.attrs.get('aria-label') == 'Pagination' and
            not any(n.tag in ('button', 'form', 'select') for n in paging.walk()), 'Unknown Delinea pagination structure')
    anchors = [n for n in paging.walk() if n.tag == 'a']
    allowed = {'blog-pagination__link', 'blog-pagination__prev-link', 'blog-pagination__prev-link--disabled',
               'blog-pagination__next-link', 'blog-pagination__next-link--disabled',
               'blog-pagination__number-link', 'blog-pagination__link--active'}
    require(all(n.closed and n.parent is paging and 'blog-pagination__link' in n.classes and n.classes <= allowed and
                len(n.classes & {'blog-pagination__prev-link', 'blog-pagination__next-link', 'blog-pagination__number-link'}) == 1
                for n in anchors), 'Unknown Delinea pagination control')
    previous = _index_one([n for n in anchors if 'blog-pagination__prev-link' in n.classes], 'Delinea previous')
    require(previous.text.strip() == 'Prev', 'Delinea previous label differs')
    if current == 1:
        require('blog-pagination__prev-link--disabled' in previous.classes and not previous.attrs.get('href'), 'Delinea first previous differs')
    else:
        require('blog-pagination__prev-link--disabled' not in previous.classes and
                html_index_number(_index_target(url, previous.attrs.get('href')), mode) == current - 1,
                'Delinea previous mismatch')
    numbered, active = [], []
    for n in [n for n in anchors if 'blog-pagination__number-link' in n.classes]:
        number = html_index_number(_index_target(url, n.attrs.get('href')), mode)
        require(n.text.strip() == str(number), 'Delinea numbered label differs')
        numbered.append(number)
        if 'blog-pagination__link--active' in n.classes or n.attrs.get('aria-current'):
            require('blog-pagination__link--active' in n.classes and n.attrs.get('aria-current') == 'true' and number == current,
                    'Delinea active page differs')
            active.append(n)
    require(len(active) == 1 and 1 <= len(numbered) <= 5 and numbered == list(range(min(numbered), max(numbered) + 1)),
            'Delinea numbered window differs')
    following = [n for n in anchors if 'blog-pagination__next-link' in n.classes]
    require(len(following) <= 1 and all(n.text.strip() == 'Next' for n in following) and
            all(n in anchors for n in nodes if n.tag == 'a' and
                n.classes & {'blog-pagination__prev-link', 'blog-pagination__next-link', 'blog-pagination__number-link'}),
            'Ambiguous or unscoped Delinea pagination')
    next_url = None
    if following and following[0].attrs.get('href'):
        require('blog-pagination__next-link--disabled' not in following[0].classes, 'Conflicting Delinea disabled next')
        next_url = _index_target(url, following[0].attrs['href'])
        require(html_index_number(next_url, mode) == current + 1 and current + 1 in numbered and len(cards) == 12,
                'Delinea next loop, gap or card-size change')
    head_next = [n for n in nodes if n.tag == 'link' and 'next' in n.attrs.get('rel', '').lower().split()]
    head_previous = [n for n in nodes if n.tag == 'link' and 'prev' in n.attrs.get('rel', '').lower().split()]
    expected_previous = DELINEA_INDEX + '/page/' + str(current - 1)
    require(len(head_previous) == (0 if current == 1 else 1) and
            all(_index_target(url, n.attrs.get('href')) == expected_previous for n in head_previous),
            'Conflicting Delinea head/visible previous')
    require(len(head_next) == (1 if next_url else 0) and all(_index_target(url, n.attrs.get('href')) == next_url for n in head_next),
            'Conflicting Delinea head/visible next')
    terminal = False
    if mode == DELINEA_HTML_MODE_V5 and following and not following[0].attrs.get('href'):
        disabled = following[0]
        expected_classes = {'blog-pagination__link', 'blog-pagination__next-link',
                            'blog-pagination__next-link--disabled'}
        require(disabled.classes == expected_classes and 'href' not in disabled.attrs
                and set(disabled.attrs) == {'class'} and disabled.text.strip() == 'Next',
                'Unproved Delinea disabled next control')
        require(not head_next and numbered == list(range(current - 4, current + 1))
                and current == max(highest_page, *numbered),
                'Unproved Delinea terminal page sequence')
        children = [child for child in disabled.children if isinstance(child, IndexNode)]
        require(all(isinstance(child, IndexNode) or not child.strip() for child in disabled.children)
                and len(children) == 2, 'Unknown Delinea disabled next descendants')
        label, icon = children
        require(label.tag == 'span' and label.closed and
                label.attrs == {'class': 'blog-pagination__link-text'} and label.text.strip() == 'Next' and
                all(isinstance(child, str) for child in label.children),
                'Unknown Delinea disabled next label')
        require(icon.tag == 'svg' and icon.closed and icon.attrs == {
                    'aria-hidden': 'true', 'version': '1.0', 'viewbox': '0 0 320 512', 'width': '13',
                    'xmlns': 'http://www.w3.org/2000/svg'},
                'Unknown Delinea disabled next icon')
        groups = [child for child in icon.children if isinstance(child, IndexNode)]
        require(all(isinstance(child, IndexNode) or not child.strip() for child in icon.children)
                and len(groups) == 1, 'Unknown Delinea disabled next icon contents')
        group = groups[0]
        require(group.tag == 'g' and group.closed and group.attrs == {'id': 'chevron-right3_layer'},
                'Unknown Delinea disabled next icon group')
        paths = [child for child in group.children if isinstance(child, IndexNode)]
        require(all(isinstance(child, IndexNode) or not child.strip() for child in group.children)
                and len(paths) == 1, 'Unknown Delinea disabled next icon paths')
        path = paths[0]
        require(path.tag == 'path' and path.closed and set(path.attrs) == {'d'} and not path.children and
                re.fullmatch(r'[MmLlHhVvCcSsQqTtAaZz0-9.,\s+-]{1,1024}', path.attrs['d']) is not None,
                'Unknown Delinea disabled next icon path')
        terminal = True
    elif mode == DELINEA_HTML_MODE_V5 and following:
        require(following[0].attrs.get('href'), 'Delinea next control has no proved disabled state')
    result = {'items': items, 'dates': {}, 'highestPage': max(highest_page, *numbered), 'currentPage': current,
              'next': next_url, 'terminalProved': terminal, 'firstDate': None, 'lastDate': None}
    if mode == DELINEA_HTML_MODE_V5:
        result['publisherLeadWarnings'] = []
    return result
    return {'items': items, 'dates': {}, 'highestPage': max(highest_page, *numbered), 'currentPage': current,
            'next': next_url, 'terminalProved': False, 'firstDate': None, 'lastDate': None}


def sonatype_index(source, url, body, highest_page, as_of):
    mode = source.get('htmlCompleteness')
    current, nodes = _html_archive(source, url, body, mode)
    region = _index_one([n for n in nodes if n.tag == 'div' and 'listing__grid' in n.classes], 'Sonatype cards')
    cards = [n for n in nodes if n.tag == 'div' and 'listing__grid-card' in n.classes]
    require(0 < len(cards) <= 16 and all(n.closed and n.parent is region for n in cards), 'Invalid Sonatype card inventory')
    dates, ordered, publisher_lead_warnings = {}, [], []
    for card in cards:
        content = _index_one([n for n in card.walk() if n.tag == 'div' and 'card-content' in n.classes], 'Sonatype card content')
        title = _index_one([n for n in content.walk() if n.tag == 'h3'], 'Sonatype title')
        link = _index_one([n for n in card.walk() if n.tag == 'a' and 'pr_link' in n.classes], 'Sonatype article link')
        require(title.text.strip(), 'Empty Sonatype title')
        target = _archive_article_url(url, link.attrs.get('href'), mode)
        meta = _index_one([n for n in content.walk() if n.tag == 'div' and 'card-content__meta' in n.classes], 'Sonatype date region')
        stamp = _index_one([n for n in meta.walk() if n.tag == 'p'], 'Sonatype date').text.strip()
        require(re.fullmatch(r'[A-Z][a-z]+ [0-9]{1,2}, [0-9]{4}', stamp), 'Malformed Sonatype card date')
        day = datetime.strptime(stamp, '%B %d, %Y').date().isoformat()
        require(day <= instant(as_of).astimezone(timezone.utc).date().isoformat() and target not in dates, 'Future date or duplicate Sonatype article')
        dates[target] = day; ordered.append(day)
        if mode == SONATYPE_HTML_MODE_V5 and target == SONATYPE_V5_PUBLISHER_LEAD_URL:
            publisher_lead_warnings.append({'url': target, 'cardTitle': title.text.strip(), 'indexDate': day,
                'reason': 'PUBLISHER_CARD_LINK_REQUIRES_PRIMARY_REVIEW'})
    require(ordered == sorted(ordered, reverse=True), 'Sonatype dates out of order')
    paging = _index_one([n for n in nodes if n.tag == 'div' and 'pagination' in n.classes], 'Sonatype pagination')
    require(not any(n.tag in ('button', 'form', 'select') for n in paging.walk()), 'Unknown Sonatype pagination structure')
    number_region = _index_one([n for n in paging.walk() if n.tag == 'ul' and 'pages' in n.classes], 'Sonatype page list')
    require(number_region.parent is paging and number_region.classes == {'pages', 'ps-0', 'mb-0'}, 'Unknown Sonatype page list')
    numbered, active, previous, following, disabled_next = [], [], [], [], []
    for n in [n for n in paging.walk() if n.tag == 'a']:
        require(n.closed, 'Unclosed Sonatype pagination link')
        if 'pagination-link' in n.classes:
            require(n.parent.tag == 'li' and n.parent.parent is number_region and
                    n.classes <= {'pagination-link', 'current-page'}, 'Unknown Sonatype numbered control')
            number = html_index_number(_index_target(url, n.attrs.get('href')), mode)
            require(n.text.strip() == str(number), 'Sonatype numbered label differs')
            numbered.append(number)
            if 'current-page' in n.classes:
                require(number == current, 'Sonatype active page differs'); active.append(n)
        else:
            parent = n.parent
            require(parent and parent.parent is paging and parent.tag == 'div' and 'pagination-btn' in parent.classes and
                    len(parent.classes & {'previous', 'next'}) == 1 and
                    parent.classes <= {'pagination-btn', 'previous', 'next', 'd-inline-block', 'mx-2', 'mx-md-3', 'hide'},
                    'Unknown Sonatype pagination control')
            if 'previous' in parent.classes:
                require(n.text.strip() == 'Prev', 'Sonatype previous label differs')
                if current == 1:
                    require('hide' in parent.classes and n.attrs.get('href') == '/press-releases?page=0#resource-grid',
                            'Sonatype first hidden previous differs')
                else:
                    require('hide' not in parent.classes and n.attrs.get('href') ==
                            '/press-releases?page=' + str(current - 1) + '#resource-grid',
                            'Sonatype previous mismatch')
                previous.append(n)
            else:
                require(n.text.strip() == 'Next', 'Sonatype next label differs')
                if 'hide' not in parent.classes:
                    target = _index_target(url, n.attrs.get('href'))
                    require(html_index_number(target, mode) == current + 1, 'Sonatype next loop or gap')
                    following.append(target)
                else:
                    require(n.attrs.get('href') == '/press-releases?page=' + str(current + 1), 'Unproved hidden Sonatype next target')
                    disabled_next.append(n)
    require(len(previous) == 1 and len(following) <= 1 and len(active) == 1 and numbered == sorted(set(numbered)) and
            len(numbered) <= 7, 'Sonatype directional or numbered controls differ')
    sequence = []
    for child in number_region.children:
        if isinstance(child, str):
            require(not child.strip(), 'Unknown Sonatype page-list text'); continue
        require(child.tag == 'li' and child.closed, 'Unknown Sonatype page-list child')
        anchors = [n for n in child.walk() if n.tag == 'a']
        if not anchors:
            require(child.text.strip() == '...', 'Unknown Sonatype page-list gap'); sequence.append(None)
        else:
            require(len(anchors) == 1 and anchors[0].parent is child, 'Ambiguous Sonatype page-list item')
            sequence.append(int(anchors[0].text.strip()))
    require(sequence and sequence[0] is not None and sequence[-1] is not None, 'Unbounded Sonatype page-list gap')
    for i, number in enumerate(sequence):
        if number is None:
            require(0 < i < len(sequence)-1 and sequence[i-1] is not None and sequence[i+1] is not None and
                    sequence[i+1] > sequence[i-1] + 1, 'Invalid Sonatype advertised gap')
        elif i and sequence[i-1] is not None:
            require(number == sequence[i-1] + 1, 'Sonatype missing numbered control')
    next_url = following[0] if following else None
    if next_url:
        require(not disabled_next and current + 1 in numbered and len(cards) == 16, 'Sonatype next/numbered controls or card size differ')
    highest_page = max(highest_page, *numbered)
    terminal = bool(disabled_next)
    if terminal:
        require(len(disabled_next) == 1 and not next_url and current == highest_page and numbered[-1] == current,
                'Unproved Sonatype terminal page')
    require(not any(n.tag == 'link' and {'next', 'prev'} & set(n.attrs.get('rel', '').lower().split()) for n in nodes),
            'Unproved Sonatype head pagination')
    result = {'items': set(dates), 'dates': dates, 'highestPage': highest_page, 'currentPage': current,
              'next': next_url, 'terminalProved': terminal, 'firstDate': ordered[0], 'lastDate': ordered[-1]}
    if mode == SONATYPE_HTML_MODE_V5:
        result['publisherLeadWarnings'] = publisher_lead_warnings
    return result


def parse_source_html_index(source, url, body, highest_page, as_of):
    """Pure source-bound layout evidence; caller owns transport and qualification."""
    modes = {PING_HTML_MODE: ping_index, PING_HTML_MODE_V2: ping_index, PING_HTML_MODE_V3: ping_index,
             DELINEA_HTML_MODE: delinea_index, DELINEA_HTML_MODE_V2: delinea_index,
             DELINEA_HTML_MODE_V3: delinea_index, DELINEA_HTML_MODE_V4: delinea_index,
             DELINEA_HTML_MODE_V5: delinea_index,
             SONATYPE_HTML_MODE: sonatype_index, SONATYPE_HTML_MODE_V2: sonatype_index,
             SONATYPE_HTML_MODE_V3: sonatype_index, SONATYPE_HTML_MODE_V4: sonatype_index,
             SONATYPE_HTML_MODE_V5: sonatype_index}
    require(source.get('htmlCompleteness') in modes, 'Unknown source HTML mode')
    require(type(highest_page) is int and highest_page >= 1, 'Invalid prior advertised HTML page')
    return modes[source['htmlCompleteness']](source, url, decoded_discovery_body(body), highest_page, as_of)


def orca_index_number(url):
    parsed = urlsplit(url)
    require(parsed.scheme == "https" and parsed.netloc == "orca.security" and not parsed.query and not parsed.fragment,
            "Unsafe Orca index destination")
    match = re.fullmatch(r"/resources/news/(?:page/([1-9]\d*)/)?", parsed.path)
    require(match is not None, "Unexpected Orca index path")
    return int(match.group(1) or 1)


def orca_index(source, url, body, highest_page):
    """Explicit candidate adapter for the archived Orca newsroom structure."""
    require(source["id"] == "orca:official:1" and source["supplierId"] == "orca" and
            source["family"] == "official_announcements" and source["allowedHosts"] == ["orca.security"] and
            source["url"] == "https://orca.security/resources/news/" and 1 <= source["maxPages"] <= 60,
            "Orca HTML mode requires its exact supplier/source binding")
    current_page = orca_index_number(url)
    nodes = list(IndexMarkup(body.decode("utf8", errors="strict")).root.walk())

    def one(values, label):
        require(len(values) == 1, "Missing or ambiguous Orca " + label)
        require(values[0].closed, "Unclosed Orca " + label)
        return values[0]

    head = one([n for n in nodes if n.tag == "head"], "head")
    newsroom = one([n for n in nodes if "newsroom-posts" in n.classes], "newsroom")
    listing = one([n for n in nodes if "newsroom-posts-listing" in n.classes and n.inside(newsroom)], "listing")
    cards_region = one([n for n in nodes if "orca-posts-container-newsroom" in n.classes and n.inside(listing)], "card container")
    pagination = one([n for n in nodes if {"orca-pagination", "archive-posts-results__show-more"} <= n.classes], "pagination")
    require(pagination.inside(newsroom), "Orca pagination outside newsroom")
    page_nodes = list(pagination.walk())
    marker = one([n for n in page_nodes if n.tag == "span" and {"page-numbers", "current"} <= n.classes and
                  n.attrs.get("aria-current") == "page"], "current page marker")
    require(marker.text.strip().isdigit() and int(marker.text.strip()) == current_page, "Orca current page mismatch")
    require(not any(n.tag in ("button", "form", "select") for n in page_nodes), "Unknown Orca pagination control")
    next_links = [n for n in nodes if n.tag == "link" and "next" in n.attrs.get("rel", "").split()]
    require(all(n.inside(head) and n.attrs.get("href") for n in next_links), "Unknown Orca head-next control")
    require(all(n.inside(pagination) for n in nodes if n.tag == "a" and {"next", "page-numbers"} <= n.classes),
            "Orca next control outside pagination")
    head_next = {urljoin(url, n.attrs["href"]) for n in next_links}
    class_next, numbered, dots = set(), {current_page}, False
    for node in page_nodes:
        if "dots" in node.classes:
            dots = True
        if node.tag != "a":
            continue
        require("page-numbers" in node.classes and node.attrs.get("href"), "Unknown Orca pagination anchor")
        target = urljoin(url, node.attrs["href"])
        number = orca_index_number(target)
        numbered.add(number)
        if "next" in node.classes:
            class_next.add(target)
        elif "prev" in node.classes:
            require(number == current_page - 1, "Unexpected Orca previous page")
        else:
            require(node.text.strip().isdigit() and int(node.text.strip()) == number, "Orca numbered page mismatch")
    require(head_next == class_next and len(head_next) <= 1, "Missing or conflicting Orca next controls")
    highest_page = max(highest_page, *numbered)
    next_url = next(iter(head_next), None)
    if next_url:
        require(orca_index_number(next_url) == current_page + 1, "Orca pagination loop or skipped page")
    else:
        require(not dots and current_page == highest_page, "Unproved Orca terminal page")

    cards = [n for n in nodes if n.tag == "div" and {"clickable-card", "horizontal-post-card"} <= n.classes and n.inside(cards_region)]
    require(bool(cards), "Orca listing has no recognized static cards")
    require(all(child in cards if isinstance(child, IndexNode) else not child.strip() for child in cards_region.children),
            "Unknown Orca card-container content")
    featured_regions = [n for n in nodes if "newsroom-listing-featured" in n.classes]
    require(len(featured_regions) <= 1, "Ambiguous Orca featured region")
    if featured_regions:
        cards += [n for n in nodes if n.tag == "article" and {"clickable-card", "post-card", "post-card--featured"} <= n.classes and n.inside(featured_regions[0])]
    items, dates = set(), {}
    for card in cards:
        require(card.closed, "Unclosed Orca card")
        card_nodes = list(card.walk())
        category = one([n for n in card_nodes if "post-card__category" in n.classes], "card category")
        label = " ".join(category.text.split())
        require(label in ("News", "Press Releases"), "Unknown Orca card category")
        title = one([n for n in card_nodes if n.tag == "h2" and "post-card__title" in n.classes], "release title")
        link = one([n for n in title.walk() if n.tag == "a" and n.attrs.get("href")], "release title link")
        require(bool(link.text.strip()), "Empty Orca card title")
        date_node = one([n for n in card_nodes if "post-card__date" in n.classes], "card date")
        value = datetime.strptime(" ".join(date_node.text.split()), "%b %d, %Y").date().isoformat()
        if label == "News":
            continue
        target = urljoin(url, link.attrs["href"])
        parsed = urlsplit(target)
        require(parsed.scheme == "https" and parsed.netloc == "orca.security" and not parsed.query and not parsed.fragment and
                re.fullmatch(r"/resources/press-releases/[A-Za-z0-9_-]+/", parsed.path), "Unsafe Orca release card")
        if card.attrs.get("data-url"):
            require(urljoin(url, card.attrs["data-url"]) == target, "Orca card URL disagreement")
        require(target not in dates or dates[target] == value, "Conflicting Orca release dates")
        items.add(target)
        dates[target] = value
    return {"items": items, "dates": dates, "next": next_url, "highestPage": highest_page}


def barracuda_shell(url, body):
    parsed = urlsplit(url)
    if parsed.scheme != "https" or parsed.netloc != "www.barracuda.com" or parsed.path != "/company/news":
        return None
    nodes = list(IndexMarkup(body.decode("utf8", errors="strict")).root.walk())
    components = [n for n in nodes if n.attrs.get("data-cmp-is") == "NewsRoom" and "cmp-news-room" in n.classes]
    containers = [n for n in nodes if n.attrs.get("data-cmp-hook-news-room") == "cardsContainer" and any(n.inside(c) for c in components)]
    endpoint = "https://www.barracuda.com/content/barracuda-corp/us/en/company/news/jcr:content/root/container/container/news_room.news_room.json"
    if len(components) == len(containers) == 1 and urljoin(url, containers[0].attrs.get("data-panel-endpoint", "")) == endpoint:
        return {"reason": "BARRACUDA_NEWSROOM_DATA_REQUIRED", "requiredEndpoints": [endpoint]}
    return {"reason": "BARRACUDA_NEWSROOM_LAYOUT_UNVERIFIED", "requiredEndpoints": []}


def discover_regulatory_index(source, request):
    """Traverse an explicitly bound issuer index without producing market facts."""
    from regulatory import validate_index_source, validate_filing_source, filing_document_inventory, TABLE_FIELDS
    observations, items, dates, seen = [], set(), {}, set()
    documents = []
    def result(complete, reason=None, **details):
        return {"complete": complete, "items": sorted(items), "itemDates": dates,
                "observations": observations, "reason": reason, **details}
    try:
        filing_documents = source['kind'] == 'sec_documents'
        (validate_filing_source if filing_documents else validate_index_source)(source)
        checked = instant(source.get("checkedAt", utcnow())).astimezone(timezone.utc)
        cutoff = (checked - timedelta(days=source.get("lookbackDays", 365))).date().isoformat()
        queue = [source["url"]]
        while queue:
            require(len(seen) < source["maxPages"], "PAGINATION_BUDGET_EXHAUSTED")
            url = queue.pop(0)
            require(url not in seen, "Duplicate SEC index continuation")
            seen.add(url)
            observation, body = request(url)
            observations.append(observation)
            if observation.get("status") not in ("fetched", "not_modified"):
                return result(False, observation.get("errorCode", "SEC_INDEX_FETCH_FAILED"))
            require(observation.get("requestedUrl") == url and observation.get("finalUrl", url) == url,
                    "SEC index response URL differs")
            value = json.loads(decoded_discovery_body(body))
            require(isinstance(value, dict), "SEC index response must be an object")
            documents.append({'url': url, 'document': value})
            if url == source["url"]:
                issuer = source["regulatoryIssuer"]
                cik = value.get("cik")
                require((type(cik) is int or isinstance(cik, str) and re.fullmatch(r"\d{1,10}", cik)) and
                        str(cik).zfill(10) == issuer["cik"] and value.get("name") == issuer["legalName"],
                        "SEC index initial issuer CIK/name differs")
                filings = value.get("filings")
                require(isinstance(filings, dict) and isinstance(filings.get("files"), list), "SEC history metadata missing")
                recent = filings.get("recent")
                names = set()
                for archive in filings["files"]:
                    require(isinstance(archive, dict) and set(archive) == {"name", "filingCount", "filingFrom", "filingTo"},
                            "SEC older index metadata schema differs")
                    name = archive["name"]
                    require(isinstance(name, str) and re.fullmatch(r"CIK" + issuer["cik"] + r"-submissions-\d{3}\.json", name),
                            "Unsafe SEC older index filename or wrong issuer")
                    require(name not in names, "Duplicate SEC older index metadata")
                    names.add(name)
                    first, last = date.fromisoformat(archive["filingFrom"]), date.fromisoformat(archive["filingTo"])
                    require(first <= last <= checked.date() and type(archive["filingCount"]) is int and archive["filingCount"] > 0,
                            "SEC older index date/count boundaries invalid")
                    if last.isoformat() >= cutoff:
                        queue.append(urljoin(source["url"], name))
            else:
                recent = value
            require(isinstance(recent, dict) and TABLE_FIELDS.issubset(recent) and
                    all(isinstance(column, list) for column in recent.values()),
                    "SEC filing index arrays missing")
            require(all(len(column) == len(recent["accessionNumber"]) for column in recent.values()),
                    "SEC filing index array lengths differ")
            for accession, filed in zip(recent["accessionNumber"], recent["filingDate"]):
                require(isinstance(accession, str) and re.fullmatch(r"\d{10}-\d{2}-\d{6}", accession), "Unsafe SEC accession")
                day = date.fromisoformat(filed).isoformat()
                require(day <= checked.date().isoformat(), "Future SEC index filing date")
                if day >= cutoff:
                    require(accession not in dates or dates[accession] == day, "Conflicting SEC accession date")
                    items.add(accession)
                    dates[accession] = day
        if filing_documents:
            selected = filing_document_inventory(source, documents, cutoff, checked.date().isoformat())
            items = {item['url'] for item in selected}
            dates = {item['url']: item['filingDate'] for item in selected}
        return result(True)
    except (ValueError, TypeError, KeyError, OSError) as exc:
        return result(False, "SEC_INDEX_INCOMPLETE", detail=str(exc)[:160])


class Page(HTMLParser):
    def __init__(self, html, source_url=None):
        super().__init__(convert_charrefs=True)
        self.source_url = source_url
        source = urlsplit(source_url or '')
        self.esentire_scope = source.scheme == 'https' and source.hostname == 'www.esentire.com' and source.path.startswith('/news-releases/') and bool(source.path.removeprefix('/news-releases/')) and not source.query and not source.fragment and not source.username and source.port in (None, 443)
        self.canonicals, self.webpage_nodes = [], []
        self.scoped_articles, self.scoped_article_text = 0, []
        self.scoped_extraction, self.publication_ambiguous = False, False
        self.links, self.feeds, self.text, self.published = [], [], [], None
        self.regions, self.region_text = [], {"article": [], "main": []}
        self.json_ld, self.json_parts, self.json_dates, self.meta_published = False, [], set(), False
        self.time_dates, self.published_from_time = set(), False
        self.skip = 0
        self.feed(html)
        self._finish_scoped_publication()
        # A labeled article publication date is usable metadata. An arbitrary
        # event time, modified date or a multi-entry listing is not.
        if not self.publication_ambiguous and not self.published and not self.json_dates and len(self.time_dates) == 1:
            self.published = next(iter(self.time_dates))
            self.published_from_time = True

    def _finish_scoped_publication(self):
        if not self.esentire_scope or not self.scoped_articles:
            return
        # This exact archived source layout has no semantic article/main element.
        # Scope the body even when its publication metadata remains conflicting.
        self.scoped_extraction = True
        matching = [node for node in self.webpage_nodes if node.get('url') == self.source_url and node.get('mainEntityOfPage') == self.source_url]
        self.publication_ambiguous = True
        if self.canonicals != [self.source_url] or len(self.webpage_nodes) != 1 or len(matching) != 1 or self.scoped_articles != 1:
            self.published = None
            return
        value = matching[0].get('datePublished')
        try:
            published = instant(value)
            require(published.date() <= date.today(), 'Future publication date')
        except (ValueError, TypeError):
            self.published = None
            return
        article = re.sub(r'\s+', ' ', ' '.join(self.scoped_article_text)).strip()
        dateline = re.search(r'^[^.!?]{0,100}?\b((?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4})\b', article)
        if dateline:
            from datetime import datetime
            try:
                day = datetime.strptime(dateline.group(1).replace(',', ''), '%B %d %Y').date().isoformat()
            except ValueError:
                self.published = None
                return
            if day != value[:10]:
                self.published = None
                return
        other_dates = self.json_dates | ({self.published} if self.published else set())
        if any(item[:10] != value[:10] for item in other_dates):
            self.published = None
            return
        self.published = value
        self.publication_ambiguous = False

    def handle_starttag(self, tag, attrs):
        a = {key: '' if value is None else value for key, value in attrs}
        self.regions = [(t, r, depth + (t == tag)) for t, r, depth in self.regions]
        region = tag if tag in ("article", "main") else "main" if a.get("role") == "main" else None
        if self.esentire_scope and 'BlogBody__Content' in a.get('class', '').split():
            self.scoped_articles += 1
            self.regions.append((tag, 'scoped_article', 1))
        if region:
            self.regions.append((tag, region, 1))
        # This explicit press-release label is verified against archived
        # Mimecast pages. Generic post-date classes can belong to sidebar cards.
        publication_classes = {'press-release-details__date'}
        if publication_classes.intersection(a.get('class', '').split()):
            self.regions.append((tag, 'publication', 1))
        regions = {r for _, r, _ in self.regions}
        if tag == 'time' and (('article' in regions and 'datePublished' in a.get('itemprop', '').split()) or
                             ('publication' in regions and bool(regions & {'main', 'article'}))):
            value = a.get('datetime', '')
            if re.fullmatch(r'\d{4}-\d{2}-\d{2}(?:T.*)?', value):
                try:
                    self.time_dates.add(date.fromisoformat(value[:10]).isoformat())
                except ValueError:
                    pass
        if tag == "script" and a.get("type") == "application/ld+json":
            self.json_ld, self.json_parts = True, []
        if tag in ("script", "style", "noscript"):
            self.skip += 1
        if tag == "a" and a.get("href"):
            self.links.append({"url": a["href"], "next": "next" in a.get("rel", "").split()})
        if tag == "link" and a.get("href") and a.get("type", "") in ("application/rss+xml", "application/atom+xml"):
            self.feeds.append(a["href"])
        if tag == 'link' and 'canonical' in a.get('rel', '').split() and a.get('href'):
            self.canonicals.append(a['href'])
        if tag == "meta" and a.get("property") in ("article:published_time", "datePublished"):
            self.published = a.get("content")
            self.meta_published = bool(self.published)

    def handle_endtag(self, tag):
        if tag == "script" and self.json_ld:
            self.json_ld = False
            try:
                value = json.loads("".join(self.json_parts))
                def dates(item):
                    if isinstance(item, list):
                        for entry in item: dates(entry)
                    elif isinstance(item, dict):
                        types = item.get("@type", [])
                        types = [types] if isinstance(types, str) else types
                        if self.esentire_scope and 'WebPage' in types:
                            self.webpage_nodes.append(item)
                        if any(t in ("Article", "NewsArticle", "BlogPosting", "PressRelease") for t in types):
                            date = item.get("datePublished", "")
                            if isinstance(date, str) and re.match(r"^\d{4}-\d{2}-\d{2}", date): self.json_dates.add(date)
                        if "@graph" in item: dates(item["@graph"])
                dates(value)
                if not self.meta_published:
                    self.published = next(iter(self.json_dates)) if len(self.json_dates) == 1 else None
            except (ValueError, TypeError):
                pass
        for index in range(len(self.regions)-1, -1, -1):
            if self.regions[index][0] == tag:
                t, r, depth = self.regions[index]
                if depth == 1:
                    self.regions.pop(index)
                else:
                    self.regions[index] = (t, r, depth-1)
        if tag in ("script", "style", "noscript"):
            self.skip = max(0, self.skip - 1)

    def handle_data(self, data):
        if self.json_ld and sum(map(len, self.json_parts)) + len(data) <= 100_000:
            self.json_parts.append(data)
        if not self.skip:
            self.text.append(data)
            if any(region == 'scoped_article' for _, region, _ in self.regions):
                self.scoped_article_text.append(data)
            for region in {region for _, region, _ in self.regions if region in self.region_text}:
                self.region_text[region].append(data)

    @property
    def readable(self):
        if self.scoped_extraction and self.scoped_articles == 1:
            return re.sub(r'\s+', ' ', ' '.join(self.scoped_article_text)).strip()
        for region in ("article", "main"):
            text = re.sub(r"\s+", " ", " ".join(self.region_text[region])).strip()
            if len(text) >= 100:
                return text
        return re.sub(r"\s+", " ", " ".join(self.text)).strip()


def scoped(url, source):
    p = urlsplit(url)
    return p.scheme == "https" and p.hostname in source["allowedHosts"] and any(p.path.startswith(prefix) for prefix in source["scopePrefixes"])


def xml_links(body, base):
    body = decoded_discovery_body(body)
    class NoDoctypeTreeBuilder(ET.TreeBuilder):
        def doctype(self, name, pubid, system):
            require(False, "XML entity declarations prohibited")
    root = ET.fromstring(body, parser=ET.XMLParser(target=NoDoctypeTreeBuilder()))
    kind = root.tag.rsplit("}", 1)[-1]
    links, indexes, modified = [], [], {}
    if kind in ("urlset", "sitemapindex"):
        for element in root.iter():
            if element.tag.rsplit("}", 1)[-1] == "loc" and element.text:
                (indexes if kind == "sitemapindex" else links).append(urljoin(base, element.text.strip()))
        for entry in root:
            fields = {e.tag.rsplit("}", 1)[-1]: e.text for e in entry}
            if fields.get("loc") and fields.get("lastmod"):
                modified[urljoin(base, fields["loc"].strip())] = fields["lastmod"].strip()
    elif kind in ("rss", "feed"):
        for element in root.iter():
            if element.tag.rsplit("}", 1)[-1] == "link" and element.attrib.get("rel") == "next":
                require(bool(element.attrib.get("href")), "Malformed feed pagination")
                indexes.append(urljoin(base, element.attrib["href"]))
        for entry in root.iter():
            if entry.tag.rsplit("}", 1)[-1] not in ("item", "entry"):
                continue
            for element in entry:
                if element.tag.rsplit("}", 1)[-1] == "link":
                    value = element.attrib.get("href") or element.text
                    if value and element.attrib.get("rel", "alternate") == "alternate":
                        links.append(urljoin(base, value.strip()))
    else:
        raise ValueError("Unsupported XML discovery format")
    return {"kind": kind, "links": sorted(set(links)), "indexes": sorted(set(indexes)), "modified": modified}


def discover_q4_press_list(source, request, *, profile=Q4_CURRENT_PROFILE):
    """One source-bound finite JSON response, with ordinary transport provenance."""
    from q4_qualification_origin import validate_source
    from q4_press_list import parse_press_list
    require(type(profile) is str and profile in (Q4_LEGACY_PROFILE, Q4_CURRENT_PROFILE),
            'Q4_DISCOVERY_PROFILE_INVALID')
    validate_source(source)
    profile_fields = {'discoveryProfile': profile} if profile == Q4_CURRENT_PROFILE else {}
    observations = []
    try:
        observed, body = request(source['url'])
        observations.append(observed)
        require(observed.get('requestedUrl') == observed.get('finalUrl') == source['url'] and
                observed.get('sourceId') == source['id'], 'Q4_INDEX_TRANSPORT_IDENTITY_DIFFERS')
        require((observed.get('status') == 'fetched' and type(observed.get('httpStatus')) is int and
                 observed['httpStatus'] == 200) or
                (observed.get('status') == 'not_modified' and type(observed.get('httpStatus')) is int and
                 observed['httpStatus'] == 304 and isinstance(observed.get('reusesObservationId'), str) and
                 bool(observed['reusesObservationId'])), 'Q4_INDEX_TRANSPORT_NOT_SUCCESSFUL')
        require(isinstance(observed.get('contentType'), str) and re.fullmatch(
                r'application/json(?:\s*;\s*charset\s*=\s*(?:utf-8|"utf-8"))?\s*',
                observed['contentType'], re.I), 'Q4_INDEX_JSON_MIME_DIFFERS')
        ref = observed.get('body')
        require(type(ref) is dict and set(ref) == {'key', 'sha256', 'bytes'} and
                type(ref['bytes']) is int and 0 < ref['bytes'] <= 2_000_000 and
                ref['key'] == 'objects/' + ref['sha256'] and type(body) is bytes and
                len(body) == ref['bytes'] and digest(body) == ref['sha256'], 'Q4_INDEX_BODY_INTEGRITY_DIFFERS')
        instant(observed.get('fetchedAt'))
        parsed = parse_press_list(body, source['id'], observed['fetchedAt'], implementation_profile=profile)
        return {**profile_fields, 'complete': True, 'items': parsed['items'], 'itemDates': parsed['itemDates'],
                'itemModified': parsed['itemModified'], 'observations': observations, 'reason': None,
                'originalDateStrings': parsed['originalDateStrings'], 'timezone': parsed['timezone'],
                'sourceDateAnomalies': parsed['sourceDateAnomalies'],
                'undeterminedWindowItems': parsed['undeterminedWindowItems'],
                'boundaryAmbiguousItems': parsed['boundaryAmbiguousItems'],
                'currentWindowQuiet': parsed['currentWindowQuiet']}
    except (ValueError, KeyError, TypeError, OSError, UnicodeError) as error:
        return {**profile_fields, 'complete': False, 'items': [], 'itemDates': {}, 'itemModified': {},
                'observations': observations, 'reason': 'Q4_INDEX_INCOMPLETE:' + str(error)[:160]}


def discover(source, request, *, q4_profile=Q4_CURRENT_PROFILE):
    """request(url) archives every response and returns an observation plus bytes."""
    if source["registration"] != "verified":
        return {"complete": False, "items": [], "observations": [], "reason": "SOURCE_BINDING_UNVERIFIED"}
    if source.get('htmlCompleteness') in ('cyera-press-list-finite-html-v1', 'prnewswire-issuer-calendar-window-v1'):
        from three_source_discovery import discover as discover_three_source
        return discover_three_source(source, request)
    if source['kind'] == 'q4_press_list':
        return discover_q4_press_list(source, request, profile=q4_profile)
    if source["kind"] == "sec_index" or source["kind"] == "sec_documents" and 'regulatoryIssuer' in source:
        return discover_regulatory_index(source, request)
    queue, seen, items, observations, item_dates, item_modified = [source["url"]], set(), set(), [], {}, {}
    highest_orca_page = 1
    orca_mode = source.get("htmlCompleteness") == ORCA_HTML_MODE
    source_html_mode = source.get('htmlCompleteness') in (PING_HTML_MODE, PING_HTML_MODE_V2, PING_HTML_MODE_V3,
        DELINEA_HTML_MODE, DELINEA_HTML_MODE_V2, DELINEA_HTML_MODE_V3, DELINEA_HTML_MODE_V4, DELINEA_HTML_MODE_V5,
        SONATYPE_HTML_MODE, SONATYPE_HTML_MODE_V2, SONATYPE_HTML_MODE_V3, SONATYPE_HTML_MODE_V4, SONATYPE_HTML_MODE_V5)
    source_label = {PING_HTML_MODE: 'PING', PING_HTML_MODE_V2: 'PING', PING_HTML_MODE_V3: 'PING',
                    DELINEA_HTML_MODE: 'DELINEA', DELINEA_HTML_MODE_V2: 'DELINEA',
                    DELINEA_HTML_MODE_V3: 'DELINEA', DELINEA_HTML_MODE_V4: 'DELINEA', DELINEA_HTML_MODE_V5: 'DELINEA',
                    SONATYPE_HTML_MODE: 'SONATYPE', SONATYPE_HTML_MODE_V2: 'SONATYPE',
                    SONATYPE_HTML_MODE_V3: 'SONATYPE', SONATYPE_HTML_MODE_V4: 'SONATYPE',
                    SONATYPE_HTML_MODE_V5: 'SONATYPE'}.get(source.get('htmlCompleteness'))
    highest_source_page, last_source_date, source_as_of = 1, None, source.get('checkedAt')
    publisher_lead_warnings = []
    def incomplete(reason, **details):
        result = {"complete": False, "items": sorted(items), "itemDates": item_dates,
                  "itemModified": item_modified, "observations": observations, "reason": reason, **details}
        if source.get('htmlCompleteness') in (DELINEA_HTML_MODE_V5, SONATYPE_HTML_MODE_V5):
            result['publisherLeadWarnings'] = list(publisher_lead_warnings)
        return result
    while queue:
        if len(seen) >= source["maxPages"]:
            return incomplete("PAGINATION_BUDGET_EXHAUSTED")
        url = queue.pop(0)
        if url in seen:
            continue
        seen.add(url)
        try:
            observation, body = request(url)
        except (OSError, ValueError):
            if not (orca_mode or source_html_mode):
                raise
            return incomplete(source_label + '_INDEX_REQUEST_FAILED' if source_html_mode else "ORCA_INDEX_REQUEST_FAILED", missingUrl=url)
        observations.append(observation)
        if observation["status"] not in ("fetched", "not_modified"):
            return incomplete(observation.get("errorCode", "FETCH_FAILED"))
        if source["kind"] == "citation":
            require(len(body) > 0, "Empty citation response")
            continue
        if source["kind"] in ("sec_facts", "sec_submissions", "sec_documents"):
            value = json.loads(body)
            if source["kind"] == "sec_facts":
                require(isinstance(value.get("facts"), dict) and value.get("cik"), "Malformed SEC companyfacts response")
            else:
                recent = value.get("filings", {}).get("recent", value)
                require(isinstance(recent.get("accessionNumber"), list), "Malformed SEC submissions response")
                # Older submission pages must also be fetched to establish the full retained index.
                cutoff = (instant(source.get("checkedAt", utcnow())) - timedelta(days=source.get("lookbackDays", 365))).date().isoformat()
                for archive in value.get("filings", {}).get("files", []):
                    if source["kind"] == "sec_documents" and archive.get("filingTo", "9999") < cutoff:
                        continue
                    name = archive.get("name", "")
                    require(re.fullmatch(r"CIK\d+-submissions-\d+\.json", name) is not None, "Unexpected SEC index filename")
                    queue.append(urljoin(source["url"], name))
                if source["kind"] == "sec_documents":
                    cik = str(int(source["cik"]))
                    if "cik" in value:
                        require(str(int(value["cik"])) == cik, "SEC document index CIK mismatch")
                    for i, accession in enumerate(recent["accessionNumber"]):
                        if recent["filingDate"][i] < cutoff or recent["form"][i] not in SEC_FILING_FORMS:
                            continue
                        primary = recent["primaryDocument"][i]
                        require(re.fullmatch(r"\d{10}-\d{2}-\d{6}", accession) and re.fullmatch(r"[A-Za-z0-9_.-]+", primary), "Unsafe SEC document path")
                        document_url = f"https://www.sec.gov/Archives/edgar/data/{cik}/{accession.replace('-', '')}/{primary}"
                        items.add(document_url)
                        item_dates[document_url] = recent["filingDate"][i]
                else:
                    items.update(recent["accessionNumber"])
            continue
        try:
            body = decoded_discovery_body(body)
            if source_html_mode:
                require(observation.get('requestedUrl') == url and observation.get('finalUrl') == url,
                        source_label + ' response request/final URL mismatch')
                source_as_of = source_as_of or observation.get('fetchedAt')
                instant(source_as_of)
                parsed_index = parse_source_html_index(source, url, body, highest_source_page, source_as_of)
                require(not (items & parsed_index['items']), 'Duplicate ' + source_label + ' card across pages')
                require(last_source_date is None or parsed_index['firstDate'] is None or
                        parsed_index['firstDate'] <= last_source_date, source_label + ' dates out of order across pages')
                items.update(parsed_index['items']); item_dates.update(parsed_index['dates']); item_modified.update(parsed_index['dates'])
                publisher_lead_warnings.extend(parsed_index.get('publisherLeadWarnings', []))
                highest_source_page = parsed_index['highestPage']; last_source_date = parsed_index['lastDate']
                if not parsed_index['next']:
                    if not parsed_index['terminalProved']:
                        return incomplete(source_label + '_TERMINAL_LAYOUT_UNPROVED', highestAdvertisedPage=highest_source_page)
                    require(parsed_index['currentPage'] == highest_source_page == len(seen), 'HTML terminal traversal has a missing page')
                else:
                    require(parsed_index['next'] not in seen, source_label + ' pagination loop')
                    queue.append(parsed_index['next'])
                continue
            if orca_mode:
                require(source["kind"] == "html_index", "Orca mode requires HTML index kind")
                parsed_index = orca_index(source, url, body, highest_orca_page)
                for target, value in parsed_index["dates"].items():
                    require(target not in item_dates or item_dates[target] == value, "Conflicting Orca dates across pages")
                items.update(parsed_index["items"])
                item_dates.update(parsed_index["dates"])
                # Explicit card publication is an index scheduling signature,
                # not semantic evidence of the event's effective date.
                item_modified.update(parsed_index["dates"])
                highest_orca_page = parsed_index["highestPage"]
                if parsed_index["next"]:
                    require(parsed_index["next"] not in seen, "Orca pagination loop")
                    queue.append(parsed_index["next"])
                continue
            shell = barracuda_shell(url, body)
            if shell:
                return incomplete(**shell)
        except ValueError as exc:
            if orca_mode or source_html_mode:
                return incomplete(source_label + '_INDEX_INCOMPLETE' if source_html_mode else "ORCA_INDEX_INCOMPLETE", detail=str(exc))
            raise
        content = body.lstrip()
        if content.startswith(b"<?xml") or re.match(br"<(rss|feed|urlset|sitemapindex)\b", content):
            parsed = xml_links(body, url)
            item_modified.update(parsed["modified"])
            for index in parsed["indexes"]:
                require(urlsplit(index).hostname in source["allowedHosts"], "Unapproved sitemap host")
                if index not in seen:
                    queue.append(index)
            items.update(item for item in parsed["links"] if scoped(item, source))
        else:
            require(source["kind"] == "html_index", "Discovery endpoint must be a validated feed, sitemap or HTML index")
            require(source.get("htmlCompleteness") == "rel-next-exhaustion-v1", "HTML completeness rule must be explicitly registered")
            page = Page(body.decode("utf8", errors="replace"))
            require(len(page.readable) > 60, "Empty or unreadable discovery page")
            for link in page.links:
                target = urljoin(url, link["url"]).split("#")[0]
                if link["next"]:
                    require(scoped(target, source), "Unapproved pagination destination")
                    if target not in seen:
                        queue.append(target)
                elif scoped(target, source) and target not in seen:
                    items.add(target)
    result = {"complete": True, "items": sorted(items), "itemDates": item_dates,
              "itemModified": item_modified, "observations": observations, "reason": None}
    if source.get('htmlCompleteness') in (DELINEA_HTML_MODE_V5, SONATYPE_HTML_MODE_V5):
        result['publisherLeadWarnings'] = list(publisher_lead_warnings)
    return result
