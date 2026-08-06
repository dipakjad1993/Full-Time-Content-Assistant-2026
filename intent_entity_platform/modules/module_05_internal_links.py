"""
Module 5: Internal Link & Cannibalization Defense Engine
Crawls sitemap and Search Console data for cannibalization and link planning.
"""
import re
import hashlib
from typing import List, Dict, Any, Optional
from ..utils.text_analytics import (
    tokenize_words, cosine_similarity, tf_idf_vectorize,
    generate_internal_link_plan
)
from ..utils.web_data import verify_url


class InternalLinkCannibalization:
    """Module 5: Internal Link & Cannibalization Defense Engine"""

    def __init__(self):
        self.module_id = "M05"
        self.module_name = "Internal Link & Cannibalization Defense Engine"

    def analyze(self, inputs: Dict[str, Any], serp_data: Dict) -> Dict[str, Any]:
        """Full internal link and cannibalization analysis pipeline."""
        seed_phrase = inputs.get("seed_phrase", "")
        primary_entity = inputs.get("primary_entity", "")
        existing_pages = inputs.get("existing_pages", [])
        sitemap_data = inputs.get("sitemap_data", [])
        gsc_data = inputs.get("gsc_data", {})
        url_data = inputs.get("_url_data", None)

        cannibalization = self._detect_cannibalization(seed_phrase, primary_entity, existing_pages, gsc_data)
        link_plan = self._generate_link_plan(seed_phrase, primary_entity, existing_pages)
        page_authority = self._assess_page_authority(existing_pages, gsc_data)
        internal_link_graph = self._build_internal_link_graph(existing_pages)
        fresh_content_strategy = self._design_fresh_content_link_strategy(seed_phrase, existing_pages)

        url_link_analysis = self._analyze_url_links(url_data, seed_phrase, primary_entity) if url_data else None

        result = {
            "module": self.module_id,
            "module_name": self.module_name,
            "cannibalization_detection": cannibalization,
            "link_plan": link_plan,
            "page_authority_assessment": page_authority,
            "internal_link_graph": internal_link_graph,
            "fresh_content_strategy": fresh_content_strategy,
            "defense_directives": self._generate_defense_directives(cannibalization, link_plan),
            "recommendations": self._generate_recommendations(cannibalization, link_plan, page_authority),
            "implementation_steps": self._generate_implementation_steps(cannibalization, link_plan, fresh_content_strategy),
            "where_to_add": self._generate_where_to_add(link_plan, fresh_content_strategy),
            "detailed_analysis": self._generate_detailed_analysis(cannibalization, link_plan, page_authority, internal_link_graph, fresh_content_strategy)
        }

        if url_data and url_link_analysis:
            result["url_link_analysis"] = url_link_analysis
            result["recommendations"] = self._merge_link_url_recommendations(result["recommendations"], url_link_analysis)
            result["detailed_analysis"]["url_link_insights"] = url_link_analysis

        return result

    def _analyze_url_links(self, url_data: Dict, seed_phrase: str, primary_entity: str) -> Dict[str, Any]:
        """Deep analysis of actual URL link structure and equity distribution."""
        url = url_data.get("url", "")
        links = url_data.get("links", [])
        word_count = url_data.get("word_count", 0)
        h2s = url_data.get("h2s", [])

        if not url:
            return {"error": "No URL provided for link analysis"}

        base_domain = ""
        if "://" in url:
            parts = url.split("://")
            if len(parts) > 1:
                base_domain = parts[1].split("/")[0]

        internal_links = []
        external_links = []
        for link in links:
            if not link:
                continue
            if base_domain and base_domain in link:
                internal_links.append(link)
            else:
                external_links.append(link)

        total_links = len(links)
        link_density = total_links / max(1, word_count / 100)

        internal_domains = set()
        for link in internal_links:
            if "://" in link:
                domain = link.split("://")[1].split("/")[0]
                internal_domains.add(domain)

        external_domains = set()
        external_tlds = {"com": 0, "org": 0, "edu": 0, "gov": 0, "net": 0, "io": 0, "co": 0, "other": 0}
        for link in external_links:
            if "://" in link:
                domain = link.split("://")[1].split("/")[0]
                external_domains.add(domain)
                tld = domain.split(".")[-1].lower() if "." in domain else "other"
                if tld in external_tlds:
                    external_tlds[tld] += 1
                else:
                    external_tlds["other"] += 1

        gov_edu_links = external_tlds.get("edu", 0) + external_tlds.get("gov", 0)

        link_issues = []
        if total_links == 0:
            link_issues.append("No links found on page. Add 5-10 internal and 3-5 external links.")
        if len(internal_links) < 3:
            link_issues.append(f"Only {len(internal_links)} internal link(s) found. Add 5-10 internal links for link equity flow.")
        if len(external_links) < 2:
            link_issues.append(f"Only {len(external_links)} external link(s) found. Add 3-5 authoritative external citations.")
        if gov_edu_links == 0 and len(external_links) > 0:
            link_issues.append("No .edu or .gov external links. Add 1-2 links to authoritative academic/government sources.")
        if link_density > 5:
            link_issues.append(f"Link density ({link_density:.1f} links per 100 words) is high. Reduce to avoid appearing spammy.")
        if link_density < 1 and total_links > 0:
            link_issues.append(f"Link density ({link_density:.1f} links per 100 words) is low. Add more contextual links.")
        if len(h2s) > 0 and total_links < len(h2s):
            link_issues.append(f"Only {total_links} total links for {len(h2s)} H2 sections. Add 1-2 links per H2 section.")

        anchor_text_analysis = self._analyze_anchor_texts(links, seed_phrase, primary_entity)

        # REAL link health verification
        link_health = self._verify_link_health(list(dict.fromkeys([l for l in links if l.startswith("http")]))[:12])

        link_quality_score = 0.0
        if len(internal_links) >= 5:
            link_quality_score += 0.25
        if len(external_links) >= 3:
            link_quality_score += 0.25
        if gov_edu_links >= 1:
            link_quality_score += 0.15
        if 1 <= link_density <= 4:
            link_quality_score += 0.15
        if len(external_domains) >= 3:
            link_quality_score += 0.10
        if len(internal_domains) <= 2:
            link_quality_score += 0.10

        return {
            "url": url,
            "total_links": total_links,
            "internal_links_count": len(internal_links),
            "external_links_count": len(external_links),
            "link_density_per_100_words": round(link_density, 2),
            "link_density_benchmark": "Optimal: 1-4 links per 100 words",
            "internal_domains": list(internal_domains),
            "internal_domains_count": len(internal_domains),
            "external_domains": list(external_domains),
            "external_domains_count": len(external_domains),
            "external_tld_distribution": external_tlds,
            "gov_edu_links": gov_edu_links,
            "gov_edu_benchmark": "Recommended: 1-2 .edu/.gov links for authority",
            "link_quality_score": round(link_quality_score, 3),
            "link_quality_tier": (
                "EXCELLENT - Well-balanced link profile" if link_quality_score > 0.8 else
                "GOOD - Minor link improvements needed" if link_quality_score > 0.6 else
                "NEEDS_WORK - Multiple link issues" if link_quality_score > 0.4 else
                "POOR - Major link restructuring required"
            ),
            "anchor_text_analysis": anchor_text_analysis,
            "link_health_verification": link_health,
            "link_issues": link_issues,
            "link_issues_count": len(link_issues),
            "equity_distribution": {
                "internal_equity_flow": "Links pass equity between pages on same domain",
                "external_equity_outflow": f"{len(external_links)} links pass equity to external domains",
                "gov_edu_authority_boost": f"{gov_edu_links} .edu/.gov links provide authority signals",
                "recommendation": "Add outbound links from highest-authority existing pages to this content"
            },
            "specific_recommendations": self._generate_link_url_recommendations(url_data, seed_phrase, primary_entity)
        }

    def _verify_link_health(self, urls: List[str]) -> Dict[str, Any]:
        """Live HTTP verification of links found on the page."""
        checks = []
        ok = 0
        broken = 0
        for u in urls:
            res = verify_url(u, timeout=8)
            status = res.get("status_code")
            reachable = bool(res.get("reachable"))
            checks.append({
                "url": u,
                "status_code": status,
                "reachable": reachable,
            })
            if reachable and status == 200:
                ok += 1
            else:
                broken += 1
        return {
            "urls_checked": len(checks),
            "live": len(checks) > 0,
            "reachable_200": ok,
            "broken_or_redirected": broken,
            "broken_links": [c["url"] for c in checks if not c["reachable"]][:10],
            "details": checks,
        }

    def _analyze_anchor_texts(self, links: List[str], seed_phrase: str, primary_entity: str) -> Dict[str, Any]:
        """Analyze anchor text quality and diversity."""
        anchor_text_patterns = {
            "exact_match": 0,
            "partial_match": 0,
            "brand": 0,
            "url": 0,
            "generic": 0,
            "other": 0
        }

        seed_words = set(tokenize_words(seed_phrase.lower()))
        entity_words = set(tokenize_words(primary_entity.lower())) if primary_entity else set()

        for link in links:
            link_lower = link.lower()
            link_words = set(tokenize_words(link_lower))

            if seed_phrase.lower() in link_lower:
                anchor_text_patterns["exact_match"] += 1
            elif seed_words & link_words:
                anchor_text_patterns["partial_match"] += 1
            elif any(brand in link_lower for brand in ["company", "brand", "official", "homepage"]):
                anchor_text_patterns["brand"] += 1
            elif link_lower.startswith("http"):
                anchor_text_patterns["url"] += 1
            elif any(generic in link_lower for generic in ["click here", "read more", "learn more", "this article", "here"]):
                anchor_text_patterns["generic"] += 1
            else:
                anchor_text_patterns["other"] += 1

        total = sum(anchor_text_patterns.values())
        diversity_score = sum(1 for v in anchor_text_patterns.values() if v > 0) / max(1, len(anchor_text_patterns))

        return {
            "anchor_text_distribution": anchor_text_patterns,
            "diversity_score": round(diversity_score, 3),
            "diversity_benchmark": "Ideal: 4+ anchor text types with no single type >50%",
            "generic_anchor_count": anchor_text_patterns["generic"],
            "generic_anchor_benchmark": "Reduce generic anchors ('click here', 'read more') to <20%",
            "recommendation": "Use varied anchor text: exact match, partial match, natural, and branded"
        }

    def _generate_link_url_recommendations(self, url_data: Dict, seed_phrase: str, primary_entity: str) -> List[Dict[str, str]]:
        """Generate specific link recommendations based on actual URL content."""
        recs = []
        links = url_data.get("links", [])
        word_count = url_data.get("word_count", 0)
        url = url_data.get("url", "")

        base_domain = ""
        if url and "://" in url:
            base_domain = url.split("://")[1].split("/")[0]

        internal_count = sum(1 for l in links if base_domain and base_domain in l)
        external_count = len(links) - internal_count

        if internal_count < 5:
            recs.append({
                "priority": "HIGH",
                "action": f"Add {5 - internal_count}+ internal links to related pages on your site",
                "detail": f"Only {internal_count} internal link(s) found. Add contextual links to 5-10 related pages for link equity flow."
            })

        if external_count < 3:
            recs.append({
                "priority": "MEDIUM",
                "action": f"Add {3 - external_count}+ external links to authoritative sources",
                "detail": f"Only {external_count} external link(s) found. Link to 3-5 authoritative sources (Gartner, Forrester, academic) for trust signals."
            })

        gov_edu = sum(1 for l in links if any(tld in l for tld in [".edu", ".gov"]))
        if gov_edu == 0:
            recs.append({
                "priority": "MEDIUM",
                "action": "Add 1-2 links to .edu or .gov domains for authority signals",
                "detail": "No academic or government links found. These provide strong trust signals."
            })

        generic_anchors = sum(1 for l in links if any(g in l.lower() for g in ["click here", "read more", "learn more", "here"]))
        if generic_anchors > 0:
            recs.append({
                "priority": "MEDIUM",
                "action": f"Replace {generic_anchors} generic anchor text with descriptive anchors",
                "detail": "Generic anchors ('click here', 'read more') waste link equity. Use descriptive text instead."
            })

        if len(links) == 0:
            recs.append({
                "priority": "HIGH",
                "action": "Add 5-10 contextual links (3-5 internal, 2-3 external)",
                "detail": "No links found. Internal links pass equity; external links signal authority and relevance."
            })

        return recs

    def _merge_link_url_recommendations(self, existing_recs: List[Dict], url_analysis: Dict) -> List[Dict[str, str]]:
        """Merge URL-specific link recommendations with existing recommendations."""
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

    def _detect_cannibalization(self, seed: str, entity: str, existing_pages: List[Dict],
                                   gsc_data: Dict) -> Dict[str, Any]:
        """Detect pages that may cannibalize the new content."""
        if not existing_pages:
            return {
                "cannibalization_risk": "LOW",
                "competing_pages": [],
                "total_competing": 0,
                "recommendation": "No existing pages detected - proceed with new content"
            }

        target_words = set(tokenize_words(f"{seed} {entity}"))
        target_words -= {"the", "a", "an", "is", "are", "for", "and", "or", "of", "in", "to", "with", "best", "top"}

        competing_pages = []
        for page in existing_pages:
            page_words = set(tokenize_words(
                f"{page.get('title', '')} {page.get('meta_description', '')} {page.get('snippet', '')}"
            ))
            overlap = len(target_words & page_words)
            overlap_ratio = overlap / max(1, len(target_words))
            if overlap_ratio > 0.3:
                competing_pages.append({
                    "url": page.get("url", ""),
                    "title": page.get("title", ""),
                    "overlap_score": round(overlap_ratio, 3),
                    "overlapping_terms": list(target_words & page_words)[:10],
                    "current_position": page.get("position", "N/A"),
                    "current impressions": page.get("impressions", 0),
                    "current clicks": page.get("clicks", 0),
                    "cannibalization_severity": (
                        "CRITICAL" if overlap_ratio > 0.7 else
                        "HIGH" if overlap_ratio > 0.5 else
                        "MODERATE" if overlap_ratio > 0.3 else "LOW"
                    ),
                    "recommended_action": self._recommend_cannibalization_action(overlap_ratio, page)
                })

        competing_pages.sort(key=lambda x: x["overlap_score"], reverse=True)

        gsc_conflict_pages = []
        if gsc_data.get("queries"):
            for query_data in gsc_data["queries"]:
                if any(tw in query_data.get("query", "").lower() for tw in target_words):
                    for page_url in query_data.get("urls", []):
                        gsc_conflict_pages.append({
                            "query": query_data["query"],
                            "url": page_url,
                            "clicks": query_data.get("clicks", 0),
                            "impressions": query_data.get("impressions", 0),
                            "position": query_data.get("position", 0)
                        })

        overall_risk = "LOW"
        if len(competing_pages) > 3 or any(p["overlap_score"] > 0.7 for p in competing_pages):
            overall_risk = "CRITICAL"
        elif len(competing_pages) > 1 or any(p["overlap_score"] > 0.5 for p in competing_pages):
            overall_risk = "HIGH"
        elif competing_pages:
            overall_risk = "MODERATE"

        return {
            "cannibalization_risk": overall_risk,
            "competing_pages": competing_pages[:10],
            "total_competing": len(competing_pages),
            "gsc_conflict_queries": gsc_conflict_pages[:10],
            "severity_breakdown": {
                "critical": sum(1 for p in competing_pages if p["cannibalization_severity"] == "CRITICAL"),
                "high": sum(1 for p in competing_pages if p["cannibalization_severity"] == "HIGH"),
                "moderate": sum(1 for p in competing_pages if p["cannibalization_severity"] == "MODERATE")
            },
            "defense_strategy": self._determine_defense_strategy(overall_risk, competing_pages),
            "estimated_organic_split": f"{100 // max(1, len(competing_pages) + 1)}% per page" if competing_pages else "100% (no competition)"
        }

    def _recommend_cannibalization_action(self, overlap_ratio: float, page: Dict) -> str:
        """Recommend action for cannibalizing page."""
        if overlap_ratio > 0.7:
            return "CONSIDER_MERGE: Pages are too similar - consider merging into single comprehensive resource"
        elif overlap_ratio > 0.5:
            return "DIFFERENTIATE: Sharply differentiate content angle, target different sub-intent"
        elif overlap_ratio > 0.3:
            return "LINK_STRATEGY: Add clear internal linking to establish topical hierarchy"
        return "MONITOR: Track ranking fluctuations and user behavior for both pages"

    def _determine_defense_strategy(self, risk: str, competing: List[Dict]) -> Dict[str, str]:
        """Determine the cannibalization defense strategy."""
        strategies = {
            "CRITICAL": {
                "primary": "Content consolidation or radical differentiation",
                "secondary": "301 redirect weaker page to stronger page",
                "tertiary": "Establish clear canonical and internal linking hierarchy",
                "timeline": "Address within 1 week before publishing"
            },
            "HIGH": {
                "primary": "Differentiate content angle and target sub-intent",
                "secondary": "Add unique data, expert quotes, or interactive elements",
                "tertiary": "Implement clear internal linking with descriptive anchor text",
                "timeline": "Address within 2 weeks"
            },
            "MODERATE": {
                "primary": "Establish clear topical hierarchy with internal links",
                "secondary": "Differentiate at least 3 H2 sections uniquely",
                "tertiary": "Monitor GSC data for ranking fluctuations",
                "timeline": "Address within 1 month"
            },
            "LOW": {
                "primary": "Standard internal linking optimization",
                "secondary": "Add cross-reference links between related pages",
                "tertiary": "Continue monitoring for emerging overlap",
                "timeline": "Ongoing monitoring"
            }
        }
        return strategies.get(risk, strategies["LOW"])

    def _generate_link_plan(self, seed: str, entity: str, existing_pages: List[Dict]) -> Dict[str, Any]:
        """Generate comprehensive internal linking plan."""
        if not existing_pages:
            return {
                "outbound_links": [],
                "inbound_links": [],
                "anchor_text_recommendations": [],
                "link_equity_score": 0
            }

        new_page_url = inputs.get("new_page_url", f"/{seed.lower().replace(' ', '-')}")
        link_plan = generate_internal_link_plan(existing_pages, f"{seed} {entity}", new_page_url)

        anchor_text_variations = self._generate_anchor_text_variations(seed, entity)

        page_priority_scores = []
        for page in existing_pages:
            score = self._calculate_link_priority_score(page, seed, entity)
            page_priority_scores.append({
                "url": page.get("url", ""),
                "title": page.get("title", ""),
                "link_priority_score": score["score"],
                "recommended_anchor": score["anchor"],
                "link_direction": score["direction"],
                "implementation_priority": score["priority"]
            })
        page_priority_scores.sort(key=lambda x: x["link_priority_score"], reverse=True)

        return {
            "outbound_from_new": link_plan.get("outbound_links", []),
            "inbound_to_new": link_plan.get("inbound_recommendations", []),
            "page_priority_scores": page_priority_scores[:15],
            "anchor_text_variations": anchor_text_variations,
            "total_link_opportunities": len(page_priority_scores),
            "high_priority_links": [p for p in page_priority_scores if p["link_priority_score"] > 0.5][:5],
            "link_equity_distribution": self._calculate_link_equity_distribution(page_priority_scores),
            "implementation_order": self._prioritize_link_implementations(page_priority_scores)
        }

    def _calculate_link_priority_score(self, page: Dict, seed: str, entity: str) -> Dict[str, Any]:
        """Calculate priority score for a linking opportunity."""
        page_words = set(tokenize_words(f"{page.get('title', '')} {page.get('snippet', '')}"))
        target_words = set(tokenize_words(f"{seed} {entity}"))
        relevance = len(page_words & target_words) / max(1, len(target_words))
        page_authority = min(1.0, (page.get("domain_authority", 50) / 100) +
                           (page.get("page_authority", 30) / 100))
        score = (relevance * 0.5 + page_authority * 0.3 + 0.2)
        anchor = f"{entity.title()} best practices" if relevance > 0.5 else page.get("title", entity)[:50]
        direction = "outbound_from_new" if score > 0.5 else "inbound_to_new"
        priority = "CRITICAL" if score > 0.7 else "HIGH" if score > 0.5 else "MEDIUM" if score > 0.3 else "LOW"
        return {
            "score": round(min(1.0, score), 3),
            "anchor": anchor,
            "direction": direction,
            "priority": priority
        }

    def _generate_anchor_text_variations(self, seed: str, entity: str) -> List[Dict[str, str]]:
        """Generate varied anchor text recommendations."""
        variations = [
            {"anchor": entity.title(), "type": "exact_match", "usage": "Primary linking context"},
            {"anchor": f"the best {entity.lower()} solutions", "type": "partial_match", "usage": "Comparison sections"},
            {"anchor": f"implementing {entity.lower()}", "type": "partial_match", "usage": "How-to sections"},
            {"anchor": f"{entity.lower()} for enterprise", "type": "partial_match", "usage": "Enterprise-focused content"},
            {"anchor": "this comprehensive guide", "type": "natural", "usage": "General references"},
            {"anchor": "learn more about this solution", "type": "natural", "usage": "CTA-style links"},
            {"anchor": f"{seed.lower()}", "type": "keyword_rich", "usage": "Contextual mentions"},
        ]
        return variations

    def _calculate_link_equity_distribution(self, page_scores: List[Dict]) -> Dict[str, Any]:
        """Calculate how link equity should be distributed."""
        total_score = sum(p["link_priority_score"] for p in page_scores)
        if total_score == 0:
            return {"distribution": [], "total_equity": 0}
        distribution = []
        for page in page_scores[:10]:
            equity_share = page["link_priority_score"] / total_score
            distribution.append({
                "url": page["url"],
                "equity_share": round(equity_share, 4),
                "recommended_links": max(1, round(equity_share * 10))
            })
        return {
            "distribution": distribution,
            "total_equity": round(total_score, 3),
            "concentration_risk": "HIGH" if len(distribution) > 0 and distribution[0]["equity_share"] > 0.4 else "LOW"
        }

    def _prioritize_link_implementations(self, page_scores: List[Dict]) -> List[Dict[str, Any]]:
        """Prioritize link implementation order."""
        prioritized = []
        for page in page_scores:
            prioritized.append({
                "url": page["url"],
                "action": f"Add {'outbound' if page['link_direction'] == 'outbound_from_new' else 'inbound'} link",
                "anchor_text": page["recommended_anchor"],
                "priority": page["implementation_priority"],
                "timeline": "day_1" if page["implementation_priority"] == "CRITICAL" else
                           "week_1" if page["implementation_priority"] == "HIGH" else "month_1"
            })
        return prioritized[:10]

    def _assess_page_authority(self, existing_pages: List[Dict], gsc_data: Dict) -> Dict[str, Any]:
        """Assess authority of existing pages for link equity."""
        if not existing_pages:
            return {"authority_distribution": [], "average_authority": 0}

        authority_data = []
        for page in existing_pages:
            gsc_metrics = {}
            if gsc_data.get("pages"):
                for pg in gsc_data["pages"]:
                    if pg.get("url") == page.get("url"):
                        gsc_metrics = pg
                        break
            authority = {
                "url": page.get("url", ""),
                "title": page.get("title", ""),
                "estimated_authority": min(100, (
                    (page.get("domain_authority", 50) * 0.4) +
                    (page.get("page_authority", 30) * 0.3) +
                    (min(50, gsc_metrics.get("clicks", 0) / 10) * 0.2) +
                    (min(30, gsc_metrics.get("impressions", 0) / 100) * 0.1)
                )),
                "gsc_clicks": gsc_metrics.get("clicks", 0),
                "gsc_impressions": gsc_metrics.get("impressions", 0),
                "gsc_position": gsc_metrics.get("position", "N/A"),
                "link_value_tier": "HIGH" if page.get("domain_authority", 0) > 60 else
                                  "MEDIUM" if page.get("domain_authority", 0) > 40 else "LOW"
            }
            authority_data.append(authority)
        authority_data.sort(key=lambda x: x["estimated_authority"], reverse=True)

        return {
            "authority_distribution": authority_data[:15],
            "average_authority": round(sum(a["estimated_authority"] for a in authority_data) / max(1, len(authority_data)), 2),
            "high_authority_pages": [a for a in authority_data if a["estimated_authority"] > 60][:5],
            "link_equity_available": sum(a["estimated_authority"] for a in authority_data)
        }

    def _build_internal_link_graph(self, existing_pages: List[Dict]) -> Dict[str, Any]:
        """Build a graph of internal link relationships."""
        link_graph = {"nodes": [], "edges": [], "orphan_pages": [], "hub_pages": []}
        for page in existing_pages:
            link_graph["nodes"].append({
                "url": page.get("url", ""),
                "title": page.get("title", "")[:50],
                "inbound_count": page.get("inbound_links", 0),
                "outbound_count": page.get("outbound_links", 0),
                "is_hub": page.get("inbound_links", 0) > 5
            })
        hub_pages = [n for n in link_graph["nodes"] if n["is_hub"]]
        orphan_pages = [n for n in link_graph["nodes"] if n["inbound_count"] == 0 and n["outbound_count"] == 0]
        link_graph["hub_pages"] = hub_pages
        link_graph["orphan_pages"] = orphan_pages
        return {
            "graph_summary": {
                "total_nodes": len(link_graph["nodes"]),
                "hub_pages": len(hub_pages),
                "orphan_pages": len(orphan_pages),
                "average_links_per_page": round(
                    sum(n["inbound_count"] + n["outbound_count"] for n in link_graph["nodes"]) /
                    max(1, len(link_graph["nodes"])), 2
                )
            },
            "link_graph": link_graph,
            "new_page_integration": {
                "target_hub_pages": [h["url"] for h in hub_pages[:5]],
                "orphan_rescue_opportunities": [o["url"] for o in orphan_pages[:5]],
                "recommended_internal_links_day_1": 5,
                "recommended_internal_links_month_1": 10
            }
        }

    def _design_fresh_content_link_strategy(self, seed: str, existing_pages: List[Dict]) -> Dict[str, Any]:
        """Design link strategy for fresh content deployment."""
        return {
            "day_1_actions": [
                "Add outbound links from 3 highest-authority existing pages to new content",
                "Add contextual internal links within existing related articles",
                "Update XML sitemap with new URL and set priority to 0.8",
                "Submit to Google Indexing API and IndexNow"
            ],
            "week_1_actions": [
                "Add new content link to site-wide navigation or featured content widget",
                "Update 5 older articles with contextual links to new content",
                "Add new content to relevant category/tag pages",
                "Share on social profiles linked to author schema"
            ],
            "month_1_actions": [
                "Monitor GSC for ranking and impression data",
                "Update internal links based on performance data",
                "Add links from new content back to 3 supporting older pages",
                "Review and optimize anchor text based on ranking keywords"
            ],
            "anchor_text_strategy": {
                "primary": f"{seed.title()}",
                "secondary": [f"best {seed.lower()}", f"{seed.lower()} guide", "this comprehensive resource"],
                "avoid": ["click here", "read more", "this article", "learn more"]
            }
        }

    def _generate_defense_directives(self, cannibalization: Dict, link_plan: Dict) -> List[Dict[str, str]]:
        """Generate defense directives for cannibalization."""
        directives = []
        risk = cannibalization.get("cannibalization_risk", "LOW")
        if risk in ["CRITICAL", "HIGH"]:
            directives.append({
                "directive": "CONTENT_DIFFERENTIATION",
                "action": f"Sharply differentiate new content from {cannibalization.get('total_competing', 0)} competing pages",
                "priority": "CRITICAL",
                "deadline": "Before publishing"
            })
            directives.append({
                "directive": "CANONICAL_STRATEGY",
                "action": "Set clear canonical URLs and internal linking hierarchy",
                "priority": "HIGH",
                "deadline": "Within 48 hours of publishing"
            })
        for page in cannibalization.get("competing_pages", [])[:3]:
            directives.append({
                "directive": "LINK_INTEGRATION",
                "action": f"Add contextual link between new content and {page['url'][:60]}",
                "priority": page["cannibalization_severity"],
                "deadline": "Day 1"
            })
        return directives

    def _generate_recommendations(self, cannibalization: Dict, link_plan: Dict, authority: Dict) -> List[Dict[str, str]]:
        """Generate recommendations."""
        recs = []
        if cannibalization.get("cannibalization_risk") == "CRITICAL":
            recs.append({
                "priority": "CRITICAL",
                "action": "Resolve critical cannibalization before publishing",
                "detail": f"{cannibalization.get('total_competing', 0)} pages with high content overlap detected"
            })
        high_priority = link_plan.get("high_priority_links", [])
        if high_priority:
            recs.append({
                "priority": "HIGH",
                "action": f"Implement {len(high_priority)} high-priority internal links on day 1",
                "detail": f"Top link from: {high_priority[0]['url'][:60]}"
            })
        if authority.get("orphan_pages", []):
            recs.append({
                "priority": "MEDIUM",
                "action": f"Rescue {len(authority.get('orphan_pages', []))} orphan pages with new internal links",
                "detail": "Orphan pages receive zero link equity - connect them immediately"
            })
        return recs

    def _generate_implementation_steps(self, cannibalization: Dict, link_plan: Dict,
                                        fresh_content_strategy: Dict) -> List[str]:
        steps = []
        steps.append("Step 1: Resolve critical cannibalization by differentiating content angles or merging overlapping pages before publishing")
        steps.append("Step 2: Add outbound links from 3 highest-authority existing pages to the new content on day 1")
        steps.append("Step 3: Add contextual internal links within 5 existing related articles pointing to the new content")
        steps.append("Step 4: Set clear canonical URLs and establish internal linking hierarchy between competing pages")
        steps.append("Step 5: Use varied anchor text (exact match, partial match, natural) across all internal links")
        steps.append("Step 6: Update XML sitemap with the new URL and set priority to 0.8")
        steps.append("Step 7: Submit new URL to Google Indexing API and IndexNow for faster indexing")
        steps.append("Step 8: Add the new content link to site-wide navigation or featured content widget within week 1")
        steps.append("Step 9: Add new content to relevant category and tag pages within the site structure")
        steps.append("Step 10: Rescue orphan pages by adding contextual links from related content within month 1")
        steps.append("Step 11: Monitor Google Search Console for ranking fluctuations and cannibalization signals within 2 weeks")
        steps.append("Step 12: Optimize anchor text based on actual ranking keywords observed in GSC data after 30 days")
        return steps

    def _generate_where_to_add(self, link_plan: Dict, fresh_content_strategy: Dict) -> List[str]:
        locations = []
        locations.append("Add outbound links from the 3 highest-authority existing pages within their body content sections")
        locations.append("Place contextual internal links within existing related articles' H2 sections using natural anchor text")
        locations.append("Add the new content link to site-wide navigation, header, footer, or featured content widget")
        locations.append("Include internal links from the new content's body paragraphs to 3-5 supporting older pages")
        locations.append("Add the new content URL to relevant category and tag archive pages")
        locations.append("Place cross-reference links between competing pages to establish topical hierarchy")
        locations.append("Add new content to XML sitemap at /sitemap.xml with priority 0.8")
        locations.append("Include contextual links in sidebar or 'Related Content' sections on existing pages")
        locations.append("Add breadcrumbs with BreadcrumbList schema linking to parent category pages")
        locations.append("Place 'Read More' links from high-traffic existing pages to the new content")
        return locations

    def _generate_detailed_analysis(self, cannibalization: Dict, link_plan: Dict,
                                     page_authority: Dict, internal_link_graph: Dict,
                                     fresh_content_strategy: Dict) -> Dict[str, Any]:
        return {
            "cannibalization_insights": {
                "risk_level": cannibalization.get("cannibalization_risk", "LOW"),
                "total_competing": cannibalization.get("total_competing", 0),
                "estimated_organic_split": cannibalization.get("estimated_organic_split", "N/A"),
                "benchmark": "Sites with 0-1 competing pages per query see 60-80% higher organic CTR than sites with 3+ competitors",
                "statistical_range": f"Cannibalization risk: {cannibalization.get('cannibalization_risk', 'LOW')} with {cannibalization.get('total_competing', 0)} competing pages",
                "expert_recommendation": "Address CRITICAL cannibalization before publishing - merge or radically differentiate overlapping content",
                "common_mistakes": ["Publishing new content without checking for existing overlapping pages", "Ignoring GSC query overlap data", "Not establishing clear canonical hierarchy"],
                "success_metrics": ["Cannibalization risk reduced to LOW", "Zero CRITICAL competing pages", "Organic CTR improvement > 20%"]
            },
            "link_plan_insights": {
                "total_link_opportunities": link_plan.get("total_link_opportunities", 0),
                "high_priority_links": len(link_plan.get("high_priority_links", [])),
                "anchor_text_variations": len(link_plan.get("anchor_text_variations", [])),
                "benchmark": "New content should receive 5 internal links on day 1 and 10+ within month 1 for proper link equity flow",
                "statistical_range": f"Link opportunities: {link_plan.get('total_link_opportunities', 0)} (target: 10+ high-priority)",
                "expert_recommendation": "Implement 3-5 high-priority links on day 1 with exact match and partial match anchor text variations",
                "common_mistakes": ["Using identical anchor text for all internal links", "Not linking from highest-authority pages", "Ignoring orphan page rescue"],
                "success_metrics": ["5+ links on day 1", "10+ links within month 1", "Anchor text diversity > 3 variations"]
            },
            "page_authority_insights": {
                "average_authority": page_authority.get("average_authority", 0),
                "link_equity_available": page_authority.get("link_equity_available", 0),
                "high_authority_pages": len(page_authority.get("high_authority_pages", [])),
                "benchmark": "Pages with DA 60+ provide highest link equity; aim to link from 3+ high-authority pages within week 1",
                "statistical_range": f"Average page authority: {page_authority.get('average_authority', 0):.0f}/100 (target: 50+)",
                "expert_recommendation": "Prioritize link acquisition from pages with DA > 60 for maximum link equity transfer",
                "common_mistakes": ["Linking only from low-authority pages", "Ignoring page authority distribution", "Not monitoring link equity flow"],
                "success_metrics": ["Average authority > 50", "3+ high-authority links", "Link equity distributed across 10+ pages"]
            },
            "internal_link_graph_insights": {
                "total_nodes": internal_link_graph.get("graph_summary", {}).get("total_nodes", 0),
                "hub_pages": internal_link_graph.get("graph_summary", {}).get("hub_pages", 0),
                "orphan_pages": internal_link_graph.get("graph_summary", {}).get("orphan_pages", 0),
                "average_links": internal_link_graph.get("graph_summary", {}).get("average_links_per_page", 0),
                "benchmark": "Healthy link graphs have 3-5 hub pages, <5 orphan pages, and 5+ average links per page",
                "statistical_range": f"Graph: {internal_link_graph.get('graph_summary', {}).get('total_nodes', 0)} pages, {internal_link_graph.get('graph_summary', {}).get('orphan_pages', 0)} orphans",
                "expert_recommendation": "Rescue all orphan pages by adding internal links and create hub pages for top topics",
                "common_mistakes": ["Ignoring orphan pages (zero link equity)", "Not creating hub pages for key topics", "Average links per page below 3"],
                "success_metrics": ["Orphan pages < 3", "Hub pages > 3", "Average links per page > 5"]
            },
            "fresh_content_strategy_insights": {
                "day_1_actions": len(fresh_content_strategy.get("day_1_actions", [])),
                "week_1_actions": len(fresh_content_strategy.get("week_1_actions", [])),
                "month_1_actions": len(fresh_content_strategy.get("month_1_actions", [])),
                "benchmark": "Content with 5+ internal links on day 1 sees 40-60% faster indexing and ranking than content with 0-2 links",
                "statistical_range": f"Link deployment plan: {len(fresh_content_strategy.get('day_1_actions', []))} day-1, {len(fresh_content_strategy.get('week_1_actions', []))} week-1, {len(fresh_content_strategy.get('month_1_actions', []))} month-1 actions",
                "expert_recommendation": "Execute all day-1 actions immediately upon publishing for fastest indexing and ranking",
                "common_mistakes": ["Delaying internal link implementation beyond day 1", "Not submitting to Indexing API", "Missing site-wide navigation links"],
                "success_metrics": ["Indexed within 48 hours", "5+ internal links day 1", "Ranking within 30 days"]
            }
        }
