#!/usr/bin/env python3
import csv, re, time
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright

BASES=[('pt','https://www.ccip.pt/pt/associados/associados'),('en','https://www.ccip.pt/en/members/members')]
OUT='ccip_members.csv'; FAILED='ccip_pages_failed.txt'; DEBUG='ccip_debug.txt'

def clean(s): return re.sub(r'\s+',' ',s or '').strip()
def total_from(text):
    for p in [r'Resultados\s+\d+\s*[-–]\s*\d+\s+de\s+([\d. ,]+)',r'Results\s+\d+\s*[-–]\s*\d+\s+of\s+([\d. ,]+)']:
        m=re.search(p,text or '',re.I)
        if m:
            d=re.sub(r'\D','',m.group(1));
            if d and 100<=int(d)<=10000:return int(d)

def field(text,names):
    lines=[clean(x) for x in (text or '').splitlines() if clean(x)]
    for i,line in enumerate(lines):
        low=line.lower().strip(' :')
        for n in names:
            if low.startswith(n+':'): return clean(line.split(':',1)[1])
            if low==n and i+1<len(lines): return lines[i+1]
    return ''

def parse(page,lang):
    prefix='/pt/associados/associados/' if lang=='pt' else '/en/members/members/'
    return page.evaluate(r'''({prefix})=>{
      const abs=h=>{try{return new URL(h,location.href).href}catch(e){return ''}};
      const isDetail=a=>{try{const u=new URL(abs(a.getAttribute('href')||''));const i=u.pathname.indexOf(prefix);if(i<0)return false;const t=u.pathname.slice(i+prefix.length).split('/').filter(Boolean);return t.length>=2&&!['search-by','all','page','search','tag','category','country'].includes((t[0]||'').toLowerCase())}catch(e){return false}};
      const external=h=>{try{const u=new URL(h,location.href);return /^https?:$/.test(u.protocol)&&!/(^|\.)ccip\.pt$/i.test(u.hostname)}catch(e){return false}};
      const cardFor=a=>{let c=a.closest('.listing-summary,.listing-summary-row,.mt-listing,.listing,article,[class*="listing-summary"]');if(c)return c;let x=a.parentElement,last=x;for(let i=0;x&&i<10;i++,x=x.parentElement){last=x;const d=[...x.querySelectorAll('a[href]')].filter(isDetail);const tx=(x.innerText||'').trim();if(d.length>=1&&d.length<=3&&tx.length>30&&tx.length<4000)return x}return last||a.parentElement};
      let aa=[...document.querySelectorAll('h1 a[href],h2 a[href],h3 a[href],h4 a[href],h5 a[href]')].filter(isDetail);if(aa.length<5)aa=[...document.querySelectorAll('a[href]')].filter(isDetail);
      const seen=new Set(),out=[];
      for(const a of aa){const url=abs(a.getAttribute('href')||'').split('#')[0],name=(a.innerText||a.textContent||'').replace(/\s+/g,' ').trim();if(!url||!name||seen.has(url))continue;seen.add(url);const c=cardFor(a),txt=c?(c.innerText||'').trim():'';let website='';if(c){for(const z of c.querySelectorAll('a[href]')){const h=abs(z.getAttribute('href')||'');if(external(h)){try{const host=new URL(h).hostname.toLowerCase();if(!/facebook|instagram|linkedin|youtube|twitter|x\.com/.test(host)){website=h;break}}catch(e){}}}}out.push({name,url,website,text:txt})}return out;
    }''',{'prefix':prefix})

def save(rows):
    cols=['company','website','category','activity','contact_person','ccip_listing_url','ccip_card_text']
    with open(OUT,'w',newline='',encoding='utf-8-sig') as f:
        w=csv.DictWriter(f,fieldnames=cols);w.writeheader();w.writerows(rows)

def main():
    rows=[];seen=set();fails=[];dbg=[]
    with sync_playwright() as p:
        b=p.chromium.launch(headless=True,args=['--no-sandbox','--disable-dev-shm-usage','--disable-blink-features=AutomationControlled'])
        ctx=b.new_context(locale='pt-PT',viewport={'width':1440,'height':1100},user_agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36')
        page=ctx.new_page();page.set_default_timeout(30000); chosen=None; total=None
        for lang,base in BASES:
            try:
                page.goto(base,wait_until='domcontentloaded',timeout=60000);page.wait_for_timeout(9000)
                body=page.locator('body').inner_text();items=parse(page,lang);dbg.append(f'{lang} title={page.title()} total={total_from(body)} items={len(items)} head={body[:1200]}')
                if len(items)>=5:chosen=(lang,base);total=total_from(body);break
            except Exception as e: dbg.append(f'{lang} failed {e!r}')
        if not chosen:
            open(DEBUG,'w',encoding='utf8').write('\n\n'.join(dbg));raise RuntimeError('CCIP blocked browser or listing selectors failed')
        lang,base=chosen; maxstart=(total+18 if total else 1500)
        for start in range(0,maxstart+1,9):
            url=base if start==0 else f'{base}?start={start}';items=None;err=''
            for attempt in range(3):
                try:
                    page.goto(url,wait_until='domcontentloaded',timeout=60000);page.wait_for_timeout(900 if start else 300)
                    body=page.locator('body').inner_text()
                    if 'request is being verified' in body.lower() or 'just a moment' in page.title().lower():page.wait_for_timeout(8000);body=page.locator('body').inner_text()
                    if total is None: total=total_from(body)
                    items=parse(page,lang)
                    if items: break
                    err=f'empty title={page.title()} head={body[:300]}'
                except Exception as e: err=repr(e);page.wait_for_timeout(2000*(attempt+1))
            if not items:fails.append((start,url,err));continue
            for x in items:
                key=x['url'].rstrip('/').lower()
                if key in seen:continue
                seen.add(key);txt=x['text']
                rows.append({'company':clean(x['name']),'website':clean(x['website']),'category':field(txt,['atividade','category']),'activity':field(txt,['actividade','activity']),'contact_person':field(txt,['pessoa contacto','pessoa de contacto','contact person']),'ccip_listing_url':x['url'],'ccip_card_text':clean(txt)})
            if start%90==0: print(f'start={start} rows={len(rows)} total={total}',flush=True);save(rows)
            if total and (len(rows)>=total or start>=total-1):break
            time.sleep(.15)
        b.close()
    save(rows)
    open(FAILED,'w',encoding='utf8').write('\n'.join(f'{a}\t{u}\t{e}' for a,u,e in fails))
    open(DEBUG,'w',encoding='utf8').write('\n\n'.join(dbg)+f'\nFINAL rows={len(rows)} total={total} failed={len(fails)}')
    print(f'FINAL rows={len(rows)} total={total} failed={len(fails)}')
    if len(rows)<1000 or (total and len(rows)<total-25):raise RuntimeError(f'Incomplete scrape {len(rows)}/{total}')
if __name__=='__main__':main()
