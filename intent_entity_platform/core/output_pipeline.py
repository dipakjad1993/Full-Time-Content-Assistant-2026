"""
Output Pipeline & Blueprint Generator
Transforms all 21 module outputs into actionable blueprints.
"""
import json
from typing import List, Dict, Any
from datetime import datetime


class OutputPipeline:
    """Generates the final content blueprint from all module analyses."""

    def __init__(self):
        self.output_types = [
            "editorial_blueprint",
            "geo_optimization",
            "technical_payload",
            "cdn_deployment",
            "sentinel_brief"
        ]

    def generate_blueprint(self, all_results: Dict[str, Any], inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Generate the complete content blueprint."""
        return {
            "blueprint_metadata": self._generate_metadata(inputs),
            "output_1_editorial_blueprint": self._generate_editorial_blueprint(all_results, inputs),
            "output_2_geo_optimization": self._generate_geo_optimization(all_results, inputs),
            "output_3_technical_payload": self._generate_technical_payload(all_results, inputs),
            "output_4_cdn_deployment": self._generate_cdn_deployment(all_results, inputs),
            "output_5_sentinel_brief": self._generate_sentinel_brief(all_results, inputs),
            "executive_summary": self._generate_executive_summary(all_results, inputs)
        }

    def _generate_metadata(self, inputs: Dict) -> Dict[str, Any]:
        return {
            "generated_at": datetime.now().isoformat(),
            "platform": "Intent, Entity & Semantic Intelligence Platform",
            "version": "1.0.0",
            "session_id": inputs.get("session_id", ""),
            "target_entity": inputs.get("primary_entity", ""),
            "target_query": inputs.get("seed_phrase", ""),
            "target_locale": inputs.get("locale", "en-US"),
            "modules_executed": 21
        }

    def _generate_editorial_blueprint(self, results: Dict, inputs: Dict) -> Dict[str, Any]:
        """Output 1: Editorial & Writing Blueprint."""
        outline = results.get("M03", {}).get("hierarchical_outline", {})
        eeat = results.get("M04", {})
        fluff = results.get("M06", {})
        intent = results.get("M14", {})

        return {
            "section": "EDITORIAL & WRITING BLUEPRINT",
            "purpose": "For writers - structured outline, SME placement, and quality targets",
            "structural_outline": {
                "h1": outline.get("h1", {}),
                "h2_sections": outline.get("h2_sections", []),
                "total_estimated_words": outline.get("structural_metrics", {}).get("total_estimated_word_count", 2500),
                "total_sections": outline.get("structural_metrics", {}).get("total_h2_count", 8)
            },
            "direct_answer_blocks": results.get("M03", {}).get("direct_answer_blocks", []),
            "smee_placement_markers": eeat.get("sme_placement_optimization", {}).get("placements", []),
            "information_gain_checklist": eeat.get("information_gain_analysis", {}).get("gaps", []),
            "unique_value_propositions": eeat.get("unique_value_identification", {}).get("unique_value_propositions", []),
            "quality_targets": {
                "readability_grade": intent.get("readability_alignment", {}).get("target_audience_level", "intermediate"),
                "flesch_kincaid_target": "8-10 for intermediate, 10-14 for advanced",
                "fluff_score_target": "< 0.3 (currently: " + str(fluff.get("overall_quality_score", {}).get("overall_score", "N/A")) + ")",
                "burstiness_target": "Coefficient of variation > 0.5",
                "ai_pattern_target": "AI probability score < 0.2",
                "word_count_target": str(outline.get("structural_metrics", {}).get("total_estimated_word_count", 2500)) + " words",
                "targets_annotation": "Heuristic industry targets for writing quality - guidance only, not measured benchmarks"
            },
            "writing_guidelines": {
                "opening_strategy": intent.get("intent_alignment", {}).get("detected_intents", ["informational"]),
                "sentence_variety": "Mix 3-word punchy sentences with 30-word complex sentences",
                "data_density": "Include 2-3 statistics per H2 section with source attribution",
                "expert_quotes": f"Include {eeat.get('sme_placement_optimization', {}).get('sme_count', 0)} expert quotes",
                "anti_patterns": "Avoid all AI clichés and blacklisted terms"
            },
            "content_flow": results.get("M03", {}).get("content_flow", {})
        }

    def _generate_geo_optimization(self, results: Dict, inputs: Dict) -> Dict[str, Any]:
        """Output 2: Direct Answer & RAG-Ready Blocks."""
        geo = results.get("M02", {})
        rag = results.get("M11", {})
        return {
            "section": "DIRECT ANSWER & GEO OPTIMIZATION",
            "purpose": "For AI/GEO optimization - answer blocks, RAG chunks, citation triggers",
            "answer_block_strategy": geo.get("aeo_optimization", {}).get("answer_block_strategy", {}),
            "engine_specific_strategies": geo.get("engine_specific_strategies", {}),
            "rag_optimized_chunks": {
                "total_chunks": rag.get("chunk_analysis", {}).get("total_chunks", 0),
                "average_tokens": rag.get("chunk_analysis", {}).get("token_statistics", {}).get("avg_tokens", 0),
                "self_contained_ratio": rag.get("chunk_analysis", {}).get("quality_metrics", {}).get("self_contained_ratio", 0),
                "rag_readiness_score": rag.get("overall_rag_score", {}).get("overall_score", 0)
            },
            "citation_triggers": geo.get("answer_triggers", {}).get("high_probability_triggers", []),
            "citation_source_targets": geo.get("citation_sources", {}).get("required_citation_targets", []),
            "geo_readiness_score": geo.get("geo_readiness_score", {}).get("overall_geo_readiness", 0),
            "estimated_ai_visibility_improvement": geo.get("aeo_optimization", {}).get("estimated_improvement", {})
        }

    def _generate_technical_payload(self, results: Dict, inputs: Dict) -> Dict[str, Any]:
        """Output 3: Technical & Structured Data Payload."""
        schema = results.get("M13", {})
        csr = results.get("M10", {})
        citations = results.get("M07", {})
        dom = results.get("M21", {})
        return {
            "section": "TECHNICAL & STRUCTURED DATA PAYLOAD",
            "purpose": "For SEOs & Devs - schema, links, technical specs",
            "json_ld_schemas": schema.get("schemas", {}),
            "nested_entity_schema": schema.get("nested_entity_schema", {}),
            "schema_validation": schema.get("validation_results", {}),
            "internal_linking_blueprint": results.get("M05", {}).get("link_plan", {}),
            "cannibalization_status": results.get("M05", {}).get("cannibalization_detection", {}).get("cannibalization_risk", "UNKNOWN"),
            "citation_verification": citations.get("verification_summary", {}),
            "hallucination_risk": citations.get("hallucination_risk_assessment", {}).get("risk_level", "UNKNOWN"),
            "csr_rendering_status": csr.get("rendering_analysis", {}).get("rendering_type", "UNKNOWN"),
            "content_availability": csr.get("content_availability", {}).get("content_available_in_initial_html", False),
            "dom_size": dom.get("dom_analysis", {}).get("total_dom_elements", 0),
            "dom_risk": dom.get("dom_analysis", {}).get("dom_size_risk", "UNKNOWN"),
            "search_engine_coverage": schema.get("search_engine_coverage", {})
        }

    def _generate_cdn_deployment(self, results: Dict, inputs: Dict) -> Dict[str, Any]:
        """Output 4: CDN & Edge Deployment Directives."""
        cdn = results.get("M16", {})
        return {
            "section": "CDN & EDGE DEPLOYMENT DIRECTIVES",
            "purpose": "For IT & DevOps - edge workers, headers, prerender",
            "edge_worker_snippet": cdn.get("edge_worker_snippet", {}),
            "server_headers": cdn.get("server_header_inspection", {}),
            "prerender_status": cdn.get("prerender_simulation", {}),
            "cdn_configuration": cdn.get("cdn_configuration", {}),
            "deployment_guide": cdn.get("deployment_guide", {}),
            "localization_hreflang": results.get("M19", {}).get("hreflang_configuration", {})
        }

    def _generate_sentinel_brief(self, results: Dict, inputs: Dict) -> Dict[str, Any]:
        """Output 5: Post-Publish Sentinel Brief."""
        tracker = results.get("M09", {})
        decay = results.get("M15", {})
        indexing = results.get("M18", {})
        ab = results.get("M17", {})
        return {
            "section": "POST-PUBLISH SENTINEL BRIEF",
            "purpose": "For performance tracking - monitoring, alerts, refresh plans",
            "citation_tracking_config": tracker.get("tracking_configuration", {}),
            "monitoring_dashboard": tracker.get("monitoring_dashboard", {}),
            "alert_system": tracker.get("alert_system", {}),
            "content_health": decay.get("overall_health_score", {}),
            "refresh_brief": decay.get("refresh_brief", {}),
            "indexing_status": indexing.get("indexing_status", {}),
            "api_push_config": indexing.get("api_push_configuration", {}),
            "ab_test_config": ab.get("test_design", {}),
            "rollback_guards": ab.get("rollback_guards", {})
        }

    def _generate_executive_summary(self, results: Dict, inputs: Dict) -> Dict[str, Any]:
        """Generate executive summary across all modules (from REAL module results)."""
        critical_issues = []
        high_priority = []
        all_recommendations = []
        for module_id, module_results in results.items():
            if not isinstance(module_results, dict):
                continue
            for rec in module_results.get("recommendations", []):
                if isinstance(rec, str):
                    rec = {"action": rec, "priority": "INFO"}
                rec["module"] = module_id
                all_recommendations.append(rec)
                if rec.get("priority") == "CRITICAL":
                    critical_issues.append(rec)
                elif rec.get("priority") == "HIGH":
                    high_priority.append(rec)
        # Real module health from actual results/errors
        module_health = {}
        module_names = {
            "M01": "serp_analysis", "M02": "geo_optimization", "M03": "semantic_structure",
            "M04": "eeat_gap", "M05": "internal_links", "M06": "fluff_detection",
            "M07": "citation_verification", "M08": "multimodal_assets", "M09": "geo_tracker",
            "M10": "csr_simulation", "M11": "rag_testing", "M12": "brand_compliance",
            "M13": "schema_generation", "M14": "intent_bounce", "M15": "content_decay",
            "M16": "cdn_edge", "M17": "ab_testing", "M18": "indexing_sentinel",
            "M19": "localization", "M20": "digital_pr", "M21": "dom_inspection",
        }
        for module_id, mname in module_names.items():
            mr = results.get(module_id, {})
            if isinstance(mr, dict) and mr.get("error"):
                module_health[mname] = f"Module {module_id[1:]} FAILED: {str(mr['error'])[:60]}"
            elif isinstance(mr, dict) and mr:
                module_health[mname] = f"Module {module_id[1:]} completed"
            else:
                module_health[mname] = f"Module {module_id[1:]} no output"

        # Real competitive landscape from live competitor research (M01 benchmarking)
        competitive_landscape = {}
        for mid, mr in results.items():
            if not isinstance(mr, dict):
                continue
            cb = mr.get("competitive_benchmarking", {}) or {}
            if cb.get("competitors_analyzed"):
                competitive_landscape = {
                    "competitors_analyzed": cb.get("competitors_analyzed", 0),
                    "serp_results_reviewed": cb.get("serp_results_reviewed", 0),
                    "your_content_vs_competitors": cb.get("your_content_vs_competitors", {}),
                    "competitor_content_benchmarks": cb.get("competitor_content_benchmarks", {}),
                    "content_gaps_vs_competitors": cb.get("content_gaps_vs_competitors", []),
                    "competitor_entity_themes": cb.get("competitor_entity_themes", []),
                    "serp_features_detected": cb.get("serp_features_detected", {}),
                }
                break

        return {
            "section": "EXECUTIVE SUMMARY",
            "total_modules_executed": len(results),
            "critical_issues_count": len(critical_issues),
            "high_priority_count": len(high_priority),
            "total_recommendations": len(all_recommendations),
            "critical_issues": critical_issues[:10],
            "high_priority_actions": high_priority[:15],
            "module_health_scores": module_health,
            "top_5_actions": (critical_issues + high_priority + all_recommendations)[:5],
            "competitive_landscape": competitive_landscape
        }

    def export_json(self, blueprint: Dict, filepath: str):
        """Export blueprint as JSON."""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(blueprint, f, indent=2, ensure_ascii=False, default=str)

    def export_summary(self, blueprint: Dict) -> str:
        """Export human-readable summary."""
        lines = []
        lines.append("=" * 80)
        lines.append("INTENT, ENTITY & SEMANTIC INTELLIGENCE PLATFORM - CONTENT BLUEPRINT")
        lines.append("=" * 80)
        meta = blueprint.get("blueprint_metadata", {})
        lines.append(f"\nGenerated: {meta.get('generated_at', '')}")
        lines.append(f"Target Entity: {meta.get('target_entity', '')}")
        lines.append(f"Target Query: {meta.get('target_query', '')}")
        lines.append(f"Modules Executed: {meta.get('modules_executed', 0)}")
        exec_summary = blueprint.get("executive_summary", {})
        lines.append(f"\n{'=' * 80}")
        lines.append("EXECUTIVE SUMMARY")
        lines.append(f"{'=' * 80}")
        lines.append(f"Critical Issues: {exec_summary.get('critical_issues_count', 0)}")
        lines.append(f"High Priority Actions: {exec_summary.get('high_priority_count', 0)}")
        lines.append(f"Total Recommendations: {exec_summary.get('total_recommendations', 0)}")
        lines.append("\nTop 5 Actions:")
        for i, action in enumerate(exec_summary.get("top_5_actions", [])[:5], 1):
            lines.append(f"  {i}. [{action.get('priority', 'INFO')}] {action.get('action', 'N/A')}")
        editorial = blueprint.get("output_1_editorial_blueprint", {})
        lines.append(f"\n{'=' * 80}")
        lines.append("OUTPUT 1: EDITORIAL BLUEPRINT")
        lines.append(f"{'=' * 80}")
        outline = editorial.get("structural_outline", {})
        lines.append(f"Estimated Words: {outline.get('total_estimated_words', 'N/A')}")
        lines.append(f"Total Sections: {outline.get('total_sections', 'N/A')}")
        h1 = outline.get("h1", {})
        lines.append(f"H1: {h1.get('title', 'N/A')}")
        for section in outline.get("h2_sections", [])[:8]:
            lines.append(f"  H2: {section.get('title', 'N/A')}")
        geo = blueprint.get("output_2_geo_optimization", {})
        lines.append(f"\n{'=' * 80}")
        lines.append("OUTPUT 2: GEO OPTIMIZATION")
        lines.append(f"{'=' * 80}")
        lines.append(f"GEO Readiness Score: {geo.get('geo_readiness_score', 'N/A')}")
        lines.append(f"RAG Readiness Score: {geo.get('rag_optimized_chunks', {}).get('rag_readiness_score', 'N/A')}")
        technical = blueprint.get("output_3_technical_payload", {})
        lines.append(f"\n{'=' * 80}")
        lines.append("OUTPUT 3: TECHNICAL PAYLOAD")
        lines.append(f"{'=' * 80}")
        lines.append(f"Schema Types Generated: {len(technical.get('json_ld_schemas', {}))}")
        lines.append(f"Cannibalization Risk: {technical.get('cannibalization_status', 'N/A')}")
        lines.append(f"Hallucination Risk: {technical.get('hallucination_risk', 'N/A')}")
        lines.append(f"DOM Size: {technical.get('dom_size', 'N/A')}")
        lines.append(f"CSR Rendering: {technical.get('csr_rendering_status', 'N/A')}")
        health = exec_summary.get("module_health_scores", {})
        failed = [v for v in health.values() if "FAILED" in v]
        no_output = [v for v in health.values() if "no output" in v]
        if failed or no_output:
            lines.append("\nATTENTION: Some modules did not complete or produced no output:")
            for v in (failed + no_output):
                lines.append(f"  - {v}")
        lines.append("=" * 80)
        return '\n'.join(lines)
