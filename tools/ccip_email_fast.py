#!/usr/bin/env python3
import argparse,csv,html as htmlmod,json,os,re,time
from concurrent.futures import ThreadPoolExecutor,as_completed
from urllib.parse import unquote,urljoin,urlparse,urlunparse
import requests
from bs4 import BeautifulSoup

ROOT='https://www.ccip.pt/en/members/members'
UA='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36'
SOCIAL=('facebook.com','instagram.com','linkedin.com','youtube.com','twitter.com','x.com','tiktok.com')
TERMS=('contact','contacto','contactos','contacts','contato','sobre','about','quem-somos','equipa','team','comercial','sales','vendas','business')
EMAIL_RE=re.compile(r'(?<![A-Za-z0-9._%+\-])([A-Za-z0-9._%+\-]{1,64}@[A-Za-z0-9.\-]{1,253}\.[A-Za-z]{2,24})(?![A-Za-z0-9._%+\-])',re.I)
BAD_TLDS={'png','jpg','jpeg','gif','svg','webp','css','js','woff','woff2','ttf','eot','ico','pdf','zip'}
BAD_DOMAINS=('example.com','sentry.io','wixpress.com','cloudflare.com','schema.org','wordpress.org','googleapis.com')
TECH=('noreply','no-reply','donotreply','postmaster','webmaster','mailer-daemon','unsubscribe')
LOW=('privacy','privacidade','dpo','rgpd','gdpr','legal','abuse','security','cookie')
SALES=('sales','comercial','commercial','vendas','negocios','business','parcerias','partnership','reservas','booking','export')
GENERAL=('info','geral','contact','contacto','contato','hello','ola','office','portugal','lisboa','porto','secretaria','admin')
SUPPORT=('support','suporte','apoio','help','customer','cliente','assistencia')
HR=('careers','jobs','recrut','recruit','emprego','rh','hr')


def clean(s):return re.sub(r'\s+',' ',s or '').strip()
def dkey(h):
    h=(h or '').lower().split(':')[0].strip('.')
    return h[4:] if h.startswith('www.') else h
def same(a,b):
    x,y=dkey(urlparse(a).hostname),dkey(urlparse(b).hostname)
    return bool(x and y and (x==y or x.endswith('.'+y) or y.endswith('.'+x)))
def sess():
    s=requests.Session();s.headers.update({'User-Agent':UA,'Accept-Language':'pt-PT,pt;q=0.9,en;q=0.8'});return s

def fetch(s,u,timeout=(4,8)):
    for verify in (True,False):
        try:
            r=s.get(u,timeout=timeout,allow_redirects=True,verify=verify)
            if r.status_code>=400:continue
            ct=(r.headers.get('content-type') or '').lower()
            if ct and 'html' not in ct and not ct.startswith('text/'):return None,r.url,f'non-html:{ct[:50]}'
            raw=r.content[:1800000]; enc=r.encoding or r.apparent_encoding or 'utf-8'
            try:return raw.decode(enc,errors='replace'),r.url,''
            except:return raw.decode('utf-8',errors='replace'),r.url,''
        except:pass
    return None,u,'fetch-failed'

def normmail(e):
    e=htmlmod.unescape(unquote(e or '')).strip(" <>[](){}'\".,;:").lower(); e=re.sub(r'\s+','',e)
    if not EMAIL_RE.fullmatch(e):return ''
    local,dom=e.rsplit('@',1);tld=dom.rsplit('.',1)[-1]
    if tld in BAD_TLDS or any(dom==d or dom.endswith('.'+d) for d in BAD_DOMAINS) or any(x in local for x in TECH):return ''
    return e

def cfdecode(h):
    try:
        b=bytes.fromhex(h);k=b[0];return bytes(x^k for x in b[1:]).decode(errors='ignore')
    except:return ''

def emails(raw,src):
    out={}; soup=BeautifulSoup(raw or '','lxml')
    for a in soup.select('a[href^="mailto:" i]'):
        p=(a.get('href') or '').split(':',1)[1].split('?',1)[0]
        for q in re.split(r'[;,]',p):
            e=normmail(q)
            if e:out.setdefault(e,src)
    for n in soup.select('[data-cfemail]'):
        e=normmail(cfdecode(n.get('data-cfemail') or ''))
        if e:out.setdefault(e,src)
    samples=[raw or '',soup.get_text(' ',strip=True)]
    for sample in samples:
        sample=htmlmod.unescape(sample)
        sample=re.sub(r'\s*(?:\[|\()\s*(?:at|arroba)\s*(?:\]|\))\s*','@',sample,flags=re.I)
        sample=re.sub(r'\s*(?:\[|\()\s*(?:dot|ponto)\s*(?:\]|\))\s*','.',sample,flags=re.I)
        for m in EMAIL_RE.finditer(sample):
            e=normmail(m.group(1))
            if e:out.setdefault(e,src)
    return out

def classify(e,site):
    local,dom=e.split('@',1); host=dkey(urlparse(site).hostname); same_dom=host and (dom==host or dom.endswith('.'+host) or host.endswith('.'+dom))
    if any(x in local for x in LOW):typ,sc='privacy/legal',15
    elif any(x in local for x in SALES):typ,sc='sales/business',100
    elif any(local==x or local.startswith(x+'.') or local.startswith(x+'-') for x in GENERAL):typ,sc='general',80
    elif any(x in local for x in SUPPORT):typ,sc='support/customer',55
    elif any(x in local for x in HR):typ,sc='hr/careers',45
    else:typ,sc='named/work',90
    return typ,sc+(8 if same_dom else 0)

def links(raw,base):
    soup=BeautifulSoup(raw or '','lxml'); c={}
    for a in soup.find_all('a',href=True):
        h=a.get('href') or ''
        if h.startswith(('mailto:','tel:','javascript:','#')):continue
        u=urljoin(base,h)
        if not same(base,u):continue
        low=(u+' '+clean(a.get_text(' ',strip=True))).lower();score=sum(1 for t in TERMS if t in low)
        if score:c[u]=max(c.get(u,0),score)
    return [u for u,_ in sorted(c.items(),key=lambda x:(-x[1],len(x[0])))[:2]]
def starts(site):
    site=clean(site)
    if not site:return []
    if not re.match(r'^https?://',site,re.I):return ['https://'+site,'http://'+site]
    p=urlparse(site);o=[site]
    if p.scheme=='http':o.insert(0,urlunparse(('https',p.netloc,p.path,p.params,p.query,p.fragment)))
    return list(dict.fromkeys(o))

def crawl(t):
    if not t['website']:
        return {**t,'all_public_emails':'','email_types':'','best_email':'','best_type':'','best_source_url':'','status':'no_website','pages_checked':0,'final_home_url':'','crawl_error':''}
    s=sess();raw=None;home='';err=''
    for u in starts(t['website']):
        raw,home,err=fetch(s,u)
        if raw:break
    if not raw:return {**t,'all_public_emails':'','email_types':'','best_email':'','best_type':'','best_source_url':'','status':'site_error','pages_checked':0,'final_home_url':home or t['website'],'crawl_error':err}
    found=emails(raw,home);pc=1
    for u in links(raw,home):
        r,f,e=fetch(s,u);pc+=1
        if r:
            for k,v in emails(r,f).items():found.setdefault(k,v)
    rank=[]
    for e,src in found.items():
        typ,sc=classify(e,home);rank.append((sc,e,typ,src))
    rank.sort(key=lambda x:(-x[0],x[1])); best=rank[0] if rank else None
    return {**t,'all_public_emails':'; '.join(x[1] for x in rank[:12]),'email_types':'; '.join(x[2] for x in rank[:12]),'best_email':best[1] if best else '','best_type':best[2] if best else '','best_source_url':best[3] if best else '','status':'found' if best else 'not_found','pages_checked':pc,'final_home_url':home,'crawl_error':''}

def ccip_page(s,n):
    u=ROOT if n==1 else f'{ROOT}/all/page{n}';raw,final,err=fetch(s,u,(5,18))
    if not raw:raise RuntimeError(f'{n}:{err}')
    soup=BeautifulSoup(raw,'lxml');blocks=soup.select('.listing-summary');exp=5 if n==147 else 9
    if len(blocks)!=exp:raise RuntimeError(f'{n}:blocks={len(blocks)} expected={exp}')
    out=[]
    for i,b in enumerate(blocks,1):
        no=(n-1)*9+i;h=b.find(['h2','h3','h4']);company=clean(h.get_text(' ',strip=True) if h else '')
        lu='';a=h.find('a',href=True) if h else None
        if a:lu=urljoin(final,a.get('href'))
        site=''
        for a in b.find_all('a',href=True):
            x=urljoin(final,a.get('href') or '');p=urlparse(x);host=(p.hostname or '').lower()
            if p.scheme in ('http','https') and host and not host.endswith('ccip.pt') and not any(z in host for z in SOCIAL):site=x;break
        out.append({'ccip_no':no,'company':company,'website':site,'ccip_listing_url':lu,'ccip_page':n,'ccip_item':i})
    return out

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--shard',type=int,required=True);ap.add_argument('--shards',type=int,default=8);ap.add_argument('--workers',type=int,default=25);ap.add_argument('--output',required=True);a=ap.parse_args();os.makedirs(a.output,exist_ok=True)
    s=sess();targets=[];pages=[n for n in range(1,148) if (n-1)%a.shards==a.shard]
    for n in pages:
        targets.extend(ccip_page(s,n));time.sleep(.03)
    print(f'shard={a.shard} pages={len(pages)} records={len(targets)} websites={sum(bool(x["website"]) for x in targets)}',flush=True)
    res=[]
    with ThreadPoolExecutor(max_workers=a.workers) as ex:
        fs={ex.submit(crawl,t):t for t in targets}
        for k,f in enumerate(as_completed(fs),1):
            try:r=f.result()
            except Exception as e:r={**fs[f],'all_public_emails':'','email_types':'','best_email':'','best_type':'','best_source_url':'','status':'crawler_exception','pages_checked':0,'final_home_url':'','crawl_error':f'{type(e).__name__}:{e}'}
            res.append(r)
            if k%25==0:print(f'shard={a.shard} done={k}/{len(targets)} found={sum(bool(x["best_email"]) for x in res)}',flush=True)
    res.sort(key=lambda x:x['ccip_no']);fields=['ccip_no','company','website','ccip_listing_url','ccip_page','ccip_item','all_public_emails','email_types','best_email','best_type','best_source_url','status','pages_checked','final_home_url','crawl_error']
    with open(os.path.join(a.output,f'ccip_email_fast_{a.shard}.csv'),'w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(res)
    sm={'shard':a.shard,'records':len(res),'websites':sum(bool(x['website']) for x in res),'with_email':sum(bool(x['best_email']) for x in res),'site_error':sum(x['status']=='site_error' for x in res),'not_found':sum(x['status']=='not_found' for x in res)}
    open(os.path.join(a.output,'summary.json'),'w').write(json.dumps(sm,indent=2));print(json.dumps(sm,indent=2),flush=True)
if __name__=='__main__':main()
