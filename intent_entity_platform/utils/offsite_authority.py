"""Off-site Authority Graph (P1): where 60% of 2026 GEO citations come from.

Live-leaning, keyless sources:
- Wikipedia/Wikidata gap (REST + wbsearchentities, live when network allows)
- Reddit / Quora / YouTube / podcast mention scan via DuckDuckGo site: queries
- Tier-1 publisher citation-likelihood heuristic (transparent, labeled)

Every figure carries source + date + confidence (live_measurement vs
cited_research split per the review). Stdlib only; failures -> honest gaps.
"""
import datetime
import json
import urllib.parse
import urllib.request
from typing import Any, Dict, List

_UA = {"User-Agent": "ContentIntelligenceBot/3.0 (+https://example.com/bot)"}
_TIER1 = ["reuters.com", "apnews.com", "bbc.com", "nytimes.com", "forbes.com",
          "techcrunch.com", "wired.com", "theverge.com", "wsj.com", "bloomberg.com"]


def _get_json(url: str, timeout: int = 12) -> Dict[str, Any]:
    try:
        with urllib.request.urlopen(
                urllib.request.Request(url, headers=_UA), timeout=timeout) as r:
            return {"ok": True,
                    "body": json.loads(r.read(300_000).decode("utf-8", errors="ignore"))}
    except Exception as e:
        return {"ok": False, "error": str(e)[:200]}


def wikipedia_gap(entity: str) -> Dict[str, Any]:
    """Live Wikipedia page-exists + Wikidata Q-ID check."""
    out: Dict[str, Any] = {"entity": entity, "source": "live_measurement",
                           "checked_at": datetime.datetime.now(datetime.timezone.utc).isoformat()}
    if not entity.strip():
        out.update({"status": "NO_ENTITY", "has_page": False})
        return out
    title = urllib.parse.quote(entity.strip().replace(" ", "_"))
    s = _get_json(f"https://en.wikipedia.org/api/rest_v1/page/summary/{title}")
    if s.get("ok") and isinstance(s.get("body"), dict) and s["body"].get("pageid"):
        b = s["body"]
        out.update({"status": "HAS_PAGE", "has_page": True, "pageid": b.get("pageid"),
                    "title": b.get("title"), "description": b.get("description"),
                    "extract_len": len(b.get("extract", "") or "")})
    else:
        out.update({"status": "GAP_NO_PAGE", "has_page": False,
                    "error": s.get("error"),
                    "recommendation": "No Wikipedia page: build Wikidata item + 2-3 secondary sources first."})
    w = _get_json("https://www.wikidata.org/w/api.php?action=wbsearchentities&format=json"
                  f"&language=en&search={urllib.parse.quote(entity.strip())}")
    if w.get("ok"):
        hits = (w.get("body", {}) or {}).get("search", []) or []
        out["wikidata"] = {"hits": len(hits),
                           "top": [{"id": h.get("id"), "label": h.get("label"),
                                    "desc": h.get("description")} for h in hits[:3]]}
    else:
        out["wikidata"] = {"hits": 0, "error": w.get("error")}
    return out


def mention_scan(entity: str, seed: str = "") -> Dict[str, Any]:
    """Keyless off-site mention scan via DDG html (best-effort, honestly labeled)."""
    from . import web_data as wd
    surfaces = {
        "reddit": f"site:reddit.com {entity} {seed}".strip(),
        "quora": f"site:quora.com {entity} {seed}".strip(),
        "youtube": f"site:youtube.com {entity} {seed}".strip(),
        "podcasts": f"{entity} podcast interview transcript",
        "github": f"site:github.com {entity}",
        "tier1": f"{entity} ({' OR '.join(['site:' + d for d in _TIER1[:5]])})",
    }
    per_surface: Dict[str, Any] = {}
    for name, q in surfaces.items():
        try:
            res = wd.web_search(q, num=5)
            items = res if isinstance(res, list) else res.get("results", res.get("organic", []))
            per_surface[name] = {"query": q, "hits": len(items or []),
                                 "top": [{"title": (i.get("title") if isinstance(i, dict) else str(i))[:120],
                                          "url": (i.get("url") or i.get("href") or "")[:200]}
                                         for i in (items or [])[:3]],
                                 "source": "live_measurement_ddg_html",
                                 "confidence": "low_single_snapshot"}
        except Exception as e:
            per_surface[name] = {"query": q, "hits": 0, "error": str(e)[:160],
                                 "source": "live_measurement_ddg_html",
                                 "confidence": "low_single_snapshot"}
    total = sum(v.get("hits", 0) for v in per_surface.values())
    return {"per_surface": per_surface, "total_hits": total,
            "method_note": "Keyless DDG site: snapshot, not exhaustive crawl. "
                           "Use Reddit/YouTube APIs for production counts.",
            "checked_at": datetime.datetime.now(datetime.timezone.utc).isoformat()}


def authority_graph(entity: str, seed: str = "", brand: str = "") -> Dict[str, Any]:
    wiki = wikipedia_gap(entity or brand or seed)
    mentions = mention_scan(entity or brand or seed, seed)
    score = 0
    if wiki.get("has_page"):
        score += 35
    if (wiki.get("wikidata", {}) or {}).get("hits"):
        score += 15
    score += min(30, mentions.get("total_hits", 0) * 3)
    if mentions.get("per_surface", {}).get("tier1", {}).get("hits"):
        score += 20
    score = max(0, min(100, score))
    return {
        "method": "offsite_authority_graph_v1",
        "method_note": "Live keyless checks (Wikipedia/Wikidata + DDG site: scan). Tier-1 likelihood is heuristic.",
        "entity": entity, "seed": seed, "brand": brand,
        "offsite_score": score,
        "tier": "STRONG" if score >= 70 else "EMERGING" if score >= 40 else "WEAK",
        "wikipedia": wiki,
        "mentions": mentions,
        "cited_research": {"note": "2026 studies: ~60% of GEO citations resolve off-site (brand mentions > backlinks).",
                           "confidence": "cited_research_industry_studies"},
        "next_actions": _next(score, wiki, mentions),
    }


def _next(score: int, wiki: Dict[str, Any], mentions: Dict[str, Any]) -> List[Dict[str, str]]:
    acts: List[Dict[str, str]] = []
    if not wiki.get("has_page"):
        acts.append({"priority": "HIGH",
                     "action": "Close the Knowledge-Graph gap: Wikidata item -> cited draft -> Wikipedia notability path.",
                     "why": "No page = weak entity resolution for every LLM."})
    low = [k for k, v in (mentions.get("per_surface", {}) or {}).items()
           if isinstance(v, dict) and v.get("hits", 0) == 0 and k in ("reddit", "quora", "youtube")]
    if low:
        acts.append({"priority": "HIGH",
                     "action": f"Seed expert answers on: {', '.join(low)} (disclosure-compliant, genuinely useful).",
                     "why": "LLMs over-cite Reddit/Quora/YouTube transcripts for how-to queries."})
    if not (mentions.get("per_surface", {}) or {}).get("tier1", {}).get("hits"):
        acts.append({"priority": "MEDIUM",
                     "action": "Pitch one data-led story to a tier-1 outlet (original stat + methodology page).",
                     "why": "Tier-1 citations anchor AI Overview trust."})
    if score >= 70:
        acts.append({"priority": "LOW", "action": "Maintain: monthly mention re-scan + record wins in history DB.",
                     "why": "Off-site moat compounds."})
    return acts
