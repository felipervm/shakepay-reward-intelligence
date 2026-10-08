"""Check deterministic data, scenario IDs, UTF-8 and local site links."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
import hashlib,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
paths=[ROOT/'data'/n for n in ['synthetic_events.csv','synthetic_reconciliation.csv','demo_summary.json']]
before={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
subprocess.run([sys.executable,str(ROOT/'analysis.py')],check=True,capture_output=True)
assert before=={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},'Stored data did not match deterministic generator'
class Links(HTMLParser):
    def __init__(self):super().__init__();self.links=[];self.ids=set()
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        if 'id' in attrs:self.ids.add(attrs['id'])
        for key in ['href','src']:
            if key in attrs:self.links.append(attrs[key])
count=0
for p in [ROOT/'index.html',ROOT/'docs/method.html',ROOT/'docs/analysis.html']:
    parser=Links();parser.feed(p.read_text(encoding='utf8'))
    for link in parser.links:
        url=urlsplit(link)
        if url.scheme or url.netloc:continue
        target=(p.parent/unquote(url.path)).resolve() if url.path else p
        assert target.is_relative_to(ROOT) and target.is_file(),f'Missing local link: {p.name}: {link}'
        if url.fragment and target.suffix=='.html':
            other=Links();other.feed(target.read_text(encoding='utf8'))
            assert url.fragment in other.ids,f'Missing anchor: {link}'
        count+=1
for p in ROOT.rglob('*'):
    if p.is_file() and '.git' not in p.parts and p.suffix in {'.html','.js','.py','.md','.json','.css'}:
        text=p.read_text(encoding='utf8')
        assert '\ufffd' not in text,f'Invalid replacement character: {p}'
        assert '\u00e2\u0080' not in text and '\u00c3\u00a2' not in text,f'Encoding corruption: {p}'
cases=json.loads((ROOT/'data/cases.json').read_text(encoding='utf8'))
assert len({c['id'] for c in cases})==len(cases)==6
print(json.dumps({'deterministic_data':'PASS','local_links_checked':count,'scenario_ids':'PASS','utf8':'PASS'}))
