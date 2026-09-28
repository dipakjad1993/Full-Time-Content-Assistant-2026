"""
Enterprise security utilities: SSRF guard, rate limiting, validation, safe fetch.
Stdlib only. Thread-safe.
"""
import ipaddress
import re
import socket
import threading
import time
import urllib.parse
import urllib.request
from typing import Dict, Tuple

_BLOCKED_HOSTNAMES = {
    "localhost", "metadata.google.internal",
}
_PRIVATE_NETS = [
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("169.254.0.0/16"),
    ipaddress.ip_network("0.0.0.0/8"),
    ipaddress.ip_network("::1/128"),
    ipaddress.ip_network("fe80::/10"),
    ipaddress.ip_network("fc00::/7"),
]
_HOST_DENY_RE = re.compile(
    r"(localhost|\.local$|\.internal$|\.lan$|169\.254\.|metadata\.google)",
    re.IGNORECASE,
)


def _ip_blocked(ip: "ipaddress._BaseAddress") -> bool:
    """True if IP is private/link-local/loopback incl. IPv4-mapped IPv6 + 6to4/Teredo."""
    try:
        for net in _PRIVATE_NETS:
            try:
                if ip in net:
                    return True
            except TypeError:
                continue  # v4 vs v6 mismatch
        # IPv4-mapped IPv6 (::ffff:127.0.0.1) — unwrap and re-check v4 nets
        mapped = getattr(ip, "ipv4_mapped", None)
        if mapped is not None:
            for net in _PRIVATE_NETS:
                try:
                    if mapped in net:
                        return True
                except TypeError:
                    continue
        # 6to4 (2002:V4V4::/48 embeds a v4) + Teredo (2001::/32): unwrap embedded v4
        try:
            if ip.version == 6:
                packed = ip.packed
                embedded = None
                if packed[:2] == b"\x20\x02":  # 6to4
                    embedded = ipaddress.ip_address(int.from_bytes(packed[2:6], "big"))
                elif packed[:4] == b"\x20\x01\x00\x00":  # Teredo: obfuscated client v4 at tail
                    obf = int.from_bytes(packed[-4:], "big") ^ 0xFFFFFFFF
                    embedded = ipaddress.ip_address(obf)
                if embedded is not None:
                    for net in _PRIVATE_NETS:
                        try:
                            if embedded in net:
                                return True
                        except TypeError:
                            continue
        except Exception:
            pass
        # stdlib truth as backstop (catches unusual ranges)
        try:
            if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved:
                # is_private covers RFC1918; keep explicit nets authoritative above
                return True
        except Exception:
            pass
    except Exception:
        return True  # fail closed on parse anomalies
    return False

MAX_FETCH_BYTES = 2_000_000
MAX_REDIRECTS = 3


def is_url_allowed(url: str) -> Tuple[bool, str]:
    """Validate a user-supplied URL against SSRF rules. Returns (allowed, reason)."""
    if not url or not isinstance(url, str):
        return False, "empty URL"
    url = url.strip()
    if len(url) > 2048:
        return False, "URL too long (max 2048 chars)"
    try:
        p = urllib.parse.urlparse(url)
    except Exception:
        return False, "unparseable URL"
    if p.scheme not in ("http", "https"):
        return False, "only http/https allowed"
    if not p.hostname:
        return False, "missing hostname"
    if "@" in (p.netloc or "") and p.hostname not in (p.netloc or ""):
        # userinfo smuggling attempt (user@host)
        if "@" in url.split("://", 1)[-1].split("/", 1)[0]:
            # allow legit userinfo? No — deny for SSRF safety
            return False, "userinfo in URL not allowed"
    host = p.hostname.lower().rstrip(".")
    if host in _BLOCKED_HOSTNAMES or _HOST_DENY_RE.search(host):
        return False, f"blocked host: {host}"
    # Fast literal-IP check (no DNS)
    try:
        ip = ipaddress.ip_address(host)
        if _ip_blocked(ip):
            return False, f"private/link-local IP blocked: {host}"
        return True, "ok"
    except ValueError:
        pass  # hostname, resolve below
    # DNS resolve + check each A record (short timeout guarded by caller)
    try:
        old_timeout = socket.getdefaulttimeout()
        socket.setdefaulttimeout(4)
        try:
            infos = socket.getaddrinfo(host, None)
        finally:
            socket.setdefaulttimeout(old_timeout)
        for fam, _, _, _, sockaddr in infos:
            ip_str = sockaddr[0]
            try:
                ip = ipaddress.ip_address(ip_str)
            except ValueError:
                continue
            if _ip_blocked(ip):
                return False, f"host resolves to private IP: {ip_str}"
        return True, "ok"
    except Exception as e:
        return False, f"DNS resolution failed: {e}"


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def safe_fetch(url: str, timeout: int = 15, max_bytes: int = MAX_FETCH_BYTES,
               extra_headers: Dict = None) -> Dict:
    """SSRF-guarded fetch with redirect cap + size cap. Returns dict like fetch_page."""
    allowed, reason = is_url_allowed(url)
    if not allowed:
        return {"ok": False, "url": url, "html": "", "status": None,
                "final_url": None, "headers": {}, "error": f"SSRF blocked: {reason}"}
    hdrs = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) ContentIntelligence/2.0",
            "Accept": "text/html,application/xhtml+xml,*/*"}
    if extra_headers:
        hdrs.update(extra_headers)
    # Manual redirect loop so we can re-validate each hop
    current = url
    headers_out: Dict = {}
    status = None
    try:
        opener = urllib.request.build_opener(_NoRedirect)
        for _ in range(MAX_REDIRECTS + 1):
            allowed, reason = is_url_allowed(current)
            if not allowed:
                return {"ok": False, "url": url, "html": "", "status": status,
                        "final_url": current, "headers": headers_out,
                        "error": f"SSRF blocked on redirect: {reason}"}
            req = urllib.request.Request(current, headers=hdrs)
            try:
                resp = opener.open(req, timeout=timeout)
                status = getattr(resp, "status", 200)
                headers_out = dict(resp.headers.items())
                raw = resp.read(max_bytes + 1)
                if len(raw) > max_bytes:
                    raw = raw[:max_bytes]
                html = raw.decode("utf-8", errors="ignore")
                return {"ok": True, "url": url, "html": html, "status": status,
                        "final_url": resp.geturl(), "headers": headers_out, "error": None}
            except urllib.error.HTTPError as e:
                if e.code in (301, 302, 303, 307, 308):
                    loc = e.headers.get("Location", "")
                    if not loc:
                        return {"ok": False, "url": url, "html": "", "status": e.code,
                                "final_url": current, "headers": dict(e.headers.items()),
                                "error": "redirect without Location"}
                    current = urllib.parse.urljoin(current, loc)
                    status = e.code
                    continue
                return {"ok": False, "url": url, "html": "", "status": e.code,
                        "final_url": current, "headers": dict(e.headers.items()),
                        "error": f"HTTP {e.code}"}
        return {"ok": False, "url": url, "html": "", "status": status,
                "final_url": current, "headers": headers_out, "error": "too many redirects (max 3)"}
    except Exception as e:
        return {"ok": False, "url": url, "html": "", "status": status,
                "final_url": current, "headers": headers_out, "error": str(e)[:300]}


# ---- Rate limiting (in-memory token bucket per IP+endpoint) ----
_RATE_STORE: Dict[str, Dict] = {}
_RATE_LOCK = threading.Lock()


def check_rate_limit(ip: str, endpoint: str, limit: int, window_s: int) -> Tuple[bool, str]:
    """Return (allowed, message). Thread-safe fixed-window counter."""
    now = time.time()
    key = f"{ip}:{endpoint}"
    with _RATE_LOCK:
        rec = _RATE_STORE.get(key)
        if not rec or now - rec.get("start", 0) > window_s:
            _RATE_STORE[key] = {"start": now, "count": 1}
            return True, "ok"
        if rec["count"] >= limit:
            retry = int(window_s - (now - rec["start"]))
            return False, f"Rate limit exceeded ({limit}/{window_s}s). Retry in {retry}s."
        rec["count"] += 1
        return True, "ok"


def validate_json_dict(data, max_keys: int = 200) -> Tuple[bool, str]:
    if data is None:
        return False, "No JSON data received"
    if not isinstance(data, dict):
        return False, "JSON body must be an object"
    if len(data) > max_keys:
        return False, "JSON body too large"
    return True, "ok"
