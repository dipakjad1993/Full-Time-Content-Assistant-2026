"""
SERP-driven Brief Generator (MarketMuse-lite, stdlib).
Input: SERP results, competitor headings, content gaps, entities, PAA/feature signals.
Output: intent, SERP features, H2/H3 outline, FAQ from PAA, word-count target ±20%,
schema recs, E-E-A-T checklist. 9 content-type presets.
"""
import re
from typing import Dict, List, Any

BRIEF_TYPES = ["how-to guide", "comparison X vs Y", "listicle", "definition / glossary",
               "product / category", "local service", "case study", "news / analysis", "faq hub"]


def _infer_intent(seed: str, serp_features: Dict) -> Dict[str, str]:
    s = (seed or "").lower()
    feats = serp_features.get("feature_names", []) if isinstance(serp_features, dict) else []
    if any(w in s for w in ["vs", "versus", "compare", "best", "top ", "review", "alternative"]):
        return {"intent": "comparative / commercial investigation", "funnel": "middle-bottom",
                "cta": "compare then convert", "brief_type": "comparison X vs Y"}
    if any(w in s for w in ["how to", "how-to", "tutorial", "guide", "steps"]):
        return {"intent": "informational / how-to", "funnel": "top-middle",
                "cta": "educate then capture", "brief_type": "how-to guide"}
    if any(w in s for w in ["price", "cost", "buy", "quote", "near me", "hire"]):
        return {"intent": "transactional", "funnel": "bottom",
                "cta": "convert", "brief_type": "product / category"}
    if "?" in s or s.startswith(("what", "why", "when", "who", "which", "is ", "does ", "can ")):
        return {"intent": "informational / AEO answer", "funnel": "top",
                "cta": "answer then deepen", "brief_type": "faq hub"}
    if "shopping_results" in feats or "local_pack" in feats:
        return {"intent": "transactional / local", "funnel": "bottom",
                "cta": "convert", "brief_type": "product / category"}
    return {"intent": "informational / mixed", "funnel": "top-middle",
            "cta": "educate", "brief_type": "definition / glossary"}


def generate_brief(seed: str, entity: str, serp_results: List[Dict],
                   competitor_headings: Dict, content_gaps: Dict,
                   entities: Dict, serp_features: Dict,
                   word_target: int = 0) -> Dict[str, Any]:
    intent = _infer_intent(seed or "", serp_features or {})
    h2s = []
    try:
        h2s = (competitor_headings or {}).get("all_h2s_sample", [])[:30]
    except Exception:
        h2s = []
    gaps = []
    try:
        gaps = (content_gaps or {}).get("content_gaps", [])[:15]
    except Exception:
        gaps = []
    paa = []
    try:
        for f in (serp_features or {}).get("features_detected", []):
            if f.get("feature") == "people_also_ask":
                paa.extend(f.get("sample_questions", [])[:8])
    except Exception:
        pass
    # Outline: definition + must-cover competitor H2 themes + gap sections + FAQ
    outline = []
    outline.append({"h2": f"What is {entity or seed}? (definition ≤ 60 words, citable)",
                    "h3": ["Core definition", "Why it matters now (2026)"], "why": "AEO/AIO extraction"})
    seen = set()
    for h in h2s[:8]:
        key = (h or "").lower().strip()
        if key and key not in seen and len(key) > 8:
            seen.add(key)
            outline.append({"h2": h, "h3": [], "why": "competitor-proven subtopic"})
    for g in gaps[:4]:
        if isinstance(g, str) and g.strip():
            outline.append({"h2": g.strip().title(), "h3": [], "why": "content gap vs competitors"})
    if paa:
        outline.append({"h2": "Frequently asked questions", "h3": paa[:6], "why": "PAA capture"})
    # Word target ±20%
    if word_target and word_target > 0:
        lo, hi = int(word_target * 0.8), int(word_target * 1.2)
    else:
        lo, hi = 1200, 2200
        if intent["brief_type"] in ("comparison X vs Y", "how-to guide"):
            lo, hi = 1800, 3000
        elif intent["brief_type"] == "faq hub":
            lo, hi = 900, 1600
    top_entities = []
    try:
        top_entities = [e.get("entity", "") for e in (entities or {}).get("top_entities", [])[:15]]
    except Exception:
        pass
    return {
        "module": "BRIEF_GENERATOR",
        "intent": intent["intent"],
        "funnel": intent["funnel"],
        "recommended_cta": intent["cta"],
        "brief_type": intent["brief_type"],
        "brief_types_available": BRIEF_TYPES,
        "serp_features": (serp_features or {}).get("feature_names", []),
        "outline_h2_h3": outline,
        "faq_from_paa": paa[:10],
        "word_count_target": {"min": lo, "target": (lo + hi) // 2, "max": hi, "rule": "±20% of competitor p75"},
        "must_include_entities": top_entities,
        "schema_recommendations": ["Article + Person author + dateModified",
                                   "BreadcrumbList", "FAQPage (only for visible Q&A)",
                                   "SpeakableSpecification (for AEO sections)",
                                   "Validate: Google Rich Results Test + Schema.org validator"],
        "eeat_checklist": ["Named author with credentials + sameAs links",
                           "≥1 unfindable fact (original research/quote/stat with source)",
                           "Comparison table where applicable (~2.5x cite rate)",
                           "Sourced statistics with links (no invented numbers)",
                           "Last-reviewed date + IndexNow/lastmod hygiene"],
        "sources": {"serp_results_used": len(serp_results or []),
                    "competitor_h2s_used": len(h2s), "gaps_used": len(gaps)},
    }
