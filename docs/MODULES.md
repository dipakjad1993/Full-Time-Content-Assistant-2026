# Module Reference (M01–M22)

Each module returns the `ModuleResult` contract (`module`, `module_name`, `status`) plus stat boxes, priority-tagged recommendations (CRITICAL/HIGH/MEDIUM/LOW), ordered implementation steps, placement guidance, and a collapsible deep-dive. Live fields are measured this run; estimates carry `method_note: heuristic estimate`.

## M01 — SERP & Knowledge Graph
Live SERP features, ranking results, entity graph, knowledge-panel readiness. Key outputs: `live_serp_results`, `serp_features`, `paa_clusters`, `entity_graph`, `topical_authority_score`, `knowledge_panel_ready`, `featured_snippet_ready`, `ai_overview_ready`. Live: DuckDuckGo SERP + PAA, Wikidata Q-ID (`wikidata_verified`).

## M02 — GEO & AEO Simulator
Per-engine readiness (AI Overview, ChatGPT, Perplexity, Gemini). Key outputs: `geo_readiness_score`, `engine_specific_strategies`, `answer_triggers`, `citation_gap_analysis`, `statistic_density`. Heuristic estimate (labeled) over live page signals.

## M03 — Semantic Structure & Schema
Heading hierarchy, semantic HTML, 40–60-word answer-block extractability. Key outputs: `heading_hierarchy_score`, `direct_answer_blocks`, `schema_coverage_analysis`, `recommended_schemas`. Live: real H1/H2/word/schema signals.

## M04 — E-E-A-T Gap Profiler
Experience/Expertise/Authoritativeness/Trust gaps + information-gain ranking. Key outputs: `eeat_scores`, `weakest_signal`, `information_gain_analysis`, `gap_priority_matrix`. Heuristic estimate (labeled).

## M05 — Internal Link & Cannibalization
Cannibalization status, link blueprint, equity scoring. Key outputs: `cannibalization_detection`, `link_plan`, `link_quality_score`, `anchor_text_analysis`. Live: `urls_checked`, `reachable_200` link-health checks.

## M06 — Fluff & Cliché Decoder
Filler, clichés, AI tropes, passive voice, readability depth. Key outputs: `overall_quality_score`, `issue_density_per_100_words`, `lexical_diversity`, `rewrite_recommendations`. Live: real text statistics.

## M07 — Citation & Source Verifier
Claims/statistics extraction, source credibility, hallucination risk. Key outputs: `hallucination_risk_score`, `stat_source_coverage_rate`, `fact_check_results`. Live: `urls_checked`, `reachable_count`.

## M08 — Multimodal Asset Blueprint
Image/video/chart/table/infographic/calculator plan + alt-text pipeline. Live: image count/alt audit; `/api/multimodal_audit` adds YouTube/transcript + WebP/AVIF scoring.

## M09 — GEO Tracker
Live SERP snapshot + tracking/alert configuration, persisted to SQLite history (`tracker_snapshot`) for longitudinal charts. Key outputs: `live_serp_snapshot`, `monitoring_dashboard`, `alert_system`.

## M10 — CSR Simulator
Bot-visible rendering estimate for Googlebot/Bingbot/GPTBot/PerplexityBot + CWV risk. Heuristic estimate (labeled; no headless render). Set `PSI_API_KEY` for measured vitals via `/api/pagespeed`.

## M11 — RAG Tester
Real chunking, query alignment, standalone-context tests. Key outputs: `overall_rag_score`, `chunk_analysis`, `standalone_ready_count`, `embedding_readiness`.

## M12 — Brand Compliance Engine
Regulated claims, trademarks, voice, disclaimers, legal risk. Key outputs: `compliance_score`, `critical_violations`, `disclaimer_injection`, `terminology_consistency`.

## M13 — Schema Payload Generator
Copy-ready JSON-LD (Article, FAQ, HowTo, Product, Author, Publisher, Breadcrumb, ItemList, Video, Organization) with validation + per-engine coverage map.

## M14 — Intent & Bounce Predictor
Intent classification, bounce-risk score, above-the-fold and scanability fixes. Heuristic estimate (labeled), grounded in live depth/read-time signals.

## M15 — Content Decay Engine
Freshness score, decay indicators, section-level refresh brief. Live: Wayback CDX snapshots (retries + backoff), date/year mentions.

## M16 — CDN Edge Previewer
Provider detection, edge-worker snippet, header inspection, pre-render simulation, deploy guide. Live: real response headers (`not_detected` when unconfirmed).

## M17 — A/B Testing Engine
Experiment designs with real power math (`minimum_sample_size`, `confidence_level`, `test_duration_days`), monitoring + rollback guardrails. Inputs are defaults (labeled), math is real.

## M18 — Indexing Sentinel
Indexing readiness, robots/sitemap checks, crawl budget, IndexNow payload. Live: robots.txt fetch, HTTP status, sitemap detection. v3.0 adds AI-crawler completeness: 9 bots (retrieval vs training split), live `llms.txt` + `ai.txt`, meta `noai` (`ai_crawler_completeness`).

## M19 — Localization Sync
Locale detection, hreflang set, entity mapping, translation priorities. The single wired engine (`LocalizationSyncEngine`); honest `NO_URL_DATA` without a fetched page.

## M20 — Digital PR Engine
Pitch angles, outlet discovery, author-trust verification, Knowledge-Graph alignment. Live: outlets covering the topic + Wikidata lookup; `/api/offsite_authority` adds Wikipedia gap + Reddit/Quora/YouTube/podcast + tier-1 likelihood.

## M21 — DOM Inspector
DOM size/depth, resources, layout-shift risk, weight estimates, prioritized optimizations. Live: image/script/lazy-load/dimension audits.

## M22 — Live LLM Citation Tester
Fixed prompt set per entity across OpenAI/Anthropic/Gemini/Perplexity (2 prompts/provider cost guard): transcripts, cited URLs, sentiment, share-of-voice — persisted to SQLite (`m22`) for trend charts. Without provider keys: labeled `honest_mock`, never sold as measured. Full runs: `POST /api/llm_test`; history: `GET /api/llm_history?key=<entity>`; nightly: `scripts/nightly_tracker_cron.py`.
