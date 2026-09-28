"""
Dual SEO+GEO content scorer (stdlib, no ML deps).
- TF-IDF cosine of draft vs top-5 competitor average (local, transparent)
- Term coverage: must-include entities, PAA-derived terms
- Structural targets: words, H2, links, images
Explicitly labeled heuristic — NOT a replacement for embedding models or
paid SERP APIs. Upgrade path: all-MiniLM-L6-v2 when numpy/scipy allowed.
"""
import math
import re
from collections import Counter
from typing import Dict, List, Any

_WORD_RE = re.compile(r"[a-z0-9][a-z0-9\-']{1,30}")


def _tokens(text: str) -> List[str]:
    return _WORD_RE.findall((text or "").lower())


def _tfidf_vecs(docs: List[str]):
    toks = [_tokens(d) for d in docs]
    df: Counter = Counter()
    for t in toks:
        for w in set(t):
            df[w] += 1
    n = max(1, len(docs))
    vecs = []
    for t in toks:
        tf = Counter(t)
        total = max(1, len(t))
        v = {}
        for w, c in tf.items():
            idf = math.log((n + 1) / (df[w] + 1)) + 1.0
            v[w] = (c / total) * idf
        vecs.append(v)
    return vecs


def _cosine(a: Dict, b: Dict) -> float:
    if not a or not b:
        return 0.0
    dot = sum(a.get(k, 0.0) * v for k, v in b.items())
    na = math.sqrt(sum(v * v for v in a.values()))
    nb = math.sqrt(sum(v * v for v in b.values()))
    if not na or not nb:
        return 0.0
    return dot / (na * nb)


def score_content(draft_text: str, competitor_texts: List[str],
                  must_include_terms: List[str] = None,
                  targets: Dict[str, float] = None) -> Dict[str, Any]:
    """Return dual SEO+GEO score 0-100 with sub-scores and word/H2/link/image gaps."""
    must_include_terms = [t.lower() for t in (must_include_terms or []) if t]
    targets = targets or {}
    docs = [draft_text or ""] + [c or "" for c in (competitor_texts or [])[:5]]
    vecs = _tfidf_vecs(docs)
    draft_v = vecs[0]
    comp_vs = vecs[1:]
    sims = [_cosine(draft_v, c) for c in comp_vs if c]
    avg_sim = round(sum(sims) / len(sims), 4) if sims else 0.0
    # Semantic similarity 0-100 (cosine is usually 0.05-0.6 for TF-IDF; scale)
    semantic_score = round(min(100.0, max(0.0, avg_sim * 220)), 1)

    draft_low = (draft_text or "").lower()
    covered, missing = [], []
    for t in must_include_terms:
        (covered if t in draft_low else missing).append(t)
    coverage = round(len(covered) / max(1, len(must_include_terms)) * 100, 1) \
        if must_include_terms else None

    words = len(_tokens(draft_text or ""))
    t_words = targets.get("words", 0) or 0
    struct_score = 100.0
    gaps = {}
    if t_words:
        ratio = words / t_words if t_words else 0
        gaps["words"] = {"yours": words, "target": t_words,
                         "delta_pct": round((words - t_words) / t_words * 100, 1)}
        struct_score = min(struct_score, 100 - min(60, abs(1 - ratio) * 100))
    for k in ("h2", "links", "images"):
        if targets.get(k) is not None:
            gaps[k] = {"target": targets[k]}

    parts, weights = [semantic_score], [0.5]
    if coverage is not None:
        parts.append(coverage)
        weights.append(0.3)
    parts.append(round(struct_score, 1))
    weights.append(0.2 if coverage is not None else 0.5)
    total = round(sum(p * w for p, w in zip(parts, weights)) / sum(weights), 1)

    return {
        "module": "CONTENT_SCORE",
        "method": "heuristic_tfidf_cosine",
        "method_note": ("Heuristic estimate — TF-IDF cosine, not neural embeddings. "
                        "Counts terms, not meaning. Upgrade to all-MiniLM-L6-v2 for production scoring."),
        "seo_score": total,
        "geo_score": round((semantic_score * 0.4 + (coverage if coverage is not None else semantic_score) * 0.6), 1),
        "semantic_similarity_vs_top5_avg": avg_sim,
        "semantic_score": semantic_score,
        "term_coverage_pct": coverage,
        "terms_covered": covered[:40],
        "terms_missing": missing[:40],
        "structure_score": round(struct_score, 1),
        "structure_gaps": gaps,
        "competitors_compared": len(comp_vs),
        "grade": "A" if total >= 85 else ("B" if total >= 70 else ("C" if total >= 55 else ("D" if total >= 40 else "F"))),
    }
