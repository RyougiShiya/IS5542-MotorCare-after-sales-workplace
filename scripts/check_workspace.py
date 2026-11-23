"""Offline UI transition regression; no model requests."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from motorcare import ui
app=ui.build()
fns=list(app.fns.values())
find=lambda name:[x.fn for x in fns if getattr(x.fn,'__name__','')==name]
pair=('BLM230-A2','BMUD30-C2')
choose=find('choose')[1]
clean=choose([],ui.empty(),'English',pair)
assert len(clean)==15 and clean[5]==1 and clean[10] is None
assert 'AL30' in clean[0]['text']
h=[{'role':'user','content':'existing ticket'}]
prompt=choose(h,{'text':'unsent','files':[]},'English',pair)
assert prompt[10]['index']==1 and prompt[11]['visible'] is True
assert prompt[1].get('__type__')=='update' # existing evidence not cleared
confirm=next(x.fn for x in fns if len(x.inputs)==2 and len(x.outputs)==15)
confirmed=confirm(prompt[10],'English')
assert confirmed[1]==[] and confirmed[5]==1 and confirmed[11]['visible'] is False
cancel=next(x.fn for x in fns if len(x.inputs)==0 and len(x.outputs)==2)
assert cancel()==(None,{'visible':False,'__type__':'update'})
assert not ui.valid_equipment('wrong',pair[1])
send=find('send')[0]
r=send(ui.empty(),h,[],'English','wrong',pair[1],pair)
assert r[1] is h and 'Unsupported' in r[3]
translated=find('translate')[0]('中文','',[])
assert len(translated)==21
assert translated[2]['label']=='电机型号'
css=(Path(ui.__file__).parent/'assets/workspace.css').read_text()
assert '#mc-demo {display:none!important' in css
print('PASS: hidden demo default, clean/dirty case transitions, confirmation/cancel, equipment validation, translation output wiring.')
