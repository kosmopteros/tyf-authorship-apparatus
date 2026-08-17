#!/usr/bin/env python3
import csv, json, re, time
from urllib.parse import urlparse, parse_qs
from playwright.sync_api import sync_playwright

ROOT='https://www.ccip.pt/pt/associados/associados'
OUT='ccip-click-output'

BAD_FIRST={'all','page','category','search','search-by','tag','country'}

def clean(s): return re.sub(r'\s+',' ',s or '').strip()
def field(text, labels):
    lines=[clean(x) for x in (text or '').splitlines() if clean(x)]
    for i,line in enumerate(lines):
        lo=line.lower().strip(' :')
        for lab in labels:
            if lo.startswith(lab+':'):
                return clean(line.split(':',1)[1])
            if lo==lab and i+1<len(lines):
                return clean(lines[i+1])
    return ''

def save(rows, meta):
    import os; os.makedirs(OUT, exist_ok=True)
    cols=['position','company','website','category','activity','contact_person','ccip_listing_url','image','directory_page','directory_source_url','card_text']
    with open(f'{OUT}/ccip_full_roster.csv','w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=cols); w.writeheader(); w.writerows(rows)
    with open(f'{OUT}/summary.json','w',encoding='utf-8') as f: json.dump(meta,f,ensure_ascii=False,indent=2)

def main():
    rows=[]; seen=set(); meta={'root':ROOT,'advertised_total':None,'pages_visited':0,'rows_captured':0,'errors':[],'page_stats':[]}
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,args=['--no-sandbox','--disable-dev-shm-usage','--disable-blink-features=AutomationControlled'])
        ctx=browser.new_context(locale='pt-PT',viewport={'width':1440,'height':1200},user_agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36',extra_http_headers={'Accept-Language':'pt-PT,pt;q=0.9,en;q=0.8'})
        page=ctx.new_page(); page.set_default_timeout(30000)
        page.goto(ROOT,wait_until='domcontentloaded',timeout=60000); page.wait_for_timeout(6000)
        for page_no in range(1, 220):
            try:
                body=page.locator('body').inner_text(timeout=15000)
                if meta['advertised_total'] is None:
                    m=re.search(r'Resultados\s+\d+\s*[-–]\s*\d+\s+de\s+(\d+)',body,re.I)
                    if m: meta['advertised_total']=int(m.group(1))
                items=page.evaluate(r'''() => {
                  const root='/pt/associados/associados/';
                  const abs=h=>{try{return new URL(h,location.href).href}catch(e){return ''}};
                  const external=h=>{try{const u=new URL(h,location.href);return /^https?:$/.test(u.protocol)&&!/(^|\.)ccip\.pt$/i.test(u.hostname)}catch(e){return false}};
                  const isDetail=a=>{try{const u=new URL(abs(a.getAttribute('href')||''));const i=u.pathname.indexOf(root);if(i<0)return false;const t=u.pathname.slice(i+root.length).split('/').filter(Boolean);return t.length>=2&&!['all','page','category','search','search-by','tag','country'].includes((t[0]||'').toLowerCase())}catch(e){return false}};
                  const cardFor=a=>{let c=a.closest('.listing-summary,.listing-summary-row,.mt-listing,.listing,article,[class*="listing-summary"],[class*="listing"]');if(c&&((c.innerText||'').length<5000))return c;let x=a.parentElement,last=x;for(let i=0;x&&i<9;i++,x=x.parentElement){last=x;const ds=[...x.querySelectorAll('a[href]')].filter(isDetail), tx=(x.innerText||'').trim();if(ds.length>=1&&ds.length<=3&&tx.length>20&&tx.length<5000)return x}return last||a.parentElement};
                  let anchors=[...document.querySelectorAll('h1 a[href],h2 a[href],h3 a[href],h4 a[href],h5 a[href],.mt-listing-title a[href],.listing-title a[href]')].filter(isDetail);
                  if(anchors.length<5) anchors=[...document.querySelectorAll('a[href]')].filter(isDetail);
                  const seen=new Set(), out=[];
                  for(const a of anchors){const url=abs(a.getAttribute('href')||'').split('#')[0],name=(a.innerText||a.textContent||'').replace(/\s+/g,' ').trim();if(!url||!name||seen.has(url))continue;seen.add(url);const c=cardFor(a);const txt=c?(c.innerText||'').trim():'';let website='',image='';if(c){for(const z of c.querySelectorAll('a[href]')){const h=abs(z.getAttribute('href')||'');if(external(h)){try{const host=new URL(h).hostname.toLowerCase();if(!/facebook|instagram|linkedin|youtube|twitter|x\.com/.test(host)){website=h;break}}catch(e){}}}const im=c.querySelector('img[src]');if(im)image=abs(im.getAttribute('src'))}out.push({name,url,website,image,text:txt})}return out;
                }''')
                before=len(rows)
                for x in items:
                    key=x['url'].rstrip('/').lower()
                    if key in seen: continue
                    seen.add(key); txt=x.get('text','')
                    rows.append({'position':len(rows)+1,'company':clean(x.get('name')),'website':clean(x.get('website')),'category':field(txt,['category','categoria']),'activity':field(txt,['actividade','atividade','activity']),'contact_person':field(txt,['pessoa contacto','pessoa de contacto','contact person']),'ccip_listing_url':clean(x.get('url')),'image':clean(x.get('image')),'directory_page':page_no,'directory_source_url':page.url,'card_text':clean(txt)})
                added=len(rows)-before; meta['pages_visited']=page_no; meta['rows_captured']=len(rows); meta['page_stats'].append({'page':page_no,'url':page.url,'items_seen':len(items),'new_rows':added,'total_rows':len(rows)})
                print(f'PAGE {page_no} items={len(items)} new={added} total={len(rows)} url={page.url}',flush=True)
                if page_no==1:
                    open(f'{OUT}/first_page.txt','w',encoding='utf-8').write(body[:10000])
                save(rows,meta)
                if meta['advertised_total'] and len(rows)>=meta['advertised_total']: break

                nxt=page.evaluate(r'''() => {
                  const abs=h=>{try{return new URL(h,location.href).href}catch(e){return ''}};
                  const cur=new URL(location.href); const curStart=parseInt(cur.searchParams.get('start')||'0',10); let candidates=[];
                  const sels=['a[rel="next"]','li.pagination-next a','li.next a','.pagination-next a','a[aria-label*="Seguinte" i]','a[title*="Seguinte" i]','a[aria-label*="Próximo" i]','a[title*="Próximo" i]','a[aria-label*="Next" i]','a[title*="Next" i]'];
                  for(const s of sels){for(const a of document.querySelectorAll(s)){const h=abs(a.getAttribute('href')||'');if(h)candidates.push({href:h,score:0})}}
                  for(const a of document.querySelectorAll('a[href]')){const h=abs(a.getAttribute('href')||'');if(!h)continue;try{const u=new URL(h);const st=u.searchParams.get('start');if(st!==null){const n=parseInt(st,10);if(Number.isFinite(n)&&n>curStart)candidates.push({href:h,score:100000+n})}const m=u.pathname.match(/\/all\/page(\d+)/i);if(m){const n=parseInt(m[1],10);if(Number.isFinite(n))candidates.push({href:h,score:200000+n})}}catch(e){}}
                  if(!candidates.length)return null; candidates.sort((a,b)=>a.score-b.score); return candidates[0].href;
                }''')
                if not nxt:
                    meta['errors'].append({'page':page_no,'error':'No next-page link found','url':page.url}); break
                old=page.url
                locator=page.locator(f'a[href="{nxt}"]').first
                try:
                    with page.expect_navigation(wait_until='domcontentloaded',timeout=60000): locator.click(timeout=15000)
                except Exception:
                    # Find by resolved href rather than literal attr.
                    clicked=page.evaluate(r'''href=>{for(const a of document.querySelectorAll('a[href]')){try{if(new URL(a.getAttribute('href'),location.href).href===href){a.click();return true}}catch(e){}}return false}''',nxt)
                    if clicked:
                        page.wait_for_load_state('domcontentloaded',timeout=60000)
                    else:
                        page.goto(nxt,wait_until='domcontentloaded',timeout=60000,referer=old)
                page.wait_for_timeout(500)
                if page.url==old:
                    meta['errors'].append({'page':page_no,'error':'Next click did not advance','url':old,'next':nxt}); break
            except Exception as e:
                meta['errors'].append({'page':page_no,'url':page.url,'error':f'{type(e).__name__}: {e}'})
                print('ERROR',meta['errors'][-1],flush=True); save(rows,meta); break
        browser.close()
    save(rows,meta)
    print(json.dumps(meta,ensure_ascii=False,indent=2),flush=True)
    target=meta['advertised_total'] or 1000
    if len(rows)<target:
        raise RuntimeError(f'Incomplete click scrape: {len(rows)}/{target}')

if __name__=='__main__': main()
