"""Real Core Web Vitals via CrUX + PageSpeed Insights (P0).

- CrUX History API: no key needed for basic field data (uses public endpoint;
  requires no key for small quota, key via CRUX_API_KEY / PSI_API_KEY for prod).
- PSI API: needs PSI_API_KEY (same as Google API key with PSI enabled).
Without keys or network, returns honest NOT_MEASURED instead of fake numbers.
Stdlib only.
"""
import json
import os
import urllib.parse
import urllib.request
from typing import Any, Dict

_CRUX_URL = "https://chromeuxreport.googleapis.com/v1/records:queryHistoryRecord"
_PSI_URL = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"


def _post_json(url: str, payload: Dict[str, Any], timeout: int = 20) -> Dict[str, Any]:
    try:
        data = json.dumps(payload).encode()
        req = urllib.request.Request(
            url, data=data,
            headers={"Content-Type": "application/json",
                     "User-Agent": "ContentIntelligenceBot/3.0"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return {"ok": True, "status": getattr(r, "status", 200),
                    "body": json.loads(r.read(1_000_000).decode("utf-8", errors="ignore"))}
    except Exception as e:
        return {"ok": False, "error": str(e)[:300]}


def _get_json(url: str, timeout: int = 25) -> Dict[str, Any]:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "ContentIntelligenceBot/3.0"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return {"ok": True, "status": getattr(r, "status", 200),
                    "body": json.loads(r.read(2_000_000).decode("utf-8", errors="ignore"))}
    except Exception as e:
        return {"ok": False, "error": str(e)[:300]}


def crux_history(url: str) -> Dict[str, Any]:
    key = os.environ.get("CRUX_API_KEY", "") or os.environ.get("PSI_API_KEY", "")
    endpoint = _CRUX_URL + (f"?key={key}" if key else "")
    res = _post_json(endpoint, {"url": url, "collectionPeriodCount": 3})
    if not res.get("ok"):
        return {"status": "NOT_MEASURED", "source": "crux_history_api",
                "error": res.get("error"),
                "note": "Set CRUX_API_KEY (or PSI_API_KEY) + network for field data."}
    try:
        rec = res["body"].get("record", {})
        metrics = rec.get("metrics", {})
        out: Dict[str, Any] = {"status": "MEASURED", "source": "crux_history_api",
                               "collection_periods": rec.get("collectionPeriods", [])}
        for m in ("largest_contentful_paint", "interaction_to_next_paint",
                  "cumulative_layout_shift"):
            hist = (metrics.get(m, {}) or {}).get("history", [])
            if hist:
                last = hist[-1]
                out[m] = {"percentiles": last.get("percentiles", {}),
                          "collection_period": last.get("collectionPeriod", {})}
        return out
    except Exception as e:
        return {"status": "NOT_MEASURED", "source": "crux_history_api",
                "error": str(e)[:200]}


def pagespeed(url: str, strategy: str = "mobile") -> Dict[str, Any]:
    key = os.environ.get("PSI_API_KEY", "")
    if not key:
        return {"status": "NOT_MEASURED", "source": "pagespeed_insights_api",
                "note": "Set PSI_API_KEY env for lab+field data. Falls back to heuristic CWV in M10.",
                "method_note": "heuristic estimate only until PSI key is configured."}
    q = urllib.parse.urlencode({"url": url, "strategy": strategy, "key": key,
                                "category": "performance"})
    res = _get_json(f"{_PSI_URL}?{q}")
    if not res.get("ok"):
        return {"status": "NOT_MEASURED", "source": "pagespeed_insights_api",
                "error": res.get("error")}
    try:
        body = res["body"]
        lighthouse = body.get("lighthouseResult", {})
        audits = lighthouse.get("audits", {})
        out: Dict[str, Any] = {"status": "MEASURED", "source": "pagespeed_insights_api",
                               "strategy": strategy,
                               "score": (lighthouse.get("categories", {})
                                         .get("performance", {}).get("score"))}
        for k in ("largest-contentful-paint", "interaction-to-next-paint",
                  "cumulative-layout-shift", "first-contentful-paint",
                  "total-blocking-time", "speed-index"):
            a = audits.get(k, {})
            if a:
                out[k] = {"display": a.get("displayValue"),
                          "numeric": a.get("numericValue"),
                          "score": a.get("score")}
        crux = ((body.get("loadingExperience", {}) or {}).get("metrics", {}))
        if crux:
            out["crux_field"] = {k: {"percentile": (v.get("percentile") if isinstance(v, dict) else v)}
                                 for k, v in crux.items()}
        return out
    except Exception as e:
        return {"status": "NOT_MEASURED", "source": "pagespeed_insights_api",
                "error": str(e)[:200]}


def full_vitals(url: str, strategy: str = "mobile") -> Dict[str, Any]:
    return {"url": url, "crux": crux_history(url),
            "psi": pagespeed(url, strategy),
            "method_note": "CrUX field data is measured (28-day RUM). "
                           "PSI lab data needs PSI_API_KEY; otherwise NOT_MEASURED, never fabricated."}
