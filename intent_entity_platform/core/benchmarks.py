"""
Standardized score benchmarks + per-module recommendation playbooks.

Powers:
- "What score should I aim for?" (rankings / AI Overview inclusion / AI citations)
- Color coding of scores in the UI + PDF
- Per-module: analysis-first, then recommendations (what / when / tools / A-B test)

All targets are transparent, standard industry benchmarks (labeled "heuristic,
unverified" where they are guidance rather than measured data). They are never
presented as measured results.
"""
from typing import Dict, Any

# ---------------------------------------------------------------------------
# Score benchmark definitions
# ---------------------------------------------------------------------------
# Each entry: key-pattern -> benchmark spec.
#  - "scale": "0-1" or "0-100"
#  - "target": the score clients/users should aim to REACH
#  - "good": minimum acceptable for competitive content
#  - "excellent": top-tier (target for featured AI outcomes)
#  - "rankings", "ai_overview", "ai_citation": short interpretation strings
SCORE_BENCHMARKS: Dict[str, Dict[str, Any]] = {
    # ----- Module 01 - SERP & Knowledge Graph -----
    "topical_authority_score": {"scale": "0-1", "target": 0.70, "good": 0.50, "excellent": 0.85,
        "rankings": "Reaching 0.70+ correlates with top-3 SERP feasibility for head terms.",
        "ai_overview": "0.80+ strongly signals the depth AI Overview extraction prefers.",
        "ai_citation": "0.75+ makes your page a likely citation source for generative answers."},
    "coverage_ratio": {"scale": "0-1", "target": 0.80, "good": 0.60, "excellent": 0.95,
        "rankings": "Entity coverage of 0.80+ matches the topical breadth of ranking pages.",
        "ai_overview": "Higher coverage = more sub-topics an AI engine can pull from.",
        "ai_citation": "Covered entities give AI engines concrete hooks to cite you."},
    "depth_score": {"scale": "0-1", "target": 0.60, "good": 0.40, "excellent": 0.80,
        "rankings": "Depth drives dwell-time signals Google weighs for long-tail terms.",
        "ai_overview": "Deeper sub-topic coverage increases AI Overview eligibility.",
        "ai_citation": "Depth gives answer engines multiple extractable passages."},
    "entity_density_score": {"scale": "0-1", "target": 0.55, "good": 0.35, "excellent": 0.75,
        "rankings": "Entity density supports topic relevance classification.",
        "ai_overview": "Named-entity richness helps AI engines build answer context.",
        "ai_citation": "More verified entities = more attribution hooks for citations."},
    "format_diversity_score": {"scale": "0-1", "target": 0.60, "good": 0.40, "excellent": 0.80,
        "rankings": "Format variety (lists, tables, FAQs) broadens rich-result eligibility.",
        "ai_overview": "Structured formats are preferred for direct answer extraction.",
        "ai_citation": "Tables/lists make passages easier for AI to quote verbatim."},

    # ----- Module 02 - GEO & AEO Simulator -----
    "geo_readiness_score": {"scale": "0-1", "target": 0.70, "good": 0.45, "excellent": 0.85,
        "rankings": "0.70+ indicates content is structured to rank in classic SERPs too.",
        "ai_overview": "Primary GEO lever: aim 0.80+ for AI Overview presence.",
        "ai_citation": "0.75+ maximizes the odds of AI-engine citation."},
    "avg_citation_probability": {"scale": "0-1", "target": 0.60, "good": 0.40, "excellent": 0.80,
        "rankings": "Lower-leverage for classic rankings, strong for AI surfaces.",
        "ai_overview": "Higher citation probability directly raises AI Overview inclusion.",
        "ai_citation": "This IS the AI-citation metric - push to 0.75+."},
    "citation_density": {"scale": "0-100", "target": 15.0, "good": 8.0, "excellent": 25.0,
        "rankings": "Balanced density (not stuffing) supports authority flows.",
        "ai_overview": "Dense, natural citations make content quotable.",
        "ai_citation": "Citations per ~100 words should sit in the 8-25 band."},
    "geo_signal_score": {"scale": "0-1", "target": 0.70, "good": 0.45, "excellent": 0.85,
        "rankings": "GEO signals (schema, structure, freshness) help rankings broadly.",
        "ai_overview": "Strong GEO signals are a precondition for AI visibility.",
        "ai_citation": "Signal strength predicts generative citation likelihood."},

    # ----- Module 03 - Semantic Structure & Schema -----
    "semantic_depth_score": {"scale": "0-1", "target": 0.65, "good": 0.45, "excellent": 0.85,
        "rankings": "Semantic depth correlates with topical relevance in ranking.",
        "ai_overview": "0.70+ aligns with how AI engines segment your content.",
        "ai_citation": "Well-structured semantics give AI clean passages to quote."},
    "keyword_coverage": {"scale": "0-1", "target": 0.75, "good": 0.55, "excellent": 0.90,
        "rankings": "Keyword/entity coverage 0.75+ matches ranking-page breadth.",
        "ai_overview": "Broad coverage answers more AI sub-queries.",
        "ai_citation": "More matched concepts = more citation opportunities."},
    "heading_hierarchy_score": {"scale": "0-1", "target": 0.90, "good": 0.75, "excellent": 1.0,
        "rankings": "A clean H1>H2>H3 tree is a ranking baseline.",
        "ai_overview": "AI engines parse headings to build answer structure - keep 0.90+.",
        "ai_citation": "Hierarchical headings make passage selection reliable."},
    "schema_percentage": {"scale": "0-100", "target": 60.0, "good": 30.0, "excellent": 90.0,
        "rankings": "% of pages with valid structured data; 60%+ is a competitive floor.",
        "ai_overview": "Schema is a strong signal for AI-rich-result eligibility.",
        "ai_citation": "Structured data helps engines trust and cite content."},

    # ----- Module 04 - E-E-A-T Gap Profiler -----
    "overall_score": {"scale": "0-1", "target": 0.75, "good": 0.55, "excellent": 0.90,
        "rankings": "E-E-A-T composite 0.75+ supports YMYL-type ranking confidence.",
        "ai_overview": "AI engines weigh trust signals heavily - aim 0.80+.",
        "ai_citation": "Trusted, cited-able content is the #1 AI-citation factor."},
    "content_differentiation_score": {"scale": "0-1", "target": 0.60, "good": 0.40, "excellent": 0.80,
        "rankings": "Differentiation separates you from the crowded middle.",
        "ai_overview": "Unique angles are what AI Overviews actually quote.",
        "ai_citation": "Original data/analysis is disproportionately cited."},
    "consensus_score": {"scale": "0-1", "target": 0.70, "good": 0.50, "excellent": 0.90,
        "rankings": "Agreement with authoritative consensus aids relevance.",
        "ai_overview": "Consistent, verifiable claims are preferred by AI.",
        "ai_citation": "Consensus-backed claims are safely citable."},

    # ----- Module 05 - Internal Link & Cannibalization -----
    "link_equity_score": {"scale": "0-1", "target": 0.70, "good": 0.45, "excellent": 0.85,
        "rankings": "Link equity distribution affects which pages rank.",
        "ai_overview": "Clear linking architecture helps AI engines map your site.",
        "ai_citation": "Strong internal links help AI verify related entities."},
    "link_quality_score": {"scale": "0-1", "target": 0.70, "good": 0.50, "excellent": 0.85,
        "rankings": "High-quality link sources raise page authority.",
        "ai_overview": "Quality links build the trust graph AI engines consult.",
        "ai_citation": "Cited-adjacent authority increases citation odds."},
    "cannibalization_risk": {"scale": "0-100", "target": 5.0, "good": 20.0, "excellent": 0.0,
        "rankings": "Keep cannibalization risk LOW (<20) - overlapping pages split rankings.",
        "ai_overview": "Cannibalization confuses AI topic assignment.",
        "ai_citation": "Ambiguous pages are less likely to be cited."},

    # ----- Module 06 - Fluff & Cliche Decoder -----
    "overall_quality_score": {"scale": "0-1", "target": 0.70, "good": 0.50, "excellent": 0.85,
        "rankings": "Dense, specific content ranks better than fluff-filled pages.",
        "ai_overview": "AI engines filter filler - specificity wins.",
        "ai_citation": "Concrete, factual passages are quotable."},
    "ai_probability_score": {"scale": "0-100", "target": 10.0, "good": 30.0, "excellent": 5.0,
        "rankings": "Keep AI-likeness penalty low (<30) to avoid quality suppression.",
        "ai_overview": "Overly generic text is excluded from AI answers.",
        "ai_citation": "Low generic-content score = higher citation chance."},
    "filler_density_percentage": {"scale": "0-100", "target": 5.0, "good": 12.0, "excellent": 2.0,
        "rankings": "Minimal filler keeps content tight and ranking-competitive.",
        "ai_overview": "Filler dilutes the passages AI engines extract.",
        "ai_citation": "Dense sentences are preferred for verbatim quotes."},

    # ----- Module 07 - Citation & Source Verifier -----
    "source_coverage_rate": {"scale": "0-100", "target": 70.0, "good": 50.0, "excellent": 90.0,
        "rankings": "% of claims backed by sources; 70%+ supports trust signals.",
        "ai_overview": "Sourced claims are far more AI-answer eligible.",
        "ai_citation": "Every sourced claim is a potential AI citation."},
    "hallucination_risk_score": {"scale": "0-100", "target": 10.0, "good": 30.0, "excellent": 5.0,
        "rankings": "Low hallucination risk protects brand trust and rankings.",
        "ai_overview": "AI engines avoid content that risks propagating errors.",
        "ai_citation": "Verified content is dramatically more citable."},
    "authority_score": {"scale": "0-1", "target": 0.70, "good": 0.50, "excellent": 0.85,
        "rankings": "Author/source authority feeds E-E-A-T rankings.",
        "ai_overview": "Authority is a first-order AI-trust signal.",
        "ai_citation": "High-authority sources are preferentially cited."},

    # ----- Module 08 - Multimodal Asset Blueprint -----
    "accessibility_compliance": {"scale": "0-100", "target": 90.0, "good": 70.0, "excellent": 100.0,
        "rankings": "Accessible media (alt text, captions) supports image rankings.",
        "ai_overview": "Media metadata helps AI understand multimodal context.",
        "ai_citation": "Descriptive media is used to enrich AI answers."},
    "data_visualization_readiness": {"scale": "0-1", "target": 0.70, "good": 0.45, "excellent": 0.85,
        "rankings": "Visual assets increase dwell time and engagement metrics.",
        "ai_overview": "Charts/tables are high-value AI-answer material.",
        "ai_citation": "Original visuals are frequently cited in AI answers."},

    # ----- Module 09 - GEO Tracker -----
    "ai_platform_readiness": {"scale": "0-1", "target": 0.70, "good": 0.45, "excellent": 0.85,
        "rankings": "Readiness for AI platforms correlates with search presence.",
        "ai_overview": "This metric directly tracks AI-Overview eligibility.",
        "ai_citation": "Higher readiness = more AI citations over time."},
    "citation_readiness_score": {"scale": "0-1", "target": 0.65, "good": 0.40, "excellent": 0.80,
        "rankings": "Tracking score - not a ranking factor itself.",
        "ai_overview": "0.70+ tracks toward visible AI Overview presence.",
        "ai_citation": "Target 0.75+ to be a recurring AI citation."},

    # ----- Module 10 - CSR Simulator -----
    "content_availability_score": {"scale": "0-1", "target": 0.95, "good": 0.85, "excellent": 1.0,
        "rankings": "Content must be crawlable/indexable - near-1.0 required.",
        "ai_overview": "AI engines need clean, renderable HTML.",
        "ai_citation": "Available content is a precondition for citation."},
    "crawlability_score": {"scale": "0-1", "target": 0.90, "good": 0.75, "excellent": 1.0,
        "rankings": "Server-rendered content ranks - JS-only content struggles.",
        "ai_overview": "Pre-rendered HTML is what AI engines actually read.",
        "ai_citation": "Rendering issues silently kill citation eligibility."},
    "overall_cwv_risk": {"scale": "0-100", "target": 20.0, "good": 40.0, "excellent": 10.0,
        "rankings": "Core Web Vitals are a confirmed ranking signal.",
        "ai_overview": "Fast, stable pages are preferred by AI crawlers.",
        "ai_citation": "Poor CWV degrades overall trust in the page."},

    # ----- Module 11 - RAG Tester -----
    "avg_alignment_score": {"scale": "0-1", "target": 0.70, "good": 0.50, "excellent": 0.85,
        "rankings": "Query-to-content alignment helps classic relevance too.",
        "ai_overview": "Alignment is what RAG retrieval scores for AI answers.",
        "ai_citation": "Aligned passages are exactly what RAG cites."},
    "average_standalone_score": {"scale": "0-1", "target": 0.70, "good": 0.50, "excellent": 0.85,
        "rankings": "Self-contained chunks are easier for engines to rank.",
        "ai_overview": "Standalone chunks prevent RAG retrieval failure.",
        "ai_citation": "Self-contained answers are verbatim-citable."},
    "avg_chunk_quality": {"scale": "0-1", "target": 0.70, "good": 0.50, "excellent": 0.85,
        "rankings": "Clean chunking improves indexable passage quality.",
        "ai_overview": "Chunk quality directly controls AI answer fidelity.",
        "ai_citation": "High-quality chunks are preferentially selected."},

    # ----- Module 12 - Brand Compliance Engine -----
    "overall_compliance_score": {"scale": "0-1", "target": 0.95, "good": 0.85, "excellent": 1.0,
        "rankings": "Compliance protects brand credibility, a trust input.",
        "ai_overview": "Regulatory/legal consistency matters for sensitive niches.",
        "ai_citation": "Compliant content is safe for AI to cite."},
    "compliance_rate": {"scale": "0-100", "target": 95.0, "good": 85.0, "excellent": 100.0,
        "rankings": "Keep violations to <5% to protect E-E-A-T.",
        "ai_overview": "AI engines downgrade non-compliant claims.",
        "ai_citation": "Low-violation content is reliably citable."},

    # ----- Module 13 - Schema Payload Generator -----
    "validation_error_rate": {"scale": "0-100", "target": 0.0, "good": 5.0, "excellent": 0.0,
        "rankings": "0% validation errors = rich-result eligibility.",
        "ai_overview": "Valid schema helps AI parse entity relations.",
        "ai_citation": "Validated schema is a strong citation signal."},
    "overall_coverage": {"scale": "0-100", "target": 75.0, "good": 50.0, "excellent": 90.0,
        "rankings": "Schema coverage across target entities feeds rich results.",
        "ai_overview": "Broader entity coverage aids AI understanding.",
        "ai_citation": "Covered entities are more likely to be cited."},

    # ----- Module 14 - Intent & Bounce Predictor -----
    "alignment_score": {"scale": "0-1", "target": 0.75, "good": 0.55, "excellent": 0.90,
        "rankings": "Search-intent alignment is a top ranking factor.",
        "ai_overview": "Intent-matching content satisfies AI follow-up queries.",
        "ai_citation": "Intent-aligned answers are what AI engines surface."},
    "engagement_score": {"scale": "0-1", "target": 0.70, "good": 0.50, "excellent": 0.85,
        "rankings": "Engagement signals (dwell, CTR) inform rankings.",
        "ai_overview": "Engaging pages keep users (and AI) on topic.",
        "ai_citation": "Engagement correlates with citation persistence."},
    "conversion_readiness": {"scale": "0-1", "target": 0.70, "good": 0.45, "excellent": 0.85,
        "rankings": "Ready CTAs convert the traffic rankings bring.",
        "ai_overview": "Clear paths help AI recommend your page for intent.",
        "ai_citation": "Actionable content gets recommended more often."},

    # ----- Module 15 - Content Decay Engine -----
    "freshness_score": {"scale": "0-1", "target": 0.70, "good": 0.45, "excellent": 0.85,
        "rankings": "Freshness is a documented ranking input (recency).",
        "ai_overview": "Fresh, dated content is preferred by AI answers.",
        "ai_citation": "Current data is citable; stale data is risky."},
    "computed_freshness_score": {"scale": "0-1", "target": 0.70, "good": 0.45, "excellent": 0.85,
        "rankings": "Computed freshness drives decay alerts.",
        "ai_overview": "Keep computed freshness high to stay AI-eligible.",
        "ai_citation": "Freshest sources win AI citations."},
    "health_score": {"scale": "0-1", "target": 0.70, "good": 0.50, "excellent": 0.85,
        "rankings": "Content health tracks historical decay patterns.",
        "ai_overview": "Healthy content stays in AI retrieval pools.",
        "ai_citation": "Healthier pages are cited more consistently."},

    # ----- Module 16 - CDN Edge Previewer -----
    "estimated_cache_hit_ratio": {"scale": "0-100", "target": 85.0, "good": 70.0, "excellent": 95.0,
        "rankings": "Cache hit ratio drives TTFB, a CWV input.",
        "ai_overview": "Fast edges keep AI crawlers happy.",
        "ai_citation": "Speed supports overall trust for citation."},
    "overall_security_score": {"scale": "0-1", "target": 0.90, "good": 0.75, "excellent": 1.0,
        "rankings": "Security (HTTPS, headers) is baseline for rankings.",
        "ai_overview": "Secure pages are trusted by AI engines.",
        "ai_citation": "Security supports credibility for citation."},

    # ----- Module 17 - A/B Testing Engine -----
    "meta_description_test_success_rate": {"scale": "0-100", "target": 70.0, "good": 50.0, "excellent": 85.0,
        "rankings": "A/B improvements compound into ranking gains.",
        "ai_overview": "Tested copy is validated for AI visibility.",
        "ai_citation": "Winning variants can be optimized for citation."},

    # ----- Module 18 - Indexing Sentinel -----
    "indexing_readiness_score": {"scale": "0-1", "target": 0.90, "good": 0.75, "excellent": 1.0,
        "rankings": "Indexing readiness is a hard precondition to rank.",
        "ai_overview": "Unindexed pages cannot be in AI answers.",
        "ai_citation": "Indexed, fetchable content is citable."},
    "crawl_efficiency_score": {"scale": "0-1", "target": 0.85, "good": 0.65, "excellent": 0.95,
        "rankings": "Efficient crawl budget = important pages get indexed.",
        "ai_overview": "Clean crawl paths help AI discover content.",
        "ai_citation": "Discovered content is cited content."},
    "error_rate": {"scale": "0-100", "target": 1.0, "good": 5.0, "excellent": 0.0,
        "rankings": "Keep crawl/index errors under 1-2%.",
        "ai_overview": "Error-free pages are reliably eligible.",
        "ai_citation": "Errors suppress citation eligibility."},

    # ----- Module 19 - Localization Sync -----
    "localization_score": {"scale": "0-1", "target": 0.85, "good": 0.65, "excellent": 1.0,
        "rankings": "Localized versions rank in target locales.",
        "ai_overview": "AI engines prefer locale-appropriate content.",
        "ai_citation": "Localized content is cited for locale queries."},
    "implementation_quality": {"scale": "0-1", "target": 0.85, "good": 0.65, "excellent": 1.0,
        "rankings": "hreflang/geo consistency prevents duplicate signals.",
        "ai_overview": "Clean hreflang helps AI pick the right version.",
        "ai_citation": "Correct locale version is preferentially cited."},

    # ----- Module 20 - Digital PR Engine -----
    "pr_readiness_score": {"scale": "0-1", "target": 0.70, "good": 0.45, "excellent": 0.85,
        "rankings": "PR-driven links/mentions feed authority rankings.",
        "ai_overview": "Entity mentions build AI knowledge about you.",
        "ai_citation": "Off-page authority is a top AI-citation factor."},
    "entity_authority_score": {"scale": "0-1", "target": 0.60, "good": 0.40, "excellent": 0.80,
        "rankings": "Entity authority supports knowledge-panel eligibility.",
        "ai_overview": "Known entities are preferred by AI engines.",
        "ai_citation": "Entity recognition precedes citation."},
    "off_page_authority": {"scale": "0-100", "target": 50.0, "good": 30.0, "excellent": 70.0,
        "rankings": "Off-page authority (DR-like band) feeds rankings.",
        "ai_overview": "Authority flows into AI trust scores.",
        "ai_citation": "Higher authority = more citations."},

    # ----- Module 21 - DOM Inspector -----
    "overall_performance_impact_score": {"scale": "0-100", "target": 20.0, "good": 40.0, "excellent": 10.0,
        "rankings": "Lower performance impact = better CWV = ranking support.",
        "ai_overview": "Lean DOM helps AI crawlers parse efficiently.",
        "ai_citation": "Performance supports overall page trust."},
    "layout_complexity_score": {"scale": "0-1", "target": 0.30, "good": 0.50, "excellent": 0.15,
        "rankings": "Low layout complexity reduces CLS risk (CWV signal).",
        "ai_overview": "Stable layouts are preferred by rendering engines.",
        "ai_citation": "Stability supports trust for citation."},
}

# Generic fallbacks (by name substring) for score keys not explicitly listed.
GENERIC_BENCHMARKS = [
    (("readiness", "quality", "authority", "coverage", "depth", "alignment", "consistency",
      "diversity", "compliance", "engagement", "freshness", "health", "equity", "readiness",
      "accessibility", "readiness"), "0-1", 0.70, 0.50, 0.85),
    (("percentage", "rate", "coverage_rate", "compliance_rate", "success_rate"), "0-100", 70.0, 50.0, 90.0),
    (("probability",), "0-1", 0.60, 0.40, 0.80),
    (("risk", "penalty", "error_rate", "impact", "density_percentage"), "0-100", 20.0, 40.0, 10.0),
]

def benchmark_for_score_key(key: str) -> Dict[str, Any]:
    """Return benchmark spec for a score key, with a generic fallback if unknown."""
    k = key.lower()
    if k in SCORE_BENCHMARKS:
        return SCORE_BENCHMARKS[k]
    for key_list, scale, target, good, excellent in GENERIC_BENCHMARKS:
        if any(token in k for token in key_list):
            return {
                "scale": scale,
                "target": target,
                "good": good,
                "excellent": excellent,
                "rankings": "Standard industry benchmark - target the recommended value for competitive rankings.",
                "ai_overview": "Aim for the excellent tier to improve AI Overview eligibility.",
                "ai_citation": "Excellent-tier scores maximize AI citation likelihood.",
            }
    return {
        "scale": "0-1",
        "target": 0.70,
        "good": 0.50,
        "excellent": 0.85,
        "rankings": "Standard benchmark - target 0.70+ for competitive performance.",
        "ai_overview": "Aim for 0.80+ to strengthen AI visibility.",
        "ai_citation": "Higher scores correlate with better AI citation odds.",
    }

def score_level(value, spec):
    """Classify a score value against a benchmark spec -> 'excellent'|'good'|'needs_work'|'fail'."""
    try:
        v = float(value)
    except (TypeError, ValueError):
        return "unknown"
    scale = spec.get("scale", "0-1")
    if scale == "0-100":
        # For risk/penalty style metrics a LOWER value is better.
        lowered = any(t in spec_key_hint(spec) for t in ("risk", "penalty", "error", "impact", "violation"))
        if lowered:
            if v <= float(spec.get("excellent", 10)):
                return "excellent"
            if v <= float(spec.get("good", 40)):
                return "good"
            if v <= float(spec.get("target", 60)):
                return "needs_work"
            return "fail"
        if v >= float(spec.get("excellent", 90)):
            return "excellent"
        if v >= float(spec.get("good", 50)):
            return "good"
        if v >= float(spec.get("target", 30)):
            return "needs_work"
        return "fail"
    else:
        if v >= float(spec.get("excellent", 0.85)):
            return "excellent"
        if v >= float(spec.get("good", 0.50)):
            return "good"
        if v >= float(spec.get("target", 0.30)):
            return "needs_work"
        return "fail"

_spec_hint_cache = {}
def spec_key_hint(spec):
    """Return a token used to infer 'lower is better' for 0-100 metrics."""
    import json as _json
    s = _json.dumps(spec, default=str)
    return s
