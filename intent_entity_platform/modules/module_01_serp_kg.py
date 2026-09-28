"""
Module 1: Real-Time SERP & Knowledge Graph Parsing
Analyzes the live search landscape for the target query across traditional SERPs and AI modules.
"""
import re
import hashlib
import json
import urllib.parse
from typing import List, Dict, Any, Optional
from ..utils.text_analytics import (
    extract_keyphrases, extract_entities_simple, tokenize_words,
    cosine_similarity, tf_idf_vectorize, text_statistics
)
from ..utils.web_data import web_search as _real_web_search, search_wikidata, _open, _read_body


class SERPKnowledgeGraphParser:
    """Module 1: Real-Time SERP & Knowledge Graph Parsing"""

    def __init__(self):
        self.module_id = "M01"
        self.module_name = "Real-Time SERP & Knowledge Graph Parsing"

    def analyze(self, inputs: Dict[str, Any], existing_content: Optional[str] = None) -> Dict[str, Any]:
        """Full SERP and entity analysis pipeline."""
        seed_phrase = inputs.get("seed_phrase", "")
        primary_entity = inputs.get("primary_entity", "")
        locale = inputs.get("locale", "en-US")
        device = inputs.get("device", "desktop")
        secondary_keywords = inputs.get("secondary_keywords", [])
        competitor_content = list(inputs.get("competitor_content", []) or [])
        url_data = inputs.get("_url_data", None)

        # REAL live SERP retrieval
        live_serp = _real_web_search(seed_phrase, 10)
        serp_results = live_serp.get("results", [])
        live_serp_status = live_serp.get("ok", False)
        live_serp_error = live_serp.get("error", None)

        # Derive competitor content from the real SERP (titles + snippets)
        for r in serp_results:
            comp = (r.get("title", "") + " " + r.get("snippet", "")).strip()
            if comp:
                competitor_content.append(comp)

        entity_graph = self._build_entity_graph(seed_phrase, primary_entity)
        serp_features = self._analyze_serp_features(seed_phrase, locale, device, serp_results)
        paa_clusters = self._cluster_paa(seed_phrase, competitor_content, serp_results)
        entity_coverage = self._assess_entity_coverage(entity_graph, competitor_content)
        topical_authority = self._score_topical_authority(entity_graph, competitor_content)
        serp_format_analysis = self._analyze_serp_formats(competitor_content)
        keyword_landscape = self._build_keyword_landscape(seed_phrase, secondary_keywords, competitor_content)

        url_analysis = self._analyze_url_content(url_data, seed_phrase, primary_entity, entity_graph) if url_data else None

        result = {
            "module": self.module_id,
            "module_name": self.module_name,
            "live_serp_results": serp_results,
            "live_serp_status": "LIVE" if live_serp_status else "UNAVAILABLE",
            "live_serp_backend": live_serp.get("backend", "unknown"),
            "live_serp_error": live_serp_error,
            "entity_graph": entity_graph,
            "serp_features": serp_features,
            "paa_clusters": paa_clusters,
            "entity_coverage": entity_coverage,
            "topical_authority_score": topical_authority,
            "serp_format_analysis": serp_format_analysis,
            "keyword_landscape": keyword_landscape,
            "competitive_gap_summary": self._generate_gap_summary(entity_coverage, paa_clusters),
            "recommendations": self._generate_recommendations(entity_graph, serp_features, paa_clusters),
            "implementation_steps": self._generate_implementation_steps(entity_graph, serp_features, paa_clusters, entity_coverage),
            "where_to_add": self._generate_where_to_add(entity_graph, serp_features),
            "detailed_analysis": self._generate_detailed_analysis(entity_graph, serp_features, paa_clusters, entity_coverage, topical_authority, keyword_landscape)
        }

        if url_data and url_analysis:
            result["url_analysis"] = url_analysis
            result["recommendations"] = self._merge_url_recommendations(result["recommendations"], url_analysis)
            result["detailed_analysis"]["url_content_insights"] = url_analysis.get("content_insights", {})

        return result

    def _analyze_url_content(self, url_data: Dict, seed_phrase: str, primary_entity: str, entity_graph: Dict) -> Dict[str, Any]:
        """Deep analysis of actual URL content for SERP and Knowledge Graph alignment."""
        page_text = url_data.get("page_text", "")
        title = url_data.get("title", "")
        meta_desc = url_data.get("meta_description", "")
        h1 = url_data.get("h1", "")
        h2s = url_data.get("h2s", [])
        word_count = url_data.get("word_count", 0)
        link_count = url_data.get("link_count", 0)
        image_count = url_data.get("image_count", 0)
        images = url_data.get("images", [])
        links = url_data.get("links", [])
        has_schema = url_data.get("has_schema", False)
        url = url_data.get("url", "")

        title_length = len(title)
        h1_length = len(h1)
        meta_desc_length = len(meta_desc)

        entity_in_title = primary_entity.lower() in title.lower() if primary_entity else False
        entity_in_h1 = primary_entity.lower() in h1.lower() if primary_entity else False
        entity_in_meta = primary_entity.lower() in meta_desc.lower() if primary_entity else False
        seed_in_title = seed_phrase.lower() in title.lower() if seed_phrase else False

        related_entities = entity_graph.get("related_entities", [])
        entity_mentions_in_text = 0
        for ent in related_entities:
            ent_name = ent.get("name", "")
            if ent_name:
                entity_mentions_in_text += page_text.lower().count(ent_name.lower())

        title_entity_score = sum([entity_in_title, entity_in_h1, entity_in_meta, seed_in_title]) / 4.0

        avg_h2_length = 0
        h2_keyword_coverage = 0
        if h2s:
            h2_lengths = [len(h) for h in h2s]
            avg_h2_length = sum(h2_lengths) / len(h2_lengths)
            seed_words = set(tokenize_words(seed_phrase))
            h2_keyword_coverage = sum(1 for h in h2s if any(w.lower() in h.lower() for w in seed_words)) / max(1, len(h2s))

        internal_links = [l for l in links if url and url.split("//")[0] + "//" in l and url.split("//")[1].split("/")[0] in l]
        external_links = [l for l in links if l not in internal_links]

        schema_potential = 0.0
        schema_types_recommended = []
        if not has_schema:
            schema_types_recommended = ["TechArticle", "FAQPage", "BreadcrumbList"]
            schema_potential = 0.5
        else:
            schema_types_recommended = ["Review existing schema for completeness"]
            schema_potential = 0.8

        knowledge_panel_score = min(1.0, (entity_in_title * 0.3 + entity_in_h1 * 0.25 + entity_in_meta * 0.15 + entity_mentions_in_text * 0.02 + title_entity_score * 0.15 + (0.15 if has_schema else 0)))

        serp_feature_readiness = {
            "ai_overview_ready": word_count >= 2000 and entity_mentions_in_text >= 5 and meta_desc_length > 0,
            "featured_snippet_ready": h1_length > 0 and len(h2s) >= 3 and word_count >= 1500,
            "knowledge_panel_ready": knowledge_panel_score > 0.6 and has_schema,
            "paa_ready": len(h2s) >= 5 and word_count >= 2000
        }

        content_issues = []
        if title_length < 30:
            content_issues.append(f"Title too short ({title_length} chars). (General industry guidance, unverified): 50-60 chars is a common SERP display length.")
        if title_length > 70:
            content_issues.append(f"Title too long ({title_length} chars). Will be truncated in SERPs. Optimal: 50-60 chars.")
        if h1_length == 0:
            content_issues.append("No H1 heading detected. Every page needs exactly one H1.")
        if h1_length > 70:
            content_issues.append(f"H1 too long ({h1_length} chars). Consider shorter H1 for featured snippet capture.")
        if meta_desc_length < 120:
            content_issues.append(f"Meta description too short ({meta_desc_length} chars). Optimal: 150-160 chars.")
        if meta_desc_length > 160:
            content_issues.append(f"Meta description too long ({meta_desc_length} chars). Will be truncated. Optimal: 150-160 chars.")
        if len(h2s) < 3:
            content_issues.append(f"Only {len(h2s)} H2 headings found. (General industry guidance, unverified): Competitive pages average 8-12 H2 sections.")
        if word_count < 1500:
            content_issues.append(f"Word count {word_count} is below minimum. (General industry guidance, unverified): Competitive niches often target 2000-4000 words.")
        if not has_schema:
            content_issues.append("No structured data detected. Add TechArticle, FAQPage, and BreadcrumbList schema.")
        if entity_mentions_in_text < 3:
            content_issues.append(f"Primary entity mentioned only {entity_mentions_in_text} times. (General industry guidance, unverified): Aim for 8-12 natural mentions.")

        return {
            "url": url,
            "page_title": title,
            "title_length": title_length,
            "title_length_benchmark": "(General industry guidance, unverified): 50-60 chars is a common target",
            "h1_heading": h1,
            "h1_length": h1_length,
            "meta_description": meta_desc[:200] + "..." if len(meta_desc) > 200 else meta_desc,
            "meta_description_length": meta_desc_length,
            "word_count": word_count,
            "word_count_benchmark": "(General industry guidance, unverified): Competitive pages often run 2000-4000 words",
            "h2_count": len(h2s),
            "h2_count_benchmark": "(General industry guidance, unverified): Top-ranking pages often have 8-12 H2 sections",
            "avg_h2_length": round(avg_h2_length, 1),
            "link_count": link_count,
            "internal_links": len(internal_links),
            "external_links": len(external_links),
            "link_benchmark": "(General industry guidance, unverified): 5-10 internal, 3-5 external links per page",
            "image_count": image_count,
            "image_benchmark": "(General industry guidance, unverified): 5-10 images with descriptive alt text per page",
            "images_without_alt": sum(1 for img in images if not img.get("alt", "").strip()),
            "has_schema_markup": has_schema,
            "entity_alignment": {
                "entity_in_title": entity_in_title,
                "entity_in_h1": entity_in_h1,
                "entity_in_meta_description": entity_in_meta,
                "seed_in_title": seed_in_title,
                "entity_mentions_in_text": entity_mentions_in_text,
                "entity_mention_benchmark": "(General industry guidance, unverified): 8-12 natural mentions is a common recommendation",
                "alignment_score": round(title_entity_score, 3)
            },
            "knowledge_panel_potential": {
                "score": round(knowledge_panel_score, 3),
                "factors": {
                    "entity_in_title": entity_in_title,
                    "entity_in_h1": entity_in_h1,
                    "entity_in_meta": entity_in_meta,
                    "schema_present": has_schema,
                    "entity_mentions": entity_mentions_in_text
                },
                "recommendation": "Add sameAs links to Wikidata, Wikipedia, and official profiles to trigger Knowledge Panel"
            },
            "serp_feature_readiness": serp_feature_readiness,
            "h2_keyword_coverage": round(h2_keyword_coverage, 3),
            "content_issues": content_issues,
            "content_issues_count": len(content_issues),
            "content_quality_tier": (
                "EXCELLENT - Page is well-optimized for SERP features" if len(content_issues) == 0 else
                "GOOD - Minor optimizations needed" if len(content_issues) <= 2 else
                "NEEDS_WORK - Multiple optimizations required" if len(content_issues) <= 5 else
                "CRITICAL - Significant restructuring needed"
            ),
            "specific_recommendations": self._generate_url_specific_recommendations(url_data, entity_graph, seed_phrase)
        }

    def _generate_url_specific_recommendations(self, url_data: Dict, entity_graph: Dict, seed_phrase: str) -> List[Dict[str, str]]:
        """Generate specific recommendations based on actual URL content."""
        recs = []
        title = url_data.get("title", "")
        h1 = url_data.get("h1", "")
        h2s = url_data.get("h2s", [])
        word_count = url_data.get("word_count", 0)
        has_schema = url_data.get("has_schema", False)
        links = url_data.get("links", [])
        images = url_data.get("images", [])

        title_length = len(title)
        if title_length < 30:
            recs.append({
                "priority": "HIGH",
                "action": f"Expand title from {title_length} to 50-60 characters",
                "detail": f"Current title '{title}' is too short for optimal SERP display. Add primary entity and value proposition."
            })
        elif title_length > 70:
            recs.append({
                "priority": "HIGH",
                "action": f"Shorten title from {title_length} to under 60 characters",
                "detail": f"Current title will be truncated in search results. Keep primary keyword within first 60 chars."
            })

        if len(h2s) < 5:
            recs.append({
                "priority": "HIGH",
                "action": f"Add {5 - len(h2s)}+ more H2 sections for comprehensive coverage",
                "detail": f"Only {len(h2s)} H2s found. (General industry guidance, unverified): Competitive pages average 8-12 H2 sections for topical depth."
            })

        if word_count < 2000:
            recs.append({
                "priority": "HIGH",
                "action": f"Expand content from {word_count} to 2000-4000 words",
                "detail": f"Current word count is below competitive threshold. Add depth to each H2 section."
            })

        if not has_schema:
            recs.append({
                "priority": "HIGH",
                "action": "Implement JSON-LD structured data (TechArticle, FAQPage, BreadcrumbList)",
                "detail": "No schema detected. (General industry guidance, unverified): pages with structured data see 25-40% higher rich snippet appearance rates."
            })

        images_without_alt = sum(1 for img in images if not img.get("alt", "").strip())
        if images_without_alt > 0:
            recs.append({
                "priority": "MEDIUM",
                "action": f"Add descriptive alt text to {images_without_alt} images",
                "detail": "Images without alt text are invisible to search engines and accessibility tools."
            })

        entity_graph_count = entity_graph.get("entity_count", 0)
        related_entities = entity_graph.get("related_entities", [])
        top_entities = [e["name"] for e in related_entities[:5]]
        recs.append({
            "priority": "MEDIUM",
            "action": f"Include references to {len(related_entities)} related entities throughout content",
            "detail": f"Top entities to reference: {', '.join(top_entities[:3])}. Aim for 2+ mentions each."
        })

        return recs

    def _merge_url_recommendations(self, existing_recs: List[Dict], url_analysis: Dict) -> List[Dict[str, str]]:
        """Merge URL-specific recommendations with existing recommendations."""
        url_recs = url_analysis.get("specific_recommendations", [])
        merged = list(existing_recs)
        for url_rec in url_recs:
            already_covered = False
            for existing in merged:
                if url_rec["action"][:30] in existing.get("action", ""):
                    already_covered = True
                    break
            if not already_covered:
                merged.append(url_rec)
        return merged

    def _build_entity_graph(self, seed_phrase: str, primary_entity: str) -> Dict[str, Any]:
        """Build a comprehensive entity graph from seed phrase and primary entity."""
        seed_words = set(tokenize_words(seed_phrase))
        entity_words = set(tokenize_words(primary_entity))
        core_entities = [
            {"name": primary_entity, "type": "primary", "relevance": 1.0},
            {"name": seed_phrase, "type": "query", "relevance": 1.0}
        ]
        related_entities = self._infer_related_entities(seed_phrase, primary_entity)
        entity_hierarchy = self._build_entity_hierarchy(primary_entity, related_entities)
        entity_relationships = self._map_entity_relationships(core_entities + related_entities)
        knowledge_graph_uris = self._suggest_knowledge_graph_uris(primary_entity, seed_phrase)
        return {
            "core_entities": core_entities,
            "related_entities": related_entities,
            "entity_hierarchy": entity_hierarchy,
            "entity_relationships": entity_relationships,
            "knowledge_graph_uris": knowledge_graph_uris,
            "entity_count": len(core_entities) + len(related_entities),
            "entity_density_score": self._calculate_entity_density(seed_phrase, related_entities)
        }

    def _infer_related_entities(self, seed_phrase: str, primary_entity: str) -> List[Dict[str, Any]]:
        """Infer related entities based on seed phrase analysis."""
        entity = primary_entity.lower()
        seed = seed_phrase.lower()
        related = []
        domain_entities = {
            "software": ["SaaS", "cloud computing", "API", "integration", "platform", "dashboard", "analytics", "automation", "workflow", "deployment"],
            "saas": ["subscription", "cloud", "multi-tenant", "API", "microservices", "scalability", "uptime", "SLA", "onboarding", "retention"],
            "accounting": ["financial reporting", "bookkeeping", "accounts payable", "accounts receivable", "general ledger", "tax compliance", "audit", "reconciliation", "budgeting", "forecasting"],
            "enterprise": ["B2B", "CRM", "ERP", "compliance", "governance", "data security", "SOC 2", "GDPR", "SSO", "RBAC"],
            "multi-currency": ["forex", "exchange rate", "currency conversion", "FX hedging", "foreign exchange", "treasury management", "multi-entity", "consolidation", "transfer pricing", "intercompany"],
            "finance": ["FP&A", "treasury", "audit", "compliance", "reporting", "budgeting", "forecasting", "variance analysis", "financial modeling", "valuation"],
            "marketing": ["SEO", "content marketing", " PPC", "conversion rate", "analytics", "attribution", "brand awareness", "lead generation", "funnel optimization", "A/B testing"],
            "technology": ["AI", "machine learning", "automation", "cloud", "API", "microservices", "DevOps", "CI/CD", "containerization", "orchestration"],
            "healthcare": ["HIPAA", "patient data", "EHR", "clinical trials", "FDA", "telemedicine", "diagnostic", "pharmaceutical", "medical devices", "compliance"],
            "legal": ["compliance", "regulation", "GDPR", "contract management", "intellectual property", "liability", "jurisdiction", "arbitration", "litigation", "due diligence"],
        }
        for domain_key, entities in domain_entities.items():
            if domain_key in seed or domain_key in entity:
                for ent in entities:
                    relevance = 0.8 if ent.lower() in seed or ent.lower() in entity else 0.5
                    related.append({
                        "name": ent,
                        "type": "domain_specific",
                        "relevance": relevance,
                        "source": f"inferred_from_{domain_key}"
                    })
        topic_words = set(tokenize_words(seed_phrase)) - {"the", "a", "an", "is", "are", "for", "and", "or", "of", "in", "to", "with"}
        for word in topic_words:
            if len(word) > 3 and not any(r["name"].lower() == word for r in related):
                related.append({
                    "name": word.title(),
                    "type": "keyword_derived",
                    "relevance": 0.6,
                    "source": "seed_phrase_extraction"
                })
        return related[:30]

    def _build_entity_hierarchy(self, primary_entity: str, related: List[Dict]) -> Dict[str, Any]:
        """Build a hierarchical structure of entity relationships."""
        return {
            "level_0_root": {"entity": primary_entity, "role": "primary_topic"},
            "level_1支柱": [
                {"entity": r["name"], "role": "supporting_concept", "relevance": r["relevance"]}
                for r in related if r["relevance"] >= 0.7
            ][:5],
            "level_2细节": [
                {"entity": r["name"], "role": "detailed_concept", "relevance": r["relevance"]}
                for r in related if 0.4 <= r["relevance"] < 0.7
            ][:10],
            "level_3边缘": [
                {"entity": r["name"], "role": "peripheral_concept", "relevance": r["relevance"]}
                for r in related if r["relevance"] < 0.4
            ][:10]
        }

    def _map_entity_relationships(self, entities: List[Dict]) -> List[Dict[str, str]]:
        """Map relationships between entities."""
        relationships = []
        for i, e1 in enumerate(entities):
            for e2 in entities[i+1:]:
                rel_type = "associated_with"
                if e1.get("type") == "primary" and e2.get("type") != "primary":
                    rel_type = "encompasses"
                elif e1.get("relevance", 0) > 0.7 and e2.get("relevance", 0) > 0.7:
                    rel_type = "co_occurs_frequently"
                relationships.append({
                    "source": e1["name"],
                    "target": e2["name"],
                    "relationship": rel_type,
                    "strength": round((e1.get("relevance", 0.5) + e2.get("relevance", 0.5)) / 2, 2)
                })
        return relationships[:50]

    def _suggest_knowledge_graph_uris(self, entity: str, query: str) -> Dict[str, str]:
        """Suggest Knowledge Graph URIs using ONLY real, verified Wikidata lookups."""
        normalized = entity.lower().replace(" ", "_")
        wd = search_wikidata(entity)
        wd_results = wd.get("results", [])
        wikidata_url = wd_results[0]["url"] if wd_results else None
        wikidata_id = wd_results[0]["id"] if wd_results else None

        same_as_candidates = []
        if wikidata_url:
            same_as_candidates.append(wikidata_url)
        if wikidata_id:
            # Resolve the entity's real sitelinks via Wikidata API for the
            # canonical Wikipedia article (only if it actually exists).
            try:
                from ..utils.web_data import fetch_page
                wd_api = ("https://www.wikidata.org/w/api.php?action=wbgetentities&ids="
                          + urllib.parse.quote(wikidata_id)
                          + "&props=sitelinks&sitefilter=enwiki&format=json")
                resp = _open(wd_api, timeout=15, headers={"Accept": "application/json"})
                if resp is not None:
                    body = _read_body(resp)
                    data = json.loads(body)
                    enwiki = (data.get("entities", {}).get(wikidata_id, {})
                              .get("sitelinks", {}).get("enwiki", {}).get("title", ""))
                    if enwiki:
                        wiki_url = "https://en.wikipedia.org/wiki/" + enwiki.replace(" ", "_")
                        same_as_candidates.append(wiki_url)
            except Exception:
                pass

        return {
            "wikidata": wikidata_url or "",
            "wikidata_id": wikidata_id or "",
            "wikidata_label": wd_results[0]["label"] if wd_results else "",
            "wikidata_description": wd_results[0]["description"] if wd_results else "",
            "sameAs_candidates": same_as_candidates,
            "search_url": f"https://www.wikidata.org/wiki/Special:Search?search={urllib.parse.quote(entity)}",
            "wikidata_verified": bool(wd_results),
            "verification_note": "No verified Knowledge Graph entity found - only public Wikidata references are provided"
        }

    def _calculate_entity_density(self, text: str, entities: List[Dict]) -> float:
        """Calculate entity density score."""
        words = tokenize_words(text)
        if not words:
            return 0.0
        entity_mentions = sum(1 for e in entities for w in tokenize_words(e["name"]) if w in [x.lower() for x in words])
        return round(min(1.0, entity_mentions / max(1, len(words))), 4)

    def _analyze_serp_features(self, query: str, locale: str, device: str, serp_results: List[Dict] = None) -> Dict[str, Any]:
        """Analyze expected SERP features for the query.

        Probabilities are labeled heuristics (not measured data): they are only
        used to prioritize optimization targets. Features actually detected in
        the live SERP are marked as detected_in_live_serp and take precedence.
        """
        query_words = set(tokenize_words(query))
        feature_probabilities = {
            "ai_overview": {"base": 0.5, "query_modifiers": {"how": 0.1, "what": 0.1, "best": 0.05, "vs": 0.05}},
            "featured_snippet": {"base": 0.5, "query_modifiers": {"how": 0.15, "what": 0.1, "why": 0.1}},
            "people_also_ask": {"base": 0.5, "query_modifiers": {"how": 0.05, "what": 0.05}},
            "knowledge_panel": {"base": 0.5, "query_modifiers": {"who": 0.2, "when": 0.15}},
            "local_pack": {"base": 0.5, "query_modifiers": {"near me": 0.3, "local": 0.2}},
            "video_pack": {"base": 0.5, "query_modifiers": {"tutorial": 0.2, "how to": 0.15, "review": 0.1}},
            "image_pack": {"base": 0.5, "query_modifiers": {"examples": 0.2, "template": 0.15}},
            "shopping_results": {"base": 0.5, "query_modifiers": {"buy": 0.3, "price": 0.2, "best": 0.1}},
            "discussion_forums": {"base": 0.5, "query_modifiers": {"reddit": 0.25, "forum": 0.3, "opinion": 0.2}},
        }
        features = {}
        for feature, config in feature_probabilities.items():
            prob = config["base"]
            for modifier, boost in config["query_modifiers"].items():
                if modifier in query.lower():
                    prob += boost
            features[feature] = {
                "probability": round(min(1.0, max(0.0, prob)), 3),
                "probability_source": "heuristic_estimate",
                "estimate": True,
                "expected": prob > 0.6,
                "optimization_priority": "high" if prob > 0.7 else "medium" if prob > 0.5 else "low"
            }

        # REAL feature detection from live SERP results
        real_detected = self._detect_real_serp_features(serp_results or [])
        detected_domains = real_detected.get("domain_signals", {})
        domain_bumps = {
            "video_pack": ["youtube.com", "youtu.be", "vimeo.com", "dailymotion.com", "twitch.tv"],
            "discussion_forums": ["reddit.com", "quora.com", "stackoverflow.com", "forums.", "forum."],
            "shopping_results": ["amazon.com", "walmart.com", "ebay.com", "bestbuy.com", "etsy.com", "shopping."],
            "knowledge_panel": ["en.wikipedia.org", "britannica.com", "wikidata.org", "imdb.com"],
            "local_pack": ["yelp.com", "tripadvisor.com", "google.com/maps", "opentable.com"],
            "image_pack": ["pinterest.com", "flickr.com", "shutterstock.com", "gettyimages.com"],
        }
        for feature, domains in domain_bumps.items():
            if feature not in features:
                continue
            hits = [d for d in domains if d in detected_domains]
            if hits:
                features[feature]["probability"] = round(min(1.0, features[feature]["probability"] + 0.1), 3)
                features[feature]["detected_in_live_serp"] = hits
                features[feature]["probability_source"] = "live_serp_detection"
                features[feature]["expected"] = True

        device_adjustments = {
            "mobile": {"ai_overview": -0.1, "featured_snippet": 0.05, "local_pack": 0.1},
            "desktop": {"ai_overview": 0.05, "knowledge_panel": 0.1},
            "tablet": {}
        }
        for feature, adjustment in device_adjustments.get(device, {}).items():
            if feature in features:
                features[feature]["probability"] = round(
                    min(1.0, max(0, features[feature]["probability"] + adjustment)), 3
                )
                features[feature]["expected"] = features[feature]["probability"] > 0.5
        return {
            "features": features,
            "primary_optimization_target": max(features.items(), key=lambda x: x[1]["probability"])[0],
            "device_profile": device,
            "locale": locale,
            "live_result_count": len(serp_results or []),
            "live_detected_features": real_detected.get("detected", []),
            "live_domain_signals": detected_domains,
            "estimated_serp_composition": self._estimate_serp_composition(features)
        }

    def _detect_real_serp_features(self, results: List[Dict]) -> Dict[str, Any]:
        """Detect SERP features from the real result set (domains + content signals)."""
        domain_signals = {}
        detected = []
        for r in results:
            url = (r.get("url", "") or "").lower()
            title = (r.get("title", "") or "").lower()
            snippet = (r.get("snippet", "") or "").lower()
            host = ""
            try:
                from urllib.parse import urlparse
                host = urlparse(url).netloc.lower()
            except Exception:
                pass
            if host:
                domain_signals.setdefault(host, 0)
                domain_signals[host] += 1
            if any(d in host for d in ["youtube.com", "youtu.be", "vimeo.com"]):
                detected.append("video_pack")
            if any(d in host for d in ["reddit.com", "quora.com", "stackoverflow.com"]):
                detected.append("discussion_forums")
            if any(d in host for d in ["amazon.com", "walmart.com", "ebay.com"]):
                detected.append("shopping_results")
            if any(d in host for d in ["en.wikipedia.org", "britannica.com"]):
                detected.append("knowledge_panel")
            if any(d in host for d in ["yelp.com", "tripadvisor.com"]):
                detected.append("local_pack")
            if "how to" in title or "tutorial" in title:
                detected.append("video_pack")
            if snippet.endswith("?") or "?" in snippet[:60]:
                detected.append("people_also_ask")
            if title.startswith(("best ", "top ", "vs ")):
                detected.append("featured_snippet")
        return {
            "detected": sorted(set(detected)),
            "domain_signals": dict(sorted(domain_signals.items(), key=lambda x: -x[1])[:15]),
        }

    def _estimate_serp_composition(self, features: Dict) -> Dict[str, Any]:
        """Estimate the SERP layout composition."""
        organic_slot_estimate = 10
        for feature, data in features.items():
            if data["expected"] and feature not in ["people_also_ask"]:
                organic_slot_estimate -= 1
        return {
            "estimated_organic_slots": max(3, organic_slot_estimate),
            "ai_overview_slot": features.get("ai_overview", {}).get("expected", False),
            "featured_snippet_slot": features.get("featured_snippet", {}).get("expected", False),
            "paa_slots": 4 if features.get("people_also_ask", {}).get("expected", False) else 0,
            "competition_intensity": "HIGH" if organic_slot_estimate <= 5 else "MODERATE" if organic_slot_estimate <= 7 else "LOW"
        }

    def _cluster_paa(self, seed_phrase: str, competitor_content: List[str], serp_results: List[Dict] = None) -> Dict[str, Any]:
        """Cluster People Also Ask questions by intent (template + real SERP extraction)."""
        common_paa_patterns = [
            "what is", "how to", "why is", "when should", "where can",
            "what are the best", "how do I", "is it worth", "what is the difference",
            "how much does", "what features", "can you", "do I need",
            "how long does", "what are the benefits", "what are the drawbacks",
            "how does it compare", "what should I look for", "is there a free"
        ]
        question_categories = {
            "definitional": [],
            "procedural": [],
            "comparative": [],
            "evaluative": [],
            "transactional": [],
            "technical": []
        }
        # REAL questions extracted from live SERP result titles/snippets
        real_questions = []
        for r in (serp_results or []):
            for field in ("title", "snippet"):
                for sent in re.split(r'[.!?]\s+', (r.get(field, "") or "")):
                    sent = sent.strip()
                    if sent.lower().startswith(("what", "how", "why", "when", "where", "which", "who", "can", "do", "is", "are", "does", "should")) and "?" in (r.get(field, "") or "")[r.get(field, "").find(sent[:20]):r.get(field, "").find(sent[:20]) + 200]:
                        real_questions.append(sent[:160])
        real_questions = list(dict.fromkeys(real_questions))[:15]

        for pattern in common_paa_patterns:
            category = "definitional"
            if any(x in pattern for x in ["how to", "how do"]):
                category = "procedural"
            elif "difference" in pattern or "compare" in pattern:
                category = "comparative"
            elif any(x in pattern for x in ["best", "worth", "benefits", "drawbacks"]):
                category = "evaluative"
            elif any(x in pattern for x in ["much", "cost", "price", "free"]):
                category = "transactional"
            elif any(x in pattern for x in ["features", "technical", "specifications"]):
                category = "technical"
            question_categories[category].append({
                "question_template": f"{pattern} {seed_phrase.lower()}?",
                "answer_format": self._suggest_answer_format(category),
                "content_block_required": True,
                "priority": "high" if category in ["definitional", "comparative"] else "medium"
            })

        # Classify real extracted questions into the same categories
        real_classified = {k: [] for k in question_categories}
        for q in real_questions:
            ql = q.lower()
            if any(x in ql for x in ["how to", "how do"]):
                cat = "procedural"
            elif any(x in ql for x in ["difference", "compare", "versus", " vs "]):
                cat = "comparative"
            elif any(x in ql for x in ["best", "worth", "benefits", "drawbacks", "is it"]):
                cat = "evaluative"
            elif any(x in ql for x in ["cost", "price", "much", "free", "buy"]):
                cat = "transactional"
            elif any(x in ql for x in ["feature", "technical", "api", "integrat"]):
                cat = "technical"
            else:
                cat = "definitional"
            real_classified[cat].append({
                "question": q,
                "answer_format": self._suggest_answer_format(cat),
                "content_block_required": True,
                "priority": "high" if cat in ["definitional", "comparative"] else "medium",
                "source": "live_serp"
            })
        for cat in question_categories:
            question_categories[cat].extend(real_classified[cat])

        return {
            "total_questions_identified": sum(len(v) for v in question_categories.values()),
            "real_questions_from_serp": real_questions,
            "real_question_count": len(real_questions),
            "categories": question_categories,
            "top_priority_questions": [
                q for qs in question_categories.values() for q in qs if q["priority"] == "high"
        ][:5],
            "content_coverage_requirement": "All high-priority questions must have dedicated content blocks"
        }

    def _suggest_answer_format(self, category: str) -> str:
        formats = {
            "definitional": "40-60 word definition paragraph with entity link",
            "procedural": "Numbered step-by-step list with 5-8 steps",
            "comparative": "Comparison table with feature matrix",
            "evaluative": "Pros/cons list with bullet points",
            "transactional": "Price range table with tier comparison",
            "technical": "Technical specification block with code examples"
        }
        return formats.get(category, "Paragraph with supporting data")

    def _assess_entity_coverage(self, entity_graph: Dict, competitor_content: List[str]) -> Dict[str, Any]:
        """Assess entity coverage across competitor content."""
        all_competitor_text = ' '.join(competitor_content) if competitor_content else ""
        covered_entities = []
        uncovered_entities = []
        all_entities = entity_graph.get("related_entities", []) + entity_graph.get("core_entities", [])
        for entity in all_entities:
            entity_name = entity["name"].lower()
            if entity_name in all_competitor_text.lower():
                covered_entities.append({
                    "entity": entity["name"],
                    "status": "covered_by_competitors",
                    "opportunity": "Must match or exceed competitor coverage"
                })
            else:
                uncovered_entities.append({
                    "entity": entity["name"],
                    "status": "gap_opportunity",
                    "opportunity": "First-mover advantage - competitors haven't covered this"
                })
        return {
            "total_entities": len(all_entities),
            "covered_by_competitors": len(covered_entities),
            "gap_opportunities": len(uncovered_entities),
            "coverage_ratio": round(len(covered_entities) / max(1, len(all_entities)), 3),
            "covered": covered_entities[:15],
            "uncovered": uncovered_entities[:15],
            "strategic_recommendation": (
                "Focus on gap entities for differentiation" if len(uncovered_entities) > len(covered_entities) else
                "Must match competitor entity coverage before differentiating"
            )
        }

    def _score_topical_authority(self, entity_graph: Dict, competitor_content: List[str]) -> Dict[str, Any]:
        """Score the required topical authority depth."""
        entity_count = entity_graph.get("entity_count", 0)
        related_count = len(entity_graph.get("related_entities", []))
        competitor_text = ' '.join(competitor_content) if competitor_content else ""
        avg_competitor_length = len(competitor_text.split()) / max(1, len(competitor_content)) if competitor_content else 0
        depth_score = min(1.0, (related_count * 0.05) + (entity_count * 0.03))
        breadth_score = min(1.0, len(set(t for e in entity_graph.get("related_entities", []) for t in tokenize_words(e["name"]))) / 50)
        required_word_count = max(2000, int(avg_competitor_length * 1.3)) if competitor_content else 2500
        return {
            "depth_score": round(depth_score, 3),
            "breadth_score": round(breadth_score, 3),
            "combined_authority_score": round((depth_score + breadth_score) / 2, 3),
            "required_word_count_estimate": required_word_count,
            "required_heading_count": max(8, entity_count // 2),
            "required_internal_links": max(3, related_count // 5),
            "required_external_citations": max(2, entity_count // 3),
            "authority_tier": (
                "TIER_1_DEEP" if depth_score > 0.7 else
                "TIER_2_MODERATE" if depth_score > 0.4 else
                "TIER_3_SURFACE"
            )
        }

    def _analyze_serp_formats(self, competitor_content: List[str]) -> Dict[str, Any]:
        """Analyze what content formats competitors use."""
        if not competitor_content:
            return {"format_distribution": {}, "recommended_formats": ["list", "table", "definition_block"]}
        format_signals = {
            "numbered_lists": r'(?:^|\n)\s*\d+[\.\)]\s+',
            "bullet_lists": r'(?:^|\n)\s*[-•*]\s+',
            "tables": r'\|.*\|.*\|',
            "code_blocks": r'```|`[^`]+`',
            "definition_blocks": r'(?:is|are|refers?\s+to)\s+(?:a|an|the)\s+\w+',
            "comparisons": r'(?:vs\.?|versus|compared?\s+to|better\s+than)',
            "statistics": r'\d+(?:\.\d+)?%',
            "quotes": r'["\u201c].*?["\u201d]',
            "images_with_alt": r'<img[^>]*alt\s*=\s*["\'][^"\']+["\']',
            "faq_format": r'(?:Q[:.]|FAQ|frequently\s+asked)',
        }
        format_counts = {}
        combined = ' '.join(competitor_content)
        for fmt, pattern in format_signals.items():
            count = len(re.findall(pattern, combined, re.IGNORECASE | re.MULTILINE))
            format_counts[fmt] = count
        total = sum(format_counts.values()) or 1
        distribution = {k: {"count": v, "percentage": round(v / total * 100, 1)} for k, v in format_counts.items()}
        sorted_formats = sorted(format_counts.items(), key=lambda x: x[1], reverse=True)
        return {
            "format_distribution": distribution,
            "dominant_formats": [f[0] for f in sorted_formats[:3]],
            "underutilized_formats": [f[0] for f in sorted_formats if f[1] == 0],
            "recommended_formats": self._recommend_formats(format_counts),
            "format_diversity_score": round(sum(1 for v in format_counts.values() if v > 0) / len(format_counts), 3)
        }

    def _recommend_formats(self, counts: Dict[str, int]) -> List[str]:
        """Recommend content formats based on competitor analysis."""
        recommendations = ["definition_block", "numbered_list"]
        if counts.get("tables", 0) < 3:
            recommendations.append("comparison_table")
        if counts.get("statistics", 0) > 5:
            recommendations.append("data_visualization")
        if counts.get("faq_format", 0) < 2:
            recommendations.append("faq_section")
        if counts.get("code_blocks", 0) > 0:
            recommendations.append("code_example")
        recommendations.append("quote_block")
        return recommendations

    def _build_keyword_landscape(self, seed: str, secondary: List[str], competitors: List[str]) -> Dict[str, Any]:
        """Build comprehensive keyword landscape analysis."""
        seed_words = set(tokenize_words(seed))
        secondary_words = set()
        for kw in secondary:
            secondary_words.update(tokenize_words(kw))
        all_target_words = seed_words | secondary_words
        competitor_words = set()
        for comp in competitors:
            competitor_words.update(tokenize_words(comp))
        gap_words = all_target_words - competitor_words - {"the", "a", "an", "is", "are", "for", "and", "or", "of", "in", "to", "with"}
        overlap_words = all_target_words & competitor_words
        keyword_clusters = self._cluster_keywords(seed, secondary)
        return {
            "primary_keyword": seed,
            "secondary_keywords": secondary,
            "keyword_gap_words": list(gap_words)[:20],
            "keyword_overlap_words": list(overlap_words)[:20],
            "keyword_clusters": keyword_clusters,
            "total_unique_keyword_terms": len(all_target_words),
            "gap_percentage": round(len(gap_words) / max(1, len(all_target_words)) * 100, 1),
            "coverage_percentage": round(len(overlap_words) / max(1, len(all_target_words)) * 100, 1),
            "recommended_long_tail_variations": self._generate_long_tails(seed, secondary)
        }

    def _cluster_keywords(self, seed: str, secondary: List[str]) -> Dict[str, List[str]]:
        """Cluster keywords into topical groups."""
        seed_words = set(tokenize_words(seed))
        clusters = {
            "core_terms": [seed] + [kw for kw in secondary if len(set(tokenize_words(kw)) & seed_words) >= 2],
            "modifier_terms": [kw for kw in secondary if any(m in kw.lower() for m in ["best", "top", "vs", "alternative", "review"])],
            "question_terms": [kw for kw in secondary if any(q in kw.lower() for q in ["how", "what", "why", "when", "where", "which"])],
            "commercial_terms": [kw for kw in secondary if any(c in kw.lower() for c in ["price", "cost", "buy", "demo", "free", "trial"])],
            "technical_terms": [kw for kw in secondary if any(t in kw.lower() for t in ["api", "integration", "architecture", "protocol", "specification"])]
        }
        return {k: v for k, v in clusters.items() if v}

    def _generate_long_tails(self, seed: str, secondary: List[str]) -> List[str]:
        """Generate long-tail keyword variations."""
        modifiers = {
            "comparison": ["vs", "compared to", "alternatives to", "better than"],
            "question": ["how to", "what is", "why use", "when to use", "where to find"],
            "commercial": ["best", "top", "review", "pricing", "free trial", "demo"],
            "informational": ["guide", "tutorial", "example", "use case", "best practices"],
            "technical": ["API", "integration", "architecture", "implementation", "setup"]
        }
        variations = []
        for category, mods in modifiers.items():
            for mod in mods[:2]:
                variations.append(f"{mod} {seed}")
        return variations[:15]

    def _generate_gap_summary(self, entity_coverage: Dict, paa_clusters: Dict) -> Dict[str, Any]:
        """Generate a competitive gap summary."""
        return {
            "entity_gaps": entity_coverage.get("gap_opportunities", 0),
            "total_entities_to_cover": entity_coverage.get("total_entities", 0),
            "paa_questions_to_answer": paa_clusters.get("total_questions_identified", 0),
            "top_priority_actions": [
                f"Cover {entity_coverage.get('gap_opportunities', 0)} uncovered entity gaps",
                f"Answer {paa_clusters.get('total_questions_identified', 0)} PAA questions",
                f"Achieve {entity_coverage.get('coverage_ratio', 0) * 100:.0f}% entity coverage ratio"
            ]
        }

    def _generate_recommendations(self, entity_graph: Dict, serp_features: Dict, paa_clusters: Dict) -> List[Dict[str, str]]:
        """Generate actionable recommendations."""
        recs = []
        if serp_features.get("features", {}).get("ai_overview", {}).get("expected"):
            recs.append({
                "priority": "CRITICAL",
                "action": "Structure content for AI Overview extraction",
                "detail": "Include 40-60 word definition blocks under each H2 heading"
            })
        if serp_features.get("features", {}).get("featured_snippet", {}).get("expected"):
            recs.append({
                "priority": "HIGH",
                "action": "Optimize for featured snippet capture",
                "detail": "Use numbered lists and direct answer paragraphs"
            })
        if paa_clusters.get("top_priority_questions"):
            recs.append({
                "priority": "HIGH",
                "action": "Create dedicated content blocks for top PAA questions",
                "detail": f"Address {len(paa_clusters['top_priority_questions'])} high-priority questions"
            })
        entity_count = entity_graph.get("entity_count", 0)
        if entity_count > 10:
            recs.append({
                "priority": "MEDIUM",
                "action": "Build comprehensive entity graph coverage",
                "detail": f"Cover {entity_count} entities to establish topical authority"
            })
        recs.append({
            "priority": "MEDIUM",
            "action": "Implement hierarchical schema markup",
            "detail": "Use nested JSON-LD with entity relationships"
        })
        return recs

    def _generate_implementation_steps(self, entity_graph: Dict, serp_features: Dict,
                                        paa_clusters: Dict, entity_coverage: Dict) -> List[str]:
        steps = []
        steps.append("Step 1: Map all core and related entities from the entity graph into a content hierarchy document")
        steps.append("Step 2: Create an H1 title that includes the primary entity and seed phrase for maximum relevance")
        steps.append("Step 3: Build H2 sections for each Level-1 entity pillar with 40-60 word direct answer blocks")
        steps.append("Step 4: Add H3 subsections for Level-2 detail entities with supporting data and statistics")
        steps.append("Step 5: Implement JSON-LD TechArticle schema in <head> with mainEntity, about, and mentions properties")
        steps.append("Step 6: Add Knowledge Graph sameAs links to Wikidata and Wikipedia for entity verification")
        steps.append("Step 7: Create dedicated FAQ blocks for each high-priority PAA question cluster")
        steps.append("Step 8: Write 40-60 word definition paragraphs immediately after each H2 heading for AI Overview extraction")
        steps.append("Step 9: Include comparison tables in sections targeting 'vs' or 'best' query modifiers")
        steps.append("Step 10: Add numbered step-by-step lists for procedural PAA questions with 5-8 steps each")
        steps.append("Step 11: Cover all gap entities identified in the entity coverage analysis before competitor benchmarking")
        steps.append("Step 12: Update XML sitemap with the new URL and submit via Google Indexing API")
        return steps

    def _generate_where_to_add(self, entity_graph: Dict, serp_features: Dict) -> List[str]:
        locations = []
        locations.append("Add JSON-LD TechArticle schema in <head> via <script type='application/ld+json'> tag")
        locations.append("Place entity sameAs links in the author/publisher schema block within <head>")
        locations.append("Include primary entity definition as the first 40-60 words immediately after the H1 heading")
        locations.append("Add FAQPage schema for People Also Ask clusters in <head> section")
        locations.append("Place comparison tables within H2 sections targeting 'vs' or 'best' query modifiers")
        locations.append("Insert entity-rich definition blocks at the start of each H2 section for Knowledge Panel triggers")
        locations.append("Add HowTo schema for procedural PAA questions within the corresponding H2 section")
        locations.append("Place numbered lists for step-by-step queries directly under the relevant H3 subheading")
        locations.append("Include BreadcrumbList schema in <head> reflecting the site navigation hierarchy")
        locations.append("Add external citation links within body paragraphs referencing authoritative sources (Gartner, Forrester, etc.)")
        return locations

    def _generate_detailed_analysis(self, entity_graph: Dict, serp_features: Dict,
                                     paa_clusters: Dict, entity_coverage: Dict,
                                     topical_authority: Dict, keyword_landscape: Dict) -> Dict[str, Any]:
        return {
            "entity_graph_insights": {
                "total_entities_mapped": entity_graph.get("entity_count", 0),
                "entity_density_benchmark": "(General industry guidance, unverified): Top-ranking pages average 15-25 unique entity mentions per 1000 words",
                "statistical_range": f"Current entity count: {entity_graph.get('entity_count', 0)} (General industry guidance, unverified target: 20-30 for competitive niches)",
                "expert_recommendation": "Ensure primary entity appears in H1, first paragraph, at least 2 H2s, and schema markup",
                "common_mistakes": ["Overusing primary entity without introducing related entities", "Ignoring Knowledge Graph URI alignment", "Missing entity relationships in schema"],
                "success_metrics": ["Entity coverage ratio > 80%", "Knowledge Graph panel trigger on brand entity", "3+ related entities per H2 section"],
                "data_origin": "unverified_industry_heuristic - not measured for this page"
            },
            "serp_features_insights": {
                "primary_target": serp_features.get("primary_optimization_target", "N/A"),
                "ai_overview_probability": serp_features.get("features", {}).get("ai_overview", {}).get("probability", 0),
                "benchmark": "(General industry guidance, unverified): AI Overviews are commonly reported to appear for ~85% of informational queries, featured snippets for ~70%",
                "statistical_range": f"Estimated organic slots: {serp_features.get('estimated_serp_composition', {}).get('estimated_organic_slots', 'N/A')}",
                "expert_recommendation": "Structure content with 40-60 word definition blocks to maximize AI Overview citation probability",
                "common_mistakes": ["Writing long introductions without direct answers", "Skipping structured data implementation", "Ignoring mobile SERP layout differences"],
                "success_metrics": ["AI Overview citation within 60 days", "Featured snippet capture rate > 30%", "Organic CTR improvement > 15%"],
                "data_origin": "unverified_industry_heuristic - not measured for this page"
            },
            "paa_clusters_insights": {
                "total_questions": paa_clusters.get("total_questions_identified", 0),
                "high_priority_count": len(paa_clusters.get("top_priority_questions", [])),
                "benchmark": "(General industry guidance, unverified): Top pages answer 7-10 PAA questions with dedicated content blocks averaging 40-60 words each",
                "statistical_range": f"Question categories covered: {sum(1 for v in paa_clusters.get('categories', {}).values() if v)}/6",
                "expert_recommendation": "Address all definitional and comparative PAA questions first as they have highest extraction probability",
                "common_mistakes": ["Answering questions in prose instead of structured format", "Missing question variations", "Answers exceeding 60 words"],
                "success_metrics": ["PAA appearance for target queries", "Answer extraction rate > 50%", "Question-specific CTR > 20%"],
                "data_origin": "unverified_industry_heuristic - not measured for this page"
            },
            "entity_coverage_insights": {
                "coverage_ratio": entity_coverage.get("coverage_ratio", 0),
                "gap_opportunities": entity_coverage.get("gap_opportunities", 0),
                "benchmark": "(General industry guidance, unverified): Competitive pages cover 75-90% of relevant entities; top 10 results average 85% coverage",
                "statistical_range": f"Current coverage: {entity_coverage.get('coverage_ratio', 0)*100:.0f}% vs unverified heuristic target: 80%+",
                "expert_recommendation": "Prioritize gap entities that competitors have not covered for first-mover differentiation advantage",
                "common_mistakes": ["Focusing only on primary entity without covering the entity graph", "Ignoring uncovered entities that represent ranking opportunities"],
                "success_metrics": ["Entity coverage ratio > 85%", "Gap entity coverage > 50%", "Entity count matching top 3 competitors"],
                "data_origin": "unverified_industry_heuristic - not measured for this page"
            },
            "topical_authority_insights": {
                "combined_score": topical_authority.get("combined_authority_score", 0),
                "required_word_count": topical_authority.get("required_word_count_estimate", 2500),
                "authority_tier": topical_authority.get("authority_tier", "UNKNOWN"),
                "benchmark": "(General industry guidance, unverified): Topically authoritative content averages 3000-5000 words with 10+ H2 sections and 5+ external citations",
                "statistical_range": f"Target word count: {topical_authority.get('required_word_count_estimate', 2500)} words, {topical_authority.get('required_heading_count', 8)} headings",
                "expert_recommendation": "Aim for TIER_1_DEEP authority by covering all Level-1 and Level-2 entities with unique data",
                "common_mistakes": ["Publishing thin content under 2000 words for competitive queries", "Missing required external citations", "Insufficient heading hierarchy depth"],
                "success_metrics": ["Organic rankings for 5+ related keywords", "Average dwell time > 4 minutes", "Featured snippet or AI Overview citation"],
                "data_origin": "unverified_industry_heuristic - not measured for this page"
            },
            "keyword_landscape_insights": {
                "total_unique_terms": keyword_landscape.get("total_unique_keyword_terms", 0),
                "gap_percentage": keyword_landscape.get("gap_percentage", 0),
                "coverage_percentage": keyword_landscape.get("coverage_percentage", 0),
                "benchmark": "(General industry guidance, unverified): Competitive pages cover 70-85% of target keyword terms; long-tail variations should include 10-15 unique phrases",
                "statistical_range": f"Keyword gap: {keyword_landscape.get('gap_percentage', 0)}% terms not found in competitor content",
                "expert_recommendation": "Target gap keywords for quick wins and use long-tail variations to build topical depth",
                "common_mistakes": ["Ignoring long-tail keyword opportunities", "Over-optimizing for exact match keywords", "Missing commercial and question-modifier terms"],
                "success_metrics": ["Keyword coverage > 80%", "Rankings for 3+ long-tail variations", "Organic traffic growth > 25% in 90 days"],
                "data_origin": "unverified_industry_heuristic - not measured for this page"
            }
        }
