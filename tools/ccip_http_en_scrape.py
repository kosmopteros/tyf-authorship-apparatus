#!/usr/bin/env python3
import csv, json, math, re, time
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urljoin, urlparse, urlunparse
import requests
from bs4 import BeautifulSoup

ROOT='https://www.ccip.pt/en/members/members'
OUT='ccip-http-en-output'
UA='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36'
BAD={'all','page','category','search','search-by','tag','country'}

def clean(s): return re.sub(r'\s+',' ',s or '').strip()
def canon(u):
    p=urlparse(u); return urlunparse((p.scheme,p.netloc,p.path.rstrip('/'),'','',''))
def is_detail(u):
    p=urlparse(u); root=urlparse(ROOT).path.rstrip('/'); path=p.path.rstrip('/')
    if not path.startswith(root+'/'): return False
    tail=[x for x in path[len(root)+1:].split('/') if x]
    return len(tail)>=2 and tail[0].lower() not in BAD

def get(url, attempts=4):
    last=None
    for i in range(attempts):
        try:
            r=requests.get(url,headers={'User-Agent':UA,'Accept-Language':'en-GB,en;q=0.9,pt;q=0.8','Referer':ROOT},timeout=40,allow_redirects=True)
            if r.status_code==200 and len(r.content)>10000: return r.text,r.url
            last=f'status={r.status_code} bytes={len(r.content)} final={r.url}'
        except Exception as e: last=f'{type(e).__name__}: {e}'
        time.sleep(1.2*(i+1))
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
    url=ROOT if n==1 else f'{ROOT}/all/page{n}'
    raw,final=get(url)
    soup=BeautifulSoup(raw,'lxml')
    body=' '.join(soup.stripped_strings)
    m=re.search(r'Results\s+(\d+)\s*[-–]\s*(\d+)\s+of\s+(\d+)',body,re.I)
    bounds=(int(m.group(1)),int(m.group(2)),int(m.group(3))) if m else None
    nodes=soup.select('h1 a[href],h2 a[href],h3 a[href],h4 a[href],h5 a[href],.mt-listing-title a[href],.listing-title a[href]')
    if not nodes: nodes=soup.find_all('a',href=True)
    out=[]; seen=set()
    for a in nodes:
        name=clean(a.get_text(' ',strip=True)); href=canon(urljoin(final,a.get('href','')))
        if not name or not is_detail(href) or href in seen: continue
        seen.add(href)
        card=a.find_parent(['article']) or a.find_parent(class_=re.compile(r'listing',re.I))
        if card is None:
            cur=a.parent
            for _ in range(8):
                if cur is None: break
                tx=clean(cur.get_text(' ',strip=True)); ds=[z for z in cur.find_all('a',href=True) if is_detail(canon(urljoin(final,z.get('href',''))))]
                if 1<=len(ds)<=3 and 20<len(tx)<5000: card=cur; break
                cur=cur.parent
        text='\n'.join(card.stripped_strings) if card else ''
        website=''; image=''
        if card:
            for z in card.find_all('a',href=True):
                h=urljoin(final,z.get('href',''))
                try:
                    u=urlparse(h); host=u.hostname or ''
                    if u.scheme in ('http','https') and 'ccip.pt' not in host.lower() and not re.search(r'facebook|instagram|linkedin|youtube|twitter|(^|\.)x\.com',host,re.I):
                        website=h; break
                except Exception: pass
            im=card.find('img',src=True)
            if im: image=urljoin(final,im.get('src'))
        out.append({'company':name,'website':website,'category':field(text,['category']),'activity':field(text,['actividade','activity']),'contact_person':field(text,['pessoa contacto','pessoa de contacto','contact person']),'ccip_listing_url':href,'image':image,'card_text':clean(text)})
    return {'page':n,'url':url,'final_url':final,'bounds':bounds,'rows':out,'html_bytes':len(raw.encode('utf-8'))}

def save(all_rows, summary):
    import os; os.makedirs(OUT,exist_ok=True)
    cols=['position','company','website','category','activity','contact_person','ccip_listing_url','image','directory_page','directory_source_url','card_text']
    with open(f'{OUT}/ccip_full_roster.csv','w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=cols);w.writeheader();w.writerows(all_rows)
    open(f'{OUT}/summary.json','w',encoding='utf-8').write(json.dumps(summary,ensure_ascii=False,indent=2))

def main():
    first=parse_page(1)
    if not first['bounds']: raise RuntimeError('Could not parse current total from page 1')
    total=first['bounds'][2]; pages=math.ceil(total/9)
    results={1:first}; errors=[]
    print(f'CURRENT total={total} pages={pages} page1_rows={len(first["rows"])}',flush=True)
    with ThreadPoolExecutor(max_workers=5) as ex:
        futs={ex.submit(parse_page,n):n for n in range(2,pages+1)}
        for fut in as_completed(futs):
            n=futs[fut]
            try:
                r=fut.result();results[n]=r
                if n%10==0 or len(r['rows'])!=9: print(f'page={n} rows={len(r["rows"])} bounds={r["bounds"]}',flush=True)
            except Exception as e:
                errors.append({'page':n,'error':f'{type(e).__name__}: {e}'})
                print('FAIL',errors[-1],flush=True)
    all_rows=[];seen=set();page_stats=[]
    for n in range(1,pages+1):
        r=results.get(n); page_stats.append({'page':n,'ok':bool(r),'rows':len(r['rows']) if r else 0,'bounds':r['bounds'] if r else None,'url':r['final_url'] if r else None})
        if not r: continue
        for row in r['rows']:
            key=row['ccip_listing_url'].lower().rstrip('/')
            if key in seen: continue
            seen.add(key);row={'position':len(all_rows)+1,**row,'directory_page':n,'directory_source_url':r['final_url']};all_rows.append(row)
    summary={'advertised_total':total,'pages':pages,'rows_captured':len(all_rows),'failed_pages':errors,'page_stats':page_stats}
    save(all_rows,summary)
    print(json.dumps({'advertised_total':total,'pages':pages,'rows_captured':len(all_rows),'failed_pages':errors},ensure_ascii=False,indent=2),flush=True)
    missing_bounds=[]
    for n,r in results.items():
        if r['bounds']:
            expected_start=(n-1)*9+1; expected_end=min(n*9,total)
            if r['bounds'][:2]!=(expected_start,expected_end): missing_bounds.append({'page':n,'got':r['bounds'],'expected':[expected_start,expected_end,total]})
    if missing_bounds: raise RuntimeError(f'Wrong pagination bounds on {len(missing_bounds)} pages: {missing_bounds[:10]}')
    if errors or len(all_rows)!=total: raise RuntimeError(f'Incomplete: rows={len(all_rows)} total={total} failed_pages={len(errors)}')

if __name__=='__main__': main()
