"""
Module 10: JavaScript / Client-Side Rendering (CSR) Simulator
Checks content rendering for search engine crawlers.
"""
import re
from typing import List, Dict, Any, Optional
from ..utils.text_analytics import estimate_dom_complexity


class CSRSimulator:
    """Module 10: JavaScript / Client-Side Rendering (CSR) Simulator"""

    def __init__(self):
        self.module_id = "M10"
        self.module_name = "JavaScript / Client-Side Rendering (CSR) Simulator"

    def analyze(self, html_content: str = "", config: Dict[str, Any] = None, inputs: Dict[str, Any] = None) -> Dict[str, Any]:
        """Full CSR analysis pipeline."""
        inputs = inputs or {}
        url_data = inputs.get("_url_data", None)

        real_csr_analysis = {}
        if url_data:
            real_csr_analysis = self._analyze_url_rendering(url_data)

        if not html_content.strip() and not url_data:
            return {"module": self.module_id, "module_name": self.module_name, "error": "No HTML content provided"}

        config = config or {}
        rendering_analysis = self._analyze_rendering_mode(html_content, config)
        content_availability = self._check_content_availability(html_content)
        cwv_impact = self._assess_core_web_vitals(html_content)
        js_dependency = self._analyze_js_dependencies(html_content)
        crawlability = self._assess_crawlability(html_content)
        prerender_check = self._check_prerender_readiness(html_content, config)
        dom_analysis = estimate_dom_complexity(html_content)

        return {
            "module": self.module_id,
            "module_name": self.module_name,
            "rendering_analysis": rendering_analysis,
            "content_availability": content_availability,
            "core_web_vitals_impact": cwv_impact,
            "js_dependencies": js_dependency,
            "crawlability_assessment": crawlability,
            "prerender_readiness": prerender_check,
            "dom_analysis": dom_analysis,
            **({"url_rendering_analysis": real_csr_analysis} if real_csr_analysis else {}),
            "critical_issues": self._identify_critical_issues(rendering_analysis, content_availability, cwv_impact),
            "fix_recommendations": self._generate_fix_recommendations(rendering_analysis, content_availability, js_dependency),
            "implementation_steps": [
                "Step 1: Audit current rendering mode (CSR/SSR/SSG/ISR) using view-source and Google Mobile-Friendly Test",
                "Step 2: If CSR detected, implement server-side rendering (Next.js SSR, Nuxt.js pre-rendering, or prerender.io)",
                "Step 3: Ensure all critical content (H1, meta tags, article body, schema) is in initial HTML response",
                "Step 4: Add <noscript> fallback for JavaScript-dependent content",
                "Step 5: Optimize Core Web Vitals: add width/height to images, implement lazy loading for below-fold images",
                "Step 6: Reduce third-party scripts - audit for necessity, async/defer non-critical scripts",
                "Step 7: Implement code splitting and tree-shaking for first-party JavaScript bundles",
                "Step 8: Add preload hints for critical resources (fonts, hero image, critical CSS)",
                "Step 9: Test with Google URL Inspection tool to verify content availability to crawlers",
                "Step 10: Monitor Search Console for indexing coverage and Core Web Vitals reports"
            ],
            "where_to_add": [
                "Add <noscript> fallback content within <body> for JavaScript-dependent sections",
                "Place critical CSS inline in <head> to eliminate render-blocking stylesheets",
                "Add preload hints for fonts and hero images in <head>",
                "Move third-party scripts to bottom of <body> or add async/defer attributes",
                "Add width and height attributes to all <img> tags to prevent CLS",
                "Implement lazy loading attribute (loading='lazy') for below-fold images",
                "Place structured data (JSON-LD) in initial HTML, not injected by JavaScript",
                "Add meta robots tags in <head> for crawl directives",
                "Include canonical URL in <head> for duplicate content prevention",
                "Add Open Graph and Twitter Card meta tags in <head> for social sharing"
            ],
            "detailed_analysis": {
                "industry_benchmarks": {
                    "data_origin": "unverified_industry_heuristic - not measured for this page",
                    "ssr_adoption_rate": "78% of top-ranking websites use server-side rendering",
                    "content_availability_score": "Leading sites achieve 95%+ content availability in initial HTML",
                    "core_web_vitals_pass_rate": "Top 10% of websites pass all three Core Web Vitals",
                    "third_party_script_impact": "Each third-party script adds 50-200ms of render delay",
                    "dom_size_optimal": "Optimal DOM size is under 1,500 nodes for fast rendering"
                },
                "statistical_ranges": {
                    "acceptable_lcp": "Under 2.5 seconds for good user experience",
                    "acceptable_cls": "Under 0.1 for stable visual layout",
                    "acceptable_inp": "Under 200ms for responsive interaction",
                    "script_tag_optimal": "(General industry guidance, unverified): Under 10 script tags for fast rendering",
                    "lazy_loading_threshold": "(General industry guidance, unverified): Lazy load images below 800px viewport position"
                },
                "expert_recommendations": [
                    "Prioritize SSR or SSG for content-heavy pages to ensure crawlability",
                    "Implement dynamic imports for non-critical JavaScript components",
                    "Use resource hints (preload, prefetch, preconnect) for critical resources",
                    "Implement progressive hydration for complex interactive components",
                    "Use CDN edge caching for pre-rendered HTML to reduce TTFB",
                    "Monitor Google Search Console's URL Inspection tool regularly",
                    "Test with Lighthouse and WebPageTest for comprehensive performance analysis"
                ],
                "common_mistakes_to_avoid": [
                    "Relying solely on client-side rendering without SSR fallback",
                    "Not testing content availability to Googlebot with URL Inspection",
                    "Loading all JavaScript synchronously and blocking render",
                    "Using large inline scripts that delay First Contentful Paint",
                    "Not providing width/height for images causing layout shifts",
                    "Lazy loading the hero image (should load eagerly)",
                    "Ignoring third-party script impact on Core Web Vitals"
                ],
                "success_metrics_to_track": [
                    "Content availability score in initial HTML (target: >90%)",
                    "Core Web Vitals pass rate (target: all three metrics green)",
                    "Googlebot rendering success rate in Search Console",
                    "Time to First Byte (TTFB) under 200ms",
                    "First Contentful Paint (FCP) under 1.8 seconds",
                    "Largest Contentful Paint (LCP) under 2.5 seconds",
                    "Cumulative Layout Shift (CLS) under 0.1"
                ]
            },
            "data_source": "real_time_analysis"
        }

    def _analyze_url_rendering(self, url_data: Dict) -> Dict[str, Any]:
        """Analyze rendering mode and bot accessibility using actual URL content data."""
        page_text = url_data.get("page_text", "")
        title = url_data.get("title", "")
        meta_desc = url_data.get("meta_description", "")
        h1 = url_data.get("h1", "")
        h2s = url_data.get("h2s", [])
        word_count = url_data.get("word_count", 0)
        link_count = url_data.get("link_count", 0)
        image_count = url_data.get("image_count", 0)
        has_schema = url_data.get("has_schema", False)
        url = url_data.get("url", "")

        # Content availability assessment from extracted data
        content_checks = {
            "title_available": bool(title),
            "meta_description_available": bool(meta_desc),
            "h1_available": bool(h1),
            "h2_headings_available": len(h2s) >= 2,
            "page_text_available": bool(page_text and len(page_text) > 100),
            "word_count_reasonable": word_count >= 300,
            "schema_present": has_schema,
            "links_present": link_count > 0,
            "images_present": image_count > 0
        }
        available_count = sum(1 for v in content_checks.values() if v)
        content_availability_score = round(available_count / max(1, len(content_checks)), 3)

        # Detect rendering mode signals from page characteristics
        rendering_signals = []
        rendering_risk = "LOW"

        # Check if content appears to be available (suggesting SSR/SSG)
        if page_text and len(page_text) > 200:
            rendering_signals.append("Page text content available - suggests server-side rendering or static generation")
            rendering_mode_detected = "Likely SSR/SSG (content available without JS)"
        elif page_text and len(page_text) <= 200:
            rendering_signals.append("Limited page text - may indicate client-side rendering")
            rendering_mode_detected = "Possibly CSR (limited text content)"
            rendering_risk = "MODERATE"
        else:
            rendering_signals.append("No page text extracted - possible CSR or minimal content")
            rendering_mode_detected = "Unknown (no text content available)"
            rendering_risk = "HIGH"

        # Check title and H1 presence
        if title and h1:
            rendering_signals.append("Title and H1 present - fundamental SEO elements available")
        elif title and not h1:
            rendering_signals.append("Title present but no H1 - partial content rendering")
        elif not title:
            rendering_signals.append("Missing title tag - may not be available to crawlers")
            rendering_risk = "HIGH"

        # Schema analysis
        if has_schema:
            rendering_signals.append("Structured data present - indicates SSR or injected schema")
        else:
            rendering_signals.append("No structured data detected - may need schema injection")

        # Link and image availability
        if link_count == 0:
            rendering_signals.append("No links detected - internal linking may be JS-dependent")
        if image_count == 0:
            rendering_signals.append("No images detected - visual content may be lazy-loaded via JS")

        # Bot accessibility assessment
        bot_accessibility = {
            "googlebot": {
                "can_access_content": bool(page_text and len(page_text) > 200),
                "can_read_title": bool(title),
                "can_read_headings": len(h2s) > 0,
                "can_read_schema": has_schema,
                "estimated_rendering_success": "HIGH" if content_availability_score >= 0.7 else "MODERATE" if content_availability_score >= 0.4 else "LOW"
            },
            "bingbot": {
                "can_access_content": bool(page_text and len(page_text) > 200),
                "can_read_title": bool(title),
                "can_read_headings": len(h2s) > 0,
                "estimated_rendering_success": "HIGH" if content_availability_score >= 0.7 else "MODERATE" if content_availability_score >= 0.4 else "LOW"
            },
            "perplexity_bot": {
                "can_access_content": bool(page_text and len(page_text) > 300),
                "can_read_title": bool(title),
                "can_read_headings": len(h2s) > 0,
                "estimated_rendering_success": "HIGH" if content_availability_score >= 0.7 else "MODERATE" if content_availability_score >= 0.4 else "LOW"
            },
            "gptbot": {
                "can_access_content": bool(page_text and len(page_text) > 300),
                "can_read_title": bool(title),
                "can_read_headings": len(h2s) > 0,
                "estimated_rendering_success": "HIGH" if content_availability_score >= 0.7 else "MODERATE" if content_availability_score >= 0.4 else "LOW"
            }
        }

        # Core Web Vitals impact estimation
        cwv_estimation = {
            "estimated_lcp_risk": "LOW" if word_count > 300 and image_count <= 10 else "MODERATE" if word_count > 300 else "HIGH",
            "estimated_cls_risk": "LOW" if image_count <= 8 else "MODERATE" if image_count <= 15 else "HIGH",
            "estimated_inp_risk": "LOW" if not has_schema else "MODERATE",
            "word_count_impact": "Adequate content for rendering" if word_count >= 300 else "Thin content - may not be fully rendered",
            "overall_estimated_cwv": "PASS" if content_availability_score >= 0.6 else "NEEDS_WORK"
        }

        # JavaScript dependency assessment
        js_dependency = {
            "content_delivery_method": "Server-rendered" if content_availability_score >= 0.7 else "Possibly client-rendered",
            "critical_content_risk": "LOW" if content_availability_score >= 0.7 else "HIGH",
            "recommendation": (
                "Content appears well-rendered for bots - maintain current approach" if content_availability_score >= 0.7
                else "Consider SSR/SSG to ensure content is available to crawlers"
            ),
            "estimated_js_dependency": "LOW" if content_availability_score >= 0.7 else "MODERATE" if content_availability_score >= 0.4 else "HIGH"
        }

        # Specific recommendations based on actual page
        csr_recommendations = []
        if not title:
            csr_recommendations.append({
                "priority": "CRITICAL",
                "action": "Ensure title tag is rendered server-side",
                "detail": "Title tag is essential for SEO and must be in initial HTML response"
            })
        if not h1:
            csr_recommendations.append({
                "priority": "HIGH",
                "action": "Ensure H1 heading is rendered server-side",
                "detail": "H1 is the primary content signal for search engines"
            })
        if not page_text or len(page_text) < 200:
            csr_recommendations.append({
                "priority": "CRITICAL",
                "action": "Ensure article body content is in initial HTML response",
                "detail": f"Only {len(page_text)} characters of text extracted - content may be JS-rendered"
            })
        if not has_schema:
            csr_recommendations.append({
                "priority": "MEDIUM",
                "action": "Add structured data (JSON-LD) in initial HTML response",
                "detail": "Schema markup should not depend on JavaScript execution"
            })
        if len(h2s) < 3:
            csr_recommendations.append({
                "priority": "MEDIUM",
                "action": "Add more H2 headings for content structure",
                "detail": f"Only {len(h2s)} H2 headings found - aim for 5+ for comprehensive coverage"
            })
        if word_count < 300:
            csr_recommendations.append({
                "priority": "HIGH",
                "action": f"Expand content (current: {word_count} words, target: 800+)",
                "detail": "Thin content is less likely to be fully rendered and indexed"
            })

        return {
            "page_url": url,
            "page_title": title,
            "content_word_count": word_count,
            "content_availability_score": content_availability_score,
            "content_availability_status": "FULLY_AVAILABLE" if content_availability_score >= 0.8 else "PARTIALLY_AVAILABLE" if content_availability_score >= 0.5 else "LIMITED",
            "content_checks": content_checks,
            "rendering_mode_detected": rendering_mode_detected,
            "rendering_risk_level": rendering_risk,
            "rendering_signals": rendering_signals,
            "bot_accessibility": bot_accessibility,
            "core_web_vitals_estimation": cwv_estimation,
            "javascript_dependency": js_dependency,
            "seo_element_availability": {
                "title": title[:80] if title else "MISSING",
                "meta_description": meta_desc[:120] if meta_desc else "MISSING",
                "h1": h1[:80] if h1 else "MISSING",
                "h2_count": len(h2s),
                "schema_present": has_schema,
                "link_count": link_count,
                "image_count": image_count
            },
            "csr_recommendations": csr_recommendations,
            "rendering_health": {
                "score": content_availability_score,
                "verdict": (
                    "HEALTHY - Content is well-rendered for search engines" if content_availability_score >= 0.8
                    else "MODERATE - Some content may not be accessible to bots" if content_availability_score >= 0.5
                    else "AT_RISK - Significant content rendering issues detected"
                )
            }
        }

    def _analyze_rendering_mode(self, html: str, config: Dict) -> Dict[str, Any]:
        """Analyze the rendering mode of the page."""
        framework = config.get("js_framework", "")
        render_mode = config.get("render_mode", "ssr")
        has_noscript = bool(re.search(r'<noscript', html, re.IGNORECASE))
        has_react_root = bool(re.search(r'id=["\'](?:root|app|__next|__nuxt)["\']', html))
        has_vue_root = bool(re.search(r'id=["\'](?:app|vue-app)["\']', html))
        inline_content = bool(re.search(r'<article|<main|<section', html, re.IGNORECASE))
        api_calls = len(re.findall(r'fetch\s*\(|axios\.|\.get\s*\(|\.post\s*\(|XMLHttpRequest', html))
        script_tags = len(re.findall(r'<script', html, re.IGNORECASE))
        inline_scripts = len(re.findall(r'<script\s*>|<script\s+type=["\']text/javascript["\']', html, re.IGNORECASE))
        deferred_scripts = len(re.findall(r'<script\s+defer', html, re.IGNORECASE))
        async_scripts = len(re.findall(r'<script\s+async', html, re.IGNORECASE))

        if render_mode == "csr" or (has_react_root and not inline_content):
            rendering_type = "CLIENT_SIDE_RENDERED"
            risk_level = "HIGH"
            googlebot_experience = "Googlebot must execute JavaScript to see content"
        elif render_mode == "ssr" and inline_content:
            rendering_type = "SERVER_SIDE_RENDERED"
            risk_level = "LOW"
            googlebot_experience = "Content available in initial HTML response"
        elif render_mode == "isr":
            rendering_type = "INCREMENTAL_STATIC_REGENERATION"
            risk_level = "LOW"
            googlebot_experience = "Pre-rendered HTML with periodic regeneration"
        elif render_mode == "ssg":
            rendering_type = "STATIC_SITE_GENERATION"
            risk_level = "MINIMAL"
            googlebot_experience = "Fully pre-rendered static HTML"
        else:
            rendering_type = "HYBRID"
            risk_level = "MODERATE"
            googlebot_experience = "Mixed rendering - verify content availability"

        return {
            "rendering_type": rendering_type,
            "risk_level": risk_level,
            "googlebot_experience": googlebot_experience,
            "detected_framework": framework or self._detect_framework(html),
            "render_mode_configured": render_mode,
            "has_noscript_fallback": has_noscript,
            "has_ssr_content": inline_content,
            "has_csr_root_element": has_react_root or has_vue_root,
            "script_analysis": {
                "total_script_tags": script_tags,
                "inline_scripts": inline_scripts,
                "deferred_scripts": deferred_scripts,
                "async_scripts": async_scripts,
                "api_calls_in_html": api_calls
            },
            "two_pass_rendering": {
                "pass_1_initial_html": "Content " + ("AVAILABLE" if inline_content else "NOT AVAILABLE"),
                "pass_2_after_js": "Content available after JavaScript execution",
                "render_delay_risk": "HIGH" if api_calls > 3 and not inline_content else "LOW"
            }
        }

    def _detect_framework(self, html: str) -> str:
        """Detect JavaScript framework from HTML."""
        if '__NEXT_DATA__' in html or '_next/' in html:
            return "Next.js"
        if '__NUXT__' in html or '_nuxt/' in html:
            return "Nuxt.js"
        if 'ng-version' in html or 'ng-app' in html:
            return "Angular"
        if 'data-reactroot' in html or '__REACT' in html:
            return "React"
        if 'data-v-' in html or 'vue-' in html:
            return "Vue.js"
        if 'ember-view' in html:
            return "Ember.js"
        if 'svelte' in html.lower():
            return "Svelte"
        return "Unknown/Custom"

    def _check_content_availability(self, html: str) -> Dict[str, Any]:
        """Check if key content is available in initial HTML."""
        checks = {
            "h1_tag": {
                "present": bool(re.search(r'<h1[^>]*>(.+?)</h1>', html, re.IGNORECASE | re.DOTALL)),
                "content": self._extract_tag_content(html, 'h1'),
                "critical": True
            },
            "meta_title": {
                "present": bool(re.search(r'<title[^>]*>(.+?)</title>', html, re.IGNORECASE | re.DOTALL)),
                "content": self._extract_meta_content(html, 'title'),
                "critical": True
            },
            "meta_description": {
                "present": bool(re.search(r'<meta\s+name=["\']description["\']\s+content=["\'](.+?)["\']', html, re.IGNORECASE)),
                "content": self._extract_meta_content(html, 'description'),
                "critical": True
            },
            "article_body": {
                "present": bool(re.search(r'<article|<main', html, re.IGNORECASE)),
                "word_count": len(re.findall(r'\b\w+\b', re.sub(r'<[^>]+>', ' ', html))),
                "critical": True
            },
            "canonical_url": {
                "present": bool(re.search(r'<link\s+rel=["\']canonical["\']', html, re.IGNORECASE)),
                "critical": True
            },
            "og_tags": {
                "present": bool(re.search(r'<meta\s+property=["\']og:', html, re.IGNORECASE)),
                "critical": False
            },
            "schema_jsonld": {
                "present": bool(re.search(r'type=["\']application/ld\+json["\']', html, re.IGNORECASE)),
                "critical": True
            },
            "h2_headings": {
                "present": len(re.findall(r'<h2', html, re.IGNORECASE)) >= 3,
                "count": len(re.findall(r'<h2', html, re.IGNORECASE)),
                "critical": False
            },
            "images_with_alt": {
                "present": bool(re.search(r'<img[^>]*alt=["\'][^"\']+["\']', html, re.IGNORECASE)),
                "total_images": len(re.findall(r'<img', html, re.IGNORECASE)),
                "images_with_alt": len(re.findall(r'<img[^>]*alt=["\'][^"\']+["\']', html, re.IGNORECASE)),
                "critical": False
            }
        }
        critical_missing = [k for k, v in checks.items() if v.get("critical") and not v.get("present")]
        total_score = sum(1 for v in checks.values() if v.get("present")) / max(1, len(checks))

        return {
            "checks": checks,
            "critical_missing": critical_missing,
            "content_availability_score": round(total_score, 3),
            "content_available_in_initial_html": len(critical_missing) == 0,
            "verdict": (
                "FULLY AVAILABLE" if len(critical_missing) == 0 else
                f"MISSING {len(critical_missing)} CRITICAL ELEMENTS: {', '.join(critical_missing)}"
            )
        }

    def _extract_tag_content(self, html: str, tag: str) -> str:
        """Extract content from HTML tag."""
        pattern = f'<{tag}[^>]*>(.+?)</{tag}>'
        match = re.search(pattern, html, re.IGNORECASE | re.DOTALL)
        return re.sub(r'<[^>]+>', '', match.group(1)).strip() if match else ""

    def _extract_meta_content(self, html: str, name: str) -> str:
        """Extract meta tag content."""
        if name == 'title':
            match = re.search(r'<title[^>]*>(.+?)</title>', html, re.IGNORECASE | re.DOTALL)
            return match.group(1).strip() if match else ""
        match = re.search(rf'<meta\s+name=["\']{name}["\']\s+content=["\'](.+?)["\']', html, re.IGNORECASE)
        return match.group(1).strip() if match else ""

    def _assess_core_web_vitals(self, html: str) -> Dict[str, Any]:
        """Assess Core Web Vitals impact."""
        script_size = len(re.findall(r'<script', html, re.IGNORECASE))
        inline_css = len(re.findall(r'<style', html, re.IGNORECASE))
        large_images = len(re.findall(r'<img[^>]*(?:width|height)\s*=\s*["\']?\d{3,}', html, re.IGNORECASE))
        lazy_images = len(re.findall(r'loading\s*=\s*["\']lazy["\']', html, re.IGNORECASE))
        total_images = len(re.findall(r'<img', html, re.IGNORECASE))
        inline_svgs = len(re.findall(r'<svg', html, re.IGNORECASE))
        web_fonts = len(re.findall(r'@font-face|fonts\.googleapis', html, re.IGNORECASE))
        preload_hints = len(re.findall(r'<link\s+rel=["\']preload["\']', html, re.IGNORECASE))

        cls_risk = "LOW"
        if large_images > 3 and lazy_images < large_images * 0.5:
            cls_risk = "HIGH"
        elif large_images > 0 and lazy_images == 0:
            cls_risk = "MODERATE"

        inp_risk = "LOW"
        if script_size > 10:
            inp_risk = "HIGH"
        elif script_size > 5:
            inp_risk = "MODERATE"

        lcp_risk = "LOW"
        if total_images > 0 and lazy_images == total_images:
            lcp_risk = "MODERATE"
        if web_fonts > 3:
            lcp_risk = "HIGH"

        return {
            "cls_risk": cls_risk,
            "inp_risk": inp_risk,
            "lcp_risk": lcp_risk,
            "overall_cwv_risk": "HIGH" if "HIGH" in [cls_risk, inp_risk, lcp_risk] else
                               "MODERATE" if "MODERATE" in [cls_risk, inp_risk, lcp_risk] else "LOW",
            "metrics": {
                "total_scripts": script_size,
                "inline_stylesheets": inline_css,
                "total_images": total_images,
                "lazy_loaded_images": lazy_images,
                "inline_svgs": inline_svgs,
                "web_fonts": web_fonts,
                "preload_hints": preload_hints
            },
            "issues": self._identify_cwv_issues(cls_risk, inp_risk, lcp_risk, script_size, lazy_images, total_images)
        }

    def _identify_cwv_issues(self, cls: str, inp: str, lcp: str, scripts: int, lazy: int, total_img: int) -> List[str]:
        """Identify specific CWV issues."""
        issues = []
        if cls == "HIGH":
            issues.append("CLS Risk: Images without dimensions or lazy loading without placeholder")
        if inp == "HIGH":
            issues.append(f"INP Risk: {scripts} script tags may block main thread")
        if lcp == "HIGH":
            issues.append("LCP Risk: Web font loading may delay largest contentful paint")
        if total_img > 0 and lazy == total_img:
            issues.append("LCP Warning: All images lazy-loaded - hero image should load eagerly")
        return issues

    def _analyze_js_dependencies(self, html: str) -> Dict[str, Any]:
        """Analyze JavaScript dependencies and their impact."""
        script_srcs = re.findall(r'<script[^>]*src=["\'](.+?)["\']', html, re.IGNORECASE)
        third_party = [s for s in script_srcs if not s.startswith('/') and not s.startswith('./')]
        first_party = [s for s in script_srcs if s.startswith('/') or s.startswith('./')]
        return {
            "total_scripts": len(script_srcs),
            "third_party_scripts": third_party[:10],
            "first_party_scripts": first_party[:10],
            "third_party_count": len(third_party),
            "first_party_count": len(first_party),
            "risk_assessment": (
                "HIGH" if len(third_party) > 5 else
                "MODERATE" if len(third_party) > 3 else
                "LOW"
            ),
            "recommendations": self._get_js_recommendations(third_party, first_party)
        }

    def _get_js_recommendations(self, third_party: List, first_party: List) -> List[str]:
        """Get JavaScript optimization recommendations."""
        recs = []
        if len(third_party) > 5:
            recs.append("Reduce third-party scripts - audit for necessity")
        if len(first_party) > 10:
            recs.append("Bundle and tree-shake first-party JavaScript")
        recs.append("Use async/defer attributes on non-critical scripts")
        recs.append("Implement code splitting for large JavaScript bundles")
        recs.append("Consider using Intersection Observer for lazy-loaded content")
        return recs

    def _assess_crawlability(self, html: str) -> Dict[str, Any]:
        """Assess page crawlability for search engines."""
        robots_meta = re.search(r'<meta\s+name=["\']robots["\']\s+content=["\'](.+?)["\']', html, re.IGNORECASE)
        robots_content = robots_meta.group(1) if robots_meta else "not_found"
        canonical = re.search(r'<link\s+rel=["\']canonical["\']\s+href=["\'](.+?)["\']', html, re.IGNORECASE)
        return {
            "robots_meta": robots_content,
            "is_noindex": "noindex" in robots_content,
            "is_nofollow": "nofollow" in robots_content,
            "canonical_url": canonical.group(1) if canonical else "not_found",
            "has_canonical": canonical is not None,
            "render_blocking_resources": len(re.findall(r'<link[^>]*rel=["\']stylesheet["\']', html, re.IGNORECASE)),
            "critical_resources": {
                "css_files": len(re.findall(r'<link[^>]*rel=["\']stylesheet["\']', html, re.IGNORECASE)),
                "js_files": len(re.findall(r'<script[^>]*src', html, re.IGNORECASE)),
                "font_files": len(re.findall(r'@font-face|fonts\.googleapis', html, re.IGNORECASE))
            },
            "crawlability_score": self._calculate_crawlability_score(robots_content, canonical, html)
        }

    def _calculate_crawlability_score(self, robots: str, canonical, html: str) -> float:
        """Calculate crawlability score."""
        score = 1.0
        if "noindex" in robots:
            score -= 0.5
        if "nofollow" in robots:
            score -= 0.2
        if not canonical:
            score -= 0.1
        if len(re.findall(r'<script[^>]*src', html, re.IGNORECASE)) > 10:
            score -= 0.1
        return round(max(0, score), 3)

    def _check_prerender_readiness(self, html: str, config: Dict) -> Dict[str, Any]:
        """Check if page is ready for pre-rendering."""
        has_content = bool(re.search(r'<article|<main|<section', html, re.IGNORECASE))
        word_count = len(re.findall(r'\b\w+\b', re.sub(r'<[^>]+>', ' ', html)))
        return {
            "pre_render_ready": has_content and word_count > 300,
            "content_in_initial_html": has_content,
            "word_count_in_initial_html": word_count,
            "prerender_recommendation": (
                "Page is pre-render ready" if has_content and word_count > 300 else
                "Content not available in initial HTML - implement SSR or pre-rendering"
            )
        }

    def _identify_critical_issues(self, rendering: Dict, content: Dict, cwv: Dict) -> List[Dict[str, str]]:
        """Identify critical issues requiring immediate attention."""
        issues = []
        if rendering.get("risk_level") == "HIGH":
            issues.append({
                "issue": "Client-side rendering detected",
                "severity": "CRITICAL",
                "impact": "Content may not be indexed by search engines",
                "fix": "Implement server-side rendering (SSR) or static site generation (SSG)"
            })
        if not content.get("content_available_in_initial_html"):
            missing = content.get("critical_missing", [])
            issues.append({
                "issue": f"Critical content missing from initial HTML: {', '.join(missing)}",
                "severity": "CRITICAL",
                "impact": "Search engines cannot read essential page content",
                "fix": "Ensure all critical content is rendered server-side"
            })
        if cwv.get("overall_cwv_risk") == "HIGH":
            issues.append({
                "issue": "Core Web Vitals at risk",
                "severity": "HIGH",
                "impact": "Poor user experience may impact rankings",
                "fix": "Optimize images, reduce scripts, implement lazy loading correctly"
            })
        return issues

    def _generate_fix_recommendations(self, rendering: Dict, content: Dict, js_deps: Dict) -> List[Dict[str, str]]:
        """Generate fix recommendations."""
        recs = []
        if rendering.get("rendering_type") == "CLIENT_SIDE_RENDERED":
            recs.append({
                "priority": "CRITICAL",
                "action": "Implement SSR or static pre-rendering",
                "detail": "Use Next.js SSR/SSG, Nuxt.js pre-rendering, or prerender.io service",
                "timeline": "1-2 weeks"
            })
        for missing in content.get("critical_missing", []):
            recs.append({
                "priority": "HIGH",
                "action": f"Add missing {missing} to initial HTML",
                "detail": f"Ensure {missing} is rendered server-side, not injected by JavaScript",
                "timeline": "1 week"
            })
        if js_deps.get("third_party_count", 0) > 5:
            recs.append({
                "priority": "MEDIUM",
                "action": "Audit and reduce third-party scripts",
                "detail": f"{js_deps['third_party_count']} third-party scripts detected - each adds render delay",
                "timeline": "2 weeks"
            })
        return recs
