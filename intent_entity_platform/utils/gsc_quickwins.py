"""
GSC Quick Wins: CSV upload fallback + striking-distance / decay / cannibalization /
AI-Appearance segmentation. Stdlib only (csv, re).
Expected CSV columns (GSC Performance export): query,page,clicks,impressions,ctr,position
(or superset — extra columns ignored, missing numeric columns default to 0).
"""
import csv
import io
import re
from typing import Dict, List, Any


def parse_gsc_csv(text: str, max_rows: int = 20000) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    try:
        reader = csv.DictReader(io.StringIO(text or ""))
        if not reader.fieldnames:
            return []
        norm = { (f or "").strip().lower(): f for f in reader.fieldnames }
        def pick(*names):
            for n in names:
                if n in norm:
                    return norm[n]
            return None
        c_q, c_p = pick("query", "keyword"), pick("page", "url", "landing page")
        c_c, c_i = pick("clicks"), pick("impressions", "impr")
        c_ctr, c_pos = pick("ctr", "avg ctr"), pick("position", "avg position", "avg. position")
        for i, r in enumerate(reader):
            if i >= max_rows:
                break
            try:
                rows.append({
                    "query": (r.get(c_q, "") if c_q else "").strip(),
                    "page": (r.get(c_p, "") if c_p else "").strip(),
                    "clicks": float(str(r.get(c_c, 0) if c_c else 0).replace(",", "") or 0),
                    "impressions": float(str(r.get(c_i, 0) if c_i else 0).replace(",", "") or 0),
                    "ctr": _num(str(r.get(c_ctr, 0) if c_ctr else 0)),
                    "position": _num(str(r.get(c_pos, 99) if c_pos else 99)),
                })
            except Exception:
                continue
    except Exception:
        return []
    return [r for r in rows if r["query"] or r["page"]]


def _num(s: str) -> float:
    s = (s or "").strip().replace("%", "")
    try:
        return float(s.replace(",", "") or 0)
    except Exception:
        return 0.0


def quick_wins(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Striking distance 4-20, decay flag (needs date col — heuristic), cannibalization, AI filter."""
    striking = [r for r in rows if 4 <= r["position"] <= 20 and r["impressions"] >= 50]
    striking.sort(key=lambda r: (-r["impressions"], r["position"]))
    # Cannibalization: same query mapping to 2+ distinct pages
    by_query: Dict[str, List[str]] = {}
    for r in rows:
        if r["query"] and r["page"]:
            by_query.setdefault(r["query"].lower(), [])
            if r["page"] not in by_query[r["query"].lower()]:
                by_query[r["query"].lower()].append(r["page"])
    cannibal = [{"query": q, "pages": p, "page_count": len(p)}
                for q, p in by_query.items() if len(p) > 1]
    cannibal.sort(key=lambda x: -x["page_count"])
    # AI Appearance heuristic: queries with question words / long-tail / PAA shape
    ai_pat = re.compile(r"^(what|how|why|when|who|which|best|vs|compare|is |does |can |should )|\?| (vs|versus) ", re.I)
    ai_rows = [r for r in rows if ai_pat.search(r["query"] or "")]
    # Decay heuristic without dates: high impressions + CTR < 1% + position > 10
    decay = [r for r in rows if r["impressions"] >= 200 and r["ctr"] < 1.0 and r["position"] > 10]
    decay.sort(key=lambda r: -r["impressions"])
    return {
        "module": "GSC_QUICK_WINS",
        "method_note": ("CSV fallback (GSC Wizard pattern). OAuth sync is the upgrade path. "
                        "Decay flag is heuristic without date-segmented exports."),
        "rows_analyzed": len(rows),
        "striking_distance_4_20": striking[:50],
        "striking_count": len(striking),
        "decay_candidates": decay[:50],
        "decay_count": len(decay),
        "cannibalization": cannibal[:50],
        "cannibalization_count": len(cannibal),
        "ai_appearance_candidates": ai_rows[:50],
        "ai_appearance_count": len(ai_rows),
        "top_queries_by_impressions": sorted(rows, key=lambda r: -r["impressions"])[:30],
    }
