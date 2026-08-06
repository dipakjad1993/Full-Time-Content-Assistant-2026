"""
Main Engine - Orchestrates all 21 modules and generates the complete blueprint.
"""
import json
import traceback
from typing import Dict, Any, Optional
from datetime import datetime
from .input_framework import InputFramework
from .output_pipeline import OutputPipeline
from ..utils.web_data import fetch_page, extract_page

from ..modules.module_01_serp_kg import SERPKnowledgeGraphParser
from ..modules.module_02_geo_aeo import GEOAEOSimulator
from ..modules.module_03_semantic_structure import SemanticStructureSchema
from ..modules.module_04_eeat_gap import EEATGapProfiler
from ..modules.module_05_internal_links import InternalLinkCannibalization
from ..modules.module_06_fluff_decoder import FluffClicheDecoder
from ..modules.module_07_citation_verifier import CitationSourceVerifier
from ..modules.module_08_multimodal_assets import MultimodalAssetBlueprint
from ..modules.module_09_geo_tracker import GEOTracker
from ..modules.module_10_csr_simulator import CSRSimulator
from ..modules.module_11_rag_tester import RAGTester
from ..modules.module_12_brand_compliance import BrandComplianceEngine
from ..modules.module_13_schema_generator import SchemaPayloadGenerator
from ..modules.module_14_intent_bounce import IntentBouncePredictor
from ..modules.module_15_content_decay import ContentDecayEngine
from ..modules.module_16_cdn_edge import CDNEdgePreviewer
from ..modules.module_17_ab_testing import ABTestingEngine
from ..modules.module_18_indexing_sentinel import IndexingLogSentinel
from ..modules.module_19_localization import LocalizationSync
from ..modules.module_20_digital_pr import DigitalPREngine
from ..modules.module_21_dom_inspector import DOMInspector


class PlatformEngine:
    """Main engine that orchestrates all 21 analysis modules."""

    def __init__(self):
        self.modules = {
            "M01": {"name": "SERP & Knowledge Graph Parser", "class": SERPKnowledgeGraphParser},
            "M02": {"name": "GEO & AEO Simulator", "class": GEOAEOSimulator},
            "M03": {"name": "Semantic Structure & Schema", "class": SemanticStructureSchema},
            "M04": {"name": "E-E-A-T Gap Profiler", "class": EEATGapProfiler},
            "M05": {"name": "Internal Link & Cannibalization", "class": InternalLinkCannibalization},
            "M06": {"name": "Fluff & Cliche Decoder", "class": FluffClicheDecoder},
            "M07": {"name": "Citation & Source Verifier", "class": CitationSourceVerifier},
            "M08": {"name": "Multimodal Asset Blueprint", "class": MultimodalAssetBlueprint},
            "M09": {"name": "GEO Tracker", "class": GEOTracker},
            "M10": {"name": "CSR Simulator", "class": CSRSimulator},
            "M11": {"name": "RAG Tester", "class": RAGTester},
            "M12": {"name": "Brand Compliance Engine", "class": BrandComplianceEngine},
            "M13": {"name": "Schema Payload Generator", "class": SchemaPayloadGenerator},
            "M14": {"name": "Intent & Bounce Predictor", "class": IntentBouncePredictor},
            "M15": {"name": "Content Decay Engine", "class": ContentDecayEngine},
            "M16": {"name": "CDN Edge Previewer", "class": CDNEdgePreviewer},
            "M17": {"name": "A/B Testing Engine", "class": ABTestingEngine},
            "M18": {"name": "Indexing & Log Sentinel", "class": IndexingLogSentinel},
            "M19": {"name": "Localization Sync", "class": LocalizationSync},
            "M20": {"name": "Digital PR Engine", "class": DigitalPREngine},
            "M21": {"name": "DOM Inspector", "class": DOMInspector},
        }
        self.output_pipeline = OutputPipeline()

    def run_analysis(self, framework: InputFramework, progress_callback=None) -> Dict[str, Any]:
        """Run complete 21-module analysis pipeline."""
        all_results = {}
        total_modules = len(self.modules)
        errors = {}

        inputs = {
            "seed_phrase": framework.seed.seed_phrase,
            "primary_entity": framework.seed.primary_entity,
            "brand_website": getattr(framework.seed, 'brand_website', ''),
            "locale": framework.seed.target_locale,
            "device": framework.seed.target_device,
            "secondary_keywords": framework.seed.secondary_keywords,
            "_url_data": getattr(framework, '_url_data', {}),
            "audience": {
                "funnel_stage": framework.audience.funnel_stage,
                "knowledge_floor": framework.audience.knowledge_floor,
                "technical_depth": framework.audience.technical_depth,
            },
            "brand": {
                "voice_profile": framework.brand.voice_profile,
                "regulated_words": framework.brand.regulated_words,
                "do_not_say_terms": framework.brand.do_not_say_terms,
                "anti_trope_blacklist": framework.brand.anti_trope_blacklist,
                "required_disclaimers": framework.brand.required_disclaimers,
                "trademark_rules": framework.brand.trademark_rules,
            },
            "sme_assets": [
                {"expert_name": a.expert_name, "expert_title": a.expert_title, "content": a.content, "verified": a.verified}
                for a in framework.first_party.sme_assets
            ],
            "proprietary_data": framework.first_party.proprietary_stats,
            "existing_pages": [],
            "competitor_content": [],
            "author": {
                "name": "Author Name",
                "title": "Expert Title",
                "organization": framework.brand.brand_name,
                "social_profiles": list(framework.first_party.author_social_profiles.values()),
                "credentials": [],
                "expertise": [framework.seed.primary_entity]
            },
            "publisher": {
                "name": framework.brand.brand_name,
                "url": "",
                "logo_url": "",
                "social_profiles": []
            }
        }

        serp_data = {}
        geo_data = {}
        outline_data = {}
        url_data = self._load_url_data(inputs)
        sample_text = url_data.get("page_text", "")
        inputs["_url_data"] = url_data
        inputs["raw_html"] = url_data.get("raw_html", "")

        for module_id, module_info in self.modules.items():
            try:
                if progress_callback:
                    progress_callback(module_id, module_info["name"], "running")
                module_instance = module_info["class"]()
                if module_id == "M01":
                    result = module_instance.analyze(inputs)
                    serp_data = result
                elif module_id == "M02":
                    result = module_instance.analyze(inputs, serp_data)
                    geo_data = result
                elif module_id == "M03":
                    result = module_instance.analyze(inputs, serp_data, geo_data)
                    outline_data = result
                elif module_id == "M04":
                    result = module_instance.analyze(inputs, serp_data)
                elif module_id == "M05":
                    result = module_instance.analyze(inputs, serp_data)
                elif module_id == "M06":
                    result = module_instance.analyze(sample_text, framework.brand.do_not_say_terms + framework.brand.anti_trope_blacklist)
                elif module_id == "M07":
                    result = module_instance.analyze(sample_text, url_data=url_data)
                elif module_id == "M08":
                    result = module_instance.analyze(sample_text, outline_data)
                elif module_id == "M09":
                    result = module_instance.analyze(inputs)
                elif module_id == "M10":
                    html_content = inputs.get("html_content", "")
                    if not html_content and url_data.get("raw_html"):
                        html_content = url_data["raw_html"]
                    elif not html_content:
                        html_content = inputs.get("raw_html", "")
                    if not html_content:
                        html_content = "<html><body><p></p></body></html>"
                    result = module_instance.analyze(html_content, {"js_framework": framework.technical.js_framework, "render_mode": framework.technical.render_mode})
                elif module_id == "M11":
                    queries = [inputs.get("seed_phrase", "")] + inputs.get("secondary_keywords", [])[:4]
                    result = module_instance.analyze(sample_text, queries)
                elif module_id == "M12":
                    result = module_instance.analyze(sample_text, inputs.get("brand", {}))
                elif module_id == "M13":
                    result = module_instance.analyze(inputs, outline_data, serp_data.get("entity_graph", {}))
                elif module_id == "M14":
                    result = module_instance.analyze(sample_text, outline_data, inputs.get("audience", {}))
                elif module_id == "M15":
                    result = module_instance.analyze(inputs)
                elif module_id == "M16":
                    result = module_instance.analyze(inputs)
                elif module_id == "M17":
                    result = module_instance.analyze(inputs)
                elif module_id == "M18":
                    result = module_instance.analyze(inputs)
                elif module_id == "M19":
                    result = module_instance.analyze(inputs)
                elif module_id == "M20":
                    result = module_instance.analyze(inputs)
                elif module_id == "M21":
                    html_content = inputs.get("html_content", "")
                    if not html_content and url_data.get("raw_html"):
                        html_content = url_data["raw_html"]
                    elif not html_content:
                        html_content = inputs.get("raw_html", "")
                    if not html_content:
                        html_content = "<html><body><p></p></body></html>"
                    result = module_instance.analyze(html_content)
                else:
                    result = {"module": module_id, "status": "not_implemented"}
                all_results[module_id] = result
                if progress_callback:
                    progress_callback(module_id, module_info["name"], "completed")
            except Exception as e:
                error_msg = f"Error in {module_id}: {str(e)}"
                all_results[module_id] = {"module": module_id, "error": error_msg, "traceback": traceback.format_exc()}
                errors[module_id] = error_msg
                if progress_callback:
                    progress_callback(module_id, module_info["name"], f"error: {str(e)}")

        blueprint = self.output_pipeline.generate_blueprint(all_results, inputs)
        return {
            "blueprint": blueprint,
            "module_results": all_results,
            "errors": errors,
            "modules_completed": len(self.modules) - len(errors),
            "modules_failed": len(errors),
            "total_modules": len(self.modules)
        }

    def _load_url_data(self, inputs: Dict) -> Dict[str, Any]:
        """
        Resolve real page data for analysis.

        Priority:
        1. Pre-populated _url_data (from /api/analyze-url - real fetched content)
        2. brand_website URL fetched live (real fetch + parse)
        3. Empty dict - modules then report honest "no content" states.
        """
        url_data = dict(inputs.get("_url_data", {}) or {})
        if url_data.get("page_text") or url_data.get("raw_html"):
            return url_data
        website = inputs.get("brand_website", "")
        if website:
            try:
                page = fetch_page(website, timeout=15)
                if page.get("ok"):
                    meta = extract_page(page.get("html", ""), website)
                    meta["raw_html"] = page.get("html", "")[:200000]
                    meta["fetched_status"] = page.get("status")
                    meta["fetched_at"] = datetime.now().isoformat()
                    return meta
            except Exception:
                pass
        return {}

    def _get_sample_text(self, inputs: Dict) -> str:
        """
        Deprecated: previously fabricated sample marketing text.
        Real content is now resolved by _load_url_data; returns real text only.
        """
        url_data = self._load_url_data(inputs)
        return url_data.get("page_text", "")

    def get_module_status(self) -> Dict[str, str]:
        """Get status of all modules."""
        return {mid: info["name"] for mid, info in self.modules.items()}
