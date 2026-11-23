"""Offline project integrity checks; no API requests or credential output."""
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from motorcare.paths import KNOWLEDGE_DIR, CASES_DIR
from motorcare import ui, engine

def read(path): return json.loads(path.read_text())
def unique(rows,key):
    ids=[r[key] for r in rows]
    assert len(ids)==len(set(ids)), f'Duplicate {key}'

sources=read(KNOWLEDGE_DIR/'sources.json'); chunks=read(KNOWLEDGE_DIR/'chunks.json'); cases=read(CASES_DIR/'cases.json')
for rows,key in [(sources,'source_id'),(chunks,'chunk_id'),(cases,'case_id')]: unique(rows,key)
ids={s['source_id'] for s in sources}
for s in sources:
    if 'local_file' in s: assert (KNOWLEDGE_DIR/s['local_file']).is_file(),s['source_id']
for c in chunks:
    assert c['source_id'] in ids
    assert c['content_zh'] and c['content_en']
for i,c in enumerate(cases):
    assert set(c['source_ids'])<=ids
    for image in c['images']: assert (CASES_DIR/image).is_file(),image
    for lang in ['English','中文']:
        assert len(ui.TEXT[lang]['names'])==len(cases)
        loaded=ui.load_case(i,lang)
        assert loaded[-1]==i
        assert all(Path(x).is_file() for x in loaded[0]['files'])
        assert ui.load_followup(lang,i)['text']==c['followup_zh' if lang=='中文' else 'followup_en']
assert ui.reset('English')[-1] is None
for lang in ['English','中文']: assert 'AL30' in engine.system_prompt(lang,True)
ui.build()
# Validate full callback state changes with a fake service, without using credentials.
original=ui.analyze
ui.analyze=lambda text,paths,history,lang: ('Example result', history+[{'role':'user','content':text}])
try:
    box,hist,display,status=ui.submit({'text':'AL30','files':[]},[],[],'English')
    assert box==ui.empty() and len(hist)==1 and len(display)==2
    before=list(hist)
    summarized,_=ui.summarize(hist,display,'中文')
    assert hist==before and len(summarized)==len(display)+1
finally: ui.analyze=original
print('PASS: source/manual/image paths, bilingual data, case selection, reset, submit, summary and UI construction. No API requests.')
