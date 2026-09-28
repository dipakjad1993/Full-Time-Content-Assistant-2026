"""
Module 17: Multi-Variant Entity A/B Testing & Split-Run Engine
Automated SEO experimentation pipeline.
"""
from typing import List, Dict, Any
from datetime import datetime, timedelta
import math
from statistics import NormalDist


class ABTestingEngine:
    """Module 17: Multi-Variant Entity A/B Testing & Split-Run Engine"""

    def __init__(self):
        self.module_id = "M17"
        self.module_name = "Multi-Variant Entity A/B Testing & Split-Run Engine"

    def _calculate_sample_size(self, baseline_p: float = 0.03, mde: float = 0.15,
                               power: float = 0.8, alpha: float = 0.05) -> Dict[str, Any]:
        """
        Compute the real required sample size per variant for a two-proportion
        z-test (e.g. organic CTR). Uses the standard closed-form formula:
            n = (Z_(1-alpha/2) + Z_power)^2 * (p0(1-p0) + p1(1-p1)) / (p1 - p0)^2
        """
        try:
            z_alpha = NormalDist().inv_cdf(1 - alpha / 2.0)
            z_beta = NormalDist().inv_cdf(power)
            p0 = max(0.0001, min(0.5, float(baseline_p)))
            p1 = min(0.999, p0 * (1 + float(mde)))
            if p1 <= p0:
                p1 = min(0.999, p0 + float(mde))
            if p1 <= p0:
                return {"baseline_p": round(p0, 4), "mde": float(mde),
                        "power": power, "alpha": alpha, "required_sample_per_variant": 0,
                        "formula": "two-proportion z-test"}
            denom = (p0 * (1 - p0) + p1 * (1 - p1)) / ((p1 - p0) ** 2)
            n = ((z_alpha + z_beta) ** 2) * denom
            return {
                "baseline_p": round(p0, 4),
                "mde": float(mde),
                "power": power,
                "alpha": alpha,
                "z_alpha_2": round(z_alpha, 3),
                "z_power": round(z_beta, 3),
                "p1_expected": round(p1, 4),
                "required_sample_per_variant": max(2, int(math.ceil(n))),
                "formula": "two-proportion z-test",
                "note": "Per-variant impressions required at 95% confidence and 80% power"
            }
        except Exception:
            return {"baseline_p": float(baseline_p), "mde": float(mde),
                    "power": power, "alpha": alpha,
                    "required_sample_per_variant": 1000, "formula": "fallback",
                    "estimate": True, "source": "heuristic, not measured"}

    def analyze(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Full A/B testing configuration pipeline."""
        url = inputs.get("url", "")
        variants = inputs.get("variants", [])
        entity = inputs.get("primary_entity", "")

        _url_data = inputs.get("_url_data", {})
        url_title = _url_data.get("title", "")
        url_page_text = _url_data.get("page_text", "")
        url_word_count = _url_data.get("word_count", 0)
        url_h1 = _url_data.get("h1", "")
        url_h2s = _url_data.get("h2s", [])
        url_image_count = _url_data.get("image_count", 0)
        url_link_count = _url_data.get("link_count", 0)
        url_has_schema = _url_data.get("has_schema", False)
        url_images = _url_data.get("images", [])

        url_ab_analysis = self._analyze_url_ab_opportunities(_url_data) if _url_data else {}

        sample_calc = self._calculate_sample_size(
            baseline_p=inputs.get("baseline_ctr", inputs.get("baseline_conversion_rate", 0.03)),
            mde=inputs.get("minimum_detectable_effect", 0.15),
        )
        sample_size_display = f"{sample_calc.get('required_sample_per_variant', 'N/A'):,}" if isinstance(sample_calc.get("required_sample_per_variant"), int) else str(sample_calc.get("required_sample_per_variant", "N/A"))

        test_design = self._design_test(inputs)
        variant_config = self._configure_variants(variants, entity)
        monitoring_setup = self._setup_monitoring(inputs)
        rollback_guards = self._configure_rollback_guards(inputs)
        statistical_framework = self._design_statistical_framework(inputs)

        return {
            "module": self.module_id,
            "module_name": self.module_name,
            "url_analyzed": _url_data.get("url", url),
            "url_ab_testing_analysis": url_ab_analysis if _url_data else {
                "status": "NO_URL_DATA",
                "message": "Provide _url_data for URL-specific A/B test design"
            },
            "test_design": test_design,
            "variant_configurations": variant_config,
            "monitoring_setup": monitoring_setup,
            "rollback_guards": rollback_guards,
            "statistical_framework": statistical_framework,
            "implementation_checklist": self._generate_checklist(test_design, variant_config),
            "recommendations": self._generate_recommendations(test_design, statistical_framework),
            "implementation_steps": [
                "Step 1: Define a clear hypothesis for each variant (e.g., 'Adding a 40-word definition block at the top will increase organic CTR by 10%+')",
                "Step 2: Create variant content for each test arm - ensure only ONE variable changes per variant to isolate impact",
                "Step 3: Deploy the control variant (A) to confirm current baseline metrics are stable for 7 days before test launch",
                "Step 4: Configure CDN worker or server-side logic to serve variants to 50/50 traffic split (or desired ratio)",
                "Step 5: Set up GSC monitoring for target queries - track clicks, impressions, CTR, and average position daily",
                "Step 6: Configure automatic rollback triggers (CTR drop >15%, position drop >3, impression drop >20%)",
                "Step 7: Launch the test on a Monday or Tuesday to avoid weekend traffic anomalies",
                "Step 8: Run daily monitoring dashboards - check for statistical anomalies, not just significance",
                "Step 9: At day 14, perform an interim significance check - if a variant is clearly losing, roll back early",
                "Step 10: At day 30, run the final analysis with Bonferroni correction for multiple variants",
                "Step 11: Document results with confidence intervals and effect sizes, not just p-values",
                "Step 12: Deploy the winning variant to 100% traffic and schedule the next test iteration"
            ],
            "where_to_add": [
                "Place variant content via CDN Worker response body modification (no origin changes needed)",
                "Add variant-specific meta tags in the <head> through edge injection or server-side rendering",
                "Deploy variant schema markup in the <script type='application/ld+json'> tag via CDN Worker",
                "Use URL query parameters or cookies for variant assignment (do not use cloaking or UA-based serving)",
                "Place variant tracking pixels in the <head> or before </body> via CDN injection",
                "Add variant identification headers (X-Test-Variant) via CDN for debugging and log correlation",
                "Deploy rollback logic in CDN Worker to instantly swap variant content on trigger conditions",
                "Place variant-specific Open Graph tags in <head> for social sharing differentiation",
                "Add variant A/B identifiers in server logs via custom headers for post-analysis correlation",
                "Configure variant deployment in CDN dashboard under Workers/Edge Functions with route rules"
            ],
            "detailed_analysis": {
                "statistical_benchmarks": {
                    "minimum_sample_size": f"{sample_size_display} impressions per variant for 80% power at 95% confidence (computed: baseline CTR {sample_calc.get('baseline_p', 'N/A')}, MDE {sample_calc.get('mde', 'N/A')})",
                    "minimum_detectable_effect": "(General industry guidance, unverified): 15% relative lift for CTR (realistic for SEO experiments)",
                    "typical_test_duration": "(General industry guidance, unverified): 30 days minimum for organic search (slower traffic than paid)",
                    "required_confidence_level": "95% (p < 0.05) with Bonferroni correction for >2 variants",
                    "power_threshold": "80% minimum - lower power increases false negative risk"
                },
                "seo_experiment_benchmarks": {
                    "data_origin": "unverified_industry_heuristic - not measured for this page",
                    "typical_ctr_lift_from_title_optimization": "5-20% relative improvement",
                    "typical_position_impact_from_content_restructure": "1-3 position improvement over 30 days",
                    "meta_description_test_success_rate": "60-70% show measurable CTR impact",
                    "schema_markup_test_impact": "10-30% CTR improvement for rich results eligible queries",
                    "definition_block_test_benchmarks": "8-15% CTR lift for informational queries"
                },
                "expert_recommendations": [
                    "Test title tag and meta description changes first - they have the fastest measurable impact",
                    "Use CDN-based serving (not page builders) to avoid latency and cloaking detection risks",
                    "Segment results by device, geo, and query intent - aggregate data can mask variant performance",
                    "Run pre-test baseline measurement for at least 7 days to establish stable control metrics",
                    "Document all changes in a test log with timestamps for reproducibility and post-analysis"
                ],
                "common_mistakes": [
                    "Running multiple simultaneous tests on the same URL contaminates results (one test per URL)",
                    "Changing multiple elements in one variant makes it impossible to attribute cause",
                    "Ending tests too early (<14 days) leads to false positives from natural variance",
                    "Ignoring novelty effects - first 3-5 days may show artificial lifts that regress",
                    "Not accounting for seasonal trends - run tests across complete business cycles when possible"
                ],
                "success_metrics": [
                    "Track primary metric (CTR) improvement with 95% confidence interval",
                    "Monitor secondary metrics (bounce rate, time on page) for unintended consequences",
                    "Measure ranking position change over the test period per variant",
                    "Track conversion rate impact if available (not just traffic metrics)",
                    "Document test velocity - time from hypothesis to statistically significant result"
                ]
            },
            "data_source": "real_time_analysis"
        }

    def _analyze_url_ab_opportunities(self, url_data: Dict) -> Dict[str, Any]:
        """Analyze actual page content to design specific A/B tests."""
        url = url_data.get("url", "")
        title = url_data.get("title", "")
        page_text = url_data.get("page_text", "")
        word_count = url_data.get("word_count", 0)
        h1 = url_data.get("h1", "")
        h2s = url_data.get("h2s", [])
        image_count = url_data.get("image_count", 0)
        link_count = url_data.get("link_count", 0)
        has_schema = url_data.get("has_schema", False)
        images = url_data.get("images", [])

        title_length = len(title)
        h1_length = len(h1)
        h2_count = len(h2s)

        current_title_word_count = len(title.split()) if title else 0
        current_meta_description_estimate = page_text[:155].replace('\n', ' ').strip() if page_text else ""

        recommended_tests = []

        if title:
            recommended_tests.append({
                "test_id": "AB_TITLE_001",
                "test_name": "Title Tag Optimization",
                "hypothesis": f"Current title ({title_length} chars, {current_title_word_count} words) can be improved for higher CTR",
                "control": {"title": title, "length": title_length},
                "variant_a": {
                    "name": "Title with Power Word",
                    "change": "Add a compelling modifier (e.g., 'Ultimate', 'Proven', 'Complete')",
                    "estimated_length": min(60, title_length + 10),
                    "rationale": "(General industry guidance, unverified): Power words increase CTR by 5-15% in SERPs"
                },
                "variant_b": {
                    "name": "Title with Current Year",
                    "change": f"Add current year to title for freshness signal",
                    "estimated_length": min(60, title_length + 6),
                    "rationale": "(General industry guidance, unverified): Year in title increases CTR by 10-25% for informational queries"
                },
                "primary_metric": "organic_ctr",
                "estimated_impact": "(General industry guidance, unverified): 5-20% CTR improvement",
                "test_duration_days": 30,
                "priority": "HIGH"
            })

        if word_count > 500:
            recommended_tests.append({
                "test_id": "AB_DEFINITION_001",
                "test_name": "Definition Block at Top",
                "hypothesis": f"Adding a 40-word definition block above the fold on this {word_count}-word page will increase time-on-page and reduce bounce rate",
                "control": {"structure": "Current intro", "word_count": word_count},
                "variant_a": {
                    "name": "Definition First",
                    "change": "Add a concise 40-word definition of the primary topic as the first paragraph",
                    "estimated_impact": "(General industry guidance, unverified): 8-15% CTR lift for informational queries"
                },
                "variant_b": {
                    "name": "Key Takeaway First",
                    "change": "Lead with the single most important takeaway or statistic",
                    "estimated_impact": "(General industry guidance, unverified): 5-12% bounce rate reduction"
                },
                "primary_metric": "bounce_rate",
                "test_duration_days": 30,
                "priority": "HIGH"
            })

        if h2_count >= 2:
            recommended_tests.append({
                "test_id": "AB_HEADING_001",
                "test_name": "H2 Heading Optimization",
                "hypothesis": f"Rewriting {h2_count} H2 headings to be more question-based and compelling will improve engagement",
                "control": {"h2s": h2s},
                "variant_a": {
                    "name": "Question-Based H2s",
                    "change": "Convert all H2s to question format (e.g., 'What is X?' instead of 'X Overview')",
                    "rationale": "Question-based headings match search intent and increase featured snippet eligibility"
                },
                "variant_b": {
                    "name": "Action-Based H2s",
                    "change": "Convert H2s to action-oriented phrases (e.g., 'How to Use X' instead of 'X Usage')",
                    "rationale": "Action-based headings improve engagement for how-to queries"
                },
                "primary_metric": "time_on_page",
                "test_duration_days": 30,
                "priority": "MEDIUM"
            })

        if not has_schema:
            recommended_tests.append({
                "test_id": "AB_SCHEMA_001",
                "test_name": "Schema Markup Injection",
                "hypothesis": "Adding structured data schema via edge worker will increase rich results CTR",
                "control": {"has_schema": False},
                "variant_a": {
                    "name": "Article Schema Added",
                    "change": "Inject Article/BlogPosting JSON-LD schema via CDN edge worker",
                    "rationale": "(General industry guidance, unverified): Schema markup can increase CTR by 10-30% for eligible queries"
                },
                "primary_metric": "organic_ctr",
                "test_duration_days": 30,
                "priority": "HIGH"
            })

        if image_count < 3 and word_count > 800:
            recommended_tests.append({
                "test_id": "AB_VISUAL_001",
                "test_name": "Visual Content Enhancement",
                "hypothesis": f"Adding 3-5 custom images/infographics to this {word_count}-word page with only {image_count} images will improve engagement",
                "control": {"image_count": image_count},
                "variant_a": {
                    "name": "Enhanced Visuals",
                    "change": f"Add {3 - image_count} custom images, charts, or screenshots",
                    "rationale": "(General industry guidance, unverified): Visual content increases time-on-page by 2-3x and social shares by 2x"
                },
                "primary_metric": "time_on_page",
                "test_duration_days": 30,
                "priority": "MEDIUM"
            })

        if link_count < 5 and word_count > 500:
            recommended_tests.append({
                "test_id": "AB_LINKS_001",
                "test_name": "Internal Link Density Test",
                "hypothesis": f"Adding contextual internal links (currently {link_count}, target 8-10) will improve page authority signals",
                "control": {"link_count": link_count},
                "variant_a": {
                    "name": "Enhanced Internal Linking",
                    "change": f"Add {8 - link_count} contextual internal links to related pages",
                    "rationale": "Internal links distribute page authority and improve crawlability"
                },
                "primary_metric": "average_position",
                "test_duration_days": 30,
                "priority": "MEDIUM"
            })

        recommended_tests.append({
            "test_id": "AB_META_001",
            "test_name": "Meta Description Optimization",
            "hypothesis": "Rewriting the meta description with a compelling CTA will improve SERP CTR",
            "control": {"current_meta": current_meta_description_estimate[:80] + "..." if current_meta_description_estimate else "No meta description"},
            "variant_a": {
                "name": "Action-Oriented Meta",
                "change": "Write meta description with clear value proposition and CTA",
                "estimated_length": 155,
                "rationale": "(General industry guidance, unverified): Meta descriptions with CTAs increase CTR by 5-15%"
            },
            "variant_b": {
                "name": "Question-Answer Meta",
                "change": "Start meta description with a question the page answers",
                "estimated_length": 155,
                "rationale": "Question-based meta descriptions match user intent for informational queries"
            },
            "primary_metric": "organic_ctr",
            "test_duration_days": 30,
            "priority": "HIGH"
        })

        return {
            "url": url,
            "page_title": title,
            "page_word_count": word_count,
            "page_h1": h1,
            "h2_count": h2_count,
            "h2_headings": h2s,
            "image_count": image_count,
            "link_count": link_count,
            "has_schema": has_schema,
            "current_title_length": title_length,
            "current_title_word_count": current_title_word_count,
            "recommended_ab_tests": recommended_tests,
            "total_recommended_tests": len(recommended_tests),
            "estimated_total_test_duration": f"{len(recommended_tests) * 30} days if run sequentially",
            "parallel_test_limit": 1,
            "test_priority_ranking": [
                {"test_id": t["test_id"], "test_name": t["test_name"], "priority": t["priority"]}
                for t in sorted(recommended_tests, key=lambda x: {"HIGH": 0, "MEDIUM": 1, "LOW": 2}.get(x["priority"], 3))
            ],
            "content_analysis_for_testing": {
                "title_optimization_potential": "HIGH" if title_length < 50 or title_length > 60 else "MODERATE",
                "definition_block_opportunity": "HIGH" if word_count > 500 else "LOW",
                "heading_optimization_potential": "HIGH" if h2_count >= 3 else "MODERATE" if h2_count >= 2 else "LOW",
                "schema_injection_opportunity": "HIGH" if not has_schema else "ALREADY_IMPLEMENTED",
                "visual_enhancement_opportunity": "HIGH" if image_count < 2 and word_count > 800 else "MODERATE" if image_count < 4 else "LOW",
                "internal_link_opportunity": "HIGH" if link_count < 4 else "MODERATE" if link_count < 8 else "OPTIMAL"
            },
            "sample_size_requirements": {
                "data_origin": "unverified_industry_heuristic - not measured for this page",
                "minimum_impressions_per_variant": 1000,
                "estimated_days_for_significance": "21-30 days depending on query volume",
                "recommended_baseline_period": "7 days before test launch",
                "confidence_level": "95% (p < 0.05)"
            }
        }

    def _design_test(self, inputs: Dict) -> Dict[str, Any]:
        """Design the A/B test structure."""
        baseline = inputs.get("baseline_ctr", inputs.get("baseline_conversion_rate", 0.03))
        mde = inputs.get("minimum_detectable_effect", 0.15)
        calc = self._calculate_sample_size(baseline_p=baseline, mde=mde)
        return {
            "test_id": f"SEO_AB_{datetime.now().strftime('%Y%m%d')}",
            "test_type": "content_variant",
            "target_url": inputs.get("url", ""),
            "entity": inputs.get("primary_entity", ""),
            "hypothesis": "Variant content structure will improve organic CTR and position",
            "primary_metric": "organic_ctr",
            "secondary_metrics": ["average_position", "impressions", "clicks", "bounce_rate"],
            "test_duration_days": 30,
            "minimum_sample_size": calc.get("required_sample_per_variant", 1000),
            "minimum_sample_size_origin": "computed via two-proportion z-test from provided baseline; fallback 1000 is heuristic, not measured",
            "confidence_level": 0.95,
            "traffic_split": {"control": 50, "variant": 50},
            "segments": ["all_traffic", "mobile", "desktop"],
            "exclusions": ["brand_queries", "direct_traffic"]
        }

    def _configure_variants(self, variants: List[Dict], entity: str) -> Dict[str, Any]:
        """Configure test variants."""
        if not variants:
            variants = [
                {"variant_id": "A", "name": "Control", "description": "Current content structure", "changes": []},
                {"variant_id": "B", "name": "Variant - Definition First", "description": "Add 40-word definition block at top", "changes": ["Add definition block", "Restructure H2 headings"]},
                {"variant_id": "C", "name": "Variant - Data Heavy", "description": "Lead with statistics and data", "changes": ["Add statistics section", "Add comparison table"]}
            ]
        configured = []
        for v in variants:
            configured.append({
                "variant_id": v.get("variant_id", f"V{len(configured)+1}"),
                "name": v.get("name", f"Variant {len(configured)+1}"),
                "description": v.get("description", ""),
                "changes": v.get("changes", []),
                "deployment_method": "cdn_worker",
                "cache_invalidation": "on_deploy",
                "tracking_enabled": True
            })
        return {
            "variants": configured,
            "total_variants": len(configured),
            "control_variant": configured[0] if configured else None,
            "test_variants": configured[1:] if len(configured) > 1 else []
        }

    def _setup_monitoring(self, inputs: Dict) -> Dict[str, Any]:
        """Setup monitoring for the test."""
        return {
            "gsc_monitoring": {
                "queries_tracked": 10,
                "metrics": ["clicks", "impressions", "ctr", "position"],
                "check_frequency": "daily",
                "alert_thresholds": {
                    "data_origin": "unverified_industry_heuristic - not measured for this page",
                    "ctr_drop": 0.15,
                    "position_drop": 3,
                    "impression_drop": 0.2
                }
            },
            "analytics_monitoring": {
                "metrics": ["bounce_rate", "time_on_page", "pages_per_session", "conversions"],
                "check_frequency": "daily",
                "segment_by": ["device", "traffic_source", "geo"]
            },
            "serp_monitoring": {
                "ai_overview_tracking": True,
                "featured_snippet_tracking": True,
                "competitor_tracking": True,
                "check_frequency": "daily"
            }
        }

    def _configure_rollback_guards(self, inputs: Dict) -> Dict[str, Any]:
        """Configure automatic rollback guardrails."""
        return {
            "auto_rollback_triggers": [
                {
                    "trigger": "CTR_DROP",
                    "condition": "(General industry guidance, unverified): CTR drops > 15% compared to control within 7 days",
                    "action": "Automatically revert variant to control",
                    "notification": "Immediate email + Slack alert"
                },
                {
                    "trigger": "POSITION_DROP",
                    "condition": "(General industry guidance, unverified): Average position drops > 3 positions within 7 days",
                    "action": "Automatically revert variant to control",
                    "notification": "Immediate email + Slack alert"
                },
                {
                    "trigger": "IMPRESSION_DROP",
                    "condition": "(General industry guidance, unverified): Impressions drop > 20% compared to control within 7 days",
                    "action": "Flag for manual review, prepare rollback",
                    "notification": "Email alert within 1 hour"
                },
                {
                    "trigger": "INDEXATION_ISSUE",
                    "condition": "Page drops from index during test",
                    "action": "Immediate rollback and emergency investigation",
                    "notification": "Immediate page + email alert"
                }
            ],
            "rollback_execution": {
                "method": "CDN worker swap",
                "execution_time": "< 5 minutes",
                "verification": "Automatic SERP position check post-rollback"
            },
            "manual_override": "Available via dashboard with 1-click rollback"
        }

    def _design_statistical_framework(self, inputs: Dict) -> Dict[str, Any]:
        """Design statistical framework for the test."""
        baseline = inputs.get("baseline_ctr", inputs.get("baseline_conversion_rate", 0.03))
        mde = inputs.get("minimum_detectable_effect", 0.15)
        calc = self._calculate_sample_size(baseline_p=baseline, mde=mde)
        return {
            "sample_size_calculation": {
                "baseline_ctr": calc.get("baseline_p", baseline),
                "minimum_detectable_effect": mde,
                "power": 0.8,
                "significance_level": 0.05,
                "required_sample_per_variant": calc.get("required_sample_per_variant", 1000),
                "estimated_days_to_significance": 30,
                "estimated_days_to_significance_origin": "heuristic, not measured",
                "calculation_method": "two-proportion z-test"
            },
            "analysis_method": "Frequentist A/B testing with sequential monitoring",
            "multiple_comparison_correction": "Bonferroni correction for > 2 variants",
            "effect_size_measurement": "Relative lift with 95% confidence interval",
            "reporting": {
                "daily_snapshot": "Automated dashboard update",
                "weekly_report": "Statistical significance check",
                "final_report": "Full analysis with recommendation"
            }
        }

    def _generate_checklist(self, test_design: Dict, variants: Dict) -> List[Dict[str, str]]:
        """Generate implementation checklist."""
        return [
            {"task": "Finalize variant content changes", "priority": "HIGH", "deadline": "Day 1"},
            {"task": "Deploy variant B via CDN worker", "priority": "HIGH", "deadline": "Day 2"},
            {"task": "Verify variant rendering for search bots", "priority": "CRITICAL", "deadline": "Day 2"},
            {"task": "Set up GSC monitoring for target queries", "priority": "HIGH", "deadline": "Day 3"},
            {"task": "Configure rollback guardrails", "priority": "HIGH", "deadline": "Day 3"},
            {"task": "Baseline measurement (7-day pre-test)", "priority": "MEDIUM", "deadline": "Day 3-10"},
            {"task": "Start test (Day 11)", "priority": "HIGH", "deadline": "Day 11"},
            {"task": "Weekly significance check", "priority": "MEDIUM", "deadline": "Weekly"},
            {"task": "Final analysis and decision", "priority": "HIGH", "deadline": "Day 40"}
        ]

    def _generate_recommendations(self, test_design: Dict, stats: Dict) -> List[Dict[str, str]]:
        """Generate A/B testing recommendations."""
        return [
            {
                "priority": "HIGH",
                "action": "Run pre-test baseline for 7 days",
                "detail": "Establish reliable baseline before introducing variants"
            },
            {
                "priority": "MEDIUM",
                "action": f"Target minimum {stats['sample_size_calculation']['required_sample_per_variant']} impressions per variant",
                "detail": f"Required for 80% power at 95% confidence"
            },
            {
                "priority": "MEDIUM",
                "action": "Test only one variable at a time",
                "detail": "Isolate impact of specific content changes"
            }
        ]
