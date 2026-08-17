#!/usr/bin/env python3
import csv, json, re, time, os
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urljoin, urlparse, urlunparse
import requests
from bs4 import BeautifulSoup

ROOT='https://www.ccip.pt/en/members/members'
OUT='ccip-http-en-output'
UA='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36'
PAGES=[13,16,20,23,25,26,27,29,34,47,52,54,58,62,65,66,69,74,75,76,82,84,86,88,93,95,100,105,107,109,116,117,118,119,128,131,133,134,135]
BAD={'all','page','category','search','search-by','tag','country'}

def clean(s): return re.sub(r'\s+',' ',s or '').strip()
def canon(u):
    p=urlparse(u); return urlunparse((p.scheme,p.netloc,p.path.rstrip('/'),'','',''))
def is_detail(u):
    p=urlparse(u); root=urlparse(ROOT).path.rstrip('/'); path=p.path.rstrip('/')
    if path.startswith(root+'/'):
        tail=[x for x in path[len(root)+1:].split('/') if x]
        return len(tail)>=1 and tail[0].lower() not in BAD
    # A few uncategorized entries are linked by the Joomla/Mosets Tree route.
    return path.startswith('/en/component/mtree/') and len([x for x in path[len('/en/component/mtree/'):].split('/') if x])>=1 and '/search-by/' not in path

def get(url):
    last=''
    for i in range(4):
        try:
            r=requests.get(url,headers={'User-Agent':UA,'Accept-Language':'en-GB,en;q=0.9,pt;q=0.8','Referer':ROOT},timeout=40,allow_redirects=True)
            if r.status_code==200 and len(r.content)>10000: return r.text,r.url
            last=f'status={r.status_code} bytes={len(r.content)} final={r.url}'
        except Exception as e: last=f'{type(e).__name__}: {e}'
        time.sleep(1.3*(i+1))
    raise RuntimeError(last)

def field(text, labels):
    lines=[clean(x) for x in (text or '').splitlines() if clean(x)]
    for i,line in enumerate(lines):
        lo=line.lower().strip(' :')
        for lab in labels:
            if lo.startswith(lab+':'): return clean(line.split(':',1)[1])
            if lo==lab and i+1<len(lines): return clean(lines[i+1])
    return ''

def parse_page(n):
    url=f'{ROOT}/all/page{n}'
    raw,final=get(url); soup=BeautifulSoup(raw,'lxml')
    body=' '.join(soup.stripped_strings)
    m=re.search(r'Results\s+(\d+)\s*[-–]\s*(\d+)\s+of\s+([\d., ]+)',body,re.I)
    bounds=(int(m.group(1)),int(m.group(2)),int(re.sub(r'\D','',m.group(3)))) if m else None
    nodes=soup.select('h1 a[href],h2 a[href],h3 a[href],h4 a[href],h5 a[href],.mt-listing-title a[href],.listing-title a[href]')
    if not nodes: nodes=soup.find_all('a',href=True)
    out=[]; seen=set()
    for a in nodes:
        name=clean(a.get_text(' ',strip=True)); href=canon(urljoin(final,a.get('href','')))
        if not name or not is_detail(href): continue
        key=(name.lower(),href.lower())
        if key in seen: continue
        seen.add(key)
        card=a.find_parent('article') or a.find_parent(class_=re.compile(r'listing',re.I))
        if card is None:
            cur=a.parent
            for _ in range(8):
                if cur is None: break
                tx=clean(cur.get_text(' ',strip=True))
                if 20 < len(tx) < 5000: card=cur
                cur=cur.parent
        text='\n'.join(card.stripped_strings) if card else ''
        website=''; image=''
        if card:
            for z in card.find_all('a',href=True):
                h=urljoin(final,z.get('href',''))
                try:
                    u=urlparse(h); host=(u.hostname or '').lower()
                    if u.scheme in ('http','https') and 'ccip.pt' not in host and not re.search(r'facebook|instagram|linkedin|youtube|twitter|(^|\.)x\.com',host,re.I): website=h; break
                except Exception: pass
            im=card.find('img',src=True)
            if im: image=urljoin(final,im.get('src'))
        out.append({'company':name,'website':website,'category':field(text,['category']),'activity':field(text,['actividade','activity']),'contact_person':field(text,['pessoa contacto','pessoa de contacto','contact person']),'ccip_listing_url':href,'image':image,'card_text':clean(text),'directory_page':n,'directory_source_url':final})
    return {'page':n,'url':final,'bounds':bounds,'rows':out}

def main():
    os.makedirs(OUT,exist_ok=True); results={}; errors=[]
    with ThreadPoolExecutor(max_workers=5) as ex:
        futs={ex.submit(parse_page,n):n for n in PAGES}
        for fut in as_completed(futs):
            n=futs[fut]
            try:
                r=fut.result(); results[n]=r; print(f'page={n} rows={len(r["rows"])} bounds={r["bounds"]}',flush=True)
            except Exception as e:
                errors.append({'page':n,'error':f'{type(e).__name__}: {e}'}); print('FAIL',errors[-1],flush=True)
    rows=[]; bad=[]
    for n in PAGES:
        r=results.get(n)
        if not r: continue
        expected=9
        if len(r['rows'])!=expected: bad.append({'page':n,'got':len(r['rows']),'expected':expected,'bounds':r['bounds']})
        rows.extend(r['rows'])
    cols=['company','website','category','activity','contact_person','ccip_listing_url','image','directory_page','directory_source_url','card_text']
    with open(f'{OUT}/ccip_patch_pages.csv','w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=cols);w.writeheader();w.writerows(rows)
    summary={'pages_requested':PAGES,'pages_returned':len(results),'rows':len(rows),'bad_pages':bad,'errors':errors}
    open(f'{OUT}/summary.json','w',encoding='utf-8').write(json.dumps(summary,ensure_ascii=False,indent=2))
    print(json.dumps(summary,ensure_ascii=False,indent=2),flush=True)
    if errors or bad: raise RuntimeError(f'Patch incomplete: bad={len(bad)} errors={len(errors)}')

if __name__=='__main__': main()
