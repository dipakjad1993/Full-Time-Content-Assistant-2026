"""
Module 8: Interactive & Multi-Modal Asset Blueprint
Generates specs for charts, calculators, images, and multimedia assets.
"""
import re
from typing import List, Dict, Any
from ..utils.text_analytics import tokenize_words, extract_entities_simple


class MultimodalAssetBlueprint:
    """Module 8: Interactive & Multi-Modal Asset Blueprint"""

    def __init__(self):
        self.module_id = "M08"
        self.module_name = "Interactive & Multi-Modal Asset Blueprint"

    def analyze(self, text: str, outline: Dict = None, schema_data: Dict = None, inputs: Dict = None) -> Dict[str, Any]:
        """Full multi-modal asset planning pipeline with REAL competitor analysis."""
        if not text.strip():
            return {"module": self.module_id, "module_name": self.module_name, "error": "No text provided"}

        inputs = inputs or {}
        url_data = inputs.get("_url_data", None)
        
        # NEW: Use real competitor data
        real_competitor_pages = inputs.get("real_competitor_pages", [])
        real_content_analysis = inputs.get("real_content_analysis", {})

        real_url_findings = {}
        if url_data:
            real_url_findings = self._analyze_url_multimodal(text, url_data, outline)

        data_points = self._identify_data_points(text)
        chart_specs = self._generate_chart_specifications(data_points)
        calculator_specs = self._generate_calculator_specifications(text)
        image_specs = self._generate_image_specifications(text, outline)
        video_specs = self._generate_video_specifications(text, outline)
        table_specs = self._generate_table_specifications(text)
        infographic_specs = self._generate_infographic_specifications(text, data_points)
        alt_text_pipeline = self._generate_alt_text_pipeline(image_specs, schema_data)
        asset_deployment = self._plan_asset_deployment(chart_specs, calculator_specs, image_specs)
        
        # NEW: Analyze real competitor multimodal usage
        real_competitor_multimodal = self._analyze_real_competitor_multimodal(real_competitor_pages, real_content_analysis)

        return {
            "module": self.module_id,
            "module_name": self.module_name,
            "data_points_identified": data_points,
            "chart_specifications": chart_specs,
            "calculator_specifications": calculator_specs,
            "image_specifications": image_specs,
            "video_specifications": video_specs,
            "table_specifications": table_specs,
            "infographic_specifications": infographic_specs,
            "alt_text_pipeline": alt_text_pipeline,
            "asset_deployment_plan": asset_deployment,
            "total_assets_recommended": (
                len(chart_specs["charts"]) + len(calculator_specs["calculators"]) +
                len(image_specs["images"]) + len(video_specs["videos"])
            ),
            "implementation_priority": self._prioritize_assets(chart_specs, calculator_specs, image_specs),
            **({"url_analysis": real_url_findings} if real_url_findings else {}),
            "implementation_steps": [
                "Step 1: Audit existing content for data points that can be visualized (percentages, monetary values, trends)",
                "Step 2: Create chart specifications using Chart.js or D3.js for each identified data cluster",
                "Step 3: Design calculator widgets (ROI, TCO, Comparison) as React/Vue components with client-side computation",
                "Step 4: Generate hero image (1200x630 WebP) and section illustrations (800x400) with descriptive alt text",
                "Step 5: Write video scripts (60-90s explainer, 3-5min tutorial) and produce with brand-consistent visuals",
                "Step 6: Build responsive comparison tables with horizontal scroll on mobile and card layout fallback",
                "Step 7: Implement lazy loading for all below-fold assets using Intersection Observer",
                "Step 8: Add ImageObject/VideoObject schema via JSON-LD in <head> for each asset",
                "Step 9: Deploy assets via CDN with WebP optimization and responsive srcset attributes",
                "Step 10: Test accessibility with screen readers and verify WCAG 2.1 AA compliance for all alt text"
            ],
            "where_to_add": [
                "Place hero image above H1 heading before content begins",
                "Embed charts within relevant H2 sections using responsive containers (max-width: 100%)",
                "Position calculator widgets after pricing or ROI discussion sections",
                "Add comparison tables in 'Comparison' or 'Alternatives' H2 sections",
                "Insert section illustrations within corresponding H2 sections below headings",
                "Place explainer video below introductory H2 section, above fold preferred",
                "Add tutorial video within HowTo implementation section",
                "Include infographics in summary or conclusion sections",
                "Add source attribution links below each chart/table",
                "Place call-to-action buttons after calculator results"
            ],
            "detailed_analysis": {
                "industry_benchmarks": {
                    "data_origin": "unverified_industry_heuristic - not measured for this page",
                    "average_assets_per_article": "3-5 visual assets for top-performing content",
                    "chart_engagement_rate": "Charts increase dwell time by 25-40% vs text-only",
                    "calculator_conversion_rate": "Interactive calculators generate 2-3x more leads than static content",
                    "video_retention_rate": "Videos retain 95% of message vs 10% for text",
                    "image_optimization_impact": "WebP images reduce load time by 30-50% vs JPEG"
                },
                "statistical_ranges": {
                    "data_origin": "unverified_industry_heuristic - not measured for this page",
                    "optimal_image_count": "4-8 images per 2000-word article",
                    "chart_data_points": "3-6 data points per chart for clarity",
                    "calculator_input_fields": "4-6 fields maximum to avoid abandonment",
                    "video_duration": "60-90 seconds for explainer, 3-5 minutes for tutorial",
                    "table_columns": "4-5 columns maximum for mobile readability"
                },
                "expert_recommendations": [
                    "Always provide text alternatives for visual assets for accessibility and SEO",
                    "Use descriptive alt text that includes target keywords naturally (not keyword-stuffed)",
                    "Implement lazy loading for all assets below the fold to improve LCP",
                    "Add interactive elements (calculators, comparison tools) to increase engagement signals",
                    "Include source attribution for all data visualizations to build trust",
                    "Test asset rendering across devices and connection speeds",
                    "Use schema markup for all visual assets to enable rich results"
                ],
                "common_mistakes_to_avoid": [
                    "Using generic alt text like 'image' or 'chart' instead of descriptive text",
                    "Embedding large uncompressed images that slow page load",
                    "Creating charts with too many data points that become unreadable",
                    "Placing videos without transcripts or captions (accessibility issue)",
                    "Using fixed-width tables that break on mobile devices",
                    "Not providing fallback images for animated charts",
                    "Forgetting to add schema markup for visual assets"
                ],
                "success_metrics_to_track": [
                    "Engagement rate increase after adding visual assets",
                    "Dwell time improvement per asset type",
                    "Calculator completion rates and lead generation",
                    "Social sharing rates for visual content",
                    "Accessibility compliance scores (WCAG 2.1 AA)",
                    "Page load speed impact after asset optimization",
                    "Rich result appearance rate for schema-marked assets"
                ]
            },
            "real_competitor_multimodal_analysis": real_competitor_multimodal,
            "data_source": "real_time_competitor_analysis" if real_competitor_multimodal and "error" not in real_competitor_multimodal else "heuristic_analysis"
        }

    def _analyze_real_competitor_multimodal(self, competitor_pages: List[Dict], content_analysis: Dict) -> Dict[str, Any]:
        """Analyze real competitor multimodal asset usage from live pages."""
        if not competitor_pages:
            return {"error": "No competitor data available"}
        
        successful_pages = [p for p in competitor_pages if p.get("fetch_success")]
        if not successful_pages:
            return {"error": "No successful competitor fetches"}
        
        competitor_assets = []
        for page in competitor_pages:
            if not page.get("fetch_success"):
                continue
            images = page.get("images", [])
            image_count = page.get("image_count", 0)
            link_count = page.get("link_count", 0)
            has_schema = page.get("has_schema", False)
            
            # Count different types of visual assets
            chart_indicators = len([img for img in images if any(w in img.get("src", "").lower() or img.get("alt", "").lower() for w in ["chart", "graph", "data", "stat", "infographic"])])
            hero_images = len([img for img in images if any(w in img.get("src", "").lower() or img.get("alt", "").lower() for w in ["hero", "banner", "featured", "main", "cover"])])
            screenshots = len([img for img in images if any(w in img.get("src", "").lower() or img.get("alt", "").lower() for w in ["screenshot", "screen", "demo", "interface", "ui"])])
            
            competitor_assets.append({
                "url": page.get("url", ""),
                "position": page.get("position", 0),
                "total_images": image_count,
                "chart_indicators": chart_indicators,
                "hero_images": hero_images,
                "screenshots": screenshots,
                "other_images": image_count - chart_indicators - hero_images - screenshots,
                "has_schema": has_schema,
                "word_count": page.get("word_count", 0),
                "images_per_1000_words": round(image_count / max(1, page.get("word_count", 1)) * 1000, 1),
                "alt_text_examples": [img.get("alt", "") for img in images[:5] if img.get("alt")]
            })
        
        # Calculate benchmarks
        avg_images = sum(c["total_images"] for c in competitor_assets) / len(competitor_assets) if competitor_assets else 0
        avg_images_per_1000 = sum(c["images_per_1000_words"] for c in competitor_assets) / len(competitor_assets) if competitor_assets else 0
        avg_charts = sum(c["chart_indicators"] for c in competitor_assets) / len(competitor_assets) if competitor_assets else 0
        schema_users = sum(1 for c in competitor_assets if c["has_schema"])
        
        return {
            "competitors_analyzed": len(competitor_assets),
            "competitor_asset_details": competitor_assets,
            "benchmarks_from_real_data": {
                "avg_images_per_page": round(avg_images, 1),
                "avg_images_per_1000_words": round(avg_images_per_1000, 1),
                "avg_charts_per_page": round(avg_charts, 1),
                "schema_usage": f"{schema_users}/{len(competitor_assets)}"
            },
            "recommendations": [
                f"Add {round(avg_images)} images per page (competitors average {avg_images:.1f})",
                f"Target {round(avg_images_per_1000)} images per 1000 words",
                f"Add {max(0, 2 - int(avg_charts))} chart/graph visualizations",
                "Implement schema markup for visual assets" if schema_users < len(competitor_assets) else "Schema markup is competitive"
            ],
            "data_source": "live_competitor_page_analysis"
        }

    def _analyze_url_multimodal(self, text: str, url_data: Dict, outline: Dict = None) -> Dict[str, Any]:
        """Deep multimodal analysis using actual URL content data."""
        page_text = url_data.get("page_text", "")
        word_count = url_data.get("word_count", 0)
        title = url_data.get("title", "")
        h1 = url_data.get("h1", "")
        h2s = url_data.get("h2s", [])
        images = url_data.get("images", [])
        links = url_data.get("links", [])
        image_count = url_data.get("image_count", 0)
        link_count = url_data.get("link_count", 0)
        has_schema = url_data.get("has_schema", False)

        actual_word_count = len(page_text.split()) if page_text else word_count

        # Analyze actual images on the page
        real_images = []
        images_with_alt = 0
        images_without_alt = 0
        empty_alt_images = 0
        alt_text_lengths = []
        for img in images:
            alt = img.get("alt", "")
            src = img.get("src", "")
            alt_len = len(alt)
            alt_text_lengths.append(alt_len)
            has_quality_alt = alt_len >= 10
            if alt and alt.strip():
                if alt_len >= 10:
                    images_with_alt += 1
                else:
                    empty_alt_images += 1
            else:
                images_without_alt += 1
            real_images.append({
                "src": src[:120],
                "alt_text": alt[:100] if alt else "(empty)",
                "alt_length": alt_len,
                "alt_quality": "GOOD" if alt_len >= 10 else "POOR" if alt_len > 0 else "MISSING",
                "seo_value": "HIGH" if alt_len >= 10 and any(kw in alt.lower() for kw in title.lower().split()[:3]) else "LOW"
            })

        avg_alt_length = round(sum(alt_text_lengths) / max(1, len(alt_text_lengths)), 1)
        alt_text_coverage = round(images_with_alt / max(1, len(images)) * 100, 1)

        # Image-to-text ratio analysis
        ideal_image_ratio = 1 / 300  # 1 image per 300 words
        actual_ratio = image_count / max(1, actual_word_count)
        ratio_comparison = actual_ratio / ideal_image_ratio if ideal_image_ratio > 0 else 0
        images_needed_for_optimal = max(0, int(actual_word_count / 300) - image_count)

        # Analyze visual content gaps based on actual headings and content
        visual_gaps = []
        data_in_text = len(re.findall(r'\d+(?:\.\d+)?%', page_text)) if page_text else 0
        comparison_in_text = bool(re.search(r'(?:compared?|versus|vs\.?|alternatives?)', page_text or "", re.IGNORECASE))
        process_in_text = bool(re.search(r'(?:step[sd]?|how[- ]to|guide|implementation)', page_text or "", re.IGNORECASE))
        quote_in_text = bool(re.search(r'["\u201c][^"\u201d]{30,}["\u201d]', page_text or ""))

        if data_in_text >= 3:
            visual_gaps.append({
                "gap": f"Page contains {data_in_text} percentage statistics but no data visualization",
                "recommendation": "Add bar chart or infographic to visualize key statistics",
                "priority": "HIGH",
                "impact": "(General industry guidance, unverified): Charts increase dwell time by 25-40% per industry research"
            })
        if comparison_in_text and image_count < 3:
            visual_gaps.append({
                "gap": "Comparison/alternative content present but lacks visual comparison table",
                "recommendation": "Add feature comparison matrix or pricing table visual",
                "priority": "HIGH",
                "impact": "(General industry guidance, unverified): Comparison visuals increase conversion by 15-25%"
            })
        if process_in_text and image_count < 2:
            visual_gaps.append({
                "gap": "Process/implementation content lacks step-by-step visuals",
                "recommendation": "Add process flow diagram or step-by-step illustration",
                "priority": "MEDIUM",
                "impact": "(General industry guidance, unverified): Process visuals improve comprehension by 30%"
            })
        if actual_word_count > 1500 and image_count < 4:
            visual_gaps.append({
                "gap": f"Long-form content ({actual_word_count} words) with only {image_count} images",
                "recommendation": f"Add {max(2, images_needed_for_optimal)} more images to reach optimal 1-per-300-words ratio",
                "priority": "MEDIUM",
                "impact": "(General industry guidance, unverified): Long-form content with adequate visuals retains 40% more readers"
            })
        if not quote_in_text and actual_word_count > 800:
            visual_gaps.append({
                "gap": "No expert quotes or testimonials detected in content",
                "recommendation": "Add expert quote callout boxes with headshot images",
                "priority": "MEDIUM",
                "impact": "Expert quotes increase content credibility and dwell time"
            })

        # Alt text quality detailed assessment
        alt_issues = []
        for img_detail in real_images:
            if img_detail["alt_quality"] == "MISSING":
                alt_issues.append(f"Image '{img_detail['src'][:60]}...' has no alt text")
            elif img_detail["alt_quality"] == "POOR":
                alt_issues.append(f"Image '{img_detail['src'][:60]}...' has insufficient alt text ({img_detail['alt_length']} chars)")

        # Suggested visual assets based on actual content
        suggested_assets = []
        if actual_word_count > 500:
            suggested_assets.append({
                "asset_type": "hero_image",
                "reason": f"Content is {actual_word_count} words - needs compelling hero for engagement",
                "specs": "1200x630 WebP, descriptive alt text with primary keyword"
            })
        if data_in_text >= 2:
            suggested_assets.append({
                "asset_type": "data_chart",
                "reason": f"{data_in_text} statistical data points identified that should be visualized",
                "specs": "800x400 responsive Chart.js/D3.js with source attribution"
            })
        if len(h2s) >= 4:
            suggested_assets.append({
                "asset_type": "section_illustrations",
                "reason": f"{len(h2s)} H2 sections would benefit from supporting visuals",
                "specs": "800x400 WebP, one per H2 section with descriptive alt text"
            })
        if actual_word_count > 1000:
            suggested_assets.append({
                "asset_type": "infographic",
                "reason": "Long-form content suitable for visual summary",
                "specs": "800x1200 SVG, key statistics and process flow"
            })

        return {
            "page_url": url_data.get("url", ""),
            "page_title": title,
            "content_word_count": actual_word_count,
            "current_image_count": image_count,
            "ideal_image_count": int(actual_word_count / 300) + 1,
            "images_needed_for_optimal": images_needed_for_optimal,
            "image_to_text_ratio": {
                "current_ratio": f"1 image per {int(actual_word_count / max(1, image_count))} words",
                "ideal_ratio": "1 image per 300 words",
                "ideal_ratio_origin": "unverified_industry_heuristic - not measured for this page",
                "ratio_score": round(min(1.0, ratio_comparison), 3),
                "status": "OPTIMAL" if ratio_comparison >= 0.8 else "NEEDS_MORE" if ratio_comparison >= 0.5 else "CRITICALLY_LOW"
            },
            "actual_images_audit": real_images,
            "alt_text_analysis": {
                "total_images": len(images),
                "images_with_good_alt": images_with_alt,
                "images_without_alt": images_without_alt,
                "images_with_short_alt": empty_alt_images,
                "average_alt_text_length": avg_alt_length,
                "alt_text_coverage_percent": alt_text_coverage,
                "alt_text_issues": alt_issues,
                "alt_quality_verdict": "GOOD" if alt_text_coverage >= 80 else "NEEDS_IMPROVEMENT" if alt_text_coverage >= 50 else "POOR"
            },
            "visual_content_gaps": visual_gaps,
            "suggested_visual_assets": suggested_assets,
            "data_visualization_readiness": {
                "statistics_in_content": data_in_text,
                "comparison_content_detected": comparison_in_text,
                "process_content_detected": process_in_text,
                "chart_priority": "HIGH" if data_in_text >= 3 else "MEDIUM" if data_in_text >= 1 else "LOW"
            },
            "schema_for_visuals": {
                "has_image_schema": has_schema,
                "recommendation": "Add ImageObject schema for all images" if not has_schema else "Image schema present - verify completeness",
                "images_needing_schema": len(images)
            },
            "benchmark_comparison": {
                "data_origin": "unverified_industry_heuristic - not measured for this page",
                "top_content_avg_images": "4-8 images per 2000-word article",
                "your_image_density": f"{round(image_count / max(1, actual_word_count / 1000), 1)} images per 1000 words",
                "industry_standard": "3-5 images per 1000 words for optimal engagement",
                "positioning": "Above average" if image_count >= actual_word_count / 300 else "Below average - add more visuals"
            }
        }

    def _identify_data_points(self, text: str) -> List[Dict[str, Any]]:
        """Identify data points suitable for visualization."""
        data_points = []
        stat_patterns = [
            (r'(\d+(?:\.\d+)?)%', "percentage", "Use bar chart or pie chart"),
            (r'\$(\d+(?:,\d{3})*(?:\.\d+)?)\s*(million|billion|trillion|M|B|K)?', "monetary", "Use bar chart or comparison table"),
            (r'(\d+(?:,\d{3})*(?:\.\d+)?)\s*(times|x)', "comparison", "Use comparison bar chart"),
            (r'(\d+(?:\.\d+)?)\s*(hours|minutes|days|weeks|months|years)', "time", "Use timeline or progress chart"),
            (r'(?:increase|decrease|growth|decline)\s+(?:of|by)\s+(\d+(?:\.\d+)?)%', "trend", "Use line chart or trend arrow"),
        ]
        seen = set()
        for pattern, dp_type, chart_suggestion in stat_patterns:
            for m in re.finditer(pattern, text, re.IGNORECASE):
                stat = m.group().strip()
                if stat not in seen:
                    seen.add(stat)
                    context = text[max(0, m.start()-50):min(len(text), m.end()+50)].strip()
                    data_points.append({
                        "data_point": stat,
                        "type": dp_type,
                        "context": context,
                        "chart_suggestion": chart_suggestion,
                        "position": m.start(),
                        "visualization_priority": "HIGH" if dp_type in ["percentage", "monetary"] else "MEDIUM"
                    })
        return data_points[:15]

    def _generate_chart_specifications(self, data_points: List[Dict]) -> Dict[str, Any]:
        """Generate chart specifications for data visualization."""
        charts = []
        chart_id = 1
        percentage_points = [d for d in data_points if d["type"] == "percentage"]
        if len(percentage_points) >= 2:
            charts.append({
                "chart_id": f"CHART_{chart_id}",
                "chart_type": "bar_chart",
                "title": "Key Metrics Comparison",
                "data_points_used": [d["data_point"] for d in percentage_points[:6]],
                "x_axis": "Metric Category",
                "y_axis": "Percentage",
                "color_scheme": "brand_primary",
                "responsive": True,
                "interactive": True,
                "tooltip_enabled": True,
                "source_attribution_required": True,
                "schema_type": "ImageObject",
                "implementation": "Chart.js or D3.js",
                "alt_text_template": "Bar chart showing [metric] comparison: [values]"
            })
            chart_id += 1
        monetary_points = [d for d in data_points if d["type"] == "monetary"]
        if len(monetary_points) >= 2:
            charts.append({
                "chart_id": f"CHART_{chart_id}",
                "chart_type": "comparison_table",
                "title": "Cost Comparison Analysis",
                "data_points_used": [d["data_point"] for d in monetary_points[:6]],
                "columns": ["Solution", "Price", "Features", "Best For"],
                "highlight_best_value": True,
                "responsive": True,
                "schema_type": "Table",
                "implementation": "HTML table with responsive CSS",
                "alt_text_template": "Comparison table showing pricing for [solutions]"
            })
            chart_id += 1
        trend_points = [d for d in data_points if d["type"] == "trend"]
        if trend_points:
            charts.append({
                "chart_id": f"CHART_{chart_id}",
                "chart_type": "line_chart",
                "title": "Trend Analysis",
                "data_points_used": [d["data_point"] for d in trend_points[:5]],
                "x_axis": "Time Period",
                "y_axis": "Value",
                "trend_line": True,
                "forecast_available": True,
                "responsive": True,
                "interactive": True,
                "schema_type": "ImageObject",
                "implementation": "Chart.js with annotations plugin",
                "alt_text_template": "Line chart showing trend of [metric] over [timeframe]"
            })
            chart_id += 1
        return {
            "charts": charts,
            "total_charts": len(charts),
            "data_points_used": sum(len(c.get("data_points_used", [])) for c in charts),
            "implementation_notes": [
                "Use responsive containers (max-width: 100%)",
                "Include source attribution below each chart",
                "Add descriptive alt text for accessibility",
                "Implement lazy loading for below-fold charts",
                "Add ImageObject schema for each chart"
            ]
        }

    def _generate_calculator_specifications(self, text: str) -> Dict[str, Any]:
        """Generate calculator widget specifications."""
        calculators = []
        roi_patterns = [
            r'(?:ROI|return\s+on\s+investment)',
            r'(?:cost\s+(?:savings?|reduction|benefit))',
            r'(?:payback\s+period)',
            r'(?:total\s+cost\s+of\s+ownership|TCO)',
        ]
        has_roi_content = any(re.search(p, text, re.IGNORECASE) for p in roi_patterns)
        if has_roi_content:
            calculators.append({
                "calculator_id": "CALC_1",
                "calculator_type": "roi_calculator",
                "title": "ROI Calculator",
                "description": "Calculate return on investment for [entity]",
                "input_fields": [
                    {"name": "current_annual_cost", "type": "currency", "label": "Current Annual Cost ($)", "default": 50000, "value_origin": "example placeholder - not measured data; replace with actual figures"},
                    {"name": "implementation_cost", "type": "currency", "label": "Implementation Cost ($)", "default": 15000, "value_origin": "example placeholder - not measured data; replace with actual figures"},
                    {"name": "annual_savings_percent", "type": "percentage", "label": "Expected Annual Savings (%)", "default": 30, "value_origin": "example placeholder - not measured data; replace with actual figures"},
                    {"name": "time_period_years", "type": "number", "label": "Analysis Period (Years)", "default": 3, "value_origin": "example placeholder - not measured data; replace with actual figures"}
                ],
                "output_fields": [
                    {"name": "total_savings", "type": "currency", "formula": "current_annual_cost * (annual_savings_percent/100) * time_period_years"},
                    {"name": "net_benefit", "type": "currency", "formula": "total_savings - implementation_cost"},
                    {"name": "roi_percent", "type": "percentage", "formula": "(net_benefit / implementation_cost) * 100"},
                    {"name": "payback_months", "type": "number", "formula": "(implementation_cost / (current_annual_cost * annual_savings_percent / 100)) * 12"}
                ],
                "chart_output": "bar_chart_comparing_costs",
                "schema_type": "SoftwareApplication",
                "interactive": True,
                "share_results": True
            })
        comparison_patterns = [
            r'(?:compare|comparison|vs\.?|versus)',
            r'(?:which\s+(?:is|solution)\s+better)',
            r'(?:best\s+(?:option|solution|choice))',
        ]
        has_comparison = any(re.search(p, text, re.IGNORECASE) for p in comparison_patterns)
        if has_comparison:
            calculators.append({
                "calculator_id": "CALC_2",
                "calculator_type": "comparison_tool",
                "title": "Solution Comparison Tool",
                "description": "Compare features and costs across solutions",
                "input_fields": [
                    {"name": "solution_a_name", "type": "text", "label": "Solution A Name"},
                    {"name": "solution_a_price", "type": "currency", "label": "Solution A Monthly Price ($)"},
                    {"name": "solution_a_features", "type": "checkbox_group", "label": "Solution A Features"},
                    {"name": "solution_b_name", "type": "text", "label": "Solution B Name"},
                    {"name": "solution_b_price", "type": "currency", "label": "Solution B Monthly Price ($)"},
                    {"name": "solution_b_features", "type": "checkbox_group", "label": "Solution B Features"},
                    {"name": "team_size", "type": "number", "label": "Team Size", "default": 10, "value_origin": "example placeholder - not measured data; replace with actual figures"}
                ],
                "output_fields": [
                    {"name": "annual_cost_a", "type": "currency"},
                    {"name": "annual_cost_b", "type": "currency"},
                    {"name": "feature_score_a", "type": "score"},
                    {"name": "feature_score_b", "type": "score"},
                    {"name": "recommended_solution", "type": "text"}
                ],
                "chart_output": "side_by_side_comparison",
                "interactive": True
            })
        tco_patterns = [
            r'(?:total\s+cost\s+of\s+ownership|TCO)',
            r'(?:total\s+cost\s+analysis)',
            r'(?:cost\s+breakdown)',
        ]
        has_tco = any(re.search(p, text, re.IGNORECASE) for p in tco_patterns)
        if has_tco:
            calculators.append({
                "calculator_id": "CALC_3",
                "calculator_type": "tco_calculator",
                "title": "Total Cost of Ownership Calculator",
                "description": "Calculate 3-year total cost of ownership",
                "input_fields": [
                    {"name": "license_cost", "type": "currency", "label": "Annual License Cost ($)"},
                    {"name": "implementation_cost", "type": "currency", "label": "One-time Implementation Cost ($)"},
                    {"name": "training_cost", "type": "currency", "label": "Annual Training Cost ($)"},
                    {"name": "maintenance_cost", "type": "currency", "label": "Annual Maintenance Cost ($)"},
                    {"name": "personnel_cost", "type": "currency", "label": "Annual Personnel Cost ($)"},
                    {"name": "years", "type": "number", "label": "Analysis Period (Years)", "default": 3, "value_origin": "example placeholder - not measured data; replace with actual figures"}
                ],
                "output_fields": [
                    {"name": "total_tco", "type": "currency"},
                    {"name": "annual_tco", "type": "currency"},
                    {"name": "cost_per_user", "type": "currency"},
                    {"name": "cost_breakdown_chart", "type": "pie_chart"}
                ],
                "interactive": True
            })
        return {
            "calculators": calculators,
            "total_calculators": len(calculators),
            "implementation_framework": "React/Vue component with Chart.js integration",
            "mobile_optimization": "Touch-friendly inputs, responsive layout",
            "data_privacy": "All calculations client-side, no data sent to server"
        }

    def _generate_image_specifications(self, text: str, outline: Dict = None) -> Dict[str, Any]:
        """Generate image and visual asset specifications."""
        images = []
        entities = extract_entities_simple(text)
        images.append({
            "image_id": "IMG_1",
            "image_type": "hero_image",
            "title": "Hero Banner Image",
            "description": "Featured image for article header and social sharing",
            "dimensions": {"width": 1200, "height": 630},
            "format": "WebP with JPEG fallback",
            "max_file_size": "150KB",
            "alt_text": "Comprehensive guide to [entity] - featured image",
            "schema_type": "ImageObject",
            "placement": "Above H1, before content begins",
            "social_optimization": {
                "og_image": "1200x630",
                "twitter_card": "summary_large_image",
                "schema_dimensions": "1200x630"
            }
        })
        if any(d.get("type") == "percentage" for d in [{"type": "percentage"}]):
            images.append({
                "image_id": "IMG_2",
                "image_type": "infographic",
                "title": "Key Statistics Infographic",
                "description": "Visual representation of key statistics and data points",
                "dimensions": {"width": 800, "height": "variable"},
                "format": "SVG with PNG fallback",
                "sections": ["Header", "Statistics Grid", "Source Attribution"],
                "alt_text": "Infographic showing key [entity] statistics and market data",
                "schema_type": "ImageObject"
            })
        images.append({
            "image_id": f"IMG_{len(images)+1}",
            "image_type": "feature_comparison",
            "title": "Feature Comparison Visual",
            "description": "Visual comparison matrix of key features",
            "dimensions": {"width": 900, "height": "variable"},
            "format": "HTML/CSS table with responsive design",
            "interactive": True,
            "alt_text": "Feature comparison table for top [entity] solutions",
            "schema_type": "Table"
        })
        for section in (outline or {}).get("h2_sections", [])[:5]:
            images.append({
                "image_id": f"IMG_{len(images)+1}",
                "image_type": "section_illustration",
                "title": f"Illustration for: {section.get('title', 'Section')[:50]}",
                "description": f"Supporting visual for {section.get('title', 'section')}",
                "dimensions": {"width": 800, "height": 400},
                "format": "WebP with alt text",
                "alt_text": f"Illustration explaining {section.get('title', 'section concept')}",
                "schema_type": "ImageObject",
                "lazy_load": True
            })
        return {
            "images": images,
            "total_images": len(images),
            "total_alt_texts": len(images),
            "schema_implementations": len(images),
            "responsive_breakpoints": ["mobile: 100%", "tablet: 80%", "desktop: 60%"],
            "optimization_checklist": [
                "Convert all images to WebP format",
                "Implement lazy loading for below-fold images",
                "Add descriptive alt text to every image",
                "Include ImageObject schema for each image",
                "Optimize file sizes (max 150KB for hero, 100KB for inline)",
                "Use responsive images with srcset attribute"
            ]
        }

    def _generate_video_specifications(self, text: str, outline: Dict = None) -> Dict[str, Any]:
        """Generate video content specifications."""
        videos = []
        videos.append({
            "video_id": "VID_1",
            "video_type": "explainer",
            "title": "[Entity] Explainer Video",
            "description": "60-second overview of what [entity] is and why it matters",
            "target_duration": "60-90 seconds",
            "script_outline": [
                "0-10s: Hook - 'What if you could [benefit]?'",
                "10-25s: Problem statement - current challenges",
                "25-50s: Solution overview - how [entity] works",
                "50-60s: Key benefit + CTA"
            ],
            "visual_requirements": [
                "Screen recordings of product/interface",
                "Animated data visualizations",
                "Text overlays for key statistics",
                "Brand-consistent color scheme"
            ],
            "placement": "Below H2 section, above fold preferred",
            "schema_type": "VideoObject",
            "thumbnail_required": True,
            "transcript_required": True,
            "caption_required": True
        })
        videos.append({
            "video_id": "VID_2",
            "video_type": "tutorial",
            "title": "[Entity] Implementation Tutorial",
            "description": "Step-by-step guide to implementing [entity]",
            "target_duration": "3-5 minutes",
            "script_outline": [
                "0-30s: Introduction and prerequisites",
                "30s-2min: Step-by-step walkthrough",
                "2min-4min: Common pitfalls and tips",
                "4min-5min: Results and next steps"
            ],
            "placement": "Within HowTo section",
            "schema_type": "VideoObject",
            "chapters_required": True,
            "transcript_required": True
        })
        return {
            "videos": videos,
            "total_videos": len(videos),
            "total_scripts": len(videos),
            "implementation_notes": [
                "Embed videos using <iframe> or <video> elements",
                "Include VideoObject schema with duration, thumbnail, and transcript",
                "Add chapter markers for videos over 2 minutes",
                "Provide text transcripts for accessibility",
                "Use lazy loading for video embeds"
            ]
        }

    def _generate_table_specifications(self, text: str) -> Dict[str, Any]:
        """Generate data table specifications."""
        tables = []
        tables.append({
            "table_id": "TABLE_1",
            "table_type": "comparison_matrix",
            "title": "Feature Comparison Table",
            "columns": ["Feature", "Solution A", "Solution B", "Solution C"],
            "rows_minimum": 8,
            "responsive_design": "Horizontal scroll on mobile",
            "highlight_best": True,
            "schema_type": "Table",
            "accessibility": "Proper th/td markup with scope attributes"
        })
        tables.append({
            "table_id": "TABLE_2",
            "table_type": "pricing_comparison",
            "title": "Pricing Tier Comparison",
            "columns": ["Plan", "Monthly Price", "Annual Price", "Features", "Best For"],
            "rows_minimum": 4,
            "responsive_design": "Card layout on mobile",
            "schema_type": "Table"
        })
        return {
            "tables": tables,
            "total_tables": len(tables),
            "responsive_strategy": "Stack cards on mobile, full table on desktop"
        }

    def _generate_infographic_specifications(self, text: str, data_points: List[Dict]) -> Dict[str, Any]:
        """Generate infographic specifications."""
        return {
            "infographics": [
                {
                    "infographic_id": "INFO_1",
                    "title": "Entity Overview Infographic",
                    "type": "statistical_summary",
                    "sections": ["Header", "Key Stats", "Benefits Grid", "Process Flow", "Sources"],
                    "data_points_used": len(data_points),
                    "dimensions": {"width": 800, "height": 1200},
                    "format": "SVG (scalable)"
                }
            ],
            "total_infographics": 1
        }

    def _generate_alt_text_pipeline(self, image_specs: Dict, schema_data: Dict = None) -> Dict[str, Any]:
        """Generate alt text for all visual assets."""
        alt_texts = []
        for img in image_specs.get("images", []):
            alt_texts.append({
                "image_id": img["image_id"],
                "alt_text": img.get("alt_text", ""),
                "schema_type": img.get("schema_type", "ImageObject"),
                "word_count": len(img.get("alt_text", "").split()),
                "includes_context": True,
                "accessibility_compliant": len(img.get("alt_text", "").split()) >= 5
            })
        return {
            "alt_texts": alt_texts,
            "total_alt_texts": len(alt_texts),
            "accessibility_compliance": "WCAG 2.1 AA",
            "best_practices": [
                "Keep alt text under 125 characters when possible",
                "Start with descriptive text, not 'Image of' or 'Picture of'",
                "Include relevant keywords naturally",
                "For charts, describe the key insight shown",
                "For decorative images, use empty alt attribute"
            ]
        }

    def _plan_asset_deployment(self, charts: Dict, calculators: Dict, images: Dict) -> Dict[str, Any]:
        """Plan asset deployment strategy."""
        total_assets = (
            charts.get("total_charts", 0) +
            calculators.get("total_calculators", 0) +
            len(images.get("images", []))
        )
        return {
            "total_assets": total_assets,
            "deployment_order": [
                "1. Hero image - publish with article",
                "2. Feature comparison table - add at comparison section",
                "3. Key statistics chart - embed in benefits section",
                "4. Calculator widgets - add after pricing section",
                "5. Supporting illustrations - add to remaining sections"
            ],
            "cdn_requirements": "All images served via CDN with WebP optimization",
            "lazy_loading": "Implement for all assets below initial viewport",
            "schema_requirements": "Add ImageObject schema for all images, SoftwareApplication for calculators"
        }

    def _prioritize_assets(self, charts: Dict, calculators: Dict, images: Dict) -> List[Dict[str, str]]:
        """Prioritize asset creation."""
        priorities = []
        for chart in charts.get("charts", [])[:3]:
            priorities.append({
                "asset": chart["title"],
                "type": "chart",
                "priority": "HIGH",
                "impact": "Increases dwell time and social sharing"
            })
        for calc in calculators.get("calculators", [])[:2]:
            priorities.append({
                "asset": calc["title"],
                "type": "calculator",
                "priority": "HIGH",
                "impact": "Generates interactive signals and repeat visits"
            })
        priorities.append({
            "asset": "Hero Image",
            "type": "image",
            "priority": "CRITICAL",
            "impact": "Required for social sharing and first impression"
        })
        return priorities[:8]
