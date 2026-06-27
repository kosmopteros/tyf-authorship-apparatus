#!/usr/bin/env python3
"""TYF v0.6 local Workbench: multi-unit drafts, notes, footnotes, Gate packets."""
import argparse, datetime, hashlib, http.server, json, os, re, secrets, socketserver, sys, urllib.parse, webbrowser
from pathlib import Path

class WorkbenchError(Exception): pass
ROOT_WORK_ID='work'

def now(): return datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat()
def H(s): return hashlib.sha256((s or '').encode()).hexdigest()
def S(x,d=''): return str(x if x is not None else d).replace('\n',' ').replace('\r',' ').strip() or d
def ID(p,*xs): return p+'-'+H('|'.join(map(str,xs))+now()+secrets.token_hex(4))[:12]
def R(p):
    try: return Path(p).read_text(encoding='utf-8')
    except FileNotFoundError: return ''
def W(p,s):
    p=Path(p); p.parent.mkdir(parents=True,exist_ok=True); t=p.with_name('.'+p.name+'.tmp')
    t.write_text(s,encoding='utf-8'); os.replace(t,p)
def J(p,x): W(p,json.dumps(x,ensure_ascii=False,indent=2,sort_keys=True)+'\n')
def JR(p,d):
    try: return json.loads(R(p))
    except Exception: return d
def JA(p,x):
    p=Path(p); p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('a',encoding='utf-8') as f: f.write(json.dumps(x,ensure_ascii=False,sort_keys=True)+'\n')
def JL(p):
    a=[]
    for l in R(p).splitlines():
        if not l.strip(): continue
        try: a.append(json.loads(l))
        except Exception: a.append({'kind':'invalid-json','raw':l})
    return a
def JW(p,rows): W(p,''.join(json.dumps(r,ensure_ascii=False,sort_keys=True)+'\n' for r in rows))
def Y(p):
    d={}
    for l in R(p).splitlines():
        if l.strip() and not l.startswith(' ') and ':' in l:
            k,_,v=l.partition(':'); v=v.strip(); d[k.strip()]=json.loads(v) if v[:1]=='"' and v[-1:]=='"' else v
    return d
def slug(s): return re.sub(r'[^A-Za-z0-9._-]+','-',S(s).lower()).strip('-._')[:80] or 'unit'
def okid(w):
    if not re.fullmatch(r'[A-Za-z0-9._-]+',S(w)): raise WorkbenchError('unsafe work id')
    return w
def inside(root,p):
    try: Path(p).resolve(False).relative_to(Path(root).resolve()); return True
    except Exception: return False
def safe(root,rel,prefixes):
    r=S(rel).replace('\\','/').lstrip('/')
    if not r or r.startswith('../') or '/../' in r or os.path.isabs(r): raise WorkbenchError('unsafe path')
    if prefixes and not any(r==x.rstrip('/') or r.startswith(x) for x in prefixes): raise WorkbenchError('wrong path zone')
    p=Path(root)/r
    if not inside(root,p): raise WorkbenchError('path escapes work')
    return r,p

def resolve_work_root(work=None):
    ws=Path.cwd().resolve()
    if not (ws/'WORKSPACE_STATE.yaml').is_file(): raise WorkbenchError('Not in a TYF workspace')
    if not work or work==ROOT_WORK_ID:
        if (ws/'work.yaml').is_file(): return ROOT_WORK_ID,ws,ws
        a=Y(ws/'WORKSPACE_STATE.yaml').get('active_work','')
        if a and (ws/'works'/okid(a)/'work.yaml').is_file(): return a,ws/'works'/a,ws
        raise WorkbenchError('No work.yaml found')
    work=okid(work); root=(ws/'works'/work).resolve()
    if not (root/'work.yaml').is_file(): raise WorkbenchError('No work.yaml found')
    return work,root,ws

def log_event(ws,kind,ref='',detail=''):
    try: JA(ws/'.tyf'/'events.jsonl',{'seq':len(JL(ws/'.tyf'/'events.jsonl'))+1,'ts':now(),'kind':kind,'ref':ref,'detail':detail})
    except Exception: pass

def key(p):
    q=Path(p); q=Path(*q.parts[1:]) if q.parts and q.parts[0] in ('drafts','manuscript') else q
    return q.with_suffix('').as_posix()
def title(p): return Path(p).stem.replace('-',' ').replace('_',' ').title() or 'Untitled'
def texts(root,top):
    b=Path(root)/top
    return [] if not b.is_dir() else sorted(str(p.relative_to(root)).replace(os.sep,'/') for p in b.rglob('*') if p.is_file() and p.suffix.lower() in ('.md','.txt','.markdown'))
def discovered(root):
    d={}
    for r in texts(root,'drafts'):
        k=key(r); d.setdefault(k,{'id':slug(k),'title':title(r),'kind':'chapter','status':'draft'})['draft']=r
    for r in texts(root,'manuscript'):
        k=key(r); u=d.setdefault(k,{'id':slug(k),'title':title(r),'kind':'chapter','status':'manuscript','draft':'drafts/'+slug(k)+'.md'}); u['manuscript']=r
    if not d:
        p=Path(root)/'drafts/candidate-draft.md'; p.parent.mkdir(parents=True,exist_ok=True); p.touch(exist_ok=True)
        d['candidate-draft']={'id':'candidate-draft','title':'Candidate Draft','kind':'chapter','status':'draft','draft':'drafts/candidate-draft.md','manuscript':''}
    return list(d.values())
def parse_map(p):
    a=[]; cur=None; on=False
    for l in R(p).splitlines():
        s=l.strip()
        if s=='units:': on=True; continue
        if not on or not s: continue
        if s.startswith('- '):
            if cur: a.append(cur)
            cur={}; s=s[2:]
        if cur is not None and ':' in s:
            k,_,v=s.partition(':'); v=v.strip(); cur[k.strip()]=json.loads(v) if v[:1]=='"' and v[-1:]=='"' else v
    if cur: a.append(cur)
    return a
def map_text(work,us):
    out=['version: 1',f'work: {json.dumps(work)}','units:']
    for u in us:
        for k in ('id','title','kind','draft','manuscript','status'): out.append(('  - ' if k=='id' else '    ')+f'{k}: {json.dumps(S(u.get(k,"")),ensure_ascii=False)}')
    return '\n'.join(out)+'\n'
def units(root,work):
    mp=Path(root)/'outline/book-map.yaml'; a=parse_map(mp) if mp.is_file() else []
    if not a: a=discovered(root); W(mp,map_text(work,a))
    return [{'id':slug(u.get('id') or u.get('draft') or u.get('manuscript')),'title':S(u.get('title'),'Untitled'),'kind':S(u.get('kind'),'chapter'),'draft':S(u.get('draft'),'drafts/'+slug(u.get('id','unit'))+'.md'),'manuscript':S(u.get('manuscript'),''),'status':S(u.get('status'),'draft')} for u in a]
def ensure_workbench_shape(root,ws,work):
    for d in ('outline','drafts','manuscript','knowledge-base','.review/surface','.review/gate-packets','.review/footnote-candidates','.tyf'):(Path(root)/d).mkdir(parents=True,exist_ok=True)
    for p,b in [(Path(root)/'knowledge-base/author-notes.jsonl',''),(Path(root)/'.tyf/workbench-state.json',json.dumps({'version':1,'work':work,'active_unit_id':'','selection':{},'updated_at':now()},indent=2)+'\n'),(Path(ws)/'.tyf/events.jsonl','')]:
        if not p.exists(): W(p,b)
    if not (Path(root)/'outline/book-map.yaml').is_file(): W(Path(root)/'outline/book-map.yaml',map_text(work,discovered(root)))
def T(root,rel,pref):
    if not rel: return {'path':'','text':'','sha256':H(''),'exists':False}
    r,p=safe(root,rel,pref); s=R(p) if p.is_file() else ''; return {'path':r,'text':s,'sha256':H(s),'exists':p.is_file()}
def notes_path(root): return Path(root)/'knowledge-base/author-notes.jsonl'
def load_notes(root): return [r for r in JL(notes_path(root)) if r.get('kind') in ('author-note','invalid-json')]
def collect_workbench_data(root,ws,work,token=''):
    ensure_workbench_shape(root,ws,work); ns=load_notes(root); out=[]
    for u in units(root,work):
        d=T(root,u['draft'],('drafts/',)); m=T(root,u['manuscript'],('manuscript/',)) if u['manuscript'] else T(root,'',())
        ps={d['path'],m['path']}; un=[n for n in ns if n.get('unit_id')==u['id'] or n.get('target_path') in ps]
        out.append({**u,'draft':d,'manuscript':m,'notes':un,'note_count':len([n for n in un if n.get('kind')=='author-note' and n.get('status')!='dismissed'])})
    st=JR(Path(root)/'.tyf/workbench-state.json',{}); meta=Y(Path(root)/'work.yaml')
    return {'version':'0.6-local-double-surface','generated_at':now(),'server':{'token':token,'side_effects':bool(token)},'work':{'id':work,'title':meta.get('title') or 'Untitled work','language':meta.get('language') or 'undetermined','status':meta.get('status') or 'unknown'},'book_map':{'path':'outline/book-map.yaml','unit_count':len(out)},'units':out,'active_unit_id':st.get('active_unit_id') or (out[0]['id'] if out else ''),'notes':{'path':'knowledge-base/author-notes.jsonl','records':ns},'style':{'style_sheet':R(Path(root)/'style-sheet.md'),'book_style':R(Path(root)/'design/book-style.yaml')},'state':st}
def save_draft(root,ws,work,rel,base_hash,text):
    r,p=safe(root,rel,('drafts/',)); cur=R(p) if p.is_file() else ''
    if H(cur)!=base_hash: return {'status':'conflict','current_text':cur,'proposed_text':text,'message':'Draft changed on disk.'}
    W(p,text); log_event(ws,'workbench-save-draft',work,r); return {'status':'saved','sha256':H(text),'message':'Draft saved. manuscript/ was not touched.'}
def create_author_note(root,ws,work,payload):
    body=S(payload.get('body'))
    if not body: raise WorkbenchError('Author note body is empty.')
    r,_=safe(root,S(payload.get('target_path')),('drafts/','manuscript/','assets/images/')) if payload.get('target_path') else ('',root)
    n={'id':ID('note',work,S(payload.get('unit_id')),r,body),'kind':'author-note','work':work,'unit_id':S(payload.get('unit_id')),'target_path':r,'target_kind':S(payload.get('target_kind'),'selection'),'quote':str(payload.get('quote') or ''),'body':body,'status':'open','provenance':'author','created_at':now(),'updated_at':now(),'manuscript_written':False}
    JA(notes_path(root),n); log_event(ws,'workbench-author-note',work,n['id']); return {'status':'noted','note':n,'message':'Author note recorded. manuscript/ was not touched.'}
def create_footnote_candidate(root,ws,work,note_id):
    rows=load_notes(root); n=next((x for x in rows if x.get('id')==note_id),None)
    if not n: raise WorkbenchError('No author note found')
    cid=ID('fn',work,note_id); c={'id':cid,'kind':'footnote-candidate','work':work,'note_id':note_id,'target_path':n.get('target_path',''),'unit_id':n.get('unit_id',''),'quote':n.get('quote',''),'candidate_text':n.get('body',''),'status':'draft','created_at':now(),'manuscript_written':False}
    d=Path(root)/'.review/footnote-candidates'; J(d/(cid+'.json'),c); W(d/(cid+'.md'),f"# TYF footnote candidate: {cid}\n\nReview-only. manuscript/ was not touched.\n\n{c['candidate_text']}\n")
    for x in rows:
        if x.get('id')==note_id: x.update({'status':'converted-to-footnote','footnote_candidate_id':cid,'updated_at':now()})
    JW(notes_path(root),rows); log_event(ws,'workbench-footnote-candidate',work,cid); return {'status':'candidate','candidate':c,'json':f'.review/footnote-candidates/{cid}.json','markdown':f'.review/footnote-candidates/{cid}.md','message':'Footnote candidate written in review space. manuscript/ was not touched.'}
def create_gate_packet(root,ws,work,payload):
    r,p=safe(root,S(payload.get('path')),('drafts/',)); cur=R(p)
    if H(cur)!=S(payload.get('base_hash')): return {'status':'conflict','current_text':cur,'message':'Draft changed on disk.'}
    pid=ID('gate',work,r); sel=str(payload.get('selection') or cur); d=Path(root)/'.review/gate-packets'; data={'id':pid,'kind':'workbench-gate-packet','work':work,'source_path':r,'source_sha256':H(cur),'selection':sel,'note':S(payload.get('note')),'created_at':now(),'manuscript_written':False}
    J(d/(pid+'.json'),data); W(d/(pid+'.md'),f"# TYF Workbench Gate packet: {pid}\n\nReview-only. manuscript/ was not touched.\n\n{sel}\n"); log_event(ws,'workbench-gate-packet',work,pid); return {'status':'packet','id':pid,'json':f'.review/gate-packets/{pid}.json','markdown':f'.review/gate-packets/{pid}.md','message':'Gate packet written. manuscript/ was not touched.'}
def update_workbench_state(root,ws,work,payload):
    p=Path(root)/'.tyf/workbench-state.json'; st=JR(p,{})
    for k in ('active_unit_id','active_path','selection','scroll','visible_panels'):
        if k in payload: st[k]=payload[k]
    st.update({'version':1,'work':work,'updated_at':now()}); J(p,st); return {'status':'saved','state':st}
def create_context_packet(root,ws,work,payload,token=''):
    data=collect_workbench_data(root,ws,work); uid=S(payload.get('unit_id'),data['active_unit_id']); u=next((x for x in data['units'] if x['id']==uid),data['units'][0]); sel=payload.get('selection') if isinstance(payload.get('selection'),dict) else {}
    cid=ID('ctx',work,uid); p={'id':cid,'kind':'amanuensis-context-packet','work':data['work'],'active_unit':{'id':u['id'],'title':u['title'],'draft_path':u['draft']['path'],'draft_sha256':u['draft']['sha256'],'manuscript_path':u['manuscript']['path']},'selection':sel,'notes':u['notes'],'created_at':now(),'manuscript_written':False}
    d=Path(root)/'.review/surface'; J(d/(cid+'.json'),p); J(d/'active-context.json',p); W(d/(cid+'.md'),f"# TYF amanuensis context packet: {cid}\n\nReview-only. manuscript/ was not touched.\n\n{sel.get('quote','') if isinstance(sel,dict) else ''}\n"); return {'status':'context','id':cid,'packet':p,'json':f'.review/surface/{cid}.json','markdown':f'.review/surface/{cid}.md','message':'Amanuensis context packet written in .review/surface/.'}

def HTML(data):
    payload=json.dumps(data,ensure_ascii=False).replace('</','<\\/')
    return """<!doctype html><meta charset=utf-8><title>TYF Workbench</title><style>body{font-family:system-ui;margin:0}main{display:grid;grid-template-columns:220px 1fr 1fr 260px;height:100vh}nav,section,aside{border-right:1px solid #ddd;overflow:auto}textarea{width:100%;height:85vh;font:18px/1.6 Georgia}pre{white-space:pre-wrap}.unit{display:block;margin:8px;padding:8px;width:90%}.tools{padding:8px;background:#eee}.note{border:1px solid #ddd;margin:6px;padding:6px}</style><main><nav id=nav></nav><section><textarea id=d></textarea><div class=tools><button id=s>Save</button><button id=n>Note</button><button id=g>Gate</button><button id=c>Context</button><span id=o></span></div></section><section><pre id=m></pre></section><aside><input id=nb placeholder='author note'><div id=notes></div><pre id=pkt></pre></aside></main><script>let D=PAYLOAD,T=D.server.token||'',A=D.active_unit_id||D.units[0]?.id,d=document.getElementById('d');function U(){return D.units.find(x=>x.id==A)||D.units[0]}function P(u,b){return fetch(u,{method:'POST',headers:{'Content-Type':'application/json','X-TYF-Token':T},body:JSON.stringify(b)}).then(r=>r.json())}function sel(){return{path:d.dataset.path,quote:d.value.slice(d.selectionStart,d.selectionEnd),start_offset:d.selectionStart,end_offset:d.selectionEnd}}function R(){let u=U();nav.innerHTML=D.units.map(x=>`<button class=unit onclick="A='${x.id}';R()">${x.title}<br>${x.draft.path}</button>`).join('');d.value=u.draft.text;d.dataset.path=u.draft.path;d.dataset.hash=u.draft.sha256;m.textContent=u.manuscript.exists?u.manuscript.text:'No approved manuscript unit.';notes.innerHTML=(u.notes||[]).map(x=>`<div class=note>${x.body}<button onclick="fn('${x.id}')">footnote</button></div>`).join('')}s.onclick=()=>P('/api/save-draft',{path:d.dataset.path,base_hash:d.dataset.hash,text:d.value}).then(x=>{o.textContent=x.message;location.reload()});n.onclick=()=>P('/api/author-note',{unit_id:U().id,target_path:d.dataset.path,target_kind:'selection',quote:sel().quote,body:nb.value}).then(x=>{o.textContent=x.message;location.reload()});function fn(id){P('/api/footnote-candidate',{note_id:id}).then(x=>{o.textContent=x.message;location.reload()})}g.onclick=()=>P('/api/gate-packet',{path:d.dataset.path,base_hash:d.dataset.hash,selection:sel().quote,note:nb.value}).then(x=>o.textContent=x.message);c.onclick=()=>P('/api/context-packet',{unit_id:U().id,selection:sel()}).then(x=>pkt.textContent=JSON.stringify(x.packet,null,2));R()</script>""".replace('PAYLOAD',payload)
def write_surface_files(root,ws,work):
    data=collect_workbench_data(root,ws,work); d=Path(root)/'.review/surface'; J(d/'workbench-data.json',data); W(d/'index.html',HTML(data)); return d/'index.html',d/'workbench-data.json'
class Srv(socketserver.ThreadingMixIn,http.server.HTTPServer): daemon_threads=True; allow_reuse_address=True
def make_handler(root,ws,work,token):
    class H(http.server.BaseHTTPRequestHandler):
        def out(self,code,obj):
            b=json.dumps(obj,ensure_ascii=False).encode(); self.send_response(code); self.send_header('Content-Type','application/json'); self.end_headers(); self.wfile.write(b)
        def do_GET(self):
            p=urllib.parse.urlparse(self.path).path; data=collect_workbench_data(root,ws,work,token)
            if p in ('/','/index.html'):
                b=HTML(data).encode(); self.send_response(200); self.send_header('Content-Type','text/html'); self.end_headers(); self.wfile.write(b)
            elif p=='/workbench-data.json': self.out(200,data)
            else: self.send_error(404)
        def do_POST(self):
            if self.headers.get('X-TYF-Token')!=token: return self.out(403,{'message':'bad token'})
            body=json.loads(self.rfile.read(int(self.headers.get('Content-Length','0'))).decode() or '{}'); p=urllib.parse.urlparse(self.path).path
            f={'/api/save-draft':lambda:save_draft(root,ws,work,body.get('path',''),body.get('base_hash',''),body.get('text','')),'/api/author-note':lambda:create_author_note(root,ws,work,body),'/api/footnote-candidate':lambda:create_footnote_candidate(root,ws,work,S(body.get('note_id'))),'/api/gate-packet':lambda:create_gate_packet(root,ws,work,body),'/api/workbench-state':lambda:update_workbench_state(root,ws,work,body),'/api/context-packet':lambda:create_context_packet(root,ws,work,body,token)}.get(p)
            if not f: return self.send_error(404)
            try:
                r=f(); self.out(409 if r.get('status')=='conflict' else 200,r)
            except WorkbenchError as e: self.out(400,{'message':str(e)})
        def log_message(self,*a): pass
    return H
def main(argv=None):
    ap=argparse.ArgumentParser(); ap.add_argument('work',nargs='?'); ap.add_argument('--serve',action='store_true'); ap.add_argument('--host',default='127.0.0.1'); ap.add_argument('--port',type=int,default=8766); ap.add_argument('--open',action='store_true'); ap.add_argument('--allow-remote',action='store_true'); a=ap.parse_args(argv)
    try:
        work,root,ws=resolve_work_root(a.work); ensure_workbench_shape(root,ws,work); hp,dp=write_surface_files(root,ws,work); print('TYF Workbench v0.6:',hp.relative_to(root)); print('Workbench data:',dp.relative_to(root)); print('No manuscript text was written.')
        if a.serve:
            if a.host not in ('127.0.0.1','localhost','::1') and not a.allow_remote: raise WorkbenchError('Refused non-loopback host')
            token=secrets.token_urlsafe(24); srv=Srv((a.host,a.port),make_handler(root,ws,work,token)); url=f'http://{a.host}:{srv.server_port}/'; print('Serving',url); webbrowser.open(url) if a.open else None; srv.serve_forever()
        return 0
    except WorkbenchError as e: print('Refused:',e,file=sys.stderr); return 2
if __name__=='__main__': raise SystemExit(main())
