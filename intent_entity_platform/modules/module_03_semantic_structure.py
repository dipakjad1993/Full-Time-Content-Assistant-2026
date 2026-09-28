"""
Module 3: Semantic Content Structuring & Schema Generation
Builds hierarchical outlines and generates contextual JSON-LD schema markup.
"""
import re
import json
from typing import List, Dict, Any, Optional
from ..utils.text_analytics import (
    extract_keyphrases, extract_entities_simple, tokenize_words,
    schema_json_ld_validate, text_statistics
)


class SemanticStructureSchema:
    """Module 3: Semantic Content Structuring & Schema Generation"""

    def __init__(self):
        self.module_id = "M03"
        self.module_name = "Semantic Content Structuring & Schema Generation"

    def analyze(self, inputs: Dict[str, Any], serp_data: Dict, geo_data: Dict) -> Dict[str, Any]:
        """Full semantic structuring and schema generation pipeline with REAL competitor data."""
        seed_phrase = inputs.get("seed_phrase", "")
        primary_entity = inputs.get("primary_entity", "")
        entity_graph = serp_data.get("entity_graph", {})
        paa_clusters = serp_data.get("paa_clusters", {})
        answer_triggers = geo_data.get("answer_triggers", {})
        audience = inputs.get("audience", {})
        url_data = inputs.get("_url_data", None)
        
        # NEW: Use real competitor data from live fetches
        real_competitor_pages = inputs.get("real_competitor_pages", [])
        real_content_analysis = inputs.get("real_content_analysis", {})
        real_schema_analysis = inputs.get("real_schema_analysis", {})

        hierarchical_outline = self._build_hierarchical_outline(
            seed_phrase, primary_entity, entity_graph, paa_clusters, audience
        )
        direct_answer_blocks = self._generate_direct_answer_blocks(seed_phrase, primary_entity, answer_triggers)
        semantic_sections = self._build_semantic_sections(hierarchical_outline, entity_graph)
        schema_payloads = self._generate_schema_payloads(seed_phrase, primary_entity, entity_graph, hierarchical_outline, inputs)
        content_flow = self._design_content_flow(hierarchical_outline, audience)
        heading_optimization = self._optimize_headings(hierarchical_outline, seed_phrase)
        
        # NEW: Analyze real competitor semantic structures
        real_competitor_structure_analysis = self._analyze_real_competitor_structure(real_competitor_pages, real_content_analysis, real_schema_analysis)

        url_structure_analysis = self._analyze_url_structure(url_data, seed_phrase, primary_entity) if url_data else None

        result = {
            "module": self.module_id,
            "module_name": self.module_name,
            "hierarchical_outline": hierarchical_outline,
            "direct_answer_blocks": direct_answer_blocks,
            "semantic_sections": semantic_sections,
            "schema_payloads": schema_payloads,
            "content_flow": content_flow,
            "heading_optimization": heading_optimization,
            "implementation_guide": self._generate_implementation_guide(hierarchical_outline, schema_payloads),
            "recommendations": self._generate_recommendations(hierarchical_outline, schema_payloads, heading_optimization),
            "implementation_steps": self._generate_implementation_steps(hierarchical_outline, schema_payloads, heading_optimization),
            "where_to_add": self._generate_where_to_add(schema_payloads, hierarchical_outline),
            "detailed_analysis": self._generate_detailed_analysis(hierarchical_outline, schema_payloads, heading_optimization, direct_answer_blocks),
            "real_competitor_structure_analysis": real_competitor_structure_analysis,
            "data_source": "real_time_competitor_analysis",
            "competitors_analyzed": len([p for p in real_competitor_pages if p.get("fetch_success")])
        }

        if url_data and url_structure_analysis:
            result["url_structure_analysis"] = url_structure_analysis
            result["recommendations"] = self._merge_structure_url_recommendations(result["recommendations"], url_structure_analysis)
            result["detailed_analysis"]["url_structure_insights"] = url_structure_analysis

        return result

    def _analyze_real_competitor_structure(self, competitor_pages: List[Dict], content_analysis: Dict, schema_analysis: Dict) -> Dict[str, Any]:
        """Analyze real competitor page structures - VERIFIED LIVE DATA."""
        if not competitor_pages:
            return {"error": "No competitor data available", "source": "N/A"}
        
        successful_pages = [p for p in competitor_pages if p.get("fetch_success")]
        if not successful_pages:
            return {"error": "No successful competitor fetches", "source": "N/A"}
        
        # Analyze each competitor's structure
        competitor_structures = []
        for page in competitor_pages:
            if not page.get("fetch_success"):
                continue
            h2s = page.get("h2s", [])
            h3s = page.get("h3s", [])
            h1 = page.get("h1", "")
            title = page.get("title", "")
            
            # Categorize heading types
            question_headings = [h for h in h2s if "?" in h]
            howto_headings = [h for h in h2s if any(w in h.lower() for w in ["how to", "guide", "tutorial", "step"])]
            comparison_headings = [h for h in h2s if any(w in h.lower() for w in ["vs", "versus", "comparison", "compare", "best"])]
            definition_headings = [h for h in h2s if any(w in h.lower() for w in ["what is", "definition", "overview", "introduction"])]
            
            competitor_structures.append({
                "url": page.get("url", ""),
                "position": page.get("position", 0),
                "title": title,
                "h1": h1,
                "h2_count": len(h2s),
                "h3_count": len(h3s),
                "heading_patterns": {
                    "question_headings": question_headings[:5],
                    "howto_headings": howto_headings[:5],
                    "comparison_headings": comparison_headings[:5],
                    "definition_headings": definition_headings[:5]
                },
                "all_h2s": h2s,
                "all_h3s": h3s,
                "word_count": page.get("word_count", 0),
                "has_schema": page.get("has_schema", False),
                "schema_count": page.get("schema_count", 0)
            })
        
        # Calculate structure benchmarks from real data
        avg_h2s = sum(c["h2_count"] for c in competitor_structures) / len(competitor_structures) if competitor_structures else 0
        avg_h3s = sum(c["h3_count"] for c in competitor_structures) / len(competitor_structures) if competitor_structures else 0
        avg_word_count = sum(c["word_count"] for c in competitor_structures) / len(competitor_structures) if competitor_structures else 0
        schema_users = sum(1 for c in competitor_structures if c["has_schema"])
        
        # Collect all heading patterns across competitors
        all_question_headings = []
        all_howto_headings = []
        all_comparison_headings = []
        all_definition_headings = []
        
        for c in competitor_structures:
            all_question_headings.extend(c["heading_patterns"]["question_headings"])
            all_howto_headings.extend(c["heading_patterns"]["howto_headings"])
            all_comparison_headings.extend(c["heading_patterns"]["comparison_headings"])
            all_definition_headings.extend(c["heading_patterns"]["definition_headings"])
        
        return {
            "competitors_analyzed": len(competitor_structures),
            "competitor_structures": competitor_structures,
            "benchmarks_from_real_data": {
                "avg_h2_count": round(avg_h2s, 1),
                "avg_h3_count": round(avg_h3s, 1),
                "avg_word_count": round(avg_word_count),
                "schema_usage": f"{schema_users}/{len(competitor_structures)}",
                "schema_percentage": round(schema_users / len(competitor_structures) * 100, 1) if competitor_structures else 0
            },
            "heading_pattern_analysis": {
                "question_headings_found": len(all_question_headings),
                "howto_headings_found": len(all_howto_headings),
                "comparison_headings_found": len(all_comparison_headings),
                "definition_headings_found": len(all_definition_headings),
                "top_question_headings": all_question_headings[:10],
                "top_howto_headings": all_howto_headings[:10],
                "top_comparison_headings": all_comparison_headings[:10],
                "top_definition_headings": all_definition_headings[:10]
            },
            "recommendations": [
                f"Target {round(avg_h2s)}+ H2 sections (competitors average {avg_h2s:.1f})",
                f"Include {round(avg_h3s)}+ H3 subsections for depth",
                f"Aim for {round(avg_word_count)}+ words (competitors average {avg_word_count:.0f})",
                "Implement schema markup" if schema_users < len(competitor_structures) else "Schema markup already competitive",
                f"Add {max(0, 5 - len(all_question_headings))} question-based H2 headings",
                f"Add {max(0, 3 - len(all_howto_headings))} how-to/guide H2 headings"
            ],
            "data_source": "live_competitor_page_analysis"
        }

    def _analyze_url_structure(self, url_data: Dict, seed_phrase: str, primary_entity: str) -> Dict[str, Any]:
        """Deep analysis of actual URL semantic structure and schema coverage."""
        page_text = url_data.get("page_text", "")
        title = url_data.get("title", "")
        h1 = url_data.get("h1", "")
        h2s = url_data.get("h2s", [])
        word_count = url_data.get("word_count", 0)
        has_schema = url_data.get("has_schema", False)

        title_length = len(title)
        h1_length = len(h1)

        heading_hierarchy_score = 0.0
        if h1 and h2s:
            heading_hierarchy_score = 0.3
            if any(primary_entity.lower() in h.lower() for h in [h1] + h2s if primary_entity):
                heading_hierarchy_score += 0.2
            if len(h2s) >= 5:
                heading_hierarchy_score += 0.15
            if len(h2s) >= 8:
                heading_hierarchy_score += 0.1
            if any("?" in h for h in h2s):
                heading_hierarchy_score += 0.1
            if any(any(c.isdigit() for c in h) for h in h2s):
                heading_hierarchy_score += 0.05
            if title_length < 70:
                heading_hierarchy_score += 0.1

        h2_content_analysis = []
        for h2 in h2s:
            h2_lower = h2.lower()
            entity_in_h2 = primary_entity.lower() in h2_lower if primary_entity else False
            has_number = any(c.isdigit() for c in h2)
            has_question = "?" in h2
            is_definition = any(w in h2_lower for w in ["what is", "what are", "definition", "overview", "introduction"])
            is_comparison = any(w in h2_lower for w in ["vs", "versus", "compared", "alternatives", "comparison", "best"])
            is_procedural = any(w in h2_lower for w in ["how to", "step", "guide", "implement", "setup"])
            is_list = any(w in h2_lower for w in ["top", "best", "list", "ranked", "tips"])
            is_faq = any(w in h2_lower for w in ["faq", "frequently asked", "questions", "answers"])

            h2_content_analysis.append({
                "heading": h2,
                "length": len(h2),
                "entity_present": entity_in_h2,
                "has_number": has_number,
                "has_question": has_question,
                "content_type": "definition" if is_definition else "comparison" if is_comparison else "procedural" if is_procedural else "list" if is_list else "faq" if is_faq else "informational",
                "optimization_score": round(sum([entity_in_h2 * 0.3, has_number * 0.2, has_question * 0.2, len(h2) < 70 * 0.15, is_definition or is_comparison or is_procedural * 0.15]), 2)
            })

        schema_analysis = self._analyze_schema_coverage(url_data)

        content_type_diversity = set(h2a["content_type"] for h2a in h2_content_analysis)
        content_type_score = min(1.0, len(content_type_diversity) / 5)

        word_count_per_section = word_count / max(1, len(h2s))
        depth_score = min(1.0, (word_count_per_section / 400) * 0.4 + (len(h2s) / 10) * 0.3 + content_type_score * 0.3)

        structure_issues = []
        if h1_length == 0:
            structure_issues.append("No H1 heading detected. Every page needs exactly one H1.")
        if h1_length > 70:
            structure_issues.append(f"H1 is {h1_length} chars. Keep under 70 chars for optimal display.")
        if len(h2s) < 3:
            structure_issues.append(f"Only {len(h2s)} H2 headings found. Minimum 3 recommended for content structure.")
        if len(h2s) < 8:
            structure_issues.append(f"Only {len(h2s)} H2 headings. (General industry guidance, unverified): Competitive content averages 8-12 H2 sections.")
        if word_count < 1500:
            structure_issues.append(f"Word count {word_count} is below 1500. Add depth to each H2 section.")
        if not has_schema:
            structure_issues.append("No structured data detected. Add TechArticle, FAQPage, and HowTo schema.")
        if not any(primary_entity.lower() in h.lower() for h in [h1] + h2s if primary_entity):
            structure_issues.append(f"Primary entity '{primary_entity}' not found in any heading. Include in H1 and at least 2 H2s.")
        if not any("?" in h for h in h2s):
            structure_issues.append("No question-format H2 headings. Add FAQ-style headings for PAA capture.")
        if word_count_per_section < 200:
            structure_issues.append(f"Average {word_count_per_section:.0f} words per H2 section. Aim for 250-400 words per section.")

        return {
            "url": url_data.get("url", ""),
            "page_title": title,
            "title_length": title_length,
            "h1_heading": h1,
            "h1_length": h1_length,
            "h2_count": len(h2s),
            "word_count": word_count,
            "heading_hierarchy_score": round(heading_hierarchy_score, 3),
            "heading_hierarchy_tier": (
                "EXCELLENT - Well-structured heading hierarchy" if heading_hierarchy_score > 0.8 else
                "GOOD - Minor heading optimizations needed" if heading_hierarchy_score > 0.6 else
                "NEEDS_WORK - Restructure headings" if heading_hierarchy_score > 0.4 else
                "POOR - Major heading restructuring required"
            ),
            "h2_content_analysis": h2_content_analysis,
            "content_type_diversity": list(content_type_diversity),
            "content_type_diversity_score": round(content_type_score, 3),
            "content_type_benchmark": "(General industry guidance, unverified): Top pages include 3-5 content types (definition, comparison, procedural, FAQ, list)",
            "word_count_per_h2_section": round(word_count_per_section, 0),
            "word_count_per_section_benchmark": "(General industry guidance, unverified): Optimal 250-400 words per H2 section",
            "semantic_depth_score": round(depth_score, 3),
            "schema_coverage_analysis": schema_analysis,
            "structure_issues": structure_issues,
            "structure_issues_count": len(structure_issues),
            "structure_quality_tier": (
                "EXCELLENT - Semantic structure is well-optimized" if len(structure_issues) == 0 else
                "GOOD - Minor structural improvements needed" if len(structure_issues) <= 2 else
                "NEEDS_WORK - Multiple structural issues" if len(structure_issues) <= 5 else
                "CRITICAL - Major restructuring required"
            ),
            "entity_in_headings": sum(1 for h in h2s if primary_entity.lower() in h.lower()) if primary_entity else 0,
            "entity_heading_benchmark": f"(General industry guidance, unverified): Primary entity should appear in H1 and 3+ H2 headings",
            "specific_recommendations": self._generate_structure_url_recommendations(url_data, seed_phrase, primary_entity)
        }

    def _analyze_schema_coverage(self, url_data: Dict) -> Dict[str, Any]:
        """Analyze schema coverage for the URL."""
        has_schema = url_data.get("has_schema", False)
        page_text = url_data.get("page_text", "")

        schema_detected = []
        if has_schema:
            schema_detected.append("Structured data present (exact types unknown without parsing)")

        has_faq_content = bool(re.search(r'(?:FAQ|Frequently Asked Questions|Q[:.]|What is|How to|How does)', page_text, re.IGNORECASE))
        has_howto_content = bool(re.search(r'(?:Step\s+\d|How to|Step-by-Step|Implementation Guide)', page_text, re.IGNORECASE))
        has_article_content = bool(re.search(r'(?:published|dateModified|author|articleSection)', page_text, re.IGNORECASE))
        has_breadcrumb_content = bool(re.search(r'(?:Home\s*[>»]|Category\s*[>»]| breadcrumbs)', page_text, re.IGNORECASE))

        recommended_schemas = []
        if has_faq_content and "FAQPage" not in schema_detected:
            recommended_schemas.append({"schema": "FAQPage", "reason": "FAQ content detected on page", "priority": "HIGH"})
        if has_howto_content and "HowTo" not in schema_detected:
            recommended_schemas.append({"schema": "HowTo", "reason": "Step-by-step content detected on page", "priority": "HIGH"})
        recommended_schemas.append({"schema": "TechArticle", "reason": "Article content - always recommended", "priority": "HIGH"})
        recommended_schemas.append({"schema": "BreadcrumbList", "reason": "Navigation structure - always recommended", "priority": "MEDIUM"})
        if has_breadcrumb_content and "BreadcrumbList" not in schema_detected:
            recommended_schemas.append({"schema": "BreadcrumbList", "reason": "Breadcrumb navigation detected on page", "priority": "MEDIUM"})

        coverage_score = 0.0
        if has_schema:
            coverage_score += 0.3
        if has_faq_content:
            coverage_score += 0.15
        if has_howto_content:
            coverage_score += 0.15
        if has_breadcrumb_content:
            coverage_score += 0.1

        return {
            "has_schema": has_schema,
            "schemas_detected": schema_detected,
            "faq_content_detected": has_faq_content,
            "howto_content_detected": has_howto_content,
            "article_content_detected": has_article_content,
            "breadcrumb_content_detected": has_breadcrumb_content,
            "recommended_schemas": recommended_schemas,
            "coverage_score": round(min(1.0, coverage_score), 3),
            "coverage_tier": (
                "COMPREHENSIVE - All major schema types implemented" if coverage_score > 0.8 else
                "PARTIAL - Some schema types missing" if coverage_score > 0.4 else
                "MINIMAL - Significant schema gaps" if coverage_score > 0.1 else
                "NONE - No structured data detected"
            )
        }

    def _generate_structure_url_recommendations(self, url_data: Dict, seed_phrase: str, primary_entity: str) -> List[Dict[str, str]]:
        """Generate specific structure recommendations based on actual URL content."""
        recs = []
        h1 = url_data.get("h1", "")
        h2s = url_data.get("h2s", [])
        word_count = url_data.get("word_count", 0)
        has_schema = url_data.get("has_schema", False)

        if not any(primary_entity.lower() in h.lower() for h in [h1] + h2s if primary_entity):
            recs.append({
                "priority": "HIGH",
                "action": f"Add primary entity '{primary_entity}' to H1 and at least 2 H2 headings",
                "detail": "Entity not found in any heading. (General industry guidance, unverified): Include in H1 and 30%+ of H2 headings for topical authority."
            })

        if len(h2s) < 8:
            recs.append({
                "priority": "HIGH",
                "action": f"Add {8 - len(h2s)} more H2 sections to reach competitive depth",
                "detail": f"Only {len(h2s)} H2s found. (General industry guidance, unverified): Top-ranking pages average 8-12 H2 sections with 250-400 words each."
            })

        question_headings = [h for h in h2s if "?" in h]
        if len(question_headings) == 0:
            recs.append({
                "priority": "MEDIUM",
                "action": "Add question-format H2 headings (e.g., 'What Is [Entity]?', 'How Does [Entity] Work?')",
                "detail": "No question-format headings found. These capture featured snippets and PAA questions."
            })

        if not has_schema:
            recs.append({
                "priority": "HIGH",
                "action": "Implement TechArticle, FAQPage, and HowTo JSON-LD schema",
                "detail": "No schema detected. (General industry guidance, unverified): pages with valid schema see 25-40% higher rich snippet rates."
            })

        word_count_per_h2 = word_count / max(1, len(h2s))
        if word_count_per_h2 < 200:
            recs.append({
                "priority": "MEDIUM",
                "action": f"Expand each H2 section from ~{word_count_per_h2:.0f} to 250-400 words",
                "detail": f"Average {word_count_per_h2:.0f} words per section is below optimal. Add depth to each section."
            })

        return recs

    def _merge_structure_url_recommendations(self, existing_recs: List[Dict], url_analysis: Dict) -> List[Dict[str, str]]:
        """Merge URL-specific structure recommendations with existing recommendations."""
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

    def _build_hierarchical_outline(self, seed: str, entity: str, entity_graph: Dict,
                                      paa_clusters: Dict, audience: Dict) -> Dict[str, Any]:
        """Build comprehensive H1 > H2 > H3 outline."""
        related_entities = entity_graph.get("related_entities", [])
        paa_questions = paa_clusters.get("top_priority_questions", [])
        knowledge_floor = audience.get("knowledge_floor", "intermediate")
        funnel_stage = audience.get("funnel_stage", "middle")

        outline = {
            "h1": {
                "title": self._generate_h1_title(seed, entity),
                "purpose": "Primary query targeting and entity definition",
                "direct_answer_required": True,
                "word_count_target": "100-150 words",
                "content_type": "definition_and_overview"
            },
            "h2_sections": []
        }

        h2_templates = self._get_h2_templates(seed, entity, related_entities, paa_questions, funnel_stage)
        for i, template in enumerate(h2_templates):
            h2_section = {
                "id": f"H2_{i+1}",
                "title": template["title"],
                "purpose": template["purpose"],
                "direct_answer_required": template.get("direct_answer", True),
                "word_count_target": template.get("word_count", "250-400 words"),
                "content_type": template.get("content_type", "informational"),
                "schema_type": template.get("schema_type", "none"),
                "entity_coverage": template.get("entities", []),
                "h3_subsections": []
            }
            for j, h3 in enumerate(template.get("h3_items", [])):
                h2_section["h3_subsections"].append({
                    "id": f"H2_{i+1}_H3_{j+1}",
                    "title": h3["title"],
                    "purpose": h3.get("purpose", "supporting_detail"),
                    "word_count_target": h3.get("word_count", "100-200 words"),
                    "content_type": h3.get("content_type", "detail"),
                    "direct_answer_required": h3.get("direct_answer", False)
                })
            outline["h2_sections"].append(h2_section)

        outline["structural_metrics"] = {
            "total_h2_count": len(outline["h2_sections"]),
            "total_h3_count": sum(len(s["h3_subsections"]) for s in outline["h2_sections"]),
            "total_estimated_word_count": self._estimate_total_words(outline),
            "direct_answer_blocks": sum(1 for s in outline["h2_sections"] if s["direct_answer_required"]),
            "content_type_diversity": len(set(s["content_type"] for s in outline["h2_sections"]))
        }
        return outline

    def _generate_h1_title(self, seed: str, entity: str) -> str:
        """Generate optimized H1 title."""
        templates = [
            f"{seed.title()}: A Comprehensive Guide for 2026",
            f"The Complete Guide to {seed.title()}",
            f"{seed.title()}: Everything You Need to Know",
            f"Understanding {seed.title()}: Features, Benefits, and Best Practices",
        ]
        return templates[0]

    def _get_h2_templates(self, seed: str, entity: str, related: List[Dict],
                          paa_questions: List[Dict], funnel_stage: str) -> List[Dict[str, Any]]:
        """Generate H2 section templates based on analysis."""
        sections = []

        sections.append({
            "title": f"What Is {entity.title()}? Definition and Core Concepts",
            "purpose": "Direct definition for AI Overview and featured snippet capture",
            "direct_answer": True,
            "word_count": "200-300 words",
            "content_type": "definition",
            "schema_type": "none",
            "entities": [entity],
            "h3_items": [
                {"title": f"Core Components of {entity.title()}", "purpose": "break_down_components", "word_count": "150-250 words"},
                {"title": f"How {entity.title()} Works: The Technical Architecture", "purpose": "explain_mechanism", "word_count": "200-300 words"},
                {"title": f"Key Terminology and Glossary", "purpose": "define_terms", "word_count": "100-200 words"}
            ]
        })

        sections.append({
            "title": f"Top Benefits of {entity.title()} for {funnel_stage.title()}-Funnel Businesses",
            "purpose": "Value proposition aligned to audience funnel stage",
            "direct_answer": True,
            "word_count": "300-400 words",
            "content_type": "benefits",
            "schema_type": "none",
            "entities": [r["name"] for r in related[:3]],
            "h3_items": [
                {"title": "Benefit 1: Operational Efficiency and Cost Reduction", "purpose": "detail_benefit", "word_count": "100-150 words"},
                {"title": "Benefit 2: Scalability and Performance", "purpose": "detail_benefit", "word_count": "100-150 words"},
                {"title": "Benefit 3: Compliance and Security", "purpose": "detail_benefit", "word_count": "100-150 words"}
            ]
        })

        sections.append({
            "title": f"{entity.title()} Features Comparison: Top Solutions Ranked",
            "purpose": "Comparison content for MoF/BoF audience",
            "direct_answer": True,
            "word_count": "400-500 words",
            "content_type": "comparison",
            "schema_type": "none",
            "entities": [],
            "h3_items": [
                {"title": "Feature Comparison Matrix", "purpose": "present_data_table", "word_count": "200-300 words"},
                {"title": "Pricing and Plan Comparison", "purpose": "present_pricing", "word_count": "150-250 words"},
                {"title": "Best Use Case for Each Solution", "purpose": "recommendation", "word_count": "150-200 words"}
            ]
        })

        sections.append({
            "title": f"How to Implement {entity.title()}: Step-by-Step Guide",
            "purpose": "Procedural content for featured snippet and HowTo schema",
            "direct_answer": True,
            "word_count": "400-500 words",
            "content_type": "procedural",
            "schema_type": "HowTo",
            "entities": [],
            "h3_items": [
                {"title": "Step 1: Assessment and Planning", "purpose": "step_detail", "word_count": "100-150 words"},
                {"title": "Step 2: Configuration and Setup", "purpose": "step_detail", "word_count": "100-150 words"},
                {"title": "Step 3: Integration and Testing", "purpose": "step_detail", "word_count": "100-150 words"},
                {"title": "Step 4: Go-Live and Optimization", "purpose": "step_detail", "word_count": "100-150 words"}
            ]
        })

        sections.append({
            "title": f"{entity.title()} vs. Alternatives: Which Solution Is Right for You?",
            "purpose": "Direct comparison for decision-stage audience",
            "direct_answer": True,
            "word_count": "350-450 words",
            "content_type": "comparison",
            "schema_type": "none",
            "entities": [],
            "h3_items": [
                {"title": "When to Choose [Primary Solution]", "purpose": "recommendation", "word_count": "100-150 words"},
                {"title": "When to Choose [Alternative]", "purpose": "recommendation", "word_count": "100-150 words"},
                {"title": "Decision Framework", "purpose": "decision_helper", "word_count": "150-200 words"}
            ]
        })

        sections.append({
            "title": f"Common {entity.title()} Challenges and How to Overcome Them",
            "purpose": "Address pain points and build trust",
            "direct_answer": True,
            "word_count": "300-400 words",
            "content_type": "problem_solution",
            "schema_type": "FAQPage",
            "entities": [],
            "h3_items": [
                {"title": "Challenge 1: Integration Complexity", "purpose": "problem_solution", "word_count": "100-150 words"},
                {"title": "Challenge 2: Data Migration and Security", "purpose": "problem_solution", "word_count": "100-150 words"},
                {"title": "Challenge 3: User Adoption and Training", "purpose": "problem_solution", "word_count": "100-150 words"}
            ]
        })

        sections.append({
            "title": f"Best Practices for {entity.title()} in 2026",
            "purpose": "Actionable recommendations with current data",
            "direct_answer": True,
            "word_count": "300-400 words",
            "content_type": "best_practices",
            "schema_type": "none",
            "entities": [],
            "h3_items": [
                {"title": "Performance Optimization Tips", "purpose": "actionable_tips", "word_count": "100-150 words"},
                {"title": "Security and Compliance Checklist", "purpose": "checklist", "word_count": "100-150 words"},
                {"title": "Future-Proofing Your Investment", "purpose": "strategic_advice", "word_count": "100-150 words"}
            ]
        })

        sections.append({
            "title": f"Expert Insights: What Industry Leaders Say About {entity.title()}",
            "purpose": "E-E-A-T enhancement through expert quotes and original data",
            "direct_answer": True,
            "word_count": "250-350 words",
            "content_type": "expert_insights",
            "schema_type": "none",
            "entities": [],
            "h3_items": [
                {"title": "Expert Quote: [Named Expert]", "purpose": "expert_quote", "word_count": "100-150 words"},
                {"title": "Original Research Findings", "purpose": "data_presentation", "word_count": "150-200 words"}
            ]
        })

        if len(sections) < 10:
            sections.append({
                "title": f"Frequently Asked Questions About {entity.title()}",
                "purpose": "FAQ capture for AI Overview and PAA",
                "direct_answer": True,
                "word_count": "300-500 words",
                "content_type": "faq",
                "schema_type": "FAQPage",
                "entities": [],
                "h3_items": [
                    {"title": f"What is {entity.title()}?", "purpose": "faq_answer", "word_count": "40-60 words"},
                    {"title": f"How much does {entity.title()} cost?", "purpose": "faq_answer", "word_count": "40-60 words"},
                    {"title": f"What are the best {entity.title()} alternatives?", "purpose": "faq_answer", "word_count": "40-60 words"},
                    {"title": f"Is {entity.title()} worth the investment?", "purpose": "faq_answer", "word_count": "40-60 words"},
                    {"title": f"How long does {entity.title()} implementation take?", "purpose": "faq_answer", "word_count": "40-60 words"}
                ]
            })

        return sections

    def _estimate_total_words(self, outline: Dict) -> int:
        """Estimate total word count for the outline."""
        total = 0
        h1_match = re.search(r'(\d+)-(\d+)', outline.get("h1", {}).get("word_count_target", "100-150"))
        if h1_match:
            total += (int(h1_match.group(1)) + int(h1_match.group(2))) // 2
        for section in outline.get("h2_sections", []):
            h2_match = re.search(r'(\d+)-(\d+)', section.get("word_count_target", "250-400"))
            if h2_match:
                total += (int(h2_match.group(1)) + int(h2_match.group(2))) // 2
            for h3 in section.get("h3_subsections", []):
                h3_match = re.search(r'(\d+)-(\d+)', h3.get("word_count_target", "100-200"))
                if h3_match:
                    total += (int(h3_match.group(1)) + int(h3_match.group(2))) // 2
        return total

    def _generate_direct_answer_blocks(self, seed: str, entity: str, answer_triggers: Dict) -> List[Dict[str, Any]]:
        """Generate direct answer blocks for AI extraction."""
        blocks = []
        blocks.append({
            "block_id": "DAB_1",
            "heading_context": f"What Is {entity.title()}?",
            "target_word_count": "40-60 words",
            "template": f"{entity.title()} is a [category] that [primary function]. It enables [target users] to [key benefit] through [mechanism]. Unlike [alternative], it [key differentiator], making it [value proposition].",
            "extraction_format": "paragraph",
            "citation_probability": "HIGH",
            "placement": "Immediately after H2 heading"
        })
        blocks.append({
            "block_id": "DAB_2",
            "heading_context": f"How Does {entity.title()} Work?",
            "target_word_count": "40-60 words",
            "template": f"{entity.title()} operates by [mechanism]. The process involves [step 1], [step 2], and [step 3]. [Key statistic] of organizations report [outcome] after implementing {entity.title()}.",
            "extraction_format": "paragraph_with_statistic",
            "citation_probability": "VERY_HIGH",
            "placement": "Under 'How It Works' H2"
        })
        blocks.append({
            "block_id": "DAB_3",
            "heading_context": f"What Are the Benefits of {entity.title()}?",
            "target_word_count": "40-60 words",
            "template": f"The primary benefits of {entity.title()} include [benefit 1], [benefit 2], and [benefit 3]. According to [source], organizations experience [specific metric improvement] on average.",
            "extraction_format": "paragraph_with_source",
            "citation_probability": "HIGH",
            "placement": "Under 'Benefits' H2"
        })
        blocks.append({
            "block_id": "DAB_4",
            "heading_context": f"How Much Does {entity.title()} Cost?",
            "target_word_count": "40-60 words",
            "template": f"{entity.title()} pricing typically ranges from [price range] depending on [factors]. [Percentage]% of vendors offer [pricing model], with enterprise plans averaging [cost].",
            "extraction_format": "paragraph_with_data",
            "citation_probability": "VERY_HIGH",
            "placement": "Under 'Pricing' H2"
        })
        blocks.append({
            "block_id": "DAB_5",
            "heading_context": f"What Is the Best {entity.title()} in 2026?",
            "target_word_count": "40-60 words",
            "template": f"The best {entity.title()} solutions in 2026 include [Solution A], [Solution B], and [Solution C]. [Solution A] leads in [metric], while [Solution B] excels at [differentiator].",
            "extraction_format": "comparison_summary",
            "citation_probability": "HIGH",
            "placement": "Under 'Best Options' H2"
        })
        return blocks

    def _build_semantic_sections(self, outline: Dict, entity_graph: Dict) -> List[Dict[str, Any]]:
        """Build semantic content requirements for each section."""
        sections = []
        for h2 in outline.get("h2_sections", []):
            section = {
                "section_id": h2["id"],
                "heading": h2["title"],
                "semantic_requirements": {
                    "must_include_entities": h2.get("entity_coverage", []),
                    "required_content_types": [h2.get("content_type", "informational")],
                    "direct_answer_block": h2.get("direct_answer_required", False),
                    "word_count_range": h2.get("word_count_target", "250-400 words"),
                    "citation_required": True,
                    "statistic_required": h2.get("content_type") in ["data", "comparison", "benefits"]
                },
                "semantic_keywords": [],
                "internal_link_opportunities": [],
                "external_citation_requirements": []
            }
            sections.append(section)
        return sections

    def _generate_schema_payloads(self, seed: str, entity: str, entity_graph: Dict, outline: Dict, inputs: Dict = None) -> Dict[str, Any]:
        """Generate comprehensive JSON-LD schema payloads."""
        inputs = inputs or {}
        author = inputs.get("author", {})
        publisher = inputs.get("publisher", {})
        author_name = (author.get("name") or "").strip()
        author_title = (author.get("title") or "").strip()
        publisher_name = (publisher.get("name") or "").strip()
        logo_url = (publisher.get("logo_url") or "").strip()

        author_obj = {
            "@type": "Person",
            "name": author_name,
            "knowsAbout": entity,
        }
        if author_title:
            author_obj["jobTitle"] = author_title
        if author.get("social_profiles"):
            author_obj["sameAs"] = author.get("social_profiles", [])

        publisher_obj = {"@type": "Organization", "name": publisher_name}
        if logo_url:
            publisher_obj["logo"] = {"@type": "ImageObject", "url": logo_url}

        article_schema = {
            "@context": "https://schema.org",
            "@type": "TechArticle",
            "headline": outline["h1"]["title"],
            "about": [
                {
                    "@type": "Thing",
                    "name": entity,
                    "sameAs": entity_graph.get("knowledge_graph_uris", {}).get("sameAs_candidates", [])
                }
            ],
            "mentions": [
                {
                    "@type": "Thing",
                    "name": r["name"]
                }
                for r in entity_graph.get("related_entities", [])[:10]
            ],
            "mainEntity": {
                "@type": "Thing",
                "name": entity
            },
            "keywords": seed,
            "articleSection": "Technology",
            "isAccessibleForFree": True,
            "inLanguage": "en-US"
        }
        if author_name:
            article_schema["author"] = author_obj
        if publisher_name:
            article_schema["publisher"] = publisher_obj

        faq_schema = {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "status": "NO_FAQ_QUESTIONS",
            "message": "FAQ schema is only generated from real questions found in the People-Also-Ask analysis or outline FAQ sections."
        }

        howto_schema = {
            "@context": "https://schema.org",
            "@type": "HowTo",
            "status": "NO_STEPS",
            "message": "HowTo schema is only generated from real implementation steps found in the outline."
        }

        brand_website = inputs.get("brand_website", "").strip().rstrip("/")
        breadcrumb_schema = {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {
                    "@type": "ListItem",
                    "position": 1,
                    "name": "Home",
                    "item": brand_website or ""
                },
                {
                    "@type": "ListItem",
                    "position": 2,
                    "name": "Resources",
                    "item": (brand_website + "/resources") if brand_website else ""
                },
                {
                    "@type": "ListItem",
                    "position": 3,
                    "name": entity,
                    "item": inputs.get("url", brand_website) or ""
                }
            ]
        }

        schemas = {
            "article": article_schema,
            "faq": faq_schema,
            "howto": howto_schema,
            "breadcrumb": breadcrumb_schema
        }

        validation_results = {}
        for name, schema in schemas.items():
            errors = schema_json_ld_validate(schema)
            validation_results[name] = {
                "valid": len(errors) == 0,
                "errors": errors
            }

        return {
            "schemas": schemas,
            "validation": validation_results,
            "implementation_notes": [
                "Place Article schema in <head> section",
                "FAQPage schema should only include questions answered on the page",
                "HowTo steps must match actual page content exactly",
                "BreadcrumbList should reflect actual navigation path",
                "Update dateModified on every content refresh"
            ]
        }

    def _design_content_flow(self, outline: Dict, audience: Dict) -> Dict[str, Any]:
        """Design optimal content flow for audience."""
        funnel_stage = audience.get("funnel_stage", "middle")
        knowledge_floor = audience.get("knowledge_floor", "intermediate")
        flow = {
            "opening_strategy": "direct_definition",
            "content_arc": "problem_solution",
            "conversion_points": [],
            "engagement_triggers": [],
            "reading_path": "linear_with_branching"
        }
        if funnel_stage == "top":
            flow["opening_strategy"] = "educational_hook"
            flow["content_arc"] = "concept_explanation"
            flow["engagement_triggers"] = ["definition", "examples", "visual_demonstration"]
        elif funnel_stage == "middle":
            flow["opening_strategy"] = "problem_acknowledgment"
            flow["content_arc"] = "comparison_and_evaluation"
            flow["conversion_points"] = ["mid_article_cta", "comparison_table", "expert_quote"]
            flow["engagement_triggers"] = ["comparison_table", "expert_quote", "statistic"]
        else:
            flow["opening_strategy"] = "solution_presentation"
            flow["content_arc"] = "proof_and_conversion"
            flow["conversion_points"] = ["pricing_section", "demo_cta", "trial_offer"]
            flow["engagement_triggers"] = ["roi_calculator", "case_study", "testimonial"]
        return flow

    def _optimize_headings(self, outline: Dict, seed: str) -> Dict[str, Any]:
        """Optimize headings for SEO and readability."""
        optimizations = []
        seed_words = set(tokenize_words(seed))
        for section in outline.get("h2_sections", []):
            heading_words = set(tokenize_words(section["title"]))
            keyword_coverage = len(seed_words & heading_words) / max(1, len(seed_words))
            optimizations.append({
                "heading": section["title"],
                "keyword_coverage": round(keyword_coverage, 3),
                "length_chars": len(section["title"]),
                "contains_number": bool(re.search(r'\d', section["title"])),
                "contains_question": "?" in section["title"],
                "contains_colon": ":" in section["title"],
                "optimization_score": round(
                    (keyword_coverage * 0.4 + (0.2 if len(section["title"]) < 70 else 0) +
                     (0.2 if bool(re.search(r'\d', section["title"])) else 0) +
                     (0.2 if "?" in section["title"] or ":" in section["title"] else 0)), 3
                )
            })
        return {
            "heading_optimizations": optimizations,
            "average_optimization_score": round(
                sum(o["optimization_score"] for o in optimizations) / max(1, len(optimizations)), 3
            ),
            "headings_needing_work": [o for o in optimizations if o["optimization_score"] < 0.4]
        }

    def _generate_implementation_guide(self, outline: Dict, schemas: Dict) -> Dict[str, Any]:
        """Generate implementation guide for content creators."""
        return {
            "content_creation_order": [
                "1. Start with H1 and first H2 (definition section) - most critical for AI Overview",
                "2. Write all direct answer blocks (40-60 words each)",
                "3. Complete comparison and data sections",
                "4. Add FAQ section with schema-ready Q&A pairs",
                "5. Insert expert quotes and proprietary data",
                "6. Finalize internal and external links",
                "7. Implement JSON-LD schema markup"
            ],
            "quality_checkpoints": [
                "Each H2 must start with a 40-60 word direct answer block",
                "Every statistic must have source attribution",
                "All expert quotes must include name and credentials",
                "FAQ answers must be 40-60 words for optimal AI extraction",
                "Comparison tables must have clear winner indicators",
                "Content must pass readability check for target audience level"
            ],
            "schema_implementation_checklist": [
                "Validate all JSON-LD using Google Rich Results Test",
                "Ensure @id references are consistent across schemas",
                "Verify sameAs links point to live, accessible profiles",
                "Test FAQPage schema with Google's structured data testing tool",
                "Confirm HowTo steps match actual page content exactly"
            ]
        }

    def _generate_recommendations(self, outline: Dict, schemas: Dict, heading_opt: Dict) -> List[Dict[str, str]]:
        """Generate structuring recommendations."""
        recs = []
        metrics = outline.get("structural_metrics", {})
        if metrics.get("total_h2_count", 0) < 8:
            recs.append({
                "priority": "HIGH",
                "action": "Add more H2 sections for comprehensive coverage",
                "detail": f"Currently {metrics.get('total_h2_count', 0)} H2s - recommend 8-12 for topically authoritative content"
            })
        if metrics.get("total_estimated_word_count", 0) < 2500:
            recs.append({
                "priority": "MEDIUM",
                "action": "Increase content depth",
                "detail": f"Estimated {metrics.get('total_estimated_word_count', 0)} words - recommend 2500-4000 for competitive terms"
            })
        for opt in heading_opt.get("headings_needing_work", [])[:3]:
            recs.append({
                "priority": "MEDIUM",
                "action": f"Optimize heading: '{opt['heading'][:50]}...'",
                "detail": f"Optimization score {opt['optimization_score']} - add target keyword, number, or question format"
            })
        if schemas.get("validation", {}):
            invalid = [k for k, v in schemas["validation"].items() if not v["valid"]]
            if invalid:
                recs.append({
                    "priority": "HIGH",
                    "action": "Fix schema validation errors",
                    "detail": f"Invalid schemas: {', '.join(invalid)}"
                })
        return recs

    def _generate_implementation_steps(self, outline: Dict, schemas: Dict, heading_opt: Dict) -> List[str]:
        steps = []
        steps.append("Step 1: Implement the JSON-LD TechArticle schema in <head> with headline, author, publisher, datePublished, and dateModified fields")
        steps.append("Step 2: Populate the author schema with Person type including name, jobTitle, and sameAs links to LinkedIn/Twitter profiles")
        steps.append("Step 3: Add the BreadcrumbList schema in <head> reflecting actual site navigation path to the article")
        steps.append("Step 4: Write the H1 title incorporating the primary seed phrase and entity for SEO relevance")
        steps.append("Step 5: Create 8-12 H2 sections following the hierarchical outline with proper heading hierarchy")
        steps.append("Step 6: Write 40-60 word direct answer blocks immediately after each H2 heading for AI Overview extraction")
        steps.append("Step 7: Add FAQPage schema in <head> with Q&A pairs matching the FAQ section on the page")
        steps.append("Step 8: Implement HowTo schema for the procedural H2 section with steps matching page content exactly")
        steps.append("Step 9: Validate all JSON-LD schemas using Google Rich Results Test before publishing")
        steps.append("Step 10: Ensure @id references are consistent across all schema types for proper entity linking")
        steps.append("Step 11: Add internal links from each H2 section to related pages using varied anchor text")
        steps.append("Step 12: Optimize all headings by adding target keywords, numbers, or question formats where missing")
        return steps

    def _generate_where_to_add(self, schemas: Dict, outline: Dict) -> List[str]:
        locations = []
        locations.append("Add TechArticle JSON-LD schema in <head> via <script type='application/ld+json'> tag")
        locations.append("Add FAQPage JSON-LD schema in <head> via a second <script type='application/ld+json'> tag")
        locations.append("Add HowTo JSON-LD schema in <head> via a third <script type='application/ld+json'> tag")
        locations.append("Add BreadcrumbList JSON-LD schema in <head> via a fourth <script type='application/ld+json'> tag")
        locations.append("Place the H1 heading as the first visible content element in the <body>")
        locations.append("Write direct answer blocks as the first paragraph immediately following each H2 heading")
        locations.append("Place comparison tables within the 'Features Comparison' H2 section")
        locations.append("Insert expert quotes as blockquotes within the 'Expert Insights' H2 section")
        locations.append("Add FAQ Q&A pairs in the 'Frequently Asked Questions' H2 section with matching schema")
        locations.append("Include step-by-step numbered lists within the 'How to Implement' H2 section")
        locations.append("Place author credentials and publication date in the article byline area below H1")
        locations.append("Add internal links within body paragraphs of each H2 section for topical authority")
        return locations

    def _generate_detailed_analysis(self, outline: Dict, schemas: Dict,
                                     heading_opt: Dict, direct_answer_blocks: List) -> Dict[str, Any]:
        metrics = outline.get("structural_metrics", {})
        return {
            "outline_structure_insights": {
                "total_h2_count": metrics.get("total_h2_count", 0),
                "total_h3_count": metrics.get("total_h3_count", 0),
                "estimated_word_count": metrics.get("total_estimated_word_count", 0),
                "direct_answer_blocks": metrics.get("direct_answer_blocks", 0),
                "benchmark": "(General industry guidance, unverified): Top-ranking content averages 10-15 H2 sections, 20-30 H3 subsections, and 3000-5000 words",
                "statistical_range": f"Current structure: {metrics.get('total_h2_count', 0)} H2s, {metrics.get('total_h3_count', 0)} H3s, ~{metrics.get('total_estimated_word_count', 0)} words",
                "expert_recommendation": "Aim for 10+ H2 sections with 2-3 H3 subsections each for comprehensive topical coverage",
                "common_mistakes": ["Too few H2 sections (less than 8)", "Missing H3 subsections for depth", "Word count under 2500 for competitive queries"],
                "success_metrics": ["10+ H2 sections", "25+ H3 subsections", "3000+ words", "8+ direct answer blocks"],
                "data_origin": "unverified_industry_heuristic - not measured for this page"
            },
            "schema_implementation_insights": {
                "total_schemas": len(schemas.get("schemas", {})),
                "validation_status": schemas.get("validation", {}),
                "benchmark": "(General industry guidance, unverified): Pages with valid TechArticle, FAQPage, and HowTo schema see 25-40% higher rich snippet appearance rates",
                "statistical_range": f"Schemas generated: {len(schemas.get('schemas', {}))} (unverified heuristic recommendation: 4 types)",
                "expert_recommendation": "Implement all 4 schema types (TechArticle, FAQPage, HowTo, BreadcrumbList) for maximum structured data coverage",
                "common_mistakes": ["Schema content not matching page content", "Missing dateModified field", "Invalid JSON-LD syntax", "Inconsistent @id references"],
                "success_metrics": ["0 schema validation errors", "Rich results appearing in SERP", "FAQPage schema triggering for question queries"],
                "data_origin": "unverified_industry_heuristic - not measured for this page"
            },
            "heading_optimization_insights": {
                "average_optimization_score": heading_opt.get("average_optimization_score", 0),
                "headings_needing_work": len(heading_opt.get("headings_needing_work", [])),
                "benchmark": "(General industry guidance, unverified): Top-optimized headings have keyword coverage > 60%, contain numbers, and are under 70 characters",
                "statistical_range": f"Average heading score: {heading_opt.get('average_optimization_score', 0)*100:.0f}% (unverified heuristic target: 60%+)",
                "expert_recommendation": "Add target keywords, numbers, or question marks to headings scoring below 40% optimization",
                "common_mistakes": ["Headings too long (70+ characters)", "Missing target keywords in H2 titles", "Not using question format for FAQ sections"],
                "success_metrics": ["Average heading score > 60%", "0 headings below 40% optimization", "All H2s under 70 characters"],
                "data_origin": "unverified_industry_heuristic - not measured for this page"
            },
            "direct_answer_blocks_insights": {
                "total_blocks": len(direct_answer_blocks),
                "block_types": [b.get("extraction_format", "unknown") for b in direct_answer_blocks],
                "benchmark": "(General industry guidance, unverified): AI Overview extracts 40-60 word paragraphs; pages with 5+ direct answer blocks have 3x higher citation probability",
                "statistical_range": f"Direct answer blocks: {len(direct_answer_blocks)} (unverified heuristic target: 5+)",
                "expert_recommendation": "Each block must be 40-60 words, start with a definition or key fact, and include at least one statistic or source",
                "common_mistakes": ["Answers exceeding 60 words", "Hedging language instead of direct statements", "Missing source attribution in answer blocks"],
                "success_metrics": ["5+ direct answer blocks", "AI Overview extraction within 30 days", "Featured snippet capture for definitional queries"],
                "data_origin": "unverified_industry_heuristic - not measured for this page"
            },
            "content_flow_insights": {
                "opening_strategy": outline.get("h1", {}).get("content_type", "definition"),
                "content_type_diversity": metrics.get("content_type_diversity", 0),
                "benchmark": "(General industry guidance, unverified): Optimal content flow includes definition, benefits, comparison, procedural, and FAQ content types",
                "statistical_range": f"Content type diversity: {metrics.get('content_type_diversity', 0)} types (unverified heuristic target: 5+)",
                "expert_recommendation": "Include at least 5 distinct content types (definition, benefits, comparison, procedural, FAQ) for comprehensive coverage",
                "common_mistakes": ["Monotonous content type throughout", "Missing comparison sections for decision-stage queries", "No FAQ section for PAA capture"],
                "success_metrics": ["5+ content types", "Balanced funnel coverage", "Featured snippet capture across content types"],
                "data_origin": "unverified_industry_heuristic - not measured for this page"
            }
        }
