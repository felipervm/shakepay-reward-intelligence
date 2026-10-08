"""Execute the notebook and render current method/analysis to static HTML."""
from pathlib import Path
import contextlib, html, io, json, os, re
ROOT=Path(__file__).resolve().parents[1]
CSS="body{background:#f4f7fd;color:#111a2b;font:17px/1.65 Arial,sans-serif;margin:0}main{max-width:920px;padding:28px;margin:35px auto}h1{font-size:40px;line-height:1.15;letter-spacing:-1px}h2{font-size:26px;margin-top:42px}a{color:#165dff}p{overflow-wrap:anywhere}pre{white-space:pre-wrap;background:#111a2b;color:#e7efff;padding:18px;overflow:auto;font:13px/1.6 monospace}"
def render(text):
    output=[]
    for line in text.splitlines():
        if not line:continue
        value=html.escape(line)
        value=re.sub(r"\[([^\]]+)\]\(([^)]+)\)",r'<a href="\2">\1</a>',value)
        value=re.sub(r"\*\*([^*]+)\*\*",r'<strong>\1</strong>',value)
        value=re.sub(r"`([^`]+)`",r'<code>\1</code>',value)
        tag='h1' if line.startswith('# ') else 'h2' if line.startswith('## ') else 'p'
        if tag=='h1':value=value[2:]
        if tag=='h2':value=value[3:]
        output.append(f'<{tag}>{value}</{tag}>')
    return ''.join(output)
def page(title,body):
    return '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+title+'</title><style>'+CSS+'</style><main><a href="../index.html">Back to study</a>'+body+'</main></html>'
method=(ROOT/'docs/RESEARCH_AND_METHOD.md').read_text(encoding='utf8')
(ROOT/'docs/method.html').write_text(page('Sources and method',render(method)),encoding='utf8')
p=ROOT/'notebooks/analysis.ipynb';notebook=json.loads(p.read_text(encoding='utf8'));scope={};old=Path.cwd();os.chdir(p.parent)
try:
    number=0
    for cell in notebook['cells']:
        if cell['cell_type']!='code':continue
        output=io.StringIO()
        with contextlib.redirect_stdout(output):exec(''.join(cell['source']),scope)
        number+=1;cell['execution_count']=number;cell['outputs']=[{'output_type':'stream','name':'stdout','text':output.getvalue().splitlines(True)}]
finally:os.chdir(old)
p.write_text(json.dumps(notebook,indent=2),encoding='utf8')
body='<h1>Executed analysis</h1><p>Every event and observed status is synthetic. This report is rebuilt from the executed notebook.</p>'
for cell in notebook['cells']:
    if cell['cell_type']=='markdown':body+=render(''.join(cell['source']))
    else:
        body+='<pre>'+html.escape(''.join(cell['source']))+'</pre>'
        for output in cell['outputs']:body+='<pre>'+html.escape(''.join(output.get('text',[])))+'</pre>'
body+='<p><a href="https://github.com/felipervm/shakepay-reward-intelligence/blob/main/notebooks/analysis.ipynb">Notebook on GitHub</a></p>'
(ROOT/'docs/analysis.html').write_text(page('Executed analysis',body),encoding='utf8')
print('Notebook executed; method and analysis HTML rebuilt.')
