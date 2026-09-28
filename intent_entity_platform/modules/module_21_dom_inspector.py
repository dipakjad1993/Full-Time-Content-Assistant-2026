"""
Module 21: Rendering & DOM Efficiency Inspector
Lints content layout and DOM complexity for performance.
"""
import re
from typing import List, Dict, Any
from ..utils.text_analytics import estimate_dom_complexity


class DOMInspector:
    """Module 21: Rendering & DOM Efficiency Inspector"""

    def __init__(self):
        self.module_id = "M21"
        self.module_name = "Rendering & DOM Efficiency Inspector"

    def analyze(self, html_content_or_inputs) -> Dict[str, Any]:
        """Full DOM efficiency analysis pipeline. Accepts html_content string or inputs dict with _url_data."""
        if isinstance(html_content_or_inputs, dict):
            inputs = html_content_or_inputs
            _url_data = inputs.get("_url_data", {})
            html_content = inputs.get("html_content", "")
        else:
            html_content = html_content_or_inputs
            _url_data = {}
            inputs = {}

        url = _url_data.get("url", "")
        url_title = _url_data.get("title", "")
        url_word_count = _url_data.get("word_count", 0)
        url_image_count = _url_data.get("image_count", 0)
        url_link_count = _url_data.get("link_count", 0)
        url_h1 = _url_data.get("h1", "")
        url_h2s = _url_data.get("h2s", [])
        url_images = _url_data.get("images", [])
        url_links = _url_data.get("links", [])
        url_has_schema = _url_data.get("has_schema", False)
        url_page_text = _url_data.get("page_text", "")

        url_dom_analysis = self._analyze_url_dom_structure(_url_data) if _url_data else {}

        if not html_content.strip() and not _url_data:
            return {
                "module": self.module_id,
                "module_name": self.module_name,
                "status": "SKIPPED",
                "message": "DOM inspection requires a target URL or HTML content. Run in URL Analysis mode (or provide page HTML) to enable this module.",
                "dom_analysis": {"status": "NO_URL_DATA", "message": "Provide a URL or HTML content for DOM inspection"},
                "optimization_recommendations": [
                    "Run this module in URL Analysis mode to inspect the live DOM structure of the page.",
                    "Use Google Lighthouse or PageSpeed Insights to measure DOM size, nesting depth, and CLS.",
                    "Keep total DOM elements under 1,500 and maximum nesting depth under 32 as general performance guidance."
                ],
                "recommendations": [
                    {"priority": "MEDIUM", "action": "Run DOM inspection on a target URL", "detail": "This module needs a URL or HTML input to analyze DOM complexity, resource weights, and interactive elements."}
                ],
                "implementation_steps": [
                    "Step 1: Provide a target URL or paste the page HTML into URL Analysis mode.",
                    "Step 2: Run the analysis to get total DOM element count and nesting depth metrics."
                ],
                "where_to_add": ["Run via URL Analysis mode to get URL-specific DOM metrics."]
            }

        dom_analysis = estimate_dom_complexity(html_content) if html_content.strip() else self._estimate_dom_from_url_data(_url_data)
        resource_analysis = self._analyze_resource_weights(html_content) if html_content.strip() else self._estimate_resources_from_url_data(_url_data)
        layout_analysis = self._analyze_layout_complexity(html_content) if html_content.strip() else {"tables": 0, "nested_tables": 0, "forms": 0, "iframes": 0, "layout_complexity_score": 0.0, "complexity_tier": "UNKNOWN"}
        interactive_elements = self._analyze_interactive_elements(html_content) if html_content.strip() else {"accordions": 0, "tabs": 0, "modals": 0, "sliders": 0, "calculators": 0, "total_interactive_elements": 0, "js_heavy_interactive": False, "main_thread_impact": "UNKNOWN"}
        performance_impact = self._assess_performance_impact(dom_analysis, resource_analysis)

        return {
            "module": self.module_id,
            "module_name": self.module_name,
            "url_analyzed": url,
            "url_dom_analysis": url_dom_analysis if _url_data else {
                "status": "NO_URL_DATA",
                "message": "Provide _url_data for URL-specific DOM analysis"
            },
            "dom_analysis": dom_analysis,
            "resource_analysis": resource_analysis,
            "layout_analysis": layout_analysis,
            "interactive_elements": interactive_elements,
            "performance_impact": performance_impact,
            "optimization_recommendations": self._generate_optimizations(dom_analysis, resource_analysis, interactive_elements),
            "implementation_steps": [
                "Step 1: Run the DOM analysis to get the total DOM element count and nesting depth metrics",
                "Step 2: Identify and remove any unused CSS classes, JavaScript functions, and HTML elements",
                "Step 3: Add explicit width and height attributes to ALL image tags to prevent CLS (Cumulative Layout Shift)",
                "Step 4: Implement lazy loading (loading='lazy') on images below the fold",
                "Step 5: Defer non-critical JavaScript using async or defer attributes on script tags",
                "Step 6: Reduce web fonts to a maximum of 2-3 weights using font-display: swap for render optimization",
                "Step 7: Flatten nested DOM elements - replace deep nesting with simpler CSS-based layouts",
                "Step 8: Replace tables used for layout with CSS Grid or Flexbox for better rendering performance",
                "Step 9: Remove or replace iframes with lightweight alternatives where possible",
                "Step 10: Convert interactive elements (accordions, tabs, modals) to CSS-only solutions where feasible",
                "Step 11: Inline critical CSS and defer non-critical stylesheets to reduce render-blocking resources",
                "Step 12: Test the optimized page using Google Lighthouse, PageSpeed Insights, and Web Vitals tools"
            ],
            "where_to_add": [
                "Place critical CSS inline in <head> via <style> tags to eliminate render-blocking requests",
                "Add lazy loading attributes directly on <img> tags for below-the-fold images",
                "Place deferred JavaScript before </body> with async or defer attributes",
                "Add explicit dimensions to <img> tags inline: <img width='800' height='600' ...>",
                "Use <link rel='preload'> in <head> for above-the-fold images and critical fonts",
                "Replace inline styles (<style> blocks) with external stylesheets loaded with media queries",
                "Place font-display: swap in @font-face declarations to prevent FOIT (Flash of Invisible Text)",
                "Add preconnect hints in <head> for third-party font and script domains",
                "Use <picture> element with WebP/AVIF sources in <head> or body for modern image formats",
                "Place structured data and non-critical meta tags after critical content to prioritize rendering"
            ],
            "detailed_analysis": {
                "dom_size_benchmarks": {
                    "optimal_dom_elements": "Under 1,500 elements for optimal performance",
                    "google_recommended_max": "Under 1,500 DOM nodes (Google Lighthouse best practice)",
                    "acceptable_range": "1,500-3,000 elements with manageable impact on rendering",
                    "critical_threshold": "Over 3,000 elements causes significant performance degradation",
                    "mobile_impact_multiplier": "DOM size impact is 2-3x worse on mobile devices vs. desktop",
                    "data_origin": "unverified_industry_heuristic - not measured for this page"
                },
                "core_web_vitals_benchmarks": {
                    "lcp_good_threshold": "Under 2.5 seconds for Largest Contentful Paint",
                    "fid_good_threshold": "Under 100ms for First Input Delay",
                    "cls_good_threshold": "Under 0.1 for Cumulative Layout Shift",
                    "inp_good_threshold": "Under 200ms for Interaction to Next Paint",
                    "ttfb_target": "Under 800ms for Time to First Byte"
                },
                "resource_weight_benchmarks": {
                    "total_page_weight_target": "Under 3MB for optimal mobile performance",
                    "javascript_budget": "Under 300KB compressed for critical scripts",
                    "css_budget": "Under 100KB for critical CSS (inline), 200KB total with deferred",
                    "image_optimization_target": "WebP/AVIF formats at 80% quality with responsive srcset",
                    "font_loading_target": "Under 100KB total for 2-3 font weights with font-display: swap",
                    "data_origin": "unverified_industry_heuristic - not measured for this page"
                },
                "expert_recommendations": [
                    "(General industry guidance, unverified): Profile DOM size with browser DevTools - a heuristic target is under 1,500 nodes for fast rendering",
                    "(General industry guidance, unverified): Use CSS containment (contain property) to isolate complex layout sections from reflow",
                    "(General industry guidance, unverified): Implement virtual scrolling for long lists instead of rendering all items in DOM",
                    "(General industry guidance, unverified): Use Intersection Observer API for lazy loading instead of scroll event listeners",
                    "(General industry guidance, unverified): Test on real mobile devices, not just Chrome DevTools throttling - real-world performance differs"
                ],
                "common_mistakes": [
                    "(General industry guidance, unverified): Using tables for layout instead of CSS Grid/Flexbox - tables create complex rendering trees",
                    "(General industry guidance, unverified): Loading all JavaScript upfront with no defer/async - blocks main thread and delays interactivity",
                    "(General industry guidance, unverified): Missing image dimensions causes CLS - high CLS is reported to hurt search rankings",
                    "(General industry guidance, unverified): Too many web fonts (5+) add render-blocking requests and can slow FCP significantly",
                    "(General industry guidance, unverified): Deeply nested DOM (>10 levels) increases paint complexity and memory usage"
                ],
                "success_metrics": [
                    "(General industry guidance, unverified): Track DOM element count and target under 1,500 (Lighthouse best-practice heuristic)",
                    "(General industry guidance, unverified): Measure LCP, FID, CLS, and INP via Chrome UX Report or PageSpeed Insights",
                    "(Guidance; the CLS threshold 0.1 is a real published Google Core Web Vitals value): Monitor CLS score - target under 0.1 for good Core Web Vitals rating",
                    "(General industry guidance, unverified): Track page weight in KB/MB and target under 3MB for mobile performance",
                    "(General industry guidance, unverified): Measure Time to Interactive (TTI) and target under 3.5 seconds on mobile 4G"
                ]
            },
            "data_source": "real_time_analysis"
        }

    def _analyze_url_dom_structure(self, url_data: Dict) -> Dict[str, Any]:
        """Analyze DOM structure and performance based on URL content data."""
        url = url_data.get("url", "")
        title = url_data.get("title", "")
        word_count = url_data.get("word_count", 0)
        image_count = url_data.get("image_count", 0)
        link_count = url_data.get("link_count", 0)
        h1 = url_data.get("h1", "")
        h2s = url_data.get("h2s", [])
        images = url_data.get("images", [])
        links = url_data.get("links", [])
        has_schema = url_data.get("has_schema", False)
        page_text = url_data.get("page_text", "")

        estimated_dom_elements = max(50, word_count // 3 + image_count * 8 + link_count * 5 + len(h2s) * 6 + 30)
        estimated_nesting_depth = min(15, 4 + (len(h2s) // 3) + (1 if image_count > 10 else 0))

        estimated_dom_size_score = min(1.0, estimated_dom_elements / 3000)
        estimated_nesting_score = min(1.0, estimated_nesting_depth / 15)

        images_without_alt = sum(1 for img in images if not img.get("alt", "").strip())
        images_with_lazy = 0

        estimated_total_resources = image_count + (1 if has_schema else 0) + max(1, word_count // 2000)
        estimated_resource_score = min(1.0, estimated_total_resources / 30)

        overall_impact = (estimated_dom_size_score * 0.4 + estimated_resource_score * 0.35 + estimated_nesting_score * 0.25)

        lcp_risk = "HIGH" if image_count > 10 else "MODERATE" if image_count > 5 else "LOW"
        fid_risk = "MODERATE" if word_count > 3000 else "LOW"
        cls_risk = "HIGH" if images_without_alt > 3 else "MODERATE" if image_count > 0 else "LOW"

        optimization_priorities = []
        if estimated_dom_elements > 1500:
            optimization_priorities.append({
                "priority": "HIGH",
                "issue": f"Estimated DOM size ({estimated_dom_elements} elements) exceeds 1500 threshold",
                "impact": "Significant rendering performance degradation",
                "fix": "Reduce DOM complexity by flattening nested elements"
            })
        if estimated_nesting_depth > 10:
            optimization_priorities.append({
                "priority": "MEDIUM",
                "issue": f"Estimated nesting depth ({estimated_nesting_depth} levels) exceeds recommended 10",
                "impact": "Increased paint complexity and memory usage",
                "fix": "Replace deep nesting with CSS Grid or Flexbox layouts"
            })
        if images_without_alt > 0:
            optimization_priorities.append({
                "priority": "HIGH",
                "issue": f"{images_without_alt} images missing alt text",
                "impact": "Accessibility violation and missed SEO opportunity",
                "fix": "Add descriptive alt text to all images"
            })
        if image_count > 5:
            optimization_priorities.append({
                "priority": "MEDIUM",
                "issue": f"{image_count} images on page - optimize for LCP",
                "impact": "Large image payload affects Largest Contentful Paint",
                "fix": "Implement lazy loading, use WebP/AVIF, add explicit dimensions"
            })
        if word_count > 3000:
            optimization_priorities.append({
                "priority": "MEDIUM",
                "issue": f"Long-form content ({word_count} words) may need virtual scrolling",
                "impact": "Large text nodes contribute to DOM size",
                "fix": "Consider collapsible sections or 'read more' for very long content"
            })

        estimated_page_weight_kb = max(50, word_count * 0.015 + image_count * 80 + len(page_text) * 0.001)
        estimated_load_time_ms = max(200, estimated_page_weight_kb * 0.8 + image_count * 200)

        return {
            "url": url,
            "page_title": title,
            "page_word_count": word_count,
            "estimated_dom_elements": estimated_dom_elements,
            "estimated_nesting_depth": estimated_nesting_depth,
            "estimated_dom_size_score": round(estimated_dom_size_score, 3),
            "estimated_nesting_score": round(estimated_nesting_score, 3),
            "dom_size_tier": (
                "OPTIMAL" if estimated_dom_elements < 1500 else
                "ACCEPTABLE" if estimated_dom_elements < 3000 else
                "CRITICAL"
            ),
            "image_count": image_count,
            "images_missing_alt": images_without_alt,
            "images_recommended_lazy_loading": image_count,
            "link_count": link_count,
            "h2_section_count": len(h2s),
            "has_structured_data": has_schema,
            "estimated_total_resources": estimated_total_resources,
            "estimated_resource_score": round(estimated_resource_score, 3),
            "overall_performance_impact_score": round(overall_impact, 3),
            "performance_impact_tier": (
                "CRITICAL" if overall_impact > 0.7 else
                "HIGH" if overall_impact > 0.5 else
                "MODERATE" if overall_impact > 0.3 else
                "LOW"
            ),
            "core_web_vitals_risk": {
                "LCP": lcp_risk,
                "FID": fid_risk,
                "CLS": cls_risk
            },
            "estimated_page_weight_kb": round(estimated_page_weight_kb, 1),
            "estimated_load_time_ms": round(estimated_load_time_ms, 0),
            "optimization_priorities": optimization_priorities,
            "optimization_priority_count": len(optimization_priorities),
            "dom_optimization_recommendations": [
                f"Target under 1,500 DOM elements (estimated: {estimated_dom_elements})",
                f"Add lazy loading to all {image_count} images below the fold",
                f"Add explicit width/height to all {image_count} images to prevent CLS",
                "Implement virtual scrolling for very long content sections",
                "Use CSS containment for complex layout sections",
                "Defer non-critical JavaScript to reduce main thread blocking"
            ]
        }

    def _estimate_dom_from_url_data(self, url_data: Dict) -> Dict[str, Any]:
        """Estimate DOM complexity from URL data when no HTML is available."""
        word_count = url_data.get("word_count", 0)
        image_count = url_data.get("image_count", 0)
        link_count = url_data.get("link_count", 0)
        h2s = url_data.get("h2s", [])
        estimated_elements = max(50, word_count // 3 + image_count * 8 + link_count * 5 + len(h2s) * 6 + 30)
        estimated_depth = min(15, 4 + (len(h2s) // 3))
        return {
            "total_dom_elements": estimated_elements,
            "max_nesting_depth": estimated_depth,
            "estimation_method": "calculated_from_url_data",
            "note": "Estimates based on URL content metrics - provide HTML for precise analysis"
        }

    def _estimate_resources_from_url_data(self, url_data: Dict) -> Dict[str, Any]:
        """Estimate resource weights from URL data when no HTML is available."""
        image_count = url_data.get("image_count", 0)
        word_count = url_data.get("word_count", 0)
        has_schema = url_data.get("has_schema", False)
        links = url_data.get("links", [])
        estimated_scripts = max(1, word_count // 2000) + (1 if has_schema else 0)
        external_links = len([l for l in links if l.startswith("http")])
        return {
            "total_images": image_count,
            "images_without_dimensions": 0,
            "images_with_lazy_loading": 0,
            "total_scripts": estimated_scripts,
            "inline_scripts": 0,
            "external_scripts": estimated_scripts,
            "total_stylesheets": 1,
            "web_fonts": 1,
            "inline_svgs": 0,
            "video_embeds": 0,
            "resource_summary": {
                "high_impact_resources": image_count + estimated_scripts,
                "optimization_potential": "HIGH" if image_count + estimated_scripts > 20 else "MODERATE" if image_count + estimated_scripts > 10 else "LOW"
            },
            "estimation_method": "calculated_from_url_data",
            "note": "Estimates based on URL content metrics - provide HTML for precise analysis"
        }

    def _analyze_resource_weights(self, html: str) -> Dict[str, Any]:
        """Analyze resource weights in HTML."""
        images = re.findall(r'<img[^>]*>', html, re.IGNORECASE)
        scripts = re.findall(r'<script[^>]*>', html, re.IGNORECASE)
        stylesheets = re.findall(r'<link[^>]*rel=["\']stylesheet["\']', html, re.IGNORECASE)
        inline_styles = re.findall(r'<style[^>]*>', html, re.IGNORECASE)
        fonts = re.findall(r'@font-face|fonts\.googleapis|typekit', html, re.IGNORECASE)
        svgs = re.findall(r'<svg[^>]*>', html, re.IGNORECASE)
        videos = re.findall(r'<video|<iframe[^>]*src=["\'](?:https?://)?(?:www\.)?(?:youtube|vimeo)', html, re.IGNORECASE)
        return {
            "total_images": len(images),
            "images_without_dimensions": sum(1 for img in images if 'width' not in img.lower() and 'height' not in img.lower()),
            "images_with_lazy_loading": sum(1 for img in images if 'loading="lazy"' in img.lower()),
            "total_scripts": len(scripts),
            "inline_scripts": sum(1 for s in scripts if 'src' not in s.lower()),
            "external_scripts": sum(1 for s in scripts if 'src' in s.lower()),
            "total_stylesheets": len(stylesheets) + len(inline_styles),
            "web_fonts": len(fonts),
            "inline_svgs": len(svgs),
            "video_embeds": len(videos),
            "resource_summary": {
                "high_impact_resources": len(images) + len(scripts) + len(fonts),
                "optimization_potential": "HIGH" if len(images) + len(scripts) > 20 else "MODERATE" if len(images) + len(scripts) > 10 else "LOW"
            }
        }

    def _analyze_layout_complexity(self, html: str) -> Dict[str, Any]:
        """Analyze layout complexity."""
        tables = re.findall(r'<table', html, re.IGNORECASE)
        nested_tables = len(re.findall(r'<table.*?<table', html, re.IGNORECASE | re.DOTALL))
        forms = re.findall(r'<form', html, re.IGNORECASE)
        iframes = re.findall(r'<iframe', html, re.IGNORECASE)
        return {
            "tables": len(tables),
            "nested_tables": nested_tables,
            "forms": len(forms),
            "iframes": len(iframes),
            "layout_complexity_score": min(1.0, (len(tables) * 0.1 + nested_tables * 0.2 + len(iframes) * 0.15)),
            "complexity_tier": (
                "HIGH" if len(tables) + nested_tables > 5 else
                "MODERATE" if len(tables) > 2 else
                "LOW"
            )
        }

    def _analyze_interactive_elements(self, html: str) -> Dict[str, Any]:
        """Analyze interactive elements and their JS requirements."""
        accordions = len(re.findall(r'(?:accordion|collapse|expandable)', html, re.IGNORECASE))
        tabs = len(re.findall(r'(?:tab-panel|tab-content|role="tab")', html, re.IGNORECASE))
        modals = len(re.findall(r'(?:modal|dialog|popup)', html, re.IGNORECASE))
        sliders = len(re.findall(r'(?:carousel|slider|swiper)', html, re.IGNORECASE))
        calculators = len(re.findall(r'(?:calculator|input.*output|form.*calculate)', html, re.IGNORECASE))
        total_interactive = accordions + tabs + modals + sliders + calculators
        return {
            "accordions": accordions,
            "tabs": tabs,
            "modals": modals,
            "sliders": sliders,
            "calculators": calculators,
            "total_interactive_elements": total_interactive,
            "js_heavy_interactive": total_interactive > 5,
            "main_thread_impact": (
                "HIGH" if total_interactive > 8 else
                "MODERATE" if total_interactive > 4 else
                "LOW"
            ),
            "recommendations": (
                ["Reduce interactive elements to < 5", "Use CSS-only solutions where possible", "Defer JS for non-critical interactions"]
                if total_interactive > 5 else
                ["Interactive elements within acceptable range"]
            )
        }

    def _assess_performance_impact(self, dom: Dict, resources: Dict) -> Dict[str, Any]:
        """Assess overall performance impact."""
        dom_size_score = min(1.0, dom.get("total_dom_elements", 0) / 3000)
        resource_score = min(1.0, resources.get("high_impact_resources", 0) / 30)
        nesting_score = min(1.0, dom.get("max_nesting_depth", 0) / 15)
        overall_impact = (dom_size_score * 0.4 + resource_score * 0.35 + nesting_score * 0.25)
        return {
            "performance_impact_score": round(overall_impact, 3),
            "impact_level": (
                "CRITICAL" if overall_impact > 0.7 else
                "HIGH" if overall_impact > 0.5 else
                "MODERATE" if overall_impact > 0.3 else
                "LOW"
            ),
            "component_scores": {
                "dom_size_impact": round(dom_size_score, 3),
                "resource_weight_impact": round(resource_score, 3),
                "nesting_depth_impact": round(nesting_score, 3)
            },
            "core_web_vitals_risk": {
                "LCP": "HIGH" if resources["total_images"] > 10 else "MODERATE" if resources["total_images"] > 5 else "LOW",
                "FID": "HIGH" if resources["total_scripts"] > 10 else "MODERATE" if resources["total_scripts"] > 5 else "LOW",
                "CLS": "HIGH" if resources["images_without_dimensions"] > 3 else "MODERATE" if resources["images_without_dimensions"] > 0 else "LOW"
            }
        }

    def _generate_optimizations(self, dom: Dict, resources: Dict, interactive: Dict) -> List[Dict[str, str]]:
        """Generate DOM optimization recommendations."""
        recs = []
        if dom.get("total_dom_elements", 0) > 1500:
            recs.append({
                "priority": "HIGH",
                "action": f"Reduce DOM size from {dom['total_dom_elements']} elements",
                "detail": "Target < 1500 DOM elements for optimal performance"
            })
        if dom.get("max_nesting_depth", 0) > 10:
            recs.append({
                "priority": "MEDIUM",
                "action": f"Flatten DOM nesting from depth {dom['max_nesting_depth']}",
                "detail": "Target < 10 levels of nesting"
            })
        if resources.get("images_without_dimensions", 0) > 0:
            recs.append({
                "priority": "HIGH",
                "action": f"Add width/height to {resources['images_without_dimensions']} images",
                "detail": "Missing image dimensions cause CLS (Cumulative Layout Shift)"
            })
        if resources.get("web_fonts", 0) > 3:
            recs.append({
                "priority": "MEDIUM",
                "action": f"Reduce web fonts from {resources['web_fonts']}",
                "detail": "Each web font adds render-blocking requests"
            })
        if interactive.get("js_heavy_interactive"):
            recs.append({
                "priority": "MEDIUM",
                "action": "Reduce interactive JavaScript elements",
                "detail": f"{interactive['total_interactive_elements']} interactive elements may impact INP"
            })
        return recs
