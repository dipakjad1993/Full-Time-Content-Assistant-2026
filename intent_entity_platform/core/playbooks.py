"""
Per-module recommendation playbooks for all 21 modules.

Each playbook gives, AFTER the analysis output:
- what_to_do      : concrete actions
- when_to_do      : timing / priority windows
- tools_to_use    : recommended tools and how to use them
- ab_test_plan    : hypothesis, variants, metrics, duration, and how to judge
                    whether the change actually worked

These are transparent, actionable guidance (not fabricated measurements).
"""
from typing import Dict, Any

MODULE_PLAYBOOKS: Dict[str, Dict[str, Any]] = {
    "M01": {
        "what_to_do": [
            "Map every related entity into a content hierarchy document before writing.",
            "Create one 40-60 word direct-answer block immediately after each H2 to target AI Overview extraction.",
            "Add a Knowledge Graph sameAs block (Wikidata + Wikipedia + official profiles) in schema.",
            "Cover uncovered gap entities first - they are the differentiation opportunity.",
            "Build dedicated FAQ blocks for every high-priority PAA question cluster.",
        ],
        "when_to_do": [
            "Before first draft (entity map) - start of the writing sprint.",
            "Schema + sameAs: during development, before staging.",
            "Entity coverage pass: after draft 1, before SEO review.",
        ],
        "tools_to_use": [
            {"tool": "Wikidata API / search", "use": "Verify real entity IDs and sitelinks for sameAs."},
            {"tool": "Google Rich Results Test", "use": "Validate TechArticle/FAQPage schema before publish."},
            {"tool": "Screaming Frog", "use": "Crawl to confirm entity mentions and heading structure."},
            {"tool": "Ahrefs / Semrush SERP", "use": "Cross-check live SERP features for the seed query."},
        ],
        "ab_test_plan": {
            "hypothesis": "Adding gap-entity coverage + direct-answer blocks increases AI Overview presence and organic CTR.",
            "variant_a": "Publish with entity coverage + direct-answer blocks.",
            "variant_b": "Publish with baseline outline (no added entity blocks).",
            "metrics": ["AI Overview presence", "featured snippet impressions", "organic CTR", "rankings"],
            "duration_days": 21,
            "check": "If A shows >=10% relative CTR lift or appears in AI Overviews while B does not, keep the new structure.",
        },
    },
    "M02": {
        "what_to_do": [
            "Front-load the most quotable definition/statistic within the first 60 words.",
            "Add explicit citation triggers: named statistics, expert quotes, and 'according to' phrasing.",
            "Optimize each section for self-contained answers (RAG-friendly).",
            "Match or beat the competitive citation density benchmark (8-25 per 100 words).",
            "Add structured answer blocks (lists, tables, Q&A) at citation hot spots.",
        ],
        "when_to_do": [
            "During drafting (citation triggers).",
            "During revision (front-loading + self-contained chunks).",
            "Weekly GEO monitoring after publish (trend check).",
        ],
        "tools_to_use": [
            {"tool": "ChatGPT / Perplexity / Gemini", "use": "Probe how your page is answered and cited pre/post publish."},
            {"tool": "GEO dashboard", "use": "Track citation visibility across engines over time."},
            {"tool": "Ahrefs content gap", "use": "Find citation-trigger phrases competitors own."},
        ],
        "ab_test_plan": {
            "hypothesis": "Front-loaded statistic + citation triggers increase AI citation rate.",
            "variant_a": "Version with front-loaded stat + 'according to' triggers.",
            "variant_b": "Version with standard intro.",
            "metrics": ["AI citation mentions", "AI Overview inclusion", "referral traffic"],
            "duration_days": 28,
            "check": "If A is cited by AI engines and B is not (or A materially more), adopt the trigger pattern.",
        },
    },
    "M03": {
        "what_to_do": [
            "Normalize heading hierarchy to a single H1 > clean H2 > H3 tree.",
            "Ensure keyword/entity coverage matches the competitive benchmark (0.75+).",
            "Add semantic markup (schema, semantic HTML5) for entities in scope.",
            "Convert underutilized formats (tables, definitions) into structured blocks.",
        ],
        "when_to_do": [
            "Outline review before writing.",
            "Structure audit after first draft.",
            "Pre-publish structure validation (automated).",
        ],
        "tools_to_use": [
            {"tool": "HTML outline extractor", "use": "Verify H1/H2/H3 hierarchy."},
            {"tool": "Schema validator", "use": "Confirm structured data parses."},
            {"tool": "Screaming Frog", "use": "Crawl for heading anomalies site-wide."},
        ],
        "ab_test_plan": {
            "hypothesis": "Restructured heading tree improves indexing of sub-topics and rich-result eligibility.",
            "variant_a": "Restructured headings + extra H2s for uncovered entities.",
            "variant_b": "Existing structure.",
            "metrics": ["indexed sub-topics", "rich-result impressions", "keyword rankings"],
            "duration_days": 14,
            "check": "If A indexes more sub-topics and gains rich results, lock in the structure.",
        },
    },
    "M04": {
        "what_to_do": [
            "Add SME quotes with real names/titles/credentials to raise E-E-A-T signals.",
            "Publish original data or analysis to boost differentiation score to 0.60+.",
            "Include author bio + social profiles + verified credentials.",
            "Back consensus-sensitive claims with authoritative sources.",
            "Show expertise (relevant certifications, case studies, proprietary data).",
        ],
        "when_to_do": [
            "SME sourcing: before drafting (interviews).",
            "Author schema + bios: before publishing.",
            "Original data: once per quarter per cluster.",
        ],
        "tools_to_use": [
            {"tool": "LinkedIn / HARO / Help a B2B Writer", "use": "Find and source expert quotes."},
            {"tool": "Schema.org Person/Organization", "use": "Mark up author/publisher credibility."},
            {"tool": "Google Search Console", "use": "Track E-E-A-T-related engagement signals."},
        ],
        "ab_test_plan": {
            "hypothesis": "Adding SME quotes + author credentials lifts rankings and AI citations.",
            "variant_a": "SME quotes + author schema version.",
            "variant_b": "No SME/author version.",
            "metrics": ["rankings", "AI citations", "organic CTR"],
            "duration_days": 21,
            "check": "If A ranks higher or is cited more, make E-E-A-T enrichment standard.",
        },
    },
    "M05": {
        "what_to_do": [
            "Consolidate cannibalizing pages (redirect or merge overlapping URLs).",
            "Build a flat, entity-based internal link architecture.",
            "Add internal links from high-authority pages to target pages.",
            "Use descriptive anchor text with target keywords.",
            "Distribute link equity toward money/keyword pages.",
        ],
        "when_to_do": [
            "Cannibalization cleanup: before new content launches.",
            "Link architecture: at site migration or quarterly.",
            "New posts: link from 2-3 existing authority pages on publish day.",
        ],
        "tools_to_use": [
            {"tool": "Screaming Frog", "use": "Audit internal links + detect cannibalization."},
            {"tool": "Ahrefs / Semrush", "use": "Rank track + identify overlapping keyword targets."},
            {"tool": "Google Search Console", "use": "Check which cannibalized page actually ranks."},
        ],
        "ab_test_plan": {
            "hypothesis": "Consolidating cannibal pages and adding internal links raises the target page's rankings.",
            "variant_a": "Consolidated + internally linked version.",
            "variant_b": "As-is with cannibalization.",
            "metrics": ["target keyword rankings", "indexed URL count", "organic sessions"],
            "duration_days": 30,
            "check": "If A outranks B and captures the impression share, finalize the consolidation.",
        },
    },
    "M06": {
        "what_to_do": [
            "Replace cliches and filler with concrete, specific sentences.",
            "Add statistics, named entities, and examples to raise specificity.",
            "Reduce AI-likeness penalty by adding human nuance and first-hand detail.",
            "Match competitive readability band (Flesch 60-70 for general topics).",
            "Break long sentences to improve readability metrics.",
        ],
        "when_to_do": [
            "Fluff pass: after first draft, before SEO review.",
            "Readability pass: final edit before publish.",
            "Decay reviews: quarterly refresh of stale sections.",
        ],
        "tools_to_use": [
            {"tool": "Hemingway / Grammarly", "use": "Find filler, passive voice, and readability issues."},
            {"tool": "Copyleaks / GPTZero", "use": "Check AI-likeness before publishing high-value content."},
            {"tool": "Originality.ai", "use": "Verify originality + human-like scoring."},
        ],
        "ab_test_plan": {
            "hypothesis": "De-fluffed, specific content increases dwell time and reduces bounce.",
            "variant_a": "De-fluffed version with concrete examples.",
            "variant_b": "Original draft.",
            "metrics": ["avg dwell time", "bounce rate", "rankings"],
            "duration_days": 14,
            "check": "If A shows longer dwell and better engagement, keep the tightened version.",
        },
    },
    "M07": {
        "what_to_do": [
            "Add credible citations to every factual claim (target 70%+ source coverage).",
            "Prefer primary/official sources over aggregators.",
            "Keep hallucination risk under 10% by removing unsupported claims.",
            "Add numbered source list with links at the end of the page.",
            "Refresh sources that are stale or dead.",
        ],
        "when_to_do": [
            "During drafting: source every claim as you write.",
            "Pre-publish: citation audit pass.",
            "Quarterly: check source liveness (HTTP 200).",
        ],
        "tools_to_use": [
            {"tool": "Google Scholar / official docs", "use": "Find authoritative primary sources."},
            {"tool": "Screenshot archive / Wayback", "use": "Verify source liveness and dates."},
            {"tool": "Claim-level audit spreadsheet", "use": "Track claim -> source coverage."},
        ],
        "ab_test_plan": {
            "hypothesis": "Fully sourced content is cited by AI engines more and ranks higher in YMYL niches.",
            "variant_a": "Fully sourced version (70%+ coverage).",
            "variant_b": "Partially sourced version.",
            "metrics": ["AI citations", "rankings", "referral traffic from sources"],
            "duration_days": 30,
            "check": "If A is cited/ranked more, mandate full sourcing for YMYL content.",
        },
    },
    "M08": {
        "what_to_do": [
            "Add descriptive alt text to all images (target 100% compliance).",
            "Include original data visualizations for key statistics.",
            "Match competitive image-to-text ratio and media counts.",
            "Add video/embed where engagement benchmarks suggest it.",
            "Ensure accessibility (captions, transcripts, contrast).",
        ],
        "when_to_do": [
            "Asset planning: with the outline (before writing).",
            "Media pass: during final editing.",
            "Accessibility audit: pre-publish.",
        ],
        "tools_to_use": [
            {"tool": "Canva / Figma / Flourish", "use": "Create original charts and visualizations."},
            {"tool": "Alt-text checkers", "use": "Validate accessibility compliance."},
            {"tool": "Media asset tracker", "use": "Track image/video usage vs benchmarks."},
        ],
        "ab_test_plan": {
            "hypothesis": "Original data visualizations + full alt text increase engagement and AI citation.",
            "variant_a": "Post with 3+ original visuals + alt text.",
            "variant_b": "Text-only post.",
            "metrics": ["time on page", "image search impressions", "AI citations"],
            "duration_days": 14,
            "check": "If A lifts engagement or citations, make visuals standard.",
        },
    },
    "M09": {
        "what_to_do": [
            "Configure GEO/AEO tracking for the seed query across engines.",
            "Set weekly monitoring of AI Overview presence and citation mentions.",
            "Track citation readiness score and act when it drops below target.",
            "Set alerts for new AI competitors appearing in answers.",
            "Log baseline scores so you can measure the impact of changes.",
        ],
        "when_to_do": [
            "Setup: immediately after publishing.",
            "Weekly: capture snapshot.",
            "Monthly: trend review + action plan.",
        ],
        "tools_to_use": [
            {"tool": "GEO tracking dashboard", "use": "Track AI visibility over time."},
            {"tool": "ChatGPT / Perplexity manual probes", "use": "Spot-check citation behavior."},
            {"tool": "Brand mention alerts", "use": "Detect new AI citations."},
        ],
        "ab_test_plan": {
            "hypothesis": "Continuous GEO tracking identifies winning content changes faster.",
            "variant_a": "Track weekly + respond to dips.",
            "variant_b": "No tracking (baseline).",
            "metrics": ["AI citation trend", "rankings", "organic traffic"],
            "duration_days": 30,
            "check": "If tracked version improves citation trend, keep the monitoring loop.",
        },
    },
    "M10": {
        "what_to_do": [
            "Ensure critical content is server-rendered (SSR) or pre-rendered.",
            "Remove noindex on pages you want indexed.",
            "Fix render-blocking scripts/styles that hurt CWV.",
            "Target Core Web Vitals within 'good' thresholds (LCP < 2.5s, CLS < 0.1).",
            "Verify content availability score stays near 1.0 for key pages.",
        ],
        "when_to_do": [
            "At development: SSR/prerender setup.",
            "Pre-launch: render + CWV audit.",
            "After any front-end change: re-run the simulator.",
        ],
        "tools_to_use": [
            {"tool": "Google Search Console URL Inspection", "use": "See how Google renders your page."},
            {"tool": "Lighthouse / PageSpeed Insights", "use": "Measure CWV + render metrics."},
            {"tool": "Prerender.io / SSR middleware", "use": "Serve rendered HTML to crawlers."},
        ],
        "ab_test_plan": {
            "hypothesis": "SSR/prerendered content indexes faster and ranks better than JS-only.",
            "variant_a": "Prerendered version.",
            "variant_b": "Client-rendered version.",
            "metrics": ["time to index", "CWV scores", "rankings"],
            "duration_days": 14,
            "check": "If A indexes faster and ranks, adopt prerendering for money pages.",
        },
    },
    "M11": {
        "what_to_do": [
            "Restructure content into self-contained chunks (each answerable standalone).",
            "Front-load each chunk with a direct answer (definition-first pattern).",
            "Reduce ambiguous pronouns to raise alignment scores.",
            "Keep chunks within token limits (250-400 tokens) with clean boundaries.",
            "Add explicit context sentences so chunks make sense out of context.",
        ],
        "when_to_do": [
            "During writing: chunk-aware drafting.",
            "After draft: RAG test pass.",
            "Pre-publish: final chunk quality check.",
        ],
        "tools_to_use": [
            {"tool": "RAG test harness", "use": "Retrieve chunks against realistic queries."},
            {"tool": "Embedding playgrounds", "use": "Check chunk-level similarity to queries."},
            {"tool": "Chunking tools (e.g., LangChain)", "use": "Validate chunk segmentation."},
        ],
        "ab_test_plan": {
            "hypothesis": "Self-contained chunking improves RAG retrieval and AI answer quality.",
            "variant_a": "Chunk-optimized version.",
            "variant_b": "Continuous prose version.",
            "metrics": ["retrieval hit rate", "answer quality", "AI citations"],
            "duration_days": 21,
            "check": "If A is retrieved/cited more by AI engines, keep chunk-optimized format.",
        },
    },
    "M12": {
        "what_to_do": [
            "Remove all blacklisted and anti-trope terms from content.",
            "Add required disclaimers in the mandated positions.",
            "Enforce brand voice consistency across all sections.",
            "Maintain trademark rules (correct usage, no genericization).",
            "Re-run compliance check before every publish.",
        ],
        "when_to_do": [
            "During drafting: auto-check for blacklisted terms.",
            "Pre-publish: full compliance gate (blocking).",
            "After brand guideline updates: re-audit all pages.",
        ],
        "tools_to_use": [
            {"tool": "Compliance linter", "use": "Auto-detect violations before publish."},
            {"tool": "Brand guidelines doc", "use": "Source of truth for voice/terms."},
            {"tool": "Legal review workflow", "use": "Approve regulated content."},
        ],
        "ab_test_plan": {
            "hypothesis": "Compliant, on-brand copy performs as well or better than off-brand variants.",
            "variant_a": "Compliant version.",
            "variant_b": "Off-brand (control).",
            "metrics": ["CTR", "conversion", "trust/survey scores"],
            "duration_days": 14,
            "check": "If A performs equal or better, keep compliance gate as a hard requirement.",
        },
    },
    "M13": {
        "what_to_do": [
            "Deploy validated JSON-LD (Article, FAQ, HowTo, Breadcrumb, Organization).",
            "Fix every validation error - target 0% error rate.",
            "Increase schema coverage across target entities to 75%+.",
            "Add sameAs references to official entity IDs.",
            "Test rich-result eligibility in Google Rich Results Test.",
        ],
        "when_to_do": [
            "Development: schema templates.",
            "Pre-publish: validation + rich result test.",
            "Quarterly: re-audit coverage as content grows.",
        ],
        "tools_to_use": [
            {"tool": "Google Rich Results Test", "use": "Validate and preview rich results."},
            {"tool": "Schema.org validator", "use": "Verify JSON-LD correctness."},
            {"tool": "Search Console", "use": "Check schema enhancement reports."},
        ],
        "ab_test_plan": {
            "hypothesis": "Validated schema increases rich-result impressions and CTR.",
            "variant_a": "With validated schema.",
            "variant_b": "Without schema.",
            "metrics": ["rich-result impressions", "CTR", "AI citations"],
            "duration_days": 14,
            "check": "If A gains rich results and higher CTR, apply schema to all eligible pages.",
        },
    },
    "M14": {
        "what_to_do": [
            "Align content format with search intent (informational vs commercial vs transactional).",
            "Match competitor heading patterns and content depth.",
            "Add clear CTAs at natural decision points.",
            "Reduce friction (fast load, clear nav) to lower bounce risk.",
            "Target alignment score 0.75+ and engagement 0.70+.",
        ],
        "when_to_do": [
            "Before writing: intent analysis.",
            "Post-publish week 1-2: bounce/engagement check.",
            "Monthly: re-validate intent alignment as SERPs shift.",
        ],
        "tools_to_use": [
            {"tool": "Google Analytics 4", "use": "Measure bounce, engagement time, conversions."},
            {"tool": "SERP intent audit", "use": "Confirm dominant intent for the query."},
            {"tool": "Hotjar / Microsoft Clarity", "use": "Observe behavior to find friction."},
        ],
        "ab_test_plan": {
            "hypothesis": "Intent-aligned, CTA-rich page reduces bounce and improves conversions.",
            "variant_a": "Intent-aligned with clear CTAs.",
            "variant_b": "Generic version.",
            "metrics": ["bounce rate", "engagement time", "conversions"],
            "duration_days": 14,
            "check": "If A lowers bounce and lifts conversions, lock in the intent-aligned template.",
        },
    },
    "M15": {
        "what_to_do": [
            "Refresh decayed content to raise freshness score to 0.70+.",
            "Update statistics and dated claims; add 'last updated' dates.",
            "Re-optimize underperforming pages against current competitors.",
            "Redirect or consolidate irrecoverably decayed pages.",
            "Set a refresh cadence per content cluster based on decay rate.",
        ],
        "when_to_do": [
            "When freshness score drops below 0.45.",
            "Quarterly: decay audit across the cluster.",
            "Before competitor updates make your content stale.",
        ],
        "tools_to_use": [
            {"tool": "Wayback Machine CDX", "use": "See historical snapshots and change signals."},
            {"tool": "Search Console", "use": "Find impression/CTR drops signaling decay."},
            {"tool": "Freshness calendar", "use": "Schedule refreshes per cluster."},
        ],
        "ab_test_plan": {
            "hypothesis": "Refreshing decayed content recovers rankings and traffic.",
            "variant_a": "Refreshed version (fresh stats + updates).",
            "variant_b": "Unchanged control.",
            "metrics": ["rankings", "organic traffic", "impressions"],
            "duration_days": 21,
            "check": "If A recovers more than B, prioritize refresh for that cluster.",
        },
    },
    "M16": {
        "what_to_do": [
            "Deploy edge workers for caching, headers, and dynamic pre-render.",
            "Verify security headers (HSTS, CSP, X-Frame-Options) are set.",
            "Raise cache hit ratio to 85%+ for TTFB improvements.",
            "Add pre-render simulation for SPA-critical content.",
            "Test edge config in staging before rollout.",
        ],
        "when_to_do": [
            "At deployment: edge config + headers.",
            "After any caching rule change: re-test.",
            "Monthly: performance regression check.",
        ],
        "tools_to_use": [
            {"tool": "Cloudflare Workers / Edge Functions", "use": "Implement caching and header rules."},
            {"tool": "Security header scanners", "use": "Validate header configuration."},
            {"tool": "CDN cache analyzers", "use": "Measure hit ratio and TTFB."},
        ],
        "ab_test_plan": {
            "hypothesis": "Edge caching + pre-render improves TTFB and CWV.",
            "variant_a": "With edge worker + pre-render.",
            "variant_b": "No edge rules.",
            "metrics": ["TTFB", "LCP", "cache hit ratio"],
            "duration_days": 7,
            "check": "If A improves metrics materially, keep the edge configuration.",
        },
    },
    "M17": {
        "what_to_do": [
            "Run statistical A/B tests on titles, meta descriptions, CTAs, and structure.",
            "Use the recommended sample size and duration before concluding.",
            "Test one variable at a time for clean attribution.",
            "Set rollback guardrails (stop if variant degrades key metrics).",
            "Automate reporting so winners ship automatically.",
        ],
        "when_to_do": [
            "Before major rewrite: test the proposed variant.",
            "Continuously: meta description / title experiments.",
            "Quarterly: structural experiments.",
        ],
        "tools_to_use": [
            {"tool": "Google Optimize (legacy) / Optimizely / VWO", "use": "Run and analyze experiments."},
            {"tool": "Statistically sound A/B calculator", "use": "Compute sample size/duration."},
            {"tool": "Search Console + GA4", "use": "Measure organic CTR and engagement."},
        ],
        "ab_test_plan": {
            "hypothesis": "Statistical testing identifies winning copy that lifts organic CTR.",
            "variant_a": "Challenger title/meta.",
            "variant_b": "Current title/meta.",
            "metrics": ["organic CTR", "impressions", "rankings"],
            "duration_days": 14,
            "check": "Ship A only if the lift is statistically significant (p<0.05) and stable over the full window.",
        },
    },
    "M18": {
        "what_to_do": [
            "Fix indexation blockers (noindex, canonical errors, crawl traps).",
            "Keep crawl error rate under 1-2%.",
            "Submit priority pages via Indexing API / Search Console.",
            "Optimize robots.txt + sitemap for clean crawl paths.",
            "Monitor time-to-first-index and alert on anomalies.",
        ],
        "when_to_do": [
            "On every publish: verify indexation within 24-72h.",
            "Weekly: crawl/error report review.",
            "After site changes: re-validate indexing config.",
        ],
        "tools_to_use": [
            {"tool": "Google Search Console", "use": "URL inspection + sitemaps + coverage report."},
            {"tool": "Indexing API", "use": "Speed up indexing of fresh, high-value pages."},
            {"tool": "Screaming Frog", "use": "Detect noindex/canonical/robots issues."},
        ],
        "ab_test_plan": {
            "hypothesis": "Indexing-API submission reduces time-to-first-index for new pages.",
            "variant_a": "Submit via Indexing API on publish.",
            "variant_b": "Rely on organic crawling.",
            "metrics": ["time to first index", "indexed URL ratio"],
            "duration_days": 21,
            "check": "If A indexes faster and more reliably, make API submission standard.",
        },
    },
    "M19": {
        "what_to_do": [
            "Implement correct hreflang tags with reciprocal links.",
            "Transcreate (not translate) content for each target locale.",
            "Localize schema, currency, dates, and regional references.",
            "Set up locale-specific sitemaps and Search Console properties.",
            "Monitor per-locale rankings and avoid duplicate-signal issues.",
        ],
        "when_to_do": [
            "At internationalization: hreflang + locale sitemaps.",
            "Per-locale content launch: transcreation pass.",
            "Quarterly: per-locale rank audit.",
        ],
        "tools_to_use": [
            {"tool": "hreflang validators", "use": "Verify reciprocal tag correctness."},
            {"tool": "Locale PIM / CMS locale fields", "use": "Manage translated assets."},
            {"tool": "Per-locale Search Console", "use": "Track performance per country/language."},
        ],
        "ab_test_plan": {
            "hypothesis": "Transcreated (vs machine-translated) content ranks higher in target locales.",
            "variant_a": "Human transcreation.",
            "variant_b": "Machine translation.",
            "metrics": ["locale rankings", "locale CTR", "locale conversions"],
            "duration_days": 30,
            "check": "If A outperforms B in the target locale, fund transcreation for that market.",
        },
    },
    "M20": {
        "what_to_do": [
            "Pitch original data/studies to relevant outlets from live research.",
            "Target verified entity themes and competitor backlink patterns.",
            "Build author/E-E-A-T trust with verified credentials and bylines.",
            "Create data visualization assets that are shareable and linkable.",
            "Track PR-readiness score and target 0.70+ before outreach.",
        ],
        "when_to_do": [
            "Original data: before pitch campaigns.",
            "Outreach: when PR-readiness >= 0.70.",
            "Quarterly: refresh outlet/entity targets from live search.",
        ],
        "tools_to_use": [
            {"tool": "HARO / Qwoted / Featured", "use": "Get quoted as a source."},
            {"tool": "Muck Rack / Cision", "use": "Manage media lists and outreach."},
            {"tool": "Ahrefs content explorer", "use": "Find entity themes + backlink patterns."},
        ],
        "ab_test_plan": {
            "hypothesis": "Original-data assets earn more backlinks and citations than opinion pieces.",
            "variant_a": "Original study/data asset + outreach.",
            "variant_b": "Opinion/thought-leadership piece.",
            "metrics": ["backlinks earned", "AI citations", "referral traffic"],
            "duration_days": 45,
            "check": "If A earns more links/citations, double down on data-driven PR.",
        },
    },
    "M21": {
        "what_to_do": [
            "Reduce DOM size and nesting depth to lower rendering complexity.",
            "Move heavy scripts to async/defer to cut render-blocking.",
            "Fix layout-shift risks (reserve space for media).",
            "Inline critical CSS / reduce style weight.",
            "Target performance impact score under 20.",
        ],
        "when_to_do": [
            "Development: build within DOM budget.",
            "Pre-launch: DOM/perf audit.",
            "After template changes: re-inspect DOM complexity.",
        ],
        "tools_to_use": [
            {"tool": "Lighthouse DOM audit", "use": "Measure DOM size and JS weight."},
            {"tool": "WebPageTest", "use": "Assess rendering and layout stability."},
            {"tool": "Bundle analyzers", "use": "Trim JS/CSS payloads."},
        ],
        "ab_test_plan": {
            "hypothesis": "Leaner DOM improves CWV and crawl efficiency.",
            "variant_a": "Optimized template (fewer nodes, async JS).",
            "variant_b": "Legacy template.",
            "metrics": ["LCP", "CLS", "DOM load", "rankings"],
            "duration_days": 14,
            "check": "If A shows better CWV and indexation, adopt the optimized template.",
        },
    },
}

def get_playbook(module_id: str) -> Dict[str, Any]:
    """Return the playbook for a module, or a generic fallback playbook."""
    return MODULE_PLAYBOOKS.get(module_id, {
        "what_to_do": [
            "Review this module's detailed analysis and address every flagged issue in priority order.",
            "Implement the recommended actions and re-run the analysis to confirm improvement.",
        ],
        "when_to_do": [
            "Before publishing new or updated content.",
            "On a regular review cadence (monthly/quarterly).",
        ],
        "tools_to_use": [
            {"tool": "This platform", "use": "Re-run the 21-module analysis to measure improvement."},
            {"tool": "Search Console / analytics", "use": "Verify ranking and engagement outcomes."},
        ],
        "ab_test_plan": {
            "hypothesis": "Addressing this module's recommendations improves rankings and AI visibility.",
            "variant_a": "Content with this module's fixes applied.",
            "variant_b": "Original content.",
            "metrics": ["rankings", "organic traffic", "AI citations"],
            "duration_days": 21,
            "check": "If the fixed variant outperforms the control, keep the changes.",
        },
    })
