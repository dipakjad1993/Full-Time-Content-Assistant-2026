"""Answer-extractability validator (2026: 40-60 word blocks, Q&A, lists, tables).

Scores per-engine extractability for ChatGPT / Gemini / Perplexity / AI Overviews:
- direct-answer blocks in the 40-60 word band (2026 consensus for citation)
- Q-formatted H2/H3 -> immediate answer adjacency
- list/table/step density (Perplexity prioritizes FAQ/list schema over backlinks)
- definition-first sentences, statistic+source proximity
- machine-extractable facts: price/spec/table + JSON-LD Product/Offer/FAQ presence
  (agentic AEO: Claude/ChatGPT agents + Amazon Rufus A9 structured-data check)

Heuristic but transparent: every score shows its rule + counts. Stdlib only.
"""
import re
from typing import Any, Dict, List

_WORD_RE = re.compile(r"[A-Za-z0-9][\w\-']*")
_Q_RE = re.compile(r"^(who|what|when|where|why|how|can|does|is|are|should|which)\b.*\?\s*$", re.I)


def _words(s: str) -> int:
    return len(_WORD_RE.findall(s or ""))


def _split_blocks(page_text: str, h2s: List[str]) -> List[Dict[str, Any]]:
    paras = [p.strip() for p in re.split(r"\n{2,}|\r?\n\r?\n", page_text or "") if p.strip()]
    if not paras and page_text:
        # fallback: sentence-window blocks of ~50 words
        toks = _WORD_RE.findall(page_text)
        for i in range(0, len(toks), 50):
            paras.append(" ".join(toks[i:i + 50]))
    return [{"text": p, "words": _words(p)} for p in paras[:80]]


def validate_extractability(page_text: str = "", h1: str = "", h2s=None,
                            html: str = "", has_schema_types=None) -> Dict[str, Any]:
    h2s = h2s or []
    schemas = set(has_schema_types or [])
    blocks = _split_blocks(page_text or "", h2s)
    in_band = [b for b in blocks if 40 <= b["words"] <= 60]
    short = [b for b in blocks if 20 <= b["words"] < 40]
    long = [b for b in blocks if b["words"] > 120]

    q_heads = [h for h in (h2s or []) if h.strip().endswith("?") or _Q_RE.match(h.strip())]
    lists = len(re.findall(r"<(ul|ol)\b", html or "", re.I))
    tables = len(re.findall(r"<table\b", html or "", re.I))
    defs = len(re.findall(r"\b(is|are|means|refers to|defined as)\b", page_text or "", re.I))
    stats = len(re.findall(r"\d+(?:\.\d+)?\s*%", page_text or ""))
    sourced_stats = len(re.findall(r"\(\s*source[^)]*\)|\[\s*source[^\]]*\]|according to", page_text or "", re.I))

    # machine-extractable facts (agentic AEO)
    price_hits = len(re.findall(r"\$\s?\d|€\s?\d|₹\s?\d|\bUSD\b|\bprice\b", (page_text or "") + (html or ""), re.I))
    spec_tables = tables
    has_product_offer = bool({"Product", "Offer", "AggregateOffer"} & schemas)
    has_faq = "FAQPage" in schemas
    rufus_risk = ("HIGH_MISSING_STRUCTURED_DATA" if (price_hits > 0 and not has_product_offer)
                  else "OK" if has_product_offer else "NO_PRICING_DETECTED")

    def pct(a: int, b: int) -> float:
        return round(100.0 * a / b, 1) if b else 0.0

    score = 0
    score += min(30, len(in_band) * 6)          # answer blocks
    score += min(15, len(q_heads) * 5)          # Q&A adjacency
    score += min(15, (lists + tables) * 4)      # list/table density
    score += min(10, defs)                      # definition-first
    score += min(10, sourced_stats * 3)         # stat+source proximity
    score += 10 if has_faq else 0               # FAQ schema (Perplexity weight)
    score += 10 if has_product_offer else 0     # agentic commerce
    score = max(0, min(100, score))

    per_engine = {
        "ai_overviews": min(100, score + (5 if tables else 0)),
        "chatgpt": score,
        "perplexity": min(100, score + (8 if has_faq else 0) + (4 if lists else 0)),
        "gemini": min(100, score + (4 if tables else 0)),
        "claude": min(100, score - (4 if long and len(long) > len(in_band) else 0)),
    }
    return {
        "method": "heuristic_rule_extractability",
        "method_note": "Rule-based extractability estimate (word-band + Q&A + list/table + schema). Not a live engine render.",
        "extractability_score": score,
        "tier": "HIGH" if score >= 75 else "MEDIUM" if score >= 50 else "LOW",
        "blocks_total": len(blocks),
        "blocks_40_60": len(in_band),
        "blocks_20_40": len(short),
        "blocks_over_120": len(long),
        "block_coverage_pct": pct(len(in_band), len(blocks)),
        "question_heads": len(q_heads),
        "question_headings": q_heads[:12],
        "list_count": lists, "table_count": tables,
        "definition_signals": defs,
        "stat_count": stats, "sourced_stat_count": sourced_stats,
        "machine_facts": {"price_mentions": price_hits, "spec_tables": spec_tables,
                          "has_product_offer": has_product_offer, "has_faq": has_faq,
                          "rufus_a9_risk": rufus_risk},
        "per_engine": per_engine,
        "top_answer_blocks": [{"words": b["words"], "preview": b["text"][:220]} for b in in_band[:5]],
        "recommendations": _recs(len(in_band), len(q_heads), lists, tables, has_faq,
                                 has_product_offer, rufus_risk, sourced_stats, stats),
    }


def _recs(in_band: int, q: int, lists: int, tables: int, faq: bool,
          offer: bool, rufus: str, sourced: int, stats: int) -> List[Dict[str, str]]:
    r: List[Dict[str, str]] = []
    if in_band < 3:
        r.append({"priority": "HIGH",
                  "action": "Add 3+ direct-answer blocks of 40-60 words, one per top H2 (definition -> fact -> source).",
                  "why": "2026 consensus extractability band for AI citations."})
    if q < 2:
        r.append({"priority": "HIGH",
                  "action": "Rewrite 2+ H2s as questions users actually ask; put the answer in the first 1-2 sentences.",
                  "why": "Q&A adjacency drives snippet + AI Overview triggers."})
    if not lists and not tables:
        r.append({"priority": "MEDIUM",
                  "action": "Add one comparison table + one stepwise list per 800 words.",
                  "why": "Perplexity/AI Overviews over-index on lists/tables."})
    if not faq:
        r.append({"priority": "MEDIUM",
                  "action": "Emit FAQPage JSON-LD for the Q&A H2s (M13 payloads).",
                  "why": "Perplexity prioritizes FAQ schema over backlinks (Q1 2026)."})
    if rufus.startswith("HIGH"):
        r.append({"priority": "HIGH",
                  "action": "Add Product/Offer JSON-LD (price, availability, SKU) wherever prices are mentioned.",
                  "why": "Agentic buyers (Rufus/ChatGPT agents) skip pages without machine facts."})
    if stats and not sourced:
        r.append({"priority": "MEDIUM",
                  "action": "Attach a named source to every % statistic ('according to X, year').",
                  "why": "Unsourced stats raise hallucination risk and lose citations."})
    if not r:
        r.append({"priority": "LOW", "action": "Hold the pattern; regression-test extractability monthly.",
                  "why": "Structure already in the citable band."})
    return r
