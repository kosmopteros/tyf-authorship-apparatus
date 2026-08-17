#!/usr/bin/env python3
import argparse
import csv
import html as htmlmod
import json
import os
import re
import ssl
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from urllib.parse import unquote, urljoin, urlparse, urlunparse

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

CCIP_ROOT = "https://www.ccip.pt/en/members/members"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36"
SOCIAL_HOSTS = ("facebook.com", "instagram.com", "linkedin.com", "youtube.com", "twitter.com", "x.com", "tiktok.com")
CONTACT_TERMS = (
    "contact", "contacto", "contactos", "contacts", "contato", "contatos", "contacte", "contact-us",
    "sobre", "about", "quem-somos", "empresa", "company", "equipa", "team", "staff", "people",
    "comercial", "commercial", "sales", "vendas", "negocios", "business", "parcerias", "partnership",
    "imprensa", "press", "media"
)
COMMON_PATHS = (
    "/contactos", "/contactos/", "/contact", "/contact/", "/contacts", "/contacts/",
    "/contact-us", "/contact-us/", "/sobre-nos", "/sobre-nos/", "/quem-somos", "/quem-somos/",
    "/about", "/about/", "/about-us", "/about-us/", "/equipa", "/equipa/", "/team", "/team/"
)
EMAIL_RE = re.compile(r"(?<![A-Za-z0-9._%+\-])([A-Za-z0-9._%+\-]{1,64}@[A-Za-z0-9.\-]{1,253}\.[A-Za-z]{2,24})(?![A-Za-z0-9._%+\-])", re.I)
OBF_RE = re.compile(
    r"([A-Za-z0-9._%+\-]{1,64})\s*(?:\[|\(|\{)?\s*(?:at|arroba)\s*(?:\]|\)|\})?\s*"
    r"([A-Za-z0-9\-]+(?:\s*(?:\[|\(|\{)?\s*(?:dot|ponto)\s*(?:\]|\)|\})?\s*[A-Za-z0-9\-]+)+)", re.I
)
BAD_TLDS = {"png", "jpg", "jpeg", "gif", "svg", "webp", "css", "js", "woff", "woff2", "ttf", "eot", "ico", "pdf", "zip"}
BAD_DOMAINS = {
    "example.com", "example.org", "example.net", "sentry.io", "wixpress.com", "cloudflare.com",
    "schema.org", "wordpress.org", "wordpress.com", "googleapis.com", "gravatar.com"
}
LOW_LOCAL = ("privacy", "privacidade", "dpo", "rgpd", "gdpr", "legal", "jurid", "abuse", "security", "cookie", "cookies")
TECH_LOCAL = ("noreply", "no-reply", "donotreply", "postmaster", "webmaster", "mailer-daemon", "unsubscribe")
HR_LOCAL = ("careers", "career", "jobs", "job", "recrut", "recruit", "emprego", "rh", "recursos.humanos", "hr")
SUPPORT_LOCAL = ("support", "suporte", "apoio", "help", "customer", "cliente", "clientes", "assistencia")
SALES_LOCAL = ("sales", "comercial", "commercial", "vendas", "negocios", "business", "partnership", "parcerias", "booking", "reservas", "export")
GENERAL_LOCAL = ("info", "geral", "contact", "contacto", "contato", "hello", "ola", "office", "portugal", "lisboa", "porto", "secretaria", "admin")


def clean(s):
    return re.sub(r"\s+", " ", s or "").strip()


def canonical_url(u):
    p = urlparse(u)
    return urlunparse((p.scheme, p.netloc, p.path or "/", "", p.query, ""))


def domain_key(host):
    host = (host or "").lower().split(":")[0].strip(".")
    if host.startswith("www."):
        host = host[4:]
    return host


def same_site(a, b):
    ha, hb = domain_key(urlparse(a).hostname), domain_key(urlparse(b).hostname)
    if not ha or not hb:
        return False
    return ha == hb or ha.endswith("." + hb) or hb.endswith("." + ha)


def make_session():
    s = requests.Session()
    s.headers.update({
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "pt-PT,pt;q=0.9,en;q=0.8",
    })
    retry = Retry(total=2, connect=2, read=1, backoff_factor=0.35, status_forcelist=[408, 425, 429, 500, 502, 503, 504], allowed_methods=["GET", "HEAD"])
    s.mount("http://", HTTPAdapter(max_retries=retry, pool_connections=20, pool_maxsize=20))
    s.mount("https://", HTTPAdapter(max_retries=retry, pool_connections=20, pool_maxsize=20))
    return s


def fetch(session, url, timeout=(7, 16)):
    last = ""
    for verify in (True, False):
        try:
            r = session.get(url, timeout=timeout, allow_redirects=True, verify=verify)
            ctype = (r.headers.get("content-type") or "").lower()
            if r.status_code >= 400:
                last = f"HTTP {r.status_code}"
                continue
            if "text/html" not in ctype and "application/xhtml" not in ctype and not ctype.startswith("text/"):
                return None, r.url, f"non-html:{ctype[:80]}"
            raw = r.content[:2_500_000]
            enc = r.encoding or r.apparent_encoding or "utf-8"
            try:
                text = raw.decode(enc, errors="replace")
            except LookupError:
                text = raw.decode("utf-8", errors="replace")
            return text, r.url, ""
        except requests.exceptions.SSLError as e:
            last = f"SSL:{type(e).__name__}"
            continue
        except Exception as e:
            last = f"{type(e).__name__}:{e}"
            break
    return None, url, last or "fetch-failed"


def decode_cfemail(hexstr):
    try:
        data = bytes.fromhex(hexstr)
        key = data[0]
        return bytes(b ^ key for b in data[1:]).decode("utf-8", errors="ignore")
    except Exception:
        return ""


def normalize_email(e):
    e = htmlmod.unescape(unquote((e or "").strip())).strip(" <>[](){}'\".,;:")
    e = re.sub(r"\s+", "", e).lower()
    if not EMAIL_RE.fullmatch(e):
        return ""
    local, dom = e.rsplit("@", 1)
    tld = dom.rsplit(".", 1)[-1].lower()
    if tld in BAD_TLDS:
        return ""
    if dom.lower() in BAD_DOMAINS or any(dom.lower().endswith("." + d) for d in BAD_DOMAINS):
        return ""
    if any(x in local for x in TECH_LOCAL):
        return ""
    if len(local) < 1 or len(dom) < 4:
        return ""
    return e


def deobfuscate_text(text):
    # Conservative transformations for common published forms such as name [at] domain [dot] pt.
    t = htmlmod.unescape(text or "")
    t = re.sub(r"\s*(?:\[|\(|\{)\s*(?:at|arroba)\s*(?:\]|\)|\})\s*", "@", t, flags=re.I)
    t = re.sub(r"\s+(?:at|arroba)\s+", "@", t, flags=re.I)
    t = re.sub(r"\s*(?:\[|\(|\{)\s*(?:dot|ponto)\s*(?:\]|\)|\})\s*", ".", t, flags=re.I)
    t = re.sub(r"\s+(?:dot|ponto)\s+", ".", t, flags=re.I)
    return t


def extract_emails(raw_html, source_url):
    found = {}
    if not raw_html:
        return found
    soup = BeautifulSoup(raw_html, "lxml")

    # mailto: is the cleanest signal.
    for a in soup.select('a[href^="mailto:" i]'):
        href = a.get("href") or ""
        payload = href.split(":", 1)[1].split("?", 1)[0]
        for piece in re.split(r"[;,]", payload):
            e = normalize_email(piece)
            if e:
                found.setdefault(e, source_url)

    # Cloudflare email protection.
    for node in soup.select("[data-cfemail]"):
        e = normalize_email(decode_cfemail(node.get("data-cfemail") or ""))
        if e:
            found.setdefault(e, source_url)

    # Visible page text plus relevant HTML attributes/scripts.
    samples = [raw_html, soup.get_text(" ", strip=True)]
    for tag in soup.find_all(True):
        for attr in ("data-email", "data-mail", "content", "title", "aria-label"):
            v = tag.get(attr)
            if isinstance(v, str) and "@" in v:
                samples.append(v)
    for sample in samples:
        sample = deobfuscate_text(sample)
        for m in EMAIL_RE.finditer(sample):
            e = normalize_email(m.group(1))
            if e:
                found.setdefault(e, source_url)
    return found


def classify_email(email, website_url):
    local, dom = email.lower().split("@", 1)
    site_host = domain_key(urlparse(website_url).hostname)
    same = site_host and (dom == site_host or dom.endswith("." + site_host) or site_host.endswith("." + dom))
    if any(x in local for x in LOW_LOCAL):
        typ, score = "privacy/legal", 15
    elif any(x in local for x in SALES_LOCAL):
        typ, score = "sales/business", 100
    elif any(local == x or local.startswith(x + ".") or local.startswith(x + "-") for x in GENERAL_LOCAL):
        typ, score = "general", 80
    elif any(x in local for x in SUPPORT_LOCAL):
        typ, score = "support/customer", 55
    elif any(x in local for x in HR_LOCAL):
        typ, score = "hr/careers", 45
    else:
        # Non-generic address is usually a named/work mailbox.
        typ, score = "named/work", 90
    if same:
        score += 8
    return typ, score


def candidate_links(raw_html, base_url):
    soup = BeautifulSoup(raw_html or "", "lxml")
    cand = {}
    for a in soup.find_all("a", href=True):
        href = a.get("href") or ""
        if href.startswith(("mailto:", "tel:", "javascript:", "#")):
            continue
        u = urljoin(base_url, href)
        if not same_site(base_url, u):
            continue
        p = urlparse(u)
        if p.scheme not in ("http", "https"):
            continue
        text = clean(a.get_text(" ", strip=True)).lower()
        low = (u + " " + text).lower()
        score = 0
        for term in CONTACT_TERMS:
            if term in low:
                score += 10
        if score:
            cu = canonical_url(u)
            cand[cu] = max(cand.get(cu, 0), score)
    return [u for u, _ in sorted(cand.items(), key=lambda kv: (-kv[1], len(kv[0])))[:7]]


def normalize_website(site):
    site = clean(site)
    if not site:
        return []
    if not re.match(r"^https?://", site, re.I):
        return ["https://" + site, "http://" + site]
    out = [site]
    p = urlparse(site)
    if p.scheme == "http":
        out.insert(0, urlunparse(("https", p.netloc, p.path, p.params, p.query, p.fragment)))
    return list(dict.fromkeys(out))


def crawl_site(target):
    session = make_session()
    site = target.get("website") or ""
    base_raw = None
    final_home = ""
    home_error = ""
    for start in normalize_website(site):
        raw, final, err = fetch(session, start)
        if raw:
            base_raw, final_home = raw, final
            break
        home_error = err
    if not base_raw:
        return {**target, "email_count": 0, "all_public_emails": "", "email_types": "", "best_email": "", "best_type": "", "best_source_url": "", "all_source_urls": "", "status": "site_error", "pages_checked": 0, "final_home_url": final_home or site, "crawl_error": home_error}

    emails = extract_emails(base_raw, final_home)
    pages_checked = 1
    visited = {canonical_url(final_home)}
    links = candidate_links(base_raw, final_home)

    # If the home page does not expose useful navigation, try common contact/about paths.
    if len(links) < 3:
        root = urlunparse((urlparse(final_home).scheme, urlparse(final_home).netloc, "", "", "", ""))
        for path in COMMON_PATHS:
            u = root.rstrip("/") + path
            if canonical_url(u) not in visited:
                links.append(u)
    # Keep crawl bounded.
    links = list(dict.fromkeys(links))[:8]

    for u in links:
        cu = canonical_url(u)
        if cu in visited:
            continue
        visited.add(cu)
        raw, final, err = fetch(session, u)
        pages_checked += 1
        if not raw:
            continue
        for e, src in extract_emails(raw, final).items():
            emails.setdefault(e, src)
        # Once we have several good addresses, extra crawling rarely adds value.
        businessish = [e for e in emails if classify_email(e, final_home)[1] >= 80]
        if len(businessish) >= 3 and pages_checked >= 3:
            break

    ranked = []
    for e, src in emails.items():
        typ, score = classify_email(e, final_home)
        ranked.append((score, e, typ, src))
    ranked.sort(key=lambda x: (-x[0], x[1]))

    # Keep all public addresses, but sort business-relevant ones first.
    all_emails = [x[1] for x in ranked]
    all_types = [x[2] for x in ranked]
    all_sources = []
    for x in ranked:
        if x[3] and x[3] not in all_sources:
            all_sources.append(x[3])
    best = ranked[0] if ranked else None
    if not best:
        status = "not_found"
    elif best[0] < 50:
        status = "found_only_low_priority"
    else:
        status = "found"
    return {
        **target,
        "email_count": len(all_emails),
        "all_public_emails": "; ".join(all_emails[:12]),
        "email_types": "; ".join(all_types[:12]),
        "best_email": best[1] if best else "",
        "best_type": best[2] if best else "",
        "best_source_url": best[3] if best else "",
        "all_source_urls": "; ".join(all_sources[:12]),
        "status": status,
        "pages_checked": pages_checked,
        "final_home_url": final_home,
        "crawl_error": "",
    }


def ccip_page(session, page_no):
    url = CCIP_ROOT if page_no == 1 else f"{CCIP_ROOT}/all/page{page_no}"
    raw, final, err = fetch(session, url, timeout=(8, 30))
    if not raw:
        raise RuntimeError(f"CCIP page {page_no}: {err}")
    soup = BeautifulSoup(raw, "lxml")
    blocks = soup.select(".listing-summary")
    expected = 5 if page_no == 147 else 9
    if len(blocks) != expected:
        raise RuntimeError(f"CCIP page {page_no}: expected {expected} listing blocks, got {len(blocks)}")
    rows = []
    for i, block in enumerate(blocks, start=1):
        ccip_no = (page_no - 1) * 9 + i
        h = block.find(["h2", "h3", "h4"])
        company = clean(h.get_text(" ", strip=True) if h else "")
        listing_url = ""
        if h:
            a = h.find("a", href=True)
            if a:
                listing_url = urljoin(final, a.get("href"))
        website = ""
        for a in block.find_all("a", href=True):
            href = urljoin(final, a.get("href") or "")
            p = urlparse(href)
            host = (p.hostname or "").lower()
            if p.scheme not in ("http", "https") or not host or host.endswith("ccip.pt"):
                continue
            if any(s in host for s in SOCIAL_HOSTS):
                continue
            website = href
            break
        rows.append({"ccip_no": ccip_no, "company": company, "website": website, "ccip_listing_url": listing_url, "ccip_page": page_no, "ccip_item": i})
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--shard", type=int, required=True)
    ap.add_argument("--shards", type=int, default=4)
    ap.add_argument("--workers", type=int, default=10)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()
    os.makedirs(args.output, exist_ok=True)

    ccip_session = make_session()
    assigned_pages = [n for n in range(1, 148) if (n - 1) % args.shards == args.shard]
    targets = []
    page_errors = []
    for n in assigned_pages:
        try:
            targets.extend(ccip_page(ccip_session, n))
        except Exception as e:
            page_errors.append({"page": n, "error": f"{type(e).__name__}:{e}"})
        time.sleep(0.08)

    print(f"SHARD {args.shard}: pages={len(assigned_pages)} targets={len(targets)} page_errors={len(page_errors)}", flush=True)
    if page_errors:
        print(json.dumps(page_errors, ensure_ascii=False, indent=2), flush=True)
        raise RuntimeError("CCIP directory capture incomplete")

    results = []
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futs = {ex.submit(crawl_site, t): t for t in targets}
        done = 0
        for fut in as_completed(futs):
            t = futs[fut]
            try:
                r = fut.result()
            except Exception as e:
                r = {**t, "email_count": 0, "all_public_emails": "", "email_types": "", "best_email": "", "best_type": "", "best_source_url": "", "all_source_urls": "", "status": "crawler_exception", "pages_checked": 0, "final_home_url": t.get("website", ""), "crawl_error": f"{type(e).__name__}:{e}"}
            results.append(r)
            done += 1
            if done % 25 == 0:
                found = sum(1 for x in results if x.get("best_email"))
                print(f"SHARD {args.shard}: done={done}/{len(targets)} found={found}", flush=True)

    results.sort(key=lambda x: int(x["ccip_no"]))
    fields = [
        "ccip_no", "company", "website", "ccip_listing_url", "ccip_page", "ccip_item",
        "email_count", "all_public_emails", "email_types", "best_email", "best_type",
        "best_source_url", "all_source_urls", "status", "pages_checked", "final_home_url", "crawl_error"
    ]
    out_csv = os.path.join(args.output, f"ccip_email_shard_{args.shard}.csv")
    with open(out_csv, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader(); w.writerows(results)

    summary = {
        "shard": args.shard,
        "shards": args.shards,
        "records": len(results),
        "with_website": sum(1 for x in results if x.get("website")),
        "with_email": sum(1 for x in results if x.get("best_email")),
        "found_status": sum(1 for x in results if x.get("status") == "found"),
        "not_found": sum(1 for x in results if x.get("status") == "not_found"),
        "site_error": sum(1 for x in results if x.get("status") == "site_error"),
        "no_website": sum(1 for x in results if not x.get("website")),
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    }
    open(os.path.join(args.output, f"summary_{args.shard}.json"), "w", encoding="utf-8").write(json.dumps(summary, ensure_ascii=False, indent=2))
    print(json.dumps(summary, ensure_ascii=False, indent=2), flush=True)

if __name__ == "__main__":
    main()
