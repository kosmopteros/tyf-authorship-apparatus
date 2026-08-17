#!/usr/bin/env python3
import csv, json, re, os, time
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup

ROOT='https://www.ccip.pt/en/members/members'
OUT='ccip-http-en-output'
PAGES=[66,75,116,133]
UA='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36'

def get(url):
    last=''
    for i in range(4):
        try:
            r=requests.get(url,headers={'User-Agent':UA,'Accept-Language':'en-GB,en;q=0.9,pt;q=0.8','Referer':ROOT},timeout=40)
            if r.status_code==200 and len(r.content)>10000:return r.text,r.url
            last=f'{r.status_code}/{len(r.content)}'
        except Exception as e:last=repr(e)
        time.sleep(i+1)
    raise RuntimeError(last)

def clean(s):return re.sub(r'\s+',' ',s or '').strip()

def main():
    os.makedirs(OUT,exist_ok=True)
    rows=[]; summary=[]
    selectors=['.listing-summary','.listing-summary-row','.mt-listing','.listing','.mtree-listing','[class*="listing-summary"]']
    for p in PAGES:
        raw,url=get(f'{ROOT}/all/page{p}'); soup=BeautifulSoup(raw,'lxml')
        selcounts={s:len(soup.select(s)) for s in selectors}
        heads=[]
        for h in soup.find_all(['h2','h3','h4','h5']):
            txt=clean(h.get_text(' ',strip=True))
            if not txt:continue
            a=h.find('a',href=True)
            href=urljoin(url,a['href']) if a else ''
            cls=' '.join(h.get('class',[]))
            par=h.parent
            pcls=' '.join(par.get('class',[])) if par else ''
            heads.append({'page':p,'heading':h.name,'text':txt,'href':href,'heading_class':cls,'parent_class':pcls})
        summary.append({'page':p,'selector_counts':selcounts,'heading_count':len(heads)})
        rows.extend(heads)
        print('PAGE',p,'selectors',selcounts,'heads',[(x['heading'],x['text'],x['href']) for x in heads],flush=True)
    with open(f'{OUT}/ccip_debug_headings.csv','w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=['page','heading','text','href','heading_class','parent_class']);w.writeheader();w.writerows(rows)
    open(f'{OUT}/summary.json','w',encoding='utf-8').write(json.dumps(summary,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
