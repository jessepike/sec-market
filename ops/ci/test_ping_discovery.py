"""Offline candidate proof; recognized nonterminal layouts never imply completion."""
import copy
import hashlib
import json
from pathlib import Path
import socket
import sys
import unittest
from unittest.mock import patch
from datetime import date, timedelta

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'web/scripts/pipeline'))
from discovery import discover, ping_index, PING_INDEX, Page
from contracts import validate_contract

NOW = '2026-10-24T01:26:57.483815Z'
SOURCE = {'id':'ping-identity:official:1','supplierId':'ping-identity','family':'official_announcements',
          'kind':'html_index','registration':'verified','url':PING_INDEX,'allowedHosts':['press.pingidentity.com'],
          'maxPages':60,'htmlCompleteness':'ping-release-pagination-v1','checkedAt':NOW}
ARCHIVE = Path('/var/tmp/smp-renewal-20261024/archive-b9f1208b/jessepike-sec-market-b9f1208bd9e957bee5cca2c0b4db28a4fc1fa63f/state')
PINS = [('a3ea17921e3b778f56c42fe0ecfa2f035db991f34afb167e6cb09dc28f4113b2', '09eb766cec6f9e2d9cbd7a3f412bdca185b7a604a635d596f2f19b506ad884f7'),
        ('277c8d143f01e294d926ca6f85eb3c9874b08107721386a69feeaf59107372e3', 'f61107756abf878060b6082d9067715f1c0ab6ce9d45946a72d1a3731f258c88')]

def layout(page=1):
    cards = ''.join(f'<li class="wd_item"><div class="wd_title"><a href="https://press.pingidentity.com/2026-10-{21-i:02d}-Ping-Release-{page}-{i},Text">Release</a></div><div class="wd_date">Oct {21-i:02d}, 2026</div></li>' for i in range(10))
    def number(n):
        return f'<li class="wd_page_link wd_page_mid2"><a href="{PING_INDEX}?o={(n-1)*10}">{n}</a></li>'
    active = f'<li class="wd_page_link wd_page_active"><span aria-current="page">{page}</span></li>'
    prev = '<span>«</span>' if page == 1 else f'<a href="{PING_INDEX}?o={(page-2)*10}">«</a>'
    controls = f'<li class="wd_page_link wd_page_prev">{prev}</li>' + (active if page == 1 else number(1)+active)
    controls += ''.join(number(n) for n in range(page+1,4))
    controls += f'<li class="wd_page_link wd_page_next"><a href="{PING_INDEX}?o={page*10}">»</a></li>'
    return f'<html><head><link rel="canonical" href="{PING_INDEX}"></head><body><a href="/2026-01-01-Footer">footer</a><div class="wd_newsfeed_releases"><ul class="wd_item_list">{cards}</ul><ul class="wd_page_links">{controls}</ul></div></body></html>'.encode()


def complete_layout(page=1, last=25):
    def number(n, role='wd_page_mid2'):
        return f'<li class="wd_page_link {role}"><a href="{PING_INDEX}?o={(n-1)*10}">{n}</a></li>'
    cards = []
    for i in range(2 if page == last else 10):
        day = date(2026, 10, 23) - timedelta(days=(page-1)*10+i)
        cards.append(f'<li class="wd_item"><div class="wd_title"><a href="{PING_INDEX.rsplit("/",1)[0]}/{day.isoformat()}-Release-{page}-{i}">Fixture</a></div>'
                     f'<div class="wd_date">{day.strftime("%b %d, %Y")}</div></li>')
    previous = '<span>«</span>' if page == 1 else f'<a href="{PING_INDEX}?o={(page-2)*10}">«</a>'
    controls = f'<li class="wd_page_link wd_page_prev">{previous}</li>'
    if page > 1:
        controls += number(1, 'wd_page_start')
        if page > 2:
            controls += '<li class="wd_page_link wd_page_skip1"><span>…</span></li>'
    controls += f'<li class="wd_page_link wd_page_active"><span aria-current="page">{page}</span></li>'
    if page < last:
        controls += number(page+1)
        if last > page+2:
            controls += '<li class="wd_page_link wd_page_skip2"><span>…</span></li>'
        if last > page+1:
            controls += number(last, 'wd_page_end')
    following = '<span>»</span>' if page == last else f'<a href="{PING_INDEX}?o={page*10}">»</a>'
    controls += f'<li class="wd_page_link wd_page_next">{following}</li>'
    return (f'<html><head><link rel="canonical" href="{PING_INDEX}"></head><body><div class="wd_newsfeed_releases">'
            f'<ul class="wd_item_list">{"".join(cards)}</ul><ul class="wd_page_links">{controls}</ul></div></body></html>').encode()

class PingDiscoveryTests(unittest.TestCase):
    def parse(self, body=None, url=PING_INDEX, source=None):
        return ping_index(source or SOURCE,url,body or layout(),1,NOW)

    def test_card_isolation_literal_commas_and_dates_are_only_scheduling(self):
        result=self.parse(); self.assertEqual(len(result['items']),10)
        self.assertTrue(all(',Text' in u for u in result['items']))
        self.assertEqual(set(result['dates'].values()),{f'2026-10-{d:02d}' for d in range(12,22)})
        self.assertIsNone(Page(layout().decode()).published)

    def test_future_card_check_uses_utc_day_for_offset_timestamps(self):
        self.assertEqual(len(ping_index(SOURCE,PING_INDEX,layout(),1,'2026-10-20T23:30:00-07:00')['items']),10)
        with self.assertRaisesRegex(ValueError,'Future Ping'):
            ping_index(SOURCE,PING_INDEX,layout(),1,'2026-10-21T00:30:00+14:00')

    def test_structural_date_url_and_paging_counterexamples(self):
        original=layout().decode()
        mutations=[('wd_item_list','wrong_list'),('wd_newsfeed_releases','wrong_region'),('wd_title','wrong_title'),
                   ('Oct 21, 2026','Oct 32, 2026'),('Oct 21, 2026','Oct 21, 2099'),('Oct 21, 2026','2026-10-21'),
                   ('/2026-10-21-Ping-Release-1-0,Text','/news-releases?o=10'),
                   ('https://press.pingidentity.com/2026-10-21','https://evil.invalid/2026-10-21'),
                   ('?o=10','?o=20'),('?o=10','?o=11'),('?o=10','?o=10&x=1'),
                   ('aria-current="page">1','aria-current="page">2'),('wd_page_mid2','unknown'),
                   ('>2</a>','>3</a>')]
        for old,new in mutations:
            with self.subTest(old=old,new=new), self.assertRaises(ValueError): self.parse(original.replace(old,new,1).encode())

    def test_article_percent_escapes_and_path_normalization_tricks_are_held(self):
        original=layout().decode()
        for path in ('%2f%2e%2e%2fabout','%2Fabout','%5cabout','%2e%2e','%00','%0a',
                     '%zz','%','../about','./about','plain/../about','plain\\about','plain\tcontrol'):
            with self.subTest(path=path),self.assertRaises(ValueError):
                self.parse(original.replace('2026-10-21-Ping-Release-1-0,Text','2026-10-21-'+path,1).encode())
        self.assertEqual(len(self.parse()['items']),10)

    def test_unobserved_head_pagination_is_held_and_never_queued(self):
        for rel,target in [('next','https://evil.invalid/other-index'),('next',PING_INDEX+'?o=10'),
                           ('prev',PING_INDEX+'?o=0'),('alternate NEXT','https://evil.invalid/')]:
            with self.subTest(rel=rel,target=target):
                body=layout().replace(b'</head>',f'<link rel="{rel}" href="{target}"></head>'.encode())
                self.assertEqual(self.run_pages({PING_INDEX:body})['reason'],'PING_INDEX_INCOMPLETE')
                requests=[]
                def request(url):
                    requests.append(url)
                    return {'status':'fetched','requestedUrl':url,'finalUrl':url,'fetchedAt':NOW},body
                result=discover(SOURCE,request)
                self.assertFalse(result['complete']);self.assertEqual(requests,[PING_INDEX])

    def test_duplicate_cards_and_conflicting_cross_page_dates_hold(self):
        text=layout().decode(); start=text.index('<li class="wd_item">'); end=text.index('</li>',start)+5
        with self.assertRaises(ValueError):self.parse(text.replace('</ul>',text[start:end]+'</ul>',1).encode())
        pages={PING_INDEX:layout(),PING_INDEX+'?o=10':layout().replace(b'>1</span>',b'>2</span>')}
        result=self.run_pages(pages);self.assertFalse(result['complete']);self.assertEqual(len(result['items']),10)

    def test_numbered_gaps_ellipsis_duplicate_controls_and_changed_asof_hold(self):
        text=layout().decode()
        start=text.index('<li class="wd_page_link wd_page_mid2">');end=text.index('</li>',start)+5
        with self.assertRaises(ValueError):self.parse((text[:start]+text[end:]).encode())
        with self.assertRaises(ValueError):self.parse(text.replace('</ul></div>',text[start:end]+'</ul></div>').encode())
        with self.assertRaises(ValueError):self.parse(text.replace('wd_page_mid2','wd_page_skip2',1).encode())
        with self.assertRaises(ValueError):self.parse(layout(),url=PING_INDEX+'?o=10')
        with self.assertRaises(ValueError):ping_index(SOURCE,PING_INDEX,layout(),1,'2026-10-20T00:00:00Z')

    def test_cross_page_duplicates_date_order_and_response_identity_hold(self):
        first=layout(); second=layout(page=2)
        # Page 2's newest day cannot be newer than page 1's oldest day.
        result=self.run_pages({PING_INDEX:first,PING_INDEX+'?o=10':second})
        self.assertEqual(result['reason'],'PING_INDEX_INCOMPLETE');self.assertEqual(len(result['items']),10)
        second=second.replace(b'2026-10-21-Ping-Release-2-0,Text',b'2026-10-21-Ping-Release-1-0,Text')
        result=self.run_pages({PING_INDEX:first,PING_INDEX+'?o=10':second})
        self.assertIn('Duplicate',result['detail'])
        def wrong(url):return {'status':'fetched','requestedUrl':url,'finalUrl':PING_INDEX+'?o=10','fetchedAt':NOW},first
        self.assertFalse(discover(SOURCE,wrong)['complete'])

    def run_pages(self,pages,source=None):
        def request(url):
            if url not in pages:raise OSError('missing archived page')
            return {'status':'fetched','requestedUrl':url,'finalUrl':url,'fetchedAt':NOW},pages[url]
        with patch.object(socket.socket,'connect',side_effect=AssertionError('network forbidden')):
            return discover(source or SOURCE,request)

    def test_missing_next_and_cap_preserve_partial_inventory(self):
        result=self.run_pages({PING_INDEX:layout()});self.assertFalse(result['complete']);self.assertEqual(len(result['items']),10)
        self.assertEqual(result['reason'],'PING_INDEX_REQUEST_FAILED')
        result=self.run_pages({PING_INDEX:layout()}, {**SOURCE,'maxPages':1})
        self.assertEqual(result['reason'],'PAGINATION_BUDGET_EXHAUSTED')
        self.assertEqual(len(result['items']),10)

    def test_unobserved_terminal_and_empty_never_succeed(self):
        text=layout().decode(); start=text.index('<li class="wd_page_link wd_page_next">');end=text.index('</li>',start)+5
        result=self.run_pages({PING_INDEX:(text[:start]+text[end:]).encode()})
        self.assertEqual(result['reason'],'PING_TERMINAL_LAYOUT_UNPROVED');self.assertEqual(len(result['items']),10)
        self.assertFalse(self.run_pages({PING_INDEX:b'<html>quiet</html>'})['complete'])

    def test_observed_terminal_controls_require_a_full_sequential_walk(self):
        pages = {PING_INDEX if n == 1 else PING_INDEX + '?o=' + str((n-1)*10): complete_layout(n) for n in range(1,26)}
        result = self.run_pages(pages)
        self.assertTrue(result['complete'])
        self.assertEqual(len(result['items']),242)  # Fictional fixture inventory, not an actual archive claim.
        del pages[PING_INDEX + '?o=100']
        missing = self.run_pages(pages)
        self.assertFalse(missing['complete'])
        self.assertEqual(len(missing['items']),100)
        self.assertEqual(missing['reason'],'PING_INDEX_REQUEST_FAILED')

    def test_disabled_next_on_an_advertised_middle_page_and_wrong_start_hold(self):
        first = complete_layout().replace(f'<a href="{PING_INDEX}?o=10">»</a>'.encode(), '<span>»</span>'.encode())
        self.assertFalse(self.run_pages({PING_INDEX:first})['complete'])
        last = complete_layout(25).replace(b'wd_page_start', b'unknown_start')
        with self.assertRaises(ValueError):ping_index(SOURCE,PING_INDEX+'?o=240',last,25,NOW)
        with self.assertRaises(ValueError):ping_index(SOURCE,PING_INDEX+'?o=240',complete_layout(25),26,NOW)

    @unittest.skipUnless(Path('/var/tmp/smp-followup-probe-20261024/target-bundle/ping-advertised-last.body').exists(),
                         'authenticated terminal body is a local replay input')
    def test_actual_terminal_body_is_recognized_without_claiming_traversal(self):
        path=Path('/var/tmp/smp-followup-probe-20261024/target-bundle/ping-advertised-last.body')
        body=path.read_bytes(); self.assertEqual(hashlib.sha256(body).hexdigest(),'f51960d7ea48f451e533fb82cf5e31084eea6c77e69ab9b071dfeca47d5a61d0')
        result=ping_index(SOURCE,PING_INDEX+'?o=240',body,25,NOW)
        self.assertTrue(result['terminalProved']);self.assertIsNone(result['next']);self.assertEqual(len(result['items']),2)
        self.assertEqual(path.read_bytes(),body)

    def test_exact_binding_and_inactive_registration(self):
        for key,value in [('id','other'),('supplierId','other'),('family','investor_acquirer'),('allowedHosts',['evil.invalid']),('maxPages',61),('url',PING_INDEX+'/')]:
            with self.subTest(key=key),self.assertRaises(ValueError):self.parse(source={**SOURCE,key:value})
        self.assertEqual(self.run_pages({}, {**SOURCE,'registration':'candidate'})['reason'],'SOURCE_BINDING_UNVERIFIED')
        # This old-mode fixture predates the qualified source's origin metadata.
        contract=json.loads((ROOT/'web/scripts/migration-proofs/daily-v2-original/market.json').read_text())
        source=next(s for s in contract['sources'] if s['id']==SOURCE['id'])
        source.update(SOURCE);validate_contract(contract)
        source['maxPages']=61
        with self.assertRaises(ValueError):validate_contract(contract)

    @unittest.skipUnless(ARCHIVE.exists(),'actual immutable archive is supplied only for local replay')
    def test_actual_pages_one_two_missing_three_yield_exact_twenty_incomplete(self):
        pages={}; originals=[]
        for bodysha,obssha in PINS:
            body=(ARCHIVE/'objects'/bodysha).read_bytes();raw=(ARCHIVE/'objects'/obssha).read_bytes()
            self.assertEqual(hashlib.sha256(body).hexdigest(),bodysha);self.assertEqual(hashlib.sha256(raw).hexdigest(),obssha)
            observation=json.loads(raw);pages[observation['requestedUrl']]=(observation,body); originals.append((bodysha,body))
        requests=[]
        def request(url):
            requests.append(url)
            if url not in pages:raise OSError('page 3 absent in immutable archive')
            return pages[url]
        with patch.object(socket.socket,'connect',side_effect=AssertionError('network forbidden')):
            result=discover(SOURCE,request)
        self.assertFalse(result['complete']);self.assertEqual(len(result['items']),20)
        self.assertEqual(result['reason'],'PING_INDEX_REQUEST_FAILED');self.assertEqual(len(result['observations']),2)
        self.assertEqual(requests,[PING_INDEX,PING_INDEX+'?o=10',PING_INDEX+'?o=20'])
        self.assertEqual(result['itemDates'],result['itemModified'])
        self.assertEqual(result['itemDates']['https://press.pingidentity.com/2026-06-16-Ping-Identity-Extends-Runtime-Identity-TM-for-AI-Agents-Across-AWS,-Google-Cloud,-and-Cloudflare'],'2026-06-16')
        for sha,body in originals:self.assertEqual((ARCHIVE/'objects'/sha).read_bytes(),body)

if __name__=='__main__':unittest.main()
