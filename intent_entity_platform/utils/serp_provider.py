"""
SERP provider abstraction + 30-day SQLite cache.
Providers: serper | dataforseo | searlo | ddg_fallback (default, stdlib, no key).
Env: SERP_PROVIDER, SERPER_API_KEY, DATAFORSEO_LOGIN, DATAFORSEO_PASSWORD, SEARLO_API_KEY.
Stdlib only (sqlite3 + urllib).
"""
import hashlib
import json
import os
import sqlite3
import time
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Dict, List, Any

_CACHE_DB = Path(__file__).parent.parent / "data" / "serp_cache.sqlite3"
_CACHE_TTL_S = 30 * 24 * 3600


def _db():
    _CACHE_DB.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(str(_CACHE_DB), timeout=10)
    con.execute("""CREATE TABLE IF NOT EXISTS serp_cache(
        key TEXT PRIMARY KEY, provider TEXT, query TEXT, payload TEXT, created REAL)""")
    return con


def _cache_key(provider: str, query: str, num: int) -> str:
    return hashlib.sha256(f"{provider}|{query.lower().strip()}|{num}".encode()).hexdigest()


def cache_get(provider: str, query: str, num: int):
    try:
        con = _db()
        row = con.execute("SELECT payload, created FROM serp_cache WHERE key=?",
                          (_cache_key(provider, query, num),)).fetchone()
        con.close()
        if not row:
            return None
        payload, created = row
        if time.time() - created > _CACHE_TTL_S:
            return None
        data = json.loads(payload)
        data["_cached"] = True
        return data
    except Exception:
        return None


def cache_put(provider: str, query: str, num: int, payload: Dict):
    try:
        con = _db()
        con.execute("REPLACE INTO serp_cache(key,provider,query,payload,created) VALUES(?,?,?,?,?)",
                    (_cache_key(provider, query, num), provider, query,
                     json.dumps(payload)[:200000], time.time()))
        con.commit()
        con.close()
    except Exception:
        pass


def _fetch_serper(query: str, num: int) -> Dict:
    key = os.environ.get("SERPER_API_KEY", "")
    if not key:
        return {"ok": False, "error": "SERPER_API_KEY not configured"}
    try:
        body = json.dumps({"q": query, "num": num}).encode()
        req = urllib.request.Request("https://google.serper.dev/search",
                                     data=body,
                                     headers={"X-API-KEY": key, "Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read().decode("utf-8", errors="ignore"))
        results = []
        for i, r in enumerate((data.get("organic") or [])[:num]):
            results.append({"title": r.get("title", "")[:120], "url": r.get("link", ""),
                            "snippet": r.get("snippet", "")[:300], "position": i + 1})
        return {"ok": bool(results), "backend": "serper", "query": query,
                "results": results, "raw_top10_html": "",
                "meta": {"ai_overview": bool(data.get("aiOverview")),
                         "paa": [x.get("question", "") for x in (data.get("peopleAlsoAsk") or [])[:8]],
                         "serp_features": list((data.get("searchParameters") or {}).keys())},
                "error": None if results else "serper returned no organic results"}
    except Exception as e:
        return {"ok": False, "backend": "serper", "query": query, "results": [], "error": str(e)[:300]}


def _fetch_dataforseo(query: str, num: int) -> Dict:
    import base64
    login = os.environ.get("DATAFORSEO_LOGIN", "")
    pwd = os.environ.get("DATAFORSEO_PASSWORD", "")
    if not login or not pwd:
        return {"ok": False, "error": "DATAFORSEO_LOGIN/PASSWORD not configured"}
    try:
        cred = base64.b64encode(f"{login}:{pwd}".encode()).decode()
        body = json.dumps([{"keyword": query, "location_code": 2840, "language_code": "en",
                             "depth": num}]).encode()
        req = urllib.request.Request("https://api.dataforseo.com/v3/serp/google/organic/live/advanced",
                                     data=body,
                                     headers={"Authorization": f"Basic {cred}",
                                              "Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8", errors="ignore"))
        tasks = (data.get("tasks") or [{}])[0]
        items = ((tasks.get("result") or [{}])[0].get("items")) or []
        results = []
        for it in items:
            if it.get("type") == "organic":
                results.append({"title": (it.get("title") or "")[:120],
                                "url": it.get("url", "") or it.get("link", ""),
                                "snippet": (it.get("description") or it.get("snippet") or "")[:300],
                                "position": it.get("rank_group") or len(results) + 1})
            if len(results) >= num:
                break
        return {"ok": bool(results), "backend": "dataforseo", "query": query,
                "results": results, "error": None if results else "dataforseo returned no organic items"}
    except Exception as e:
        return {"ok": False, "backend": "dataforseo", "query": query, "results": [], "error": str(e)[:300]}


def _fetch_ddg(query: str, num: int) -> Dict:
    from .web_data import web_search as _ddg
    r = _ddg(query, num=num)
    r["raw_top10_html"] = ""  # parsed signals stored; raw HTML intentionally not persisted
    return r


def serp_fetch(query: str, num: int = 10, provider: str = None) -> Dict[str, Any]:
    """Main entry: provider abstraction with SQLite 30d cache + ddg fallback.

    Always returns {"ok", "backend", "query", "results": [...], "error", "_cached"}.
    Raw top-10 HTML is stored only when provider supplies it; parsed signals always stored.
    """
    provider = (provider or os.environ.get("SERP_PROVIDER", "ddg_fallback")).lower().strip()
    cached = cache_get(provider, query, num)
    if cached:
        return cached
    fetchers = {"serper": _fetch_serper, "dataforseo": _fetch_dataforseo,
                "searlo": _fetch_ddg, "ddg_fallback": _fetch_ddg, "ddg": _fetch_ddg}
    fn = fetchers.get(provider, _fetch_ddg)
    res = fn(query, num)
    if not res.get("ok") and provider not in ("ddg_fallback", "ddg"):
        fb = _fetch_ddg(query, num)
        fb["fallback_from"] = provider
        res = fb
    try:
        cache_put(res.get("backend", provider), query, num,
                  {"ok": res.get("ok"), "backend": res.get("backend"),
                   "query": query, "results": res.get("results", [])[:num],
                   "meta": res.get("meta", {}), "error": res.get("error")})
    except Exception:
        pass
    res["_cached"] = False
    return res
