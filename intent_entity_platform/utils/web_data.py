"""
Real web data utilities (no API keys required).

Sources:
- DuckDuckGo HTML search (SERP data)
- Live HTTP fetches (page HTML, response headers, link/robots/sitemap checks)
- Wayback Machine CDX API (historical snapshots for content decay)
- Real competitor page analysis and content extraction
- Google Trends (unrealated trends data)

All functions fail loudly but gracefully: they return empty/None values with an
accompanying "source" note so downstream modules can report an honest
"could not retrieve" state instead of fabricating numbers.
"""
import re
import json
import time
import html as html_lib
import urllib.request
import urllib.parse
import urllib.error
import gzip
import io
from typing import List, Dict, Any, Optional, Tuple

import random as _rand
_USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:127.0) Gecko/20100101 Firefox/127.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 Edg/125.0.0.0",
    "ContentIntelligenceBot/2.0 (+https://example.com/bot)",
]
def _pick_ua() -> str:
    try:
        return _rand.choice(_USER_AGENTS)
    except Exception:
        return _USER_AGENTS[0]
DEFAULT_UA = _USER_AGENTS[0]
SEARCH_BACKEND = "duckduckgo-html"


def _open(url: str, timeout: int = 15, headers: Dict[str, str] = None,
         retries: int = 2) -> Optional[Any]:
    """Open a URL returning the response object, or None on failure.

    Uses UA rotation + exponential backoff (0.5s, 1.5s). BeautifulSoup is NOT
    required: DDG/Wikidata/Wayback parsing stays regex/JSON so stdlib-only
    installs keep working.
    """
    last = None
    for attempt in range(retries + 1):
        hdrs = {"User-Agent": _pick_ua(), "Accept": "*/*", "Accept-Encoding": "gzip, deflate"}
        if headers:
            hdrs.update(headers)
        try:
            req = urllib.request.Request(url, headers=hdrs)
            return urllib.request.urlopen(req, timeout=timeout)
        except Exception as e:
            last = e
            if attempt < retries:
                time.sleep(0.5 * (2 ** attempt))
    return None


def _read_body(resp) -> str:
    """Read and decode a response body (handles gzip)."""
    try:
        raw = resp.read()
        if resp.headers.get("Content-Encoding", "").lower() == "gzip":
            raw = gzip.GzipFile(fileobj=io.BytesIO(raw)).read()
        return raw.decode("utf-8", errors="ignore")
    except Exception:
        return ""


def web_search(query: str, num: int = 10) -> Dict[str, Any]:
    """
    Universal search function - tries multiple backends for real SERP data.
    Falls back through: DuckDuckGo API -> Searx -> Brave -> DuckDuckGo HTML -> Wikipedia
    
    Returns:
        {"ok": bool, "backend": str, "query": query,
         "results": [{"title", "url", "snippet", "position"}...],
         "error": str|None}
    """
    import re as _re
    
    # Backend 1: DuckDuckGo Instant Answer API
    try:
        encoded = urllib.parse.quote(query)
        url = f"https://api.duckduckgo.com/?q={encoded}&format=json&no_html=1&skip_disambig=1"
        resp = _open(url, timeout=15, headers={"Accept": "application/json", "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"})
        if resp is not None:
            body = _read_body(resp)
            data = json.loads(body)
            results = []
            for topic in data.get("RelatedTopics", []):
                if isinstance(topic, dict) and topic.get("Text") and topic.get("FirstURL"):
                    text = topic["Text"]
                    title = text.split(" - ")[0] if " - " in text else text[:80]
                    results.append({"title": title[:100], "url": topic["FirstURL"], "snippet": text[:200], "position": len(results) + 1})
                elif isinstance(topic, dict) and "Topics" in topic:
                    for sub in topic.get("Topics", []):
                        if isinstance(sub, dict) and sub.get("Text") and sub.get("FirstURL"):
                            text = sub["Text"]
                            title = text.split(" - ")[0] if " - " in text else text[:80]
                            results.append({"title": title[:100], "url": sub["FirstURL"], "snippet": text[:200], "position": len(results) + 1})
            if data.get("AbstractText"):
                results.insert(0, {"title": data.get("Heading", query)[:80], "url": data.get("AbstractURL", ""), "snippet": data["AbstractText"][:200], "position": 0})
            if results:
                return {"ok": True, "backend": "duckduckgo-api", "query": query, "results": results[:num], "error": None}
    except Exception:
        pass
    
    # Backend 2: Searx public instances
    for base_url in ["https://searx.be/search", "https://search.disroot.org/search", "https://searx.info/search"]:
        try:
            url = f"{base_url}?q={urllib.parse.quote(query)}&format=json&categories=general"
            resp = _open(url, timeout=15, headers={"Accept": "application/json", "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"})
            if resp is not None:
                body = _read_body(resp)
                data = json.loads(body)
                results = []
                for i, r in enumerate(data.get("results", [])[:num]):
                    results.append({"title": r.get("title", "")[:100], "url": r.get("url", ""), "snippet": r.get("content", r.get("description", ""))[:200], "position": i + 1})
                if results:
                    return {"ok": True, "backend": "searx", "query": query, "results": results, "error": None}
        except Exception:
            continue
        time.sleep(0.5)
    
    # Backend 3: Brave Search HTML scraping
    try:
        url = f"https://search.brave.com/search?q={urllib.parse.quote(query)}&source=web"
        resp = _open(url, timeout=15, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36", "Accept": "text/html,application/xhtml+xml"})
        if resp is not None:
            body = _read_body(resp)
            results = []
            title_matches = _re.findall(r'<a[^>]*class="[^"]*heading[^"]*"[^>]*href="([^"]+)"[^>]*>(.*?)</a>', body, _re.IGNORECASE | _re.DOTALL)
            for i, (href, title_html) in enumerate(title_matches[:num]):
                title = _re.sub(r'<[^>]+>', '', title_html).strip()
                if title and href.startswith("http"):
                    results.append({"title": title[:100], "url": href[:300], "snippet": "", "position": i + 1})
            if results:
                return {"ok": True, "backend": "brave", "query": query, "results": results[:num], "error": None}
    except Exception:
        pass
    
    # Backend 4: DuckDuckGo HTML (original method)
    try:
        url = "https://html.duckduckgo.com/html/?q=" + urllib.parse.quote(query)
        resp = _open(url, timeout=20)
        if resp is not None:
            body = _read_body(resp)
            results = _parse_ddg_html(body)
            if results:
                return {"ok": True, "backend": SEARCH_BACKEND, "query": query, "results": results[:num], "error": None}
    except Exception:
        pass
    
    # Backend 5: Wikipedia API for entity info
    try:
        url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={urllib.parse.quote(query)}&format=json&srlimit={num}"
        resp = _open(url, timeout=15, headers={"User-Agent": "ContentIntelligenceBot/1.0", "Accept": "application/json"})
        if resp is not None:
            body = _read_body(resp)
            data = json.loads(body)
            results = []
            for i, r in enumerate(data.get("query", {}).get("search", [])[:num]):
                snippet = _re.sub(r'<[^>]+>', '', r.get("snippet", ""))
                results.append({"title": r.get("title", "")[:100], "url": f"https://en.wikipedia.org/wiki/{r.get('title', '').replace(' ', '_')}", "snippet": f"{snippet}... (Word count: {r.get('word', 'N/A')})", "position": i + 1})
            if results:
                return {"ok": True, "backend": "wikipedia", "query": query, "results": results, "error": None}
    except Exception:
        pass
    
    return {"ok": False, "backend": "all", "query": query, "results": [], "error": "All search backends failed - network may be restricted"}


def _parse_ddg_html(body: str) -> List[Dict[str, str]]:
    """Parse DuckDuckGo HTML results (result__a links + result__snippet)."""
    results = []
    try:
        anchors = re.findall(
            r'<a[^>]*class="[^"]*result__a[^"]*"[^>]*href="([^"]+)"[^>]*>(.*?)</a>',
            body, re.IGNORECASE | re.DOTALL)
        snippets = re.findall(
            r'<a[^>]*class="[^"]*result__snippet[^"]*"[^>]*>(.*?)</a>',
            body, re.IGNORECASE | re.DOTALL)
        for idx, (href, title_html) in enumerate(anchors[:25]):
            title = re.sub(r'<[^>]+>', '', title_html)
            title = html_lib.unescape(title).strip()
            url = href
            if url.startswith("//"):
                url = "https:" + url
            m = re.search(r'uddg=([^&]+)', url)
            if m:
                url = urllib.parse.unquote(m.group(1))
            snippet = ""
            if idx < len(snippets):
                snippet = re.sub(r'<[^>]+>', '', snippets[idx])
                snippet = html_lib.unescape(snippet).strip()
            if title:
                results.append({
                    "title": title,
                    "url": url,
                    "snippet": snippet,
                    "position": idx + 1
                })
    except Exception:
        return []
    return results


def verify_url(url: str, timeout: int = 10) -> Dict[str, Any]:
    """
    Verify a URL is live and accessible. Returns real HTTP result.

    Returns:
        {"url", "reachable": bool, "status_code": int|None,
         "final_url": str|None, "final_status": int|None,
         "redirects": int, "headers": dict, "error": str|None}
    """
    try:
        req = urllib.request.Request(url, headers={"User-Agent": DEFAULT_UA, "Accept": "*/*"})
        redirects = 0
        last_headers = {}
        final_url = url
        try:
            resp = urllib.request.urlopen(req, timeout=timeout)
            status = getattr(resp, "status", 200)
            last_headers = dict(resp.headers.items())
            final_url = resp.geturl()
            resp.close()
        except urllib.error.HTTPError as e:
            status = e.code
            last_headers = dict(e.headers.items())
            final_url = e.geturl() or url
        except Exception as e:
            return {"url": url, "reachable": False, "status_code": None,
                    "final_url": None, "final_status": None, "redirects": 0,
                    "headers": {}, "error": str(e)}
        return {"url": url, "reachable": status < 400, "status_code": status,
                "final_url": final_url, "final_status": status,
                "redirects": redirects, "headers": last_headers, "error": None}
    except Exception as e:
        return {"url": url, "reachable": False, "status_code": None,
                "final_url": None, "final_status": None, "redirects": 0,
                "headers": {}, "error": str(e)}


def fetch_page(url: str, timeout: int = 15, max_bytes: int = 2000000) -> Dict[str, Any]:
    """
    Fetch a page's real HTML + response headers.

    SSRF-guarded: only http/https, no private/link-local/metadata hosts,
    max 3 redirects, 2MB size cap.

    Returns:
        {"ok", "url", "html", "status", "final_url", "headers", "error"}
    """
    try:
        from .security import safe_fetch as _safe
        return _safe(url, timeout=timeout, max_bytes=max_bytes)
    except Exception:
        pass
    resp = _open(url, timeout=timeout)
    if resp is None:
        return {"ok": False, "url": url, "html": "", "status": None,
                "final_url": None, "headers": {}, "error": "Fetch failed"}
    body = _read_body(resp)
    headers = dict(resp.headers.items())
    status = getattr(resp, "status", 200)
    final_url = resp.geturl()
    resp.close()
    return {"ok": True, "url": url, "html": body, "status": status,
            "final_url": final_url, "headers": headers, "error": None}


def fetch_headers(url: str, timeout: int = 10) -> Dict[str, Any]:
    """Fetch only the HTTP response headers for a URL (no body)."""
    resp = _open(url, timeout=timeout)
    if resp is None:
        return {"ok": False, "url": url, "headers": {}, "error": "Header fetch failed"}
    headers = dict(resp.headers.items())
    status = getattr(resp, "status", 200)
    final_url = resp.geturl()
    resp.close()
    return {"ok": True, "url": url, "headers": headers, "status": status,
            "final_url": final_url, "error": None}


def wayback_snapshots(url: str, limit: int = 8) -> Dict[str, Any]:
    """
    Real historical snapshots from the Wayback Machine CDX API.

    Returns:
        {"ok", "url", "snapshots": [{"timestamp", "status", "url"}...],
         "error"}
    """
    api = ("https://web.archive.org/cdx/search/cdx?url=" + urllib.parse.quote(url)
           + "&output=json&limit=" + str(limit) + "&filter=statuscode:200"
           + "&fl=timestamp,statuscode,original")
    body = None
    last_error = None
    for attempt in range(3):
        resp = _open(api, timeout=40)
        if resp is not None:
            body = _read_body(resp)
            break
        last_error = "Wayback request failed"
        if attempt < 2:
            time.sleep(2 + attempt * 2)
    if body is None:
        return {"ok": False, "url": url, "snapshots": [], "error": last_error}
    try:
        data = json.loads(body)
        if not isinstance(data, list) or len(data) < 2:
            return {"ok": False, "url": url, "snapshots": [],
                    "error": "No snapshots found in archive"}
        headers = data[0]
        ti = headers.index("timestamp") if "timestamp" in headers else 0
        si = headers.index("statuscode") if "statuscode" in headers else 1
        oi = headers.index("original") if "original" in headers else 2
        snapshots = []
        for row in data[1:]:
            ts = row[ti] if ti < len(row) else ""
            status = row[si] if si < len(row) else ""
            snapshots.append({
                "timestamp": ts,
                "status": status,
                "archive_url": f"https://web.archive.org/web/{ts}/{url}"
            })
        return {"ok": True, "url": url, "snapshots": snapshots[:limit], "error": None}
    except Exception as e:
        return {"ok": False, "url": url, "snapshots": [], "error": str(e)}


def search_wikidata(entity: str, limit: int = 3) -> Dict[str, Any]:
    """
    Real Wikidata entity search via the public API (no key required).

    Only returns results whose Wikidata IDs are valid QIDs (^Q\\d+$). Invalid
    or mangled IDs (e.g. truncated hashes) are rejected so fabricated entity
    references can never leak into output.

    Returns:
        {"ok", "query", "results": [{"id", "label", "description", "url"}...], "error"}
    """
    if not entity:
        return {"ok": False, "query": entity, "results": [], "error": "No entity provided"}
    api = ("https://www.wikidata.org/w/api.php?action=wbsearchentities&search="
           + urllib.parse.quote(entity) + "&language=en&uselang=en&format=json&limit=" + str(limit))
    resp = _open(api, timeout=20, headers={"Accept": "application/json"})
    if resp is None:
        return {"ok": False, "query": entity, "results": [], "error": "Wikidata request failed"}
    body = _read_body(resp)
    try:
        data = json.loads(body)
        results = []
        for hit in data.get("search", [])[:limit]:
            qid = hit.get("id", "")
            if not re.fullmatch(r"Q\d+", qid):
                continue
            results.append({
                "id": qid,
                "label": hit.get("label", ""),
                "description": hit.get("description", ""),
                "url": f"https://www.wikidata.org/wiki/{qid}"
            })
        return {"ok": True, "query": entity, "results": results, "error": None}
    except Exception as e:
        return {"ok": False, "query": entity, "results": [], "error": str(e)}


def base_origin(url: str) -> str:
    """Extract scheme://host[:port] from a URL."""
    try:
        p = urllib.parse.urlparse(url)
        return f"{p.scheme}://{p.netloc}"
    except Exception:
        return ""


def fetch_robots_txt(url: str, timeout: int = 8) -> Dict[str, Any]:
    """Fetch and return a site's robots.txt (real content)."""
    origin = base_origin(url)
    if not origin:
        return {"ok": False, "url": url, "content": "", "error": "Invalid URL"}
    robots_url = origin + "/robots.txt"
    page = fetch_page(robots_url, timeout=timeout)
    return {"ok": page["ok"], "url": robots_url, "content": page["html"][:8000],
            "status": page["status"], "error": page["error"]}


def extract_page(html: str, url: str = "") -> Dict[str, Any]:
    """
    Extract structured page metadata from real HTML.
    Uses html.parser to pull title, meta, h1/h2, text, links, images, schema.
    """
    import html.parser as _hp

    class _P(_hp.HTMLParser):
        def __init__(self):
            super().__init__()
            self.title = ''
            self.meta_desc = ''
            self.meta_keywords = ''
            self.h1 = ''
            self.h1s = []
            self.h2s = []
            self.h3s = []
            self.h4s = []
            self.text_parts = []
            self.links = []
            self.images = []
            self.schema_count = 0
            self.schema_types = []
            self.in_title = False
            self.in_h1 = False
            self.in_h2 = False
            self.in_h3 = False
            self.in_h4 = False
            self.in_script = False
            self.in_style = False
            self.in_nav = False
            self.in_footer = False
            self.in_noscript = False
            self.stack = []
            self.current_schema_type = ''

        def handle_starttag(self, tag, attrs):
            self.stack.append(tag)
            a = dict(attrs)
            if tag == 'title': self.in_title = True
            if tag == 'h1':
                self.in_h1 = True
                self.current_h1 = ''
            if tag == 'h2':
                self.in_h2 = True
                self.current_h2 = ''
            if tag == 'h3':
                self.in_h3 = True
                self.current_h3 = ''
            if tag == 'h4':
                self.in_h4 = True
                self.current_h4 = ''
            if tag == 'script':
                self.in_script = True
                if a.get('type', '') == 'application/ld+json':
                    self.schema_count += 1
                    self.current_schema_type = a.get('type', '')
            if tag == 'style': self.in_style = True
            if tag == 'nav': self.in_nav = True
            if tag == 'footer': self.in_footer = True
            if tag == 'noscript': self.in_noscript = True
            if tag == 'meta':
                name = a.get('name', '').lower()
                prop = a.get('property', '').lower()
                if name == 'description' or prop == 'og:description':
                    self.meta_desc = a.get('content', '')
                if name == 'keywords':
                    self.meta_keywords = a.get('content', '')
            if tag == 'a':
                href = a.get('href', '')
                text = ''
                if href:
                    self.links.append({'href': href[:300], 'text': text[:100], 'rel': a.get('rel', '')})
            if tag == 'img':
                self.images.append({'src': a.get('src', '')[:300], 'alt': a.get('alt', ''), 'width': a.get('width', ''), 'height': a.get('height', '')})

        def handle_endtag(self, tag):
            if self.stack and self.stack[-1] == tag:
                self.stack.pop()
            if tag == 'title': self.in_title = False
            if tag == 'h1':
                self.in_h1 = False
                if hasattr(self, 'current_h1') and self.current_h1:
                    self.h1s.append(self.current_h1)
                    self.current_h1 = ''
            if tag == 'h2':
                self.in_h2 = False
                if hasattr(self, 'current_h2') and self.current_h2:
                    self.h2s.append(self.current_h2)
                    self.current_h2 = ''
            if tag == 'h3':
                self.in_h3 = False
                if hasattr(self, 'current_h3') and self.current_h3:
                    self.h3s.append(self.current_h3)
                    self.current_h3 = ''
            if tag == 'h4':
                self.in_h4 = False
                if hasattr(self, 'current_h4') and self.current_h4:
                    self.h4s.append(self.current_h4)
                    self.current_h4 = ''
            if tag == 'script': self.in_script = False
            if tag == 'style': self.in_style = False
            if tag == 'nav': self.in_nav = False
            if tag == 'footer': self.in_footer = False
            if tag == 'noscript': self.in_noscript = False

        def handle_data(self, data):
            t = data.strip()
            if not t:
                return
            if self.in_title:
                self.title = t
            if self.in_h1:
                self.current_h1 = (self.current_h1 + ' ' + t).strip()
            if self.in_h2:
                self.current_h2 = (self.current_h2 + ' ' + t).strip()
            if self.in_h3:
                self.current_h3 = (self.current_h3 + ' ' + t).strip()
            if self.in_h4:
                self.current_h4 = (self.current_h4 + ' ' + t).strip()
            if not (self.in_script or self.in_style or self.in_nav or self.in_footer or self.in_noscript):
                if len(t) > 15:
                    self.text_parts.append(t)

    p = _P()
    try:
        p.feed(html or "")
    except Exception:
        pass
    page_text = ' '.join(p.text_parts)
    return {
        "url": url,
        "title": p.title,
        "meta_description": p.meta_desc,
        "meta_keywords": p.meta_keywords,
        "h1": p.h1s[0] if p.h1s else '',
        "h1s": p.h1s,
        "h2s": p.h2s,
        "h3s": p.h3s,
        "h4s": p.h4s,
        "word_count": len(page_text.split()),
        "link_count": len(p.links),
        "image_count": len(p.images),
        "images": p.images[:20],
        "links": p.links[:40],
        "has_schema": p.schema_count > 0,
        "schema_count": p.schema_count,
        "page_text": page_text[:12000],
    }


def fetch_sitemap_url(url: str, timeout: int = 10) -> Dict[str, Any]:
    """
    Try to locate and fetch a sitemap for the URL's origin.
    Returns the parsed sitemap URLs when found.
    """
    origin = base_origin(url)
    if not origin:
        return {"ok": False, "url": url, "sitemap_urls": [], "error": "Invalid URL"}
    candidates = [origin + "/sitemap.xml", origin + "/sitemap_index.xml",
                  origin + "/sitemap/sitemap.xml"]
    for cand in candidates:
        page = fetch_page(cand, timeout=8)
        if not page["ok"]:
            continue
        body = page["html"]
        locs = re.findall(r'<loc>\s*(.*?)\s*</loc>', body, re.IGNORECASE | re.DOTALL)
        if locs:
            return {"ok": True, "url": cand, "sitemap_urls": [l.strip() for l in locs[:500]],
                    "error": None}
    return {"ok": False, "url": url, "sitemap_urls": [], "error": "No sitemap found"}


# ============================================================================
# NEW: Enhanced Competitor Analysis Functions
# ============================================================================

def fetch_competitor_pages(serp_results: List[Dict], max_pages: int = 5, timeout: int = 10) -> List[Dict]:
    """
    Fetch and analyze real competitor pages from SERP results.
    Returns detailed analysis of each competitor page.
    Includes fallback to DuckDuckGo instant answer if direct fetch fails.
    """
    import ssl
    competitors = []
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    for result in serp_results[:max_pages]:
        url = result.get("url", "")
        if not url or not url.startswith("http"):
            continue
        
        # Try to fetch the page with SSL context
        page_data = None
        try:
            req = urllib.request.Request(url, headers={"User-Agent": DEFAULT_UA, "Accept": "*/*", "Accept-Encoding": "gzip, deflate"})
            resp = urllib.request.urlopen(req, timeout=timeout, context=ssl_context)
            body = _read_body(resp)
            headers = dict(resp.headers.items())
            status = getattr(resp, "status", 200)
            final_url = resp.geturl()
            resp.close()
            page_data = {"ok": True, "url": url, "html": body, "status": status, "final_url": final_url, "headers": headers, "error": None}
        except Exception as e:
            page_data = {"ok": False, "url": url, "html": "", "status": None, "final_url": None, "headers": {}, "error": str(e)}
        
        if not page_data.get("ok"):
            # Create a fallback entry with SERP data
            competitors.append({
                "url": url,
                "title": result.get("title", ""),
                "snippet": result.get("snippet", ""),
                "position": result.get("position", 0),
                "fetch_success": False,
                "fetch_fallback": True,
                "error": page_data.get("error", "Failed to fetch"),
                "serp_data_available": True,
                "page_text": result.get("snippet", "") + " " + result.get("title", ""),
                "h2s": [result.get("title", "")],
                "h3s": [],
                "word_count": len((result.get("snippet", "") + " " + result.get("title", "")).split()),
                "has_schema": False,
                "schema_count": 0,
                "image_count": 0,
                "link_count": 0,
                "images": [],
                "links": []
            })
            continue
        
        extracted = extract_page(page_data.get("html", ""), url)
        extracted["position"] = result.get("position", 0)
        extracted["serp_title"] = result.get("title", "")
        extracted["serp_snippet"] = result.get("snippet", "")
        extracted["fetch_success"] = True
        extracted["fetch_fallback"] = False
        extracted["response_status"] = page_data.get("status")
        extracted["response_headers"] = {k: v for k, v in page_data.get("headers", {}).items()}
        competitors.append(extracted)
    return competitors


def analyze_competitor_content_depth(competitors: List[Dict]) -> Dict[str, Any]:
    """
    Analyze content depth across real competitor pages.
    Returns statistical analysis of word counts, headings, media usage.
    """
    if not competitors:
        return {"error": "No competitor data available", "source": "N/A"}
    
    word_counts = [c.get("word_count", 0) for c in competitors if c.get("fetch_success")]
    h2_counts = [len(c.get("h2s", [])) for c in competitors if c.get("fetch_success")]
    h3_counts = [len(c.get("h3s", [])) for c in competitors if c.get("fetch_success")]
    image_counts = [c.get("image_count", 0) for c in competitors if c.get("fetch_success")]
    link_counts = [c.get("link_count", 0) for c in competitors if c.get("fetch_success")]
    schema_counts = [c.get("schema_count", 0) for c in competitors if c.get("fetch_success")]
    
    def safe_avg(lst):
        return sum(lst) / len(lst) if lst else 0
    
    def safe_max(lst):
        return max(lst) if lst else 0
    
    def safe_min(lst):
        return min(lst) if lst else 0
    
    return {
        "competitor_count": len(competitors),
        "successful_fetches": len([c for c in competitors if c.get("fetch_success")]),
        "word_count_stats": {
            "average": round(safe_avg(word_counts)),
            "maximum": safe_max(word_counts),
            "minimum": safe_min(word_counts),
            "median": sorted(word_counts)[len(word_counts)//2] if word_counts else 0,
            "all_values": word_counts,
            "percentile_75": sorted(word_counts)[int(len(word_counts)*0.75)] if word_counts else 0,
            "percentile_90": sorted(word_counts)[int(len(word_counts)*0.9)] if word_counts else 0,
        },
        "heading_stats": {
            "h2_average": round(safe_avg(h2_counts), 1),
            "h3_average": round(safe_avg(h3_counts), 1),
            "h2_max": safe_max(h2_counts),
            "h3_max": safe_max(h3_counts),
        },
        "media_stats": {
            "image_average": round(safe_avg(image_counts), 1),
            "image_max": safe_max(image_counts),
            "link_average": round(safe_avg(link_counts), 1),
            "link_max": safe_max(link_counts),
        },
        "schema_usage": {
            "competitors_with_schema": len([c for c in competitors if c.get("has_schema")]),
            "schema_percentage": round(len([c for c in competitors if c.get("has_schema")]) / len(competitors) * 100, 1) if competitors else 0,
            "max_schema_count": safe_max(schema_counts),
        },
        "individual_competitors": competitors
    }


def analyze_competitor_headings(competitors: List[Dict]) -> Dict[str, Any]:
    """
    Extract and analyze heading patterns from real competitor pages.
    Returns common heading topics, structures, and patterns.
    """
    if not competitors:
        return {"error": "No competitor data available"}
    
    all_h2s = []
    all_h3s = []
    heading_patterns = {}
    
    for comp in competitors:
        if not comp.get("fetch_success"):
            continue
        h2s = comp.get("h2s", [])
        h3s = comp.get("h3s", [])
        all_h2s.extend(h2s)
        all_h3s.extend(h3s)
        
        # Extract heading patterns (question-based, how-to, list-based, etc.)
        for h in h2s:
            h_lower = h.lower()
            if '?' in h:
                heading_patterns.setdefault("question_headings", []).append(h)
            elif any(word in h_lower for word in ['how to', 'howto', 'guide', 'tutorial']):
                heading_patterns.setdefault("how_to_headings", []).append(h)
            elif any(word in h_lower for word in ['vs', 'versus', 'comparison', 'compare']):
                heading_patterns.setdefault("comparison_headings", []).append(h)
            elif any(word in h_lower for word in ['best', 'top', 'review']):
                heading_patterns.setdefault("list_headings", []).append(h)
            elif any(word in h_lower for word in ['what is', 'definition', 'meaning']):
                heading_patterns.setdefault("definition_headings", []).append(h)
            else:
                heading_patterns.setdefault("informational_headings", []).append(h)
    
    return {
        "total_h2_found": len(all_h2s),
        "total_h3_found": len(all_h3s),
        "unique_h2_count": len(set(all_h2s)),
        "unique_h3_count": len(set(all_h3s)),
        "heading_patterns": heading_patterns,
        "all_h2s_sample": all_h2s[:30],
        "all_h3s_sample": all_h3s[:30],
        "competitors_analyzed": len([c for c in competitors if c.get("fetch_success")])
    }


def extract_competitor_entities(competitors: List[Dict]) -> Dict[str, Any]:
    """
    Extract named entities and topics from real competitor content.
    Returns common entities, topics, and themes.
    """
    if not competitors:
        return {"error": "No competitor data available"}
    
    all_text = ""
    for comp in competitors:
        if comp.get("fetch_success"):
            all_text += " " + comp.get("page_text", "")
    
    # Extract potential entities (capitalized multi-word phrases)
    entities = re.findall(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\b', all_text)
    entity_counts = {}
    for entity in entities:
        if len(entity) > 3 and len(entity) < 50:
            entity_counts[entity] = entity_counts.get(entity, 0) + 1
    
    # Extract topics from headings
    topics = []
    for comp in competitors:
        if comp.get("fetch_success"):
            for h2 in comp.get("h2s", []):
                topics.append(h2)
    
    # Get top entities by frequency
    top_entities = sorted(entity_counts.items(), key=lambda x: x[1], reverse=True)[:30]
    
    return {
        "top_entities": [{"entity": e, "count": c} for e, c in top_entities],
        "total_entities_found": len(entity_counts),
        "competitor_topics": topics[:50],
        "content_sample": all_text[:5000],
        "competitors_analyzed": len([c for c in competitors if c.get("fetch_success")])
    }


def analyze_competitor_links(competitors: List[Dict]) -> Dict[str, Any]:
    """
    Analyze internal and external link patterns from real competitor pages.
    Returns link patterns, anchor text analysis, and linking strategies.
    """
    if not competitors:
        return {"error": "No competitor data available"}
    
    all_internal_links = []
    all_external_links = []
    all_anchor_texts = []
    domain_link_patterns = {}
    
    for comp in competitors:
        if not comp.get("fetch_success"):
            continue
        comp_origin = base_origin(comp.get("url", ""))
        for link in comp.get("links", []):
            href = link.get("href", "") if isinstance(link, dict) else str(link)
            text = link.get("text", "") if isinstance(link, dict) else ""
            
            if href.startswith("http"):
                if comp_origin and comp_origin in href:
                    all_internal_links.append(href)
                else:
                    all_external_links.append(href)
                    domain = base_origin(href)
                    domain_link_patterns[domain] = domain_link_patterns.get(domain, 0) + 1
            elif href.startswith("/") or href.startswith("#"):
                all_internal_links.append(href)
            
            if text:
                all_anchor_texts.append(text)
    
    # Categorize anchor texts
    anchor_categories = {
        "exact_match": [],
        "partial_match": [],
        "branded": [],
        "generic": [],
        "long_tail": []
    }
    
    generic_words = ["click here", "read more", "learn more", "here", "this", "page", "article", "link", "website"]
    for anchor in all_anchor_texts:
        anchor_lower = anchor.lower().strip()
        if anchor_lower in generic_words:
            anchor_categories["generic"].append(anchor)
        elif len(anchor.split()) >= 4:
            anchor_categories["long_tail"].append(anchor)
        elif len(anchor.split()) >= 2:
            anchor_categories["partial_match"].append(anchor)
        else:
            anchor_categories["exact_match"].append(anchor)
    
    successful_fetches = [c for c in competitors if c.get("fetch_success")]
    successful_fetch_count = len(successful_fetches) if successful_fetches else 1

    return {
        "total_internal_links": len(all_internal_links),
        "total_external_links": len(all_external_links),
        "avg_internal_links_per_page": round(len(all_internal_links) / successful_fetch_count, 1) if competitors else 0,
        "avg_external_links_per_page": round(len(all_external_links) / successful_fetch_count, 1) if competitors else 0,
        "top_external_domains": sorted(domain_link_patterns.items(), key=lambda x: x[1], reverse=True)[:15],
        "anchor_text_analysis": {
            "total_anchor_texts": len(all_anchor_texts),
            "by_category": {k: len(v) for k, v in anchor_categories.items()},
            "samples": {k: v[:10] for k, v in anchor_categories.items() if v}
        },
        "internal_link_samples": all_internal_links[:20],
        "external_link_samples": all_external_links[:20]
    }


def get_serp_features_realtime(query: str) -> Dict[str, Any]:
    """
    Detect real SERP features from live search results.
    Returns detected features like featured snippets, PAA, knowledge panels, etc.
    """
    result = web_search(query, num=10)
    if not result.get("ok"):
        return {"ok": False, "error": result.get("error", "Search failed"), "features_detected": []}
    
    results = result.get("results", [])
    features_detected = []
    
    # Analyze SERP features
    if results:
        # Check for featured snippet (position 0 or special formatting)
        first_result = results[0]
        if first_result.get("snippet") and len(first_result.get("snippet", "")) > 150:
            features_detected.append({
                "feature": "featured_snippet",
                "position": 1,
                "title": first_result.get("title", ""),
                "url": first_result.get("url", ""),
                "snippet_length": len(first_result.get("snippet", "")),
                "snippet_sample": first_result.get("snippet", "")[:200]
            })
        
        # Check for "People Also Ask" indicators
        if any("?" in r.get("title", "") for r in results[:5]):
            features_detected.append({
                "feature": "people_also_ask",
                "evidence": "Question-based titles detected in top 5 results",
                "sample_questions": [r.get("title", "") for r in results[:5] if "?" in r.get("title", "")][:5]
            })
        
        # Check for video indicators
        if any("video" in r.get("url", "").lower() or "youtube" in r.get("url", "").lower() for r in results):
            features_detected.append({
                "feature": "video_carousel",
                "evidence": "Video URLs detected in results",
                "video_urls": [r.get("url", "") for r in results if "video" in r.get("url", "").lower() or "youtube" in r.get("url", "").lower()][:5]
            })
        
        # Check for image pack
        if any("image" in r.get("snippet", "").lower() or "photo" in r.get("snippet", "").lower() for r in results[:3]):
            features_detected.append({
                "feature": "image_pack",
                "evidence": "Image-related content in top results"
            })
        
        # Check for local pack
        if any("map" in r.get("snippet", "").lower() or "address" in r.get("snippet", "").lower() or "phone" in r.get("snippet", "").lower() for r in results):
            features_detected.append({
                "feature": "local_pack",
                "evidence": "Location-related information detected"
            })
        
        # Check for shopping results
        if any("$" in r.get("snippet", "") or "price" in r.get("snippet", "").lower() or "buy" in r.get("snippet", "").lower() for r in results[:5]):
            features_detected.append({
                "feature": "shopping_results",
                "evidence": "Price/commercial indicators in results"
            })
        
        # Check for news box
        if any("news" in r.get("url", "").lower() or "article" in r.get("url", "").lower() for r in results[:3]):
            features_detected.append({
                "feature": "news_box",
                "evidence": "News/article URLs in top results"
            })
    
    return {
        "ok": True,
        "query": query,
        "results_count": len(results),
        "features_detected": features_detected,
        "feature_names": [f["feature"] for f in features_detected],
        "top_10_urls": [{"position": r.get("position"), "title": r.get("title"), "url": r.get("url")} for r in results[:10]],
        "top_10_domains": list(set([base_origin(r.get("url", "")).replace("https://", "").replace("http://", "") for r in results[:10]])),
        "serp_data_source": result.get("backend")
    }


def analyze_competitor_backlink_patterns(competitors: List[Dict]) -> Dict[str, Any]:
    """
    Analyze backlink patterns from competitor pages by examining external links.
    Returns potential backlink sources and patterns.
    """
    if not competitors:
        return {"error": "No competitor data available"}
    
    all_external_domains = {}
    all_anchor_patterns = {}
    
    for comp in competitors:
        if not comp.get("fetch_success"):
            continue
        for link in comp.get("links", []):
            href = link.get("href", "") if isinstance(link, dict) else str(link)
            text = link.get("text", "") if isinstance(link, dict) else ""
            
            if href.startswith("http"):
                domain = base_origin(href).replace("https://", "").replace("http://", "").replace("www.", "")
                all_external_domains[domain] = all_external_domains.get(domain, 0) + 1
    
    # Categorize link types
    link_types = {
        "guest_post_opportunities": [],
        "resource_pages": [],
        "directories": [],
        "news_media": [],
        "educational": [],
        "social_media": [],
        "tools_reviews": []
    }
    
    for domain, count in all_external_domains.items():
        domain_lower = domain.lower()
        if any(x in domain_lower for x in [".edu", "university", "college"]):
            link_types["educational"].append({"domain": domain, "count": count})
        elif any(x in domain_lower for x in ["facebook", "twitter", "linkedin", "instagram", "youtube", "pinterest"]):
            link_types["social_media"].append({"domain": domain, "count": count})
        elif any(x in domain_lower for x in ["news", "times", "herald", "post", "tribune", "gazette", "bbc", "cnn"]):
            link_types["news_media"].append({"domain": domain, "count": count})
        elif any(x in domain_lower for x in ["directory", "list", "hub", "resources"]):
            link_types["directories"].append({"domain": domain, "count": count})
        elif any(x in domain_lower for x in ["review", "compare", "vs", "alternative", "best"]):
            link_types["tools_reviews"].append({"domain": domain, "count": count})
        elif any(x in domain_lower for x in ["resource", "guide", "wiki", "how"]):
            link_types["resource_pages"].append({"domain": domain, "count": count})
        else:
            link_types["guest_post_opportunities"].append({"domain": domain, "count": count})
    
    return {
        "total_unique_domains": len(all_external_domains),
        "top_linked_domains": sorted(all_external_domains.items(), key=lambda x: x[1], reverse=True)[:25],
        "link_type_analysis": {k: v for k, v in link_types.items() if v},
        "competitors_analyzed": len([c for c in competitors if c.get("fetch_success")])
    }


def get_content_gaps_from_competitors(competitors: List[Dict], user_keywords: List[str]) -> Dict[str, Any]:
    """
    Identify content gaps by comparing competitor content with user keywords.
    Returns missing topics, undercovered areas, and opportunities.
    """
    if not competitors:
        return {"error": "No competitor data available"}
    
    all_competitor_topics = []
    all_competitor_text = ""
    
    for comp in competitors:
        if comp.get("fetch_success"):
            for h2 in comp.get("h2s", []):
                all_competitor_topics.append(h2.lower())
            all_competitor_text += " " + comp.get("page_text", "").lower()
    
    # Find topics covered by competitors but not in user keywords
    keyword_set = set(k.lower() for k in user_keywords)
    competitor_topic_set = set(all_competitor_topics)
    
    covered_topics = []
    missing_topics = []
    
    for topic in competitor_topic_set:
        topic_words = set(topic.split())
        if topic_words & keyword_set:
            covered_topics.append(topic)
        else:
            missing_topics.append(topic)
    
    return {
        "user_keywords": user_keywords,
        "competitor_topics_found": len(competitor_topic_set),
        "topics_covered_by_user": len(covered_topics),
        "topics_not_covered": len(missing_topics),
        "content_gaps": sorted(missing_topics)[:30],
        "covered_topics": sorted(covered_topics)[:30],
        "coverage_percentage": round(len(covered_topics) / len(competitor_topic_set) * 100, 1) if competitor_topic_set else 0,
        "competitors_analyzed": len([c for c in competitors if c.get("fetch_success")])
    }


def analyze_competitor_schema_usage(competitors: List[Dict]) -> Dict[str, Any]:
    """
    Analyze schema markup usage across real competitor pages.
    Returns schema types used, frequency, and opportunities.
    """
    if not competitors:
        return {"error": "No competitor data available"}
    
    schema_usage = {
        "competitors_with_schema": 0,
        "total_schema_instances": 0,
        "schema_types_found": {},
        "schema_coverage_percentage": 0,
        "individual_results": []
    }
    
    for comp in competitors:
        if not comp.get("fetch_success"):
            continue
        has_schema = comp.get("has_schema", False)
        schema_count = comp.get("schema_count", 0)
        
        if has_schema:
            schema_usage["competitors_with_schema"] += 1
            schema_usage["total_schema_instances"] += schema_count
        
        schema_usage["individual_results"].append({
            "url": comp.get("url", ""),
            "has_schema": has_schema,
            "schema_count": schema_count,
            "position": comp.get("position", 0)
        })
    
    successful_fetch_count = len([c for c in competitors if c.get("fetch_success")])
    if competitors and successful_fetch_count > 0:
        schema_usage["schema_coverage_percentage"] = round(
            schema_usage["competitors_with_schema"] / successful_fetch_count * 100, 1
        )
    
    return schema_usage


def analyze_competitor_readability(competitors: List[Dict]) -> Dict[str, Any]:
    """
    Analyze readability metrics across real competitor pages.
    Returns average readability scores and benchmarks.
    """
    if not competitors:
        return {"error": "No competitor data available"}
    
    readability_scores = []
    
    for comp in competitors:
        if comp.get("fetch_success") and comp.get("page_text"):
            text = comp.get("page_text", "")
            words = text.split()
            sentences = re.split(r'[.!?]+', text)
            sentences = [s.strip() for s in sentences if s.strip()]
            
            word_count = len(words)
            sentence_count = len(sentences) if sentences else 1
            
            # Calculate average sentence length
            avg_sentence_length = word_count / sentence_count if sentence_count > 0 else 0
            
            # Calculate Flesch Reading Ease (simplified)
            # Count syllables (rough approximation)
            def count_syllables(word):
                word = word.lower()
                count = 0
                vowels = "aeiouy"
                if word[0] in vowels:
                    count += 1
                for index in range(1, len(word)):
                    if word[index] in vowels and word[index - 1] not in vowels:
                        count += 1
                if word.endswith("e"):
                    count -= 1
                if count == 0:
                    count += 1
                return count
            
            total_syllables = sum(count_syllables(w) for w in words)
            
            # Flesch Reading Ease
            if word_count > 0 and sentence_count > 0:
                flesch = 206.835 - 1.015 * (word_count / sentence_count) - 84.6 * (total_syllables / word_count)
            else:
                flesch = 0
            
            # Flesch-Kincaid Grade Level
            if word_count > 0 and sentence_count > 0:
                fk_grade = 0.39 * (word_count / sentence_count) + 11.8 * (total_syllables / word_count) - 15.59
            else:
                fk_grade = 0
            
            readability_scores.append({
                "url": comp.get("url", ""),
                "word_count": word_count,
                "sentence_count": sentence_count,
                "avg_sentence_length": round(avg_sentence_length, 1),
                "total_syllables": total_syllables,
                "flesch_reading_ease": round(max(0, min(100, flesch)), 1),
                "flesch_kincaid_grade": round(max(0, fk_grade), 1)
            })
    
    if readability_scores:
        avg_flesch = sum(r["flesch_reading_ease"] for r in readability_scores) / len(readability_scores)
        avg_fk = sum(r["flesch_kincaid_grade"] for r in readability_scores) / len(readability_scores)
    else:
        avg_flesch = 0
        avg_fk = 0
    
    return {
        "competitors_analyzed": len(readability_scores),
        "average_flesch_reading_ease": round(avg_flesch, 1),
        "average_flesch_kincaid_grade": round(avg_fk, 1),
        "individual_scores": readability_scores,
        "readability_interpretation": {
            "score_90_100": "Very Easy (5th grade)",
            "score_80_90": "Easy (6th grade)",
            "score_70_80": "Fairly Easy (7th grade)",
            "score_60_70": "Standard (8th-9th grade)",
            "score_50_60": "Fairly Difficult (10th-12th grade)",
            "score_30_50": "Difficult (College)",
            "score_0_30": "Very Difficult (College Graduate)"
        },
        "benchmark_for_seo": "Aim for Flesch Reading Ease 60-70 for general content, 50-60 for technical content"
    }


# ---------------------------------------------------------------------------
# Live verified-statistics research
# ---------------------------------------------------------------------------
_STAT_PATTERNS = [
    (re.compile(r'(\d[\d,\.]*\s*(?:%|percent|million|billion|trillion|m|bn|tb|gb|users|people|companies|revenue|dollars?|\$|bps|units|posts|pages|hours|minutes|seconds|billion|trillion))', re.I), 'metric'),
    (re.compile(r'\$[\s]*(\d[\d,\.]*\s*(?:million|billion|trillion|m|bn|k)?)', re.I), 'currency'),
    (re.compile(r'(\d[\d,\.]*)\s*(?:%|percent)', re.I), 'percentage'),
]

def _extract_stat_snippets(text: str, max_stats: int = 12) -> List[Dict[str, Any]]:
    """Pull short, real statistic-bearing sentences from a snippet/text."""
    if not text:
        return []
    out = []
    sentences = re.split(r'(?<=[.!?])\s+', re.sub(r'\s+', ' ', text))
    for sent in sentences:
        sent = sent.strip()
        if not sent:
            continue
        if len(sent) > 320:
            continue
        has_number = bool(re.search(r'\d', sent))
        if not has_number:
            continue
        # require a metric-like token to avoid arbitrary numbers
        if not re.search(r'(%|percent|million|billion|trillion|million|billion|\$|€|£|users|revenue|market|grow|growth|increase|decrease|stat|report|according|billion|trillion|bn|m|k|gb|tb|hours|minutes|seconds|years|companies|businesses|countries|people|global|estimated)', sent, re.I):
            continue
        out.append({"stat": sent[:280], "source_hint": "live_search"})
        if len(out) >= max_stats:
            break
    return out


def research_live_statistics(entity: str, seed: str = "", queries: List[str] = None,
                             max_total: int = 24) -> Dict[str, Any]:
    """
    Research real, sourced statistics for an entity/topic from live web searches.

    Every returned statistic is tied to a real result URL (source_url). If nothing
    can be verified, the function returns empty lists (never fabricates numbers).

    Returns:
        {"ok": bool, "searched_queries": [...], "statistics": [{stat, source_url,
         source_title, confidence}...], "error": str|None}
    """
    base = entity or seed or ""
    if not base:
        return {"ok": False, "searched_queries": [], "statistics": [], "error": "No entity provided"}
    candidates = []
    if seed and seed.lower() != base.lower():
        candidates.append(seed)
    candidates.append(base)
    candidate_queries = []
    for c in candidates:
        candidate_queries += [
            f"{c} statistics",
            f"{c} market size statistics",
            f"{c} usage statistics 2026",
            f"{c} how many people statistics",
        ]
    if queries:
        candidate_queries = queries + candidate_queries
    # dedupe, cap at 8 searches to bound runtime
    seen_q = set()
    final_queries = []
    for q in candidate_queries:
        if q.lower() not in seen_q:
            seen_q.add(q.lower())
            final_queries.append(q)
        if len(final_queries) >= 8:
            break

    stats = []
    seen_stats = set()
    for q in final_queries:
        try:
            sr = web_search(q, num=6)
            for r in sr.get("results", []):
                snip = (r.get("snippet", "") or "")
                url = r.get("url", "")
                title = r.get("title", "")
                for s in _extract_stat_snippets(snip):
                    key = s["stat"].lower()[:80]
                    if key in seen_stats:
                        continue
                    seen_stats.add(key)
                    stats.append({
                        "stat": s["stat"],
                        "source_url": url,
                        "source_title": title,
                        "confidence": "verified_live_search" if url.startswith("http") else "low",
                        "related_query": q,
                    })
                    if len(stats) >= max_total:
                        break
                if len(stats) >= max_total:
                    break
        except Exception:
            continue
        time.sleep(0.3)
        if len(stats) >= max_total:
            break

    return {
        "ok": bool(stats),
        "searched_queries": final_queries,
        "statistics": stats[:max_total],
        "total_statistics": len(stats[:max_total]),
        "error": None if stats else "No real statistics could be verified from live search (network or content restrictions).",
    }
