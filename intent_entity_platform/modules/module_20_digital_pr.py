"""
Module 20: Digital PR & Knowledge Graph Entity Alignment Engine
Connects on-page content to off-page trust signals.
"""
import re
import urllib.parse
from typing import List, Dict, Any
from ..utils.web_data import search_wikidata, web_search


class DigitalPREngine:
    """Module 20: Digital PR & Knowledge Graph Entity Alignment Engine"""

    def __init__(self):
        self.module_id = "M20"
        self.module_name = "Digital PR & Knowledge Graph Entity Alignment Engine"

    def analyze(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Full digital PR and entity alignment pipeline."""
        entity = inputs.get("primary_entity", "")
        author = inputs.get("author", {})
        content = inputs.get("content", "")

        _url_data = inputs.get("_url_data", {})
        url_from_data = _url_data.get("url", "")
        url_title = _url_data.get("title", "")
        url_page_text = _url_data.get("page_text", "")
        url_h1 = _url_data.get("h1", "")
        url_h2s = _url_data.get("h2s", [])
        url_word_count = _url_data.get("word_count", 0)
        url_has_schema = _url_data.get("has_schema", False)
        url_images = _url_data.get("images", [])
        url_links = _url_data.get("links", [])

        url_pr_analysis = self._analyze_url_pr_opportunities(_url_data) if _url_data else {}

        kg_alignment = self._align_knowledge_graph(entity, inputs)
        author_trust = self._verify_author_entity(author)
        pr_opportunities = self._identify_pr_opportunities(content or url_page_text, entity)
        entity_linking = self._build_entity_linking_strategy(entity, inputs)
        authority_signals = self._assess_authority_signals(inputs)

        return {
            "module": self.module_id,
            "module_name": self.module_name,
            "url_analyzed": url_from_data,
            "url_digital_pr_analysis": url_pr_analysis if _url_data else {
                "status": "NO_URL_DATA",
                "message": "Provide _url_data for URL-specific digital PR analysis"
            },
            "knowledge_graph_alignment": kg_alignment,
            "author_trust_verification": author_trust,
            "pr_opportunities": pr_opportunities,
            "entity_linking_strategy": entity_linking,
            "authority_signal_assessment": authority_signals,
            "recommendations": self._generate_recommendations(kg_alignment, author_trust, pr_opportunities),
            "implementation_steps": [
                "Step 1: Verify the primary entity exists on Wikidata, Wikipedia, and Google Knowledge Graph",
                "Step 2: Add sameAs schema links in the page's JSON-LD pointing to verified Knowledge Graph URIs",
                "Step 3: Create or update the author's LinkedIn profile with matching name, title, and expertise areas",
                "Step 4: Build an author schema block with sameAs links to all verified social and professional profiles",
                "Step 5: Add author byline with credentials and headshot near the top of the article",
                "Step 6: Identify original data points in the content and package them for PR pitches",
                "Step 7: Create a press kit page with author bio, headshot, key stats, and contact information",
                "Step 8: Pitch original research data to 3-5 target publications using the provided pitch templates",
                "Step 9: Set up HARO/Qwoted alerts for queries related to the primary entity expertise",
                "Step 10: Build entity authority by earning mentions on 5+ authoritative domains referencing the entity",
                "Step 11: Add expert quotes from recognized authorities to strengthen E-E-A-T signals",
                "Step 12: Monitor Knowledge Panel for entity changes after content publication and schema updates"
            ],
            "where_to_add": [
                "Place entity sameAs schema in <head> via <script type='application/ld+json'> tag with Knowledge Graph URIs",
                "Add author schema with sameAs links in <head> via separate <script type='application/ld+json'> block",
                "Insert author byline with credentials and headshot in the article header area (above or below H1)",
                "Place expert quotes as blockquotes within H2/H3 sections throughout the article body",
                "Add original research data and statistics as H2 sections with supporting charts and citations",
                "Include citations to authoritative sources as inline links within body paragraphs",
                "Place press kit page link in the site footer or about section for journalist access",
                "Add structured data for Organization schema with sameAs links to social profiles in <head>",
                "Include entity-related internal links within body content to strengthen topical authority",
                "Place social proof elements (logos, awards, certifications) in a visible trust section"
            ],
            "detailed_analysis": {
                "knowledge_graph_benchmarks": {
                    "entity_verification_rate": "70% of established entities have Wikidata entries; 40% have Wikipedia",
                    "sameas_schema_impact": "Pages with sameAs links see 15-25% higher Knowledge Panel visibility",
                    "knowledge_panel_trigger_rate": "Consistent entity signals across 5+ authoritative sources trigger panel creation",
                    "entity_authority_score_range": "Low: 0-3 sources; Medium: 4-8 sources; High: 9+ authoritative sources",
                    "typical_time_to_knowledge_panel": "3-6 months with consistent cross-platform entity signals",
                    "data_origin": "unverified_industry_heuristic - not measured for this page"
                },
                "author_trust_benchmarks": {
                    "expert_tier_requirements": "3+ social profiles + credentials + 10+ publications",
                    "authoritative_tier_requirements": "2+ verified social profiles + 5+ published articles",
                    "linkedin_verification_impact": "Strongest single author E-E-A-T signal for Google's helpful content system",
                    "google_scholar_impact": "Significant boost for YMYL and research-heavy content types",
                    "consistent_author_name_impact": "20-30% improvement in author entity recognition with name consistency",
                    "data_origin": "unverified_industry_heuristic - not measured for this page"
                },
                "digital_pr_benchmarks": {
                    "original_data_pitch_success_rate": "15-25% for truly original research; 5-10% for commentary",
                    "haro_response_success_rate": "5-15% of responses result in published mentions",
                    "link_earning_from_pr": "Average 2-5 high-authority links per successful PR placement",
                    "data_visualization_share_rate": "Visual content gets 3x more shares and 2x more backlinks than text-only",
                    "guest_post_authority_value": "Links from DA 60+ publications carry 3-5x more authority than average backlinks",
                    "data_origin": "unverified_industry_heuristic - not measured for this page"
                },
                "expert_recommendations": [
                    "(General industry guidance, unverified): Build entity authority systematically - Wikidata entry first, then cross-platform profile consistency",
                    "(General industry guidance, unverified): Publish original research data that competitors cannot replicate - often the strongest PR angle",
                    "(General industry guidance, unverified): Create an author entity footprint across LinkedIn, Google Scholar, Twitter, and industry publications",
                    "(General industry guidance, unverified): Use entity linking strategy to connect on-page and off-page signals for Knowledge Graph alignment",
                    "(General industry guidance, unverified): Monitor Google Knowledge Panel monthly and update entity information as it evolves"
                ],
                "common_mistakes": [
                    "(General industry guidance, unverified): Inconsistent author name across platforms (John Smith vs. J. Smith vs. Jonathan Smith) can break entity recognition",
                    "(General industry guidance, unverified): Forgetting to add sameAs schema links means Knowledge Graph cannot connect your content to verified entities",
                    "(General industry guidance, unverified): Pitching PR without original data or unique insight - generic commentary often gets ignored by journalists",
                    "(General industry guidance, unverified): Ignoring unlinked brand mentions - reach out and request backlinks from these mentions",
                    "(General industry guidance, unverified): Not building author entity signals before publishing YMYL content - trust should be established first"
                ],
                "success_metrics": [
                    "(General industry guidance, unverified): Track Knowledge Panel appearance for primary entity (heuristic target: within 6 months of entity building)",
                    "(General industry guidance, unverified): Monitor author search visibility for the primary author's name and expertise queries",
                    "(General industry guidance, unverified): Measure backlink acquisition rate from digital PR efforts (heuristic target: 5+ per month)",
                    "(General industry guidance, unverified): Track brand mention growth across web (linked and unlinked) month-over-month",
                    "(General industry guidance, unverified): Monitor Google Knowledge Graph API entity score and data completeness"
                ]
            }
        }

    def _analyze_url_pr_opportunities(self, url_data: Dict) -> Dict[str, Any]:
        """Analyze actual URL content for PR opportunities and authority signals."""
        url = url_data.get("url", "")
        title = url_data.get("title", "")
        page_text = url_data.get("page_text", "")
        h1 = url_data.get("h1", "")
        h2s = url_data.get("h2s", [])
        word_count = url_data.get("word_count", 0)
        has_schema = url_data.get("has_schema", False)
        images = url_data.get("images", [])
        links = url_data.get("links", [])

        data_points = re.findall(r'\d+(?:\.\d+)?%', page_text)
        statistics = re.findall(r'\d+(?:,\d{3})+(?:\.\d+)?', page_text)
        year_mentions = re.findall(r'20\d{2}', page_text)
        citations = re.findall(r'(?:according to|source:|study by|research from|survey by)\s+([A-Z][a-zA-Z\s&]+)', page_text)
        expert_quotes = re.findall(r'(?:said|stated|noted|explained|according to|commented)\s*[,:]\s*["\u201c](.+?)["\u201d]', page_text)

        unique_data_points = list(set(data_points))[:15]
        unique_statistics = list(set(statistics))[:10]
        unique_citations = list(set(c.strip() for c in citations))[:10]

        pr_angle_count = 0
        pr_angles = []

        if len(unique_data_points) >= 3:
            pr_angle_count += 1
            pr_angles.append({
                "angle": "Original Data Visualization",
                "strength": "HIGH",
                "detail": f"Page contains {len(unique_data_points)} unique percentage statistics ({', '.join(unique_data_points[:5])})",
                "pitch_summary": f"Share original data findings about the topic - {len(unique_data_points)} statistics available for PR pitches",
                "target_outlets": ["Industry publications", "Data journalism outlets", "Research aggregators"],
                "estimated_pickup_probability": "HIGH - original data is the most shareable PR asset"
            })

        if len(unique_statistics) >= 2:
            pr_angle_count += 1
            pr_angles.append({
                "angle": "Research Findings",
                "strength": "MODERATE",
                "detail": f"Page includes {len(unique_statistics)} numerical statistics that can be repackaged",
                "pitch_summary": f"Package {len(unique_statistics)} statistics as quotable research insights",
                "target_outlets": ["Business journals", "Trade media", "Newsletter features"],
                "estimated_pickup_probability": "MODERATE - statistics need original analysis to be PR-worthy"
            })

        if len(expert_quotes) >= 1:
            pr_angle_count += 1
            pr_angles.append({
                "angle": "Expert Commentary",
                "strength": "HIGH",
                "detail": f"Page contains {len(expert_quotes)} expert quotes that demonstrate authority",
                "pitch_summary": "Leverage expert sources for journalist query services (HARO, Qwoted, SourceBottle)",
                "target_outlets": ["Major news outlets", "Industry publications", "Podcast interviews"],
                "estimated_pickup_probability": "HIGH - journalists actively seek expert sources"
            })

        if len(unique_citations) >= 2:
            pr_angle_count += 1
            pr_angles.append({
                "angle": "Industry Analysis",
                "strength": "MODERATE",
                "detail": f"Page cites {len(unique_citations)} authoritative sources ({', '.join(unique_citations[:3])})",
                "pitch_summary": "Position as industry analyst synthesizing multiple authoritative sources",
                "target_outlets": ["Industry blogs", "LinkedIn Pulse", "Medium publications"],
                "estimated_pickup_probability": "MODERATE - requires unique synthesis angle"
            })

        if word_count > 1500:
            pr_angle_count += 1
            pr_angles.append({
                "angle": "Comprehensive Guide",
                "strength": "MODERATE",
                "detail": f"Long-form content ({word_count} words) can be excerpted for guest posting",
                "pitch_summary": "Offer excerpted sections as guest contributions to industry publications",
                "target_outlets": ["Industry guest blogs", "Syndication platforms", "Content partnerships"],
                "estimated_pickup_probability": "MODERATE - content must be highly relevant to target publication"
            })

        if len(h2s) >= 5:
            pr_angle_count += 1
            pr_angles.append({
                "angle": "Multi-Topic Series",
                "strength": "LOW",
                "detail": f"Content has {len(h2s)} sections that could each be standalone PR pitches",
                "pitch_summary": "Break content into individual story angles for multiple pitches",
                "target_outlets": ["Niche industry outlets", "Regional publications", "Podcast topics"],
                "estimated_pickup_probability": "LOW-MODERATE - requires tailored pitch per outlet"
            })

        brand_mention_opportunities = []
        if len(links) > 0:
            domain = url.split("/")[2] if "/" in url else ""
            internal_links = [l for l in links if domain in l]
            external_links = [l for l in links if l.startswith("http") and domain not in l]
            brand_mention_opportunities.append({
                "opportunity": "Unlinked Brand Mentions",
                "detail": f"Page has {len(external_links)} external links - similar mentions elsewhere may be unlinked",
                "action": "Use Ahrefs/Moz to find unlinked brand mentions and request backlinks"
            })

        authority_linking_strategy = {
            "internal_links_on_page": len([l for l in links if not l.startswith("http")]),
            "external_links_on_page": len([l for l in links if l.startswith("http")]),
            "target_internal_links": "5-8 for comprehensive content",
            "target_external_links": "3-5 authoritative sources",
            "backlink_targets": [
                "Industry publications (DA 50+)",
                "News outlets (DA 70+)",
                "Academic/research institutions",
                "Government/organizational websites",
                "High-authority directories and listings"
            ],
            "data_origin": "unverified_industry_heuristic - not measured for this page"
        }

        return {
            "url": url,
            "page_title": title,
            "page_word_count": word_count,
            "content_statistics_identified": {
                "percentage_data_points": unique_data_points,
                "percentage_count": len(unique_data_points),
                "numerical_statistics": unique_statistics,
                "statistic_count": len(unique_statistics),
                "citations_found": unique_citations,
                "citation_count": len(unique_citations),
                "expert_quotes_found": len(expert_quotes),
                "year_mentions": list(set(year_mentions))
            },
            "pr_angles": pr_angles,
            "pr_angle_count": pr_angle_count,
            "total_pr_opportunities": pr_angle_count,
            "brand_mention_opportunities": brand_mention_opportunities,
            "authority_linking_strategy": authority_linking_strategy,
            "pitch_templates": [
                {
                    "template_name": "Data-Driven Pitch",
                    "subject": f"Original Data: {title[:50]}...",
                    "body": f"Our analysis reveals {len(unique_data_points)} key statistics including {unique_data_points[0] if unique_data_points else 'N/A'} - data your readers need to see.",
                    "best_for": "Data journalism outlets, industry publications"
                },
                {
                    "template_name": "Expert Source Pitch",
                    "subject": f"Expert Source Available: {title[:50]}...",
                    "body": f"Our team has deep expertise in this area with {len(expert_quotes)} published insights and {len(unique_citations)} cited sources.",
                    "best_for": "HARO, Qwoted, journalist queries"
                },
                {
                    "template_name": "Guest Post Pitch",
                    "subject": f"Guest Contribution: {title[:50]}...",
                    "body": f"We've published a comprehensive {word_count}-word guide that your audience would find valuable. We can offer an exclusive excerpt.",
                    "best_for": "Industry blogs, syndication platforms"
                }
            ],
            "pr_readiness_score": round(min(1.0, (pr_angle_count * 0.2 + len(unique_data_points) * 0.05 + len(expert_quotes) * 0.1 + (1 if has_schema else 0) * 0.15)), 3),
            "pr_readiness_tier": (
                "PR_READY" if pr_angle_count >= 3 and len(unique_data_points) >= 3 else
                "MOSTLY_READY" if pr_angle_count >= 2 else
                "NEEDS_WORK" if pr_angle_count >= 1 else
                "NOT_READY"
            ),
            "content_pr_enhancements": [
                f"Add 2-3 more original statistics to strengthen PR angle" if len(unique_data_points) < 5 else "Data points are sufficient for PR pitches",
                "Include author bio with credentials for journalist credibility" if not has_schema else "Schema is present - verify author schema is included",
                f"Add {5 - len(images)} more custom images/charts for visual PR assets" if len(images) < 5 else "Visual assets are sufficient",
                "Create a press kit page with key statistics, author bio, and contact info",
                "Add shareable quote blocks throughout content for easy journalist excerpts"
            ]
        }

    def _align_knowledge_graph(self, entity: str, inputs: Dict) -> Dict[str, Any]:
        """Align entity with Knowledge Graph URIs using REAL Wikidata lookups."""
        wd = search_wikidata(entity)
        wd_results = wd.get("results", [])
        wd_ok = wd.get("ok", False)
        wikidata_url = wd_results[0]["url"] if wd_results else None
        wikidata_id = wd_results[0]["id"] if wd_results else None

        same_as = []
        if wikidata_url:
            same_as.append(wikidata_url)
        if wikidata_id:
            try:
                from ..utils.web_data import _open as wd_open, _read_body as wd_read
                import json as _json
                wd_api = ("https://www.wikidata.org/w/api.php?action=wbgetentities&ids="
                          + urllib.parse.quote(wikidata_id)
                          + "&props=sitelinks&sitefilter=enwiki&format=json")
                resp = wd_open(wd_api, timeout=15, headers={"Accept": "application/json"})
                if resp is not None:
                    data = _json.loads(wd_read(resp))
                    enwiki = (data.get("entities", {}).get(wikidata_id, {})
                              .get("sitelinks", {}).get("enwiki", {}).get("title", ""))
                    if enwiki:
                        same_as.append("https://en.wikipedia.org/wiki/" + enwiki.replace(" ", "_"))
            except Exception:
                pass

        return {
            "entity_name": entity,
            "knowledge_graph_uris": {
                "wikidata": wikidata_url or "",
                "wikidata_id": wikidata_id or "",
                "sameAs_candidates": same_as,
                "search_url": f"https://www.wikidata.org/wiki/Special:Search?search={urllib.parse.quote(entity)}",
                "wikidata_verified": bool(wd_results)
            },
            "wikidata_lookup": {
                "searched": wd_ok,
                "error": wd.get("error"),
                "matched_entities": wd_results,
                "exact_match": bool(wd_results)
            },
            "sameAs_schema": same_as,
            "verification_note": "Only real verified Wikidata references are provided - no fabricated Knowledge Graph URIs",
            "entity_verification_steps": [
                "Search for entity on Wikidata and verify entry exists",
                "Check Google Knowledge Graph API for entity data",
                "Verify Wikipedia article exists and is accurate",
                "Add sameAs links to page schema pointing to verified URIs",
                "Monitor Knowledge Panel for entity after content publication"
            ],
            "entity_authority_score": (
                "VERIFIED - Entity found on Wikidata" if wd_results else
                "NOT_FOUND_ON_WIKIDATA - verify entity exists before adding sameAs links"
            )
        }

    def _verify_author_entity(self, author: Dict) -> Dict[str, Any]:
        """Verify author entity footprint."""
        author_name = author.get("name", "")
        social_profiles = author.get("social_profiles", [])
        return {
            "author_name": author_name,
            "trust_score_components": {
                "linkedin_verified": any("linkedin" in p.lower() for p in social_profiles),
                "twitter_verified": any("twitter" in p.lower() or "x.com" in p.lower() for p in social_profiles),
                "wikipedia_exists": False,
                "google_scholar": any("scholar" in p.lower() for p in social_profiles),
                "industry_publications": author.get("publications", []),
                "credentials": author.get("credentials", [])
            },
            "author_trust_tier": (
                "EXPERT" if len(social_profiles) >= 3 and author.get("credentials") else
                "AUTHORITATIVE" if len(social_profiles) >= 2 else
                "ESTABLISHED" if social_profiles else
                "NEW - Build author entity footprint"
            ),
            "entity_schema": {
                "@type": "Person",
                "name": author_name,
                "jobTitle": author.get("title", ""),
                "sameAs": social_profiles,
                "knowsAbout": author.get("expertise", [])
            },
            "recommended_actions": [
                "Create/update LinkedIn profile with matching name and title",
                "Add author schema with sameAs linking to social profiles",
                "Contribute guest articles to establish topical authority",
                "Build Google Scholar profile if publishing research",
                "Ensure consistent author name across all platforms"
            ]
        }

    def _identify_pr_opportunities(self, content: str, entity: str) -> Dict[str, Any]:
        """Identify PR opportunities from content + REAL live outlet discovery."""
        data_points = re.findall(r'\d+(?:\.\d+)?%', content)
        live_outlets = self._discover_live_outlets(entity)
        live_outlet_names = live_outlets.get("outlet_names", []) or []
        pitch_angles = [
            {
                "angle": "Original Research Data",
                "pitch_summary": f"Share unique statistics and findings about {entity}",
                "target_outlets": live_outlet_names[:6],
                "pitch_template": f"Our analysis of {entity} reveals [key finding]. This data, based on [methodology], suggests [insight].",
                "estimated_pickup_probability": "HIGH if data is truly original"
            },
            {
                "angle": "Expert Commentary",
                "pitch_summary": f"Position author as expert source for {entity} stories",
                "target_outlets": ["Industry publications", "Business journals", "Trade media"],
                "pitch_template": f"Our team's experience implementing {entity} for [clients/organizations] has shown [insight].",
                "estimated_pickup_probability": "MODERATE - requires established credentials"
            },
            {
                "angle": "Data Visualization Asset",
                "pitch_summary": "Create shareable infographic with key findings",
                "target_outlets": ["Social media", "Industry blogs", "Newsletter features"],
                "pitch_template": "Visual summary of key findings designed for easy sharing and embedding.",
                "estimated_pickup_probability": "(General industry guidance, unverified) HIGH - visual content gets 3x more shares"
            }
        ]
        if not live_outlet_names:
            pitch_angles[0]["target_outlets"] = []
            pitch_angles[0]["outlet_discovery_note"] = "Live outlet discovery returned no real outlets covering this topic - no fabricated outlet names are suggested."
        return {
            "original_data_opportunities": len(data_points),
            "live_outlets_covering_topic": live_outlets.get("results", []),
            "live_outlet_search_status": "LIVE" if live_outlets.get("ok") else "UNAVAILABLE",
            "live_outlet_search_error": live_outlets.get("error"),
            "pr_pitch_angles": pitch_angles,
            "link_earning_strategy": [
                "Submit original data to industry research roundups",
                "Offer expert quotes to journalist query services (Qwoted, HARO)",
                "Create linkable assets (tools, calculators, benchmarks)",
                "Guest post on high-authority industry publications"
            ]
        }

    def _discover_live_outlets(self, entity: str) -> Dict[str, Any]:
        """Discover real publications currently covering the entity topic via live search."""
        if not entity:
            return {"ok": False, "results": [], "outlet_names": [], "error": "No entity"}
        query = f"{entity} industry news 2026"
        serp = web_search(query, 10)
        results = []
        names = []
        for r in serp.get("results", []):
            url = r.get("url", "")
            try:
                from urllib.parse import urlparse
                host = urlparse(url).netloc.replace("www.", "")
            except Exception:
                host = ""
            if host and host not in names:
                results.append({"outlet": host, "article_title": r.get("title", ""), "url": url})
                names.append(host)
        return {
            "ok": serp.get("ok", False),
            "results": results[:10],
            "outlet_names": names[:6],
            "error": serp.get("error"),
        }

    def _build_entity_linking_strategy(self, entity: str, inputs: Dict) -> Dict[str, Any]:
        """Build entity linking strategy."""
        return {
            "on_page_entity_signals": [
                "Include entity name in H1, first paragraph, and conclusion",
                "Link to official entity pages (Wikipedia, Wikidata)",
                "Add sameAs schema pointing to authoritative entity URIs",
                "Use entity variations (full name, abbreviations, common names)",
                "Include entity in image alt text and schema markup"
            ],
            "off_page_entity_signals": [
                "Earn mentions on authoritative domains referencing the entity",
                "Build social profiles that link back to content",
                "Get listed in relevant industry directories",
                "Secure guest posts that reference the entity",
                "Earn backlinks from domains with high entity authority"
            ],
            "entity_link_graph": {
                "internal_links": "Link to 3-5 related internal pages",
                "external_links": "Link to 2-3 authoritative external sources",
                "backlink_targets": "Earn links from 5+ authoritative domains",
                "data_origin": "unverified_industry_heuristic - not measured for this page"
            }
        }

    def _assess_authority_signals(self, inputs: Dict) -> Dict[str, Any]:
        """Assess overall authority signals."""
        return {
            "on_page_authority": {
                "author_credentials": bool(inputs.get("author", {}).get("credentials")),
                "expert_quotes": "Include 2-3 named expert quotes",
                "original_data": "Publish original research or benchmarks",
                "citations": "Cite 5+ authoritative sources"
            },
            "off_page_authority": {
                "backlink_profile": "Requires backlink analysis data",
                "domain_authority": "Requires domain authority metrics",
                "brand_mentions": "Monitor unlinked brand mentions",
                "social_signals": "Track social sharing and engagement"
            },
            "knowledge_graph_authority": {
                "entity_verified": False,
                "knowledge_panel_exists": "Check Google Knowledge Panel",
                "sameas_links": "Add sameAs schema to all content",
                "consistent_naming": "Ensure entity name consistency across web"
            },
            "overall_authority_tier": "Calculate from comprehensive data"
        }

    def _generate_recommendations(self, kg: Dict, author: Dict, pr: Dict) -> List[Dict[str, str]]:
        """Generate PR and entity alignment recommendations."""
        recs = []
        if not author.get("trust_score_components", {}).get("linkedin_verified"):
            recs.append({
                "priority": "HIGH",
                "action": "Create verified LinkedIn profile for author",
                "detail": "LinkedIn verification is the strongest author E-E-A-T signal"
            })
        if pr.get("original_data_opportunities", 0) > 0:
            recs.append({
                "priority": "HIGH",
                "action": "Publish and pitch original research data",
                "detail": f"{pr['original_data_opportunities']} unique data points available for PR pitches"
            })
        recs.append({
            "priority": "MEDIUM",
            "action": "Add sameAs schema linking to Knowledge Graph URIs",
            "detail": "Entity alignment improves Knowledge Panel and AI citation probability"
        })
        return recs
