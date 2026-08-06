"""
Real web data utilities (no API keys required).

Sources:
- DuckDuckGo HTML search (SERP data)
- Live HTTP fetches (page HTML, response headers, link/robots/sitemap checks)
- Wayback Machine CDX API (historical snapshots for content decay)

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

DEFAULT_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
SEARCH_BACKEND = "duckduckgo-html"


def _open(url: str, timeout: int = 15, headers: Dict[str, str] = None) -> Optional[Any]:
    """Open a URL returning the response object, or None on failure."""
    hdrs = {"User-Agent": DEFAULT_UA, "Accept": "*/*", "Accept-Encoding": "gzip, deflate"}
    if headers:
        hdrs.update(headers)
    try:
        req = urllib.request.Request(url, headers=hdrs)
        return urllib.request.urlopen(req, timeout=timeout)
    except Exception:
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


def web_search(query: str, num: int = 8) -> Dict[str, Any]:
    """
    Real SERP retrieval via DuckDuckGo HTML endpoint.

    Returns:
        {"ok": bool, "backend": "duckduckgo-html", "query": query,
         "results": [{"title", "url", "snippet", "position"}...],
         "error": str|None}
    """
    url = "https://html.duckduckgo.com/html/?q=" + urllib.parse.quote(query)
    resp = _open(url, timeout=20)
    if resp is None:
        return {"ok": False, "backend": SEARCH_BACKEND, "query": query,
                "results": [], "error": "Search request failed (network/blocked)"}
    body = _read_body(resp)
    results = _parse_ddg_html(body)
    if not results:
        return {"ok": False, "backend": SEARCH_BACKEND, "query": query,
                "results": [], "error": "No results parsed from search response"}
    return {"ok": True, "backend": SEARCH_BACKEND, "query": query,
            "results": results[:num], "error": None}


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
            # DDG wraps real URLs in a redirect (uddg=)
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


def fetch_page(url: str, timeout: int = 15) -> Dict[str, Any]:
    """
    Fetch a page's real HTML + response headers.

    Returns:
        {"ok", "url", "html", "status", "final_url", "headers", "error"}
    """
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
            results.append({
                "id": hit.get("id", ""),
                "label": hit.get("label", ""),
                "description": hit.get("description", ""),
                "url": f"https://www.wikidata.org/wiki/{hit.get('id', '')}"
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
            self.h1 = ''
            self.h2s = []
            self.text_parts = []
            self.links = []
            self.images = []
            self.schema_count = 0
            self.in_title = False
            self.in_h1 = False
            self.in_h2 = False
            self.in_script = False
            self.in_style = False
            self.in_nav = False
            self.in_footer = False
            self.stack = []

        def handle_starttag(self, tag, attrs):
            self.stack.append(tag)
            a = dict(attrs)
            if tag == 'title': self.in_title = True
            if tag == 'h1': self.in_h1 = True
            if tag == 'h2': self.in_h2 = True
            if tag == 'script':
                self.in_script = True
                if a.get('type', '') == 'application/ld+json':
                    self.schema_count += 1
            if tag == 'style': self.in_style = True
            if tag == 'nav': self.in_nav = True
            if tag == 'footer': self.in_footer = True
            if tag == 'meta':
                name = a.get('name', '').lower()
                prop = a.get('property', '').lower()
                if name == 'description' or prop == 'og:description':
                    self.meta_desc = a.get('content', '')
            if tag == 'a':
                href = a.get('href', '')
                if href:
                    self.links.append(href[:300])
            if tag == 'img':
                self.images.append({'src': a.get('src', '')[:300], 'alt': a.get('alt', '')})

        def handle_endtag(self, tag):
            if self.stack and self.stack[-1] == tag:
                self.stack.pop()
            if tag == 'title': self.in_title = False
            if tag == 'h1': self.in_h1 = False
            if tag == 'h2': self.in_h2 = False
            if tag == 'script': self.in_script = False
            if tag == 'style': self.in_style = False
            if tag == 'nav': self.in_nav = False
            if tag == 'footer': self.in_footer = False

        def handle_data(self, data):
            t = data.strip()
            if not t:
                return
            if self.in_title:
                self.title = t
            if self.in_h1:
                self.h1 = t
            if self.in_h2:
                self.h2s.append(t)
            if not (self.in_script or self.in_style or self.in_nav or self.in_footer):
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
        "h1": p.h1,
        "h2s": p.h2s,
        "word_count": len(page_text.split()),
        "link_count": len(p.links),
        "image_count": len(p.images),
        "images": p.images[:20],
        "links": p.links[:40],
        "has_schema": p.schema_count > 0,
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
