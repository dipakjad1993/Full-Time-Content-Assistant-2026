"""
Module 16: Edge Routing & CDN Injection Previewer
Previews edge-injected schema, headers, and pre-rendered HTML.
"""
from typing import List, Dict, Any
from ..utils.text_analytics import generate_edge_worker_snippet
from ..utils.web_data import fetch_headers


class CDNEdgePreviewer:
    """Module 16: Edge Routing & CDN Injection Previewer"""

    def __init__(self):
        self.module_id = "M16"
        self.module_name = "Edge Routing & CDN Injection Previewer"

    def analyze(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Full CDN edge preview pipeline."""
        cdn_provider = inputs.get("cdn_provider", "cloudflare")
        schema_data = inputs.get("schema_data", {})
        meta_tags = inputs.get("meta_tags", {})
        headers = inputs.get("headers", {})
        render_mode = inputs.get("render_mode", "ssr")

        _url_data = inputs.get("_url_data", {})
        url = _url_data.get("url", inputs.get("url", ""))
        title = _url_data.get("title", "")
        page_text = _url_data.get("page_text", "")
        word_count = _url_data.get("word_count", 0)
        has_schema = _url_data.get("has_schema", False)
        image_count = _url_data.get("image_count", 0)
        link_count = _url_data.get("link_count", 0)
        h1 = _url_data.get("h1", "")
        h2s = _url_data.get("h2s", [])

        url_cdn_analysis = self._analyze_url_cdn_optimization(_url_data) if _url_data else {}

        server_headers = self._inspect_server_headers(inputs, url)
        detected_tech = server_headers.get("detected_server_technology", {})
        detected_cdn = detected_tech.get("cdn_provider")
        if detected_cdn and "NOT_DETECTED" not in detected_cdn:
            cdn_provider = detected_cdn.lower().replace(" ", "_").replace("-", "_")
        elif detected_cdn and "NOT_DETECTED" in detected_cdn:
            configured = inputs.get("cdn_provider")
            cdn_provider = configured if configured else "not_detected"

        edge_worker = self._generate_edge_worker(cdn_provider, schema_data, meta_tags, headers)
        prerender_simulation = self._simulate_prerender(inputs, render_mode)
        cdn_config = self._generate_cdn_config(cdn_provider, inputs)
        deployment_guide = self._create_deployment_guide(cdn_provider, edge_worker)

        return {
            "module": self.module_id,
            "module_name": self.module_name,
            "cdn_provider": cdn_provider,
            "url_analyzed": url,
            "analysis_timestamp": "2026-08-01",
            "url_cdn_optimization_analysis": url_cdn_analysis if _url_data else {
                "status": "NO_URL_DATA",
                "message": "Provide _url_data for URL-specific CDN analysis"
            },
            "edge_worker_snippet": edge_worker,
            "server_header_inspection": server_headers,
            "prerender_simulation": prerender_simulation,
            "cdn_configuration": cdn_config,
            "deployment_guide": deployment_guide,
            "recommendations": self._generate_recommendations(cdn_provider, edge_worker, server_headers),
            "performance_optimization": {
                "data_origin": "unverified_industry_heuristic - not measured for this page",
                "estimated_ttfb_improvement": "40-60ms reduction with edge caching",
                "cache_hit_ratio_target": "95%+ for static content, 80%+ for dynamic",
                "bandwidth_savings": "30-50% reduction in origin requests",
                "global_latency": "< 50ms TTFB for 95% of global users",
                "edge_compute_limits": {
                    "cloudflare_workers": "10ms CPU time (free), 30s (paid)",
                    "fastly_compute": "50ms per request",
                    "cloudfront_functions": "2ms execution time",
                    "akamai_edge_workers": "4096ms per request"
                }
            },
            "security_headers_audit": {
                "strict_transport_security": {"status": "RECOMMENDED", "value": "max-age=31536000; includeSubDomains; preload"},
                "content_security_policy": {"status": "RECOMMENDED", "value": "default-src 'self'; script-src 'self' 'unsafe-inline'"},
                "x_content_type_options": {"status": "RECOMMENDED", "value": "nosniff"},
                "referrer_policy": {"status": "RECOMMENDED", "value": "strict-origin-when-cross-origin"},
                "permissions_policy": {"status": "RECOMMENDED", "value": "geolocation=(), microphone=(), camera=()"},
                "overall_security_score": "85/100 - Good, implement remaining headers",
                "overall_security_score_origin": "unverified_industry_heuristic - not measured for this page"
            },
            "edge_computing_strategies": {
                "a_b_testing": "Route traffic through edge workers for variant serving",
                "personalization": "Use edge logic for geo-based content customization",
                "bot_detection": "Implement edge-level bot detection before origin",
                "rate_limiting": "Apply rate limits at edge to protect origin",
                "image_optimization": "Serve WebP/AVIF via edge image transformation",
                "edge_side_includes": "Use ESI for personalized page fragments"
            },
            "monitoring_and_observability": {
                "data_origin": "unverified_industry_heuristic - not measured for this page",
                "key_metrics": [
                    "Cache Hit Ratio (target: >90%)",
                    "TTFB by region (target: <100ms)",
                    "Error rate (target: <0.1%)",
                    "Worker execution time (target: <5ms)",
                    "Bandwidth per region"
                ],
                "alerting_rules": [
                    "Cache hit ratio drops below 80%",
                    "TTFB exceeds 200ms for any region",
                    "Error rate exceeds 1%",
                    "Origin requests increase by >50%"
                ],
                "log_aggregation": "Centralize CDN logs with origin logs for correlation",
                "real_user_monitoring": "Implement RUM for actual user experience data"
            },
            "implementation_steps": [
                "Step 1: Choose your CDN provider and create an account if not already set up (Cloudflare, Fastly, Akamai, or CloudFront)",
                "Step 2: Copy the generated edge worker snippet and create a new Worker/Edge Function in your CDN dashboard",
                "Step 3: Configure the route pattern to match your target content URLs (e.g., your-domain.com/blog/*)",
                "Step 4: Set environment variables for schema TTL and cache behavior in the Worker settings",
                "Step 5: Deploy the Worker to a staging or preview environment first for validation",
                "Step 6: Use curl with a Googlebot User-Agent to verify schema injection appears in the page source",
                "Step 7: Test the injected schema with Google Rich Results Test and Schema.org validator",
                "Step 8: Add or correct all required HTTP response headers (Cache-Control, X-Robots-Tag, etc.) via CDN settings",
                "Step 9: Configure separate cache policies for search bots vs. regular users (bot-aware caching)",
                "Step 10: Deploy to production and verify with live URL inspection in GSC",
                "Step 11: Set up monitoring dashboards for cache hit ratio, TTFB, and worker execution time",
                "Step 12: Configure alerting rules for cache misses, high latency, and error rate spikes"
            ],
            "where_to_add": [
                "Deploy edge Worker at the CDN layer to intercept requests before they reach origin",
                "Add or modify HTTP headers in the CDN's Worker response or VCL rules (not origin)",
                "Place schema JSON-LD injection logic in the Worker's response body transformation step",
                "Configure cache rules in CDN dashboard under Cache/Edge Cache settings",
                "Add security headers (HSTS, CSP, etc.) in CDN response headers or Worker output",
                "Set X-Robots-Tag headers in the CDN Worker to control bot behavior without origin changes",
                "Place pre-rendered HTML patches in CDN edge storage (KV/R2/Edge Storage) for bot serving",
                "Configure rate limiting rules in CDN firewall/WAF settings to protect origin",
                "Add monitoring hooks in Worker event handlers (request/response lifecycle)",
                "Set up CDN analytics dashboard for real-time observability of edge performance"
            ],
            "detailed_analysis": {
                "performance_benchmarks": {
                    "data_origin": "unverified_industry_heuristic - not measured for this page",
                    "edge_caching_ttfb_improvement": "40-60ms reduction in Time to First Byte vs. origin-only serving",
                    "cache_hit_ratio_target": "95%+ for static content, 80%+ for semi-dynamic content",
                    "bandwidth_savings": "30-50% reduction in origin server requests with proper caching",
                    "global_latency_with_cdn": "P95 TTFB under 100ms for 95% of global users",
                    "worker_cold_start_overhead": "Cloudflare Workers: <1ms; Fastly Compute: 2-5ms; CloudFront Functions: <1ms"
                },
                "cdn_provider_comparison": {
                    "cloudflare": "Best for edge compute (Workers), free tier available, 300+ PoPs, built-in WAF",
                    "fastly": "Best for real-time cache invalidation, VCL flexibility, Compute@Edge for complex logic",
                    "cloudfront": "Best for AWS-native stacks, Lambda@Edge for complex transforms, 225+ PoPs",
                    "akamai": "Best for enterprise scale, EdgeWorkers for custom logic, 4000+ PoPs globally"
                },
                "security_headers_benchmarks": {
                    "hsts": "max-age=31536000 (1 year) with includeSubDomains and preload",
                    "csp": "Restrict script-src and style-src to self; use nonces for inline scripts",
                    "x_content_type_options": "nosniff prevents MIME-type sniffing attacks",
                    "referrer_policy": "strict-origin-when-cross-origin balances privacy and analytics",
                    "permissions_policy": "Disable unused browser APIs (camera, microphone, geolocation)"
                },
                "expert_recommendations": [
                    "Always deploy Workers to staging first - edge compute errors can cause site-wide outages",
                    "Use stale-while-revalidate caching to serve cached content while refreshing in background",
                    "Implement bot-aware caching: serve pre-rendered HTML to search bots, dynamic to users",
                    "Set cache invalidation webhooks on content publish events for near-real-time updates",
                    "Monitor Worker execution time limits per provider to avoid silent failures on complex logic"
                ],
                "common_mistakes": [
                    "Forgetting to test edge-injected schema with Google Rich Results Test before production deploy",
                    "Setting overly aggressive cache TTLs that prevent search bots from seeing updated content",
                    "Not configuring separate cache policies for bot vs. user traffic (serving JS-rendered shells to bots)",
                    "Deploying Workers without error handling - uncaught exceptions return 500 to all visitors",
                    "Ignoring CDN billing - edge compute and bandwidth costs can spike with high-traffic sites"
                ],
                "success_metrics": [
                    "(General industry guidance, unverified): Track TTFB improvement by region (target: <100ms for 95th percentile globally)",
                    "(General industry guidance, unverified): Monitor cache hit ratio weekly (target: >90% for content pages)",
                    "(General industry guidance, unverified): Measure origin request reduction (target: 30-50% fewer origin hits)",
                    "Verify schema injection with Google Rich Results Test weekly",
                    "Track Worker execution time and error rate via CDN analytics dashboard"
                ]
            }
        }

    def _analyze_url_cdn_optimization(self, url_data: Dict) -> Dict[str, Any]:
        """Analyze actual URL content for CDN optimization opportunities."""
        url = url_data.get("url", "")
        title = url_data.get("title", "")
        page_text = url_data.get("page_text", "")
        word_count = url_data.get("word_count", 0)
        has_schema = url_data.get("has_schema", False)
        image_count = url_data.get("image_count", 0)
        link_count = url_data.get("link_count", 0)
        h1 = url_data.get("h1", "")
        h2s = url_data.get("h2s", [])
        images = url_data.get("images", [])

        estimated_page_size_kb = max(10, word_count * 0.015 + image_count * 50 + len(page_text) * 0.001)
        estimated_ttfb_ms = 200 if estimated_page_size_kb > 500 else 150 if estimated_page_size_kb > 200 else 100

        cache_headers = []
        if word_count > 500:
            cache_headers.append({
                "header": "Cache-Control",
                "recommended_value": "public, max-age=3600, stale-while-revalidate=86400",
                "reason": f"Content page with {word_count} words - cache for 1 hour with stale-while-revalidate"
            })
        if image_count > 0:
            cache_headers.append({
                "header": "Cache-Control",
                "recommended_value": "public, max-age=604800, immutable",
                "reason": f"{image_count} images detected - cache static assets for 7 days"
            })

        edge_injection_opportunities = []
        if not has_schema:
            edge_injection_opportunities.append({
                "opportunity": "Schema Injection via Edge Worker",
                "detail": "Page has no structured data - inject Article/BlogPosting JSON-LD at edge",
                "estimated_impact": "(General industry guidance, unverified): 10-30% CTR improvement from rich results eligibility",
                "implementation": "Cloudflare Worker or Fastly VCL to inject schema before response"
            })
        if len(h2s) > 0:
            edge_injection_opportunities.append({
                "opportunity": "Dynamic Meta Description Enhancement",
                "detail": f"Page has {len(h2s)} H2 sections - generate meta description from first H2",
                "estimated_impact": "(General industry guidance, unverified): 5-15% CTR improvement from optimized meta descriptions",
                "implementation": "Edge worker extracts H1 and first H2 to generate meta description"
            })
        if word_count > 1000:
            edge_injection_opportunities.append({
                "opportunity": "Table of Contents Injection",
                "detail": f"Long-form content ({word_count} words) with {len(h2s)} sections - inject TOC at edge",
                "estimated_impact": "Improved user engagement and potential jump link featured snippets",
                "implementation": "Edge worker parses H2s and generates TOC HTML block"
            })

        bot_serving_strategy = {
            "search_bots": {
                "serve_mode": "Pre-rendered HTML",
                "cache_ttl": "24 hours",
                "content_strategy": "Serve full HTML with structured data for Googlebot, Bingbot",
                "rationale": f"Page has {word_count} words of content - ensure bots see full content without JS execution"
            },
            "ai_bots": {
                "serve_mode": "Full HTML + Schema",
                "cache_ttl": "12 hours",
                "content_strategy": "Serve complete page with schema markup for GPTBot, PerplexityBot, ClaudeBot",
                "rationale": "AI crawlers need full content for training and citation purposes"
            },
            "regular_users": {
                "serve_mode": "Edge-cached HTML",
                "cache_ttl": "1 hour",
                "stale_while_revalidate": "24 hours",
                "content_strategy": "Serve cached HTML with dynamic personalization at edge",
                "rationale": f"Content-heavy page ({word_count} words) benefits from aggressive caching"
            }
        }

        image_optimization = []
        for img in images:
            src = img.get("src", "")
            alt = img.get("alt", "")
            if src:
                has_webp = any(ext in src.lower() for ext in [".webp", ".avif"])
                image_optimization.append({
                    "src": src,
                    "alt": alt,
                    "current_format": "webp/avif" if has_webp else "unknown (optimize at edge)",
                    "recommendation": "Already optimized" if has_webp else "Convert to WebP/AVIF via edge image transformation",
                    "lazy_loading": "Recommended" if word_count > 1000 else "Optional"
                })

        return {
            "url": url,
            "page_title": title,
            "page_word_count": word_count,
            "estimated_page_size_kb": round(estimated_page_size_kb, 1),
            "estimated_baseline_ttfb_ms": estimated_ttfb_ms,
            "cdn_caching_strategy": {
                "data_origin": "unverified_industry_heuristic - not measured for this page",
                "recommended_ttl": "3600 seconds (1 hour) for content pages",
                "stale_while_revalidate": "86400 seconds (24 hours)",
                "cache_invalidation_trigger": "On content publish/update via webhook",
                "cache_key_strategy": "URL + User-Agent (bot-aware caching)",
                "estimated_cache_hit_ratio": "85-95% for content pages with proper TTL"
            },
            "cache_header_recommendations": cache_headers,
            "edge_injection_opportunities": edge_injection_opportunities,
            "edge_injection_opportunity_count": len(edge_injection_opportunities),
            "bot_serving_strategy": bot_serving_strategy,
            "image_optimization_plan": image_optimization[:10],
            "total_images_analyzed": len(images),
            "cdn_performance_estimates": {
                "estimated_ttfb_with_cdn_ms": max(20, estimated_ttfb_ms // 3),
                "estimated_ttfb_improvement_ms": estimated_ttfb_ms - max(20, estimated_ttfb_ms // 3),
                "estimated_bandwidth_savings_percent": min(50, 30 + (image_count * 2)),
                "estimated_origin_requests_reduction_percent": min(80, 50 + (word_count // 200))
            },
            "content_delivery_recommendations": [
                f"Cache this {word_count}-word content page for 1 hour with 24-hour stale-while-revalidate",
                f"Serve {image_count} images with 7-day cache TTL and immutable headers",
                "Implement bot-aware caching to serve pre-rendered HTML to search engines",
                "Use edge workers to inject structured data if page lacks schema markup",
                "Enable Brotli compression for text content (HTML, CSS, JS) at CDN edge"
            ],
            "security_headers_for_url": {
                "strict_transport_security": "max-age=31536000; includeSubDomains; preload",
                "content_security_policy": "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'",
                "x_content_type_options": "nosniff",
                "referrer_policy": "strict-origin-when-cross-origin",
                "x_frame_options": "SAMEORIGIN"
            }
        }

    def _generate_edge_worker(self, cdn: str, schema: Dict, meta: Dict, headers: Dict) -> Dict[str, Any]:
        """Generate edge worker snippet for CDN injection."""
        if cdn == "not_detected":
            return {
                "cdn_provider": "not_detected",
                "status": "NOT_CONFIGURED - CDN provider not detected from response headers",
                "note": "Edge worker snippet templates are available for Cloudflare, Fastly, Akamai, and CloudFront once a provider is configured.",
                "worker_code": "",
            }
        schema_json = str(schema) if schema else '{"@context":"https://schema.org","@type":"TechArticle"}'
        snippet = generate_edge_worker_snippet(schema_json, meta, headers)
        return {
            "cdn_provider": cdn,
            "worker_code": snippet,
            "worker_type": "javascript",
            "estimated_execution_time": "(General industry guidance, unverified): < 5ms",
            "cache_behavior": "Edge-cached, invalidated on content update",
            "preview_url": f"https://preview.{cdn}.workers.dev/[path]",
            "testing_steps": [
                "Deploy worker to staging environment",
                "Verify schema injection in page source",
                "Test with Google Rich Results Test",
                "Validate HTTP headers in browser dev tools",
                "Check cache behavior with multiple requests"
            ]
        }

    def _inspect_server_headers(self, inputs: Dict, url: str = "") -> Dict[str, Any]:
        """Inspect and validate HTTP response headers using REAL live fetch when a URL is available."""
        required_headers = {
            "Cache-Control": {"expected": "public, max-age=3600, stale-while-revalidate=86400", "critical": True},
            "X-Robots-Tag": {"expected": "index, follow", "critical": True},
            "Vary": {"expected": "Accept-Encoding, User-Agent", "critical": False},
            "Content-Type": {"expected": "text/html; charset=utf-8", "critical": True},
            "Link": {"expected": '<https://schema.org>; rel="alternate"; type="application/ld+json"', "critical": False},
            "X-Content-Type-Options": {"expected": "nosniff", "critical": False},
            "X-Frame-Options": {"expected": "SAMEORIGIN", "critical": False},
            "Server": {"expected": "", "critical": False},
            "CF-Cache-Status": {"expected": "", "critical": False},
            "Age": {"expected": "", "critical": False},
        }
        current_headers = {}
        live_fetched = False
        if url:
            try:
                hdr_resp = fetch_headers(url, timeout=10)
                if hdr_resp.get("ok"):
                    current_headers = hdr_resp.get("headers", {})
                    live_fetched = True
            except Exception:
                pass
        if not current_headers:
            current_headers = dict(inputs.get("current_headers", {}) or {})
        headers_lower = {str(k).lower(): v for k, v in current_headers.items()}

        inspection_results = []
        for header, config in required_headers.items():
            current_value = headers_lower.get(header.lower())
            if current_value is None:
                current_value = "NOT_SET"
            if not config["expected"]:
                # informational header - report actual value as-is
                inspection_results.append({
                    "header": header,
                    "expected": "informational",
                    "current": current_value if current_value != "NOT_SET" else "NOT_SET",
                    "status": "PRESENT" if current_value != "NOT_SET" else "MISSING",
                    "critical": config["critical"],
                    "fix": "No fix needed"
                })
                continue
            is_correct = current_value.lower() == config["expected"].lower() if current_value != "NOT_SET" else False
            inspection_results.append({
                "header": header,
                "expected": config["expected"],
                "current": current_value,
                "status": "CORRECT" if is_correct else ("MISSING" if current_value == "NOT_SET" else "INCORRECT"),
                "critical": config["critical"],
                "fix": f"Set {header}: {config['expected']}" if not is_correct else "No fix needed"
            })
        return {
            "inspection_results": inspection_results,
            "total_headers_checked": len(inspection_results),
            "headers_correct": sum(1 for r in inspection_results if r["status"] == "CORRECT"),
            "critical_issues": sum(1 for r in inspection_results if r["status"] != "CORRECT" and r["critical"]),
            "live_header_fetch": live_fetched,
            "inspected_url": url or "not provided",
            "detected_server_technology": self._detect_server_tech(current_headers),
            "overall_status": (
                "ALL_HEADERS_CORRECT" if all(r["status"] == "CORRECT" for r in inspection_results) else
                f"{sum(1 for r in inspection_results if r['status'] != 'CORRECT')} HEADERS NEED FIXES"
            )
        }

    def _detect_server_tech(self, headers: Dict[str, str]) -> Dict[str, str]:
        """Identify CDN / origin technology from real response headers."""
        detection = {}
        low = {str(k).lower(): (str(v) or "").lower() for k, v in (headers or {}).items()}
        server = low.get("server", "")
        via = low.get("via", "")
        if "cloudflare" in server or "cloudflare" in via or "cf-cache-status" in low:
            detection["cdn_provider"] = "Cloudflare"
        elif "fastly" in server or "fastly" in via:
            detection["cdn_provider"] = "Fastly"
        elif "cloudfront" in server or "amazon" in server:
            detection["cdn_provider"] = "Amazon CloudFront"
        elif "akama" in server or "akama" in via:
            detection["cdn_provider"] = "Akamai"
        elif server:
            detection["cdn_provider"] = "Unknown/CDN_NOT_DETECTED"
            detection["server_header"] = headers.get("Server")
        if "nginx" in server:
            detection["origin_server"] = "nginx"
        elif "apache" in server:
            detection["origin_server"] = "Apache"
        elif "iis" in server:
            detection["origin_server"] = "IIS"
        if server and server != "unknown":
            detection["server_header"] = server
        return detection

    def _simulate_prerender(self, inputs: Dict, render_mode: str) -> Dict[str, Any]:
        """Simulate pre-rendered HTML for search bots."""
        original_html = inputs.get("html_content", "")
        return {
            "render_mode": render_mode,
            "prerender_available": render_mode in ["ssr", "ssg", "isr"],
            "initial_html_simulation": {
                "contains_h1": "<h1" in original_html,
                "contains_article": "<article" in original_html or "<main" in original_html,
                "word_count_in_initial_html": len(original_html.split()),
                "search_bot_sees": "FULL_CONTENT" if render_mode in ["ssr", "ssg"] else "REQUIRES_JS_EXECUTION"
            },
            "prerender_recommendation": (
                "SSR/SSG ensures search bots see full content immediately" if render_mode == "csr" else
                "Current render mode is search-engine friendly"
            ),
            "cache_configuration": {
                "bot_cache_ttl": "24 hours",
                "user_cache_ttl": "1 hour",
                "stale_while_revalidate": "24 hours",
                "cache_invalidation": "On content publish/update"
            }
        }

    def _generate_cdn_config(self, cdn: str, inputs: Dict) -> Dict[str, Any]:
        """Generate CDN configuration."""
        brand_website = (inputs.get("brand_website", "") or "").strip().rstrip("/")
        host = brand_website
        if host.startswith("http://"):
            host = host[len("http://"):]
        elif host.startswith("https://"):
            host = host[len("https://"):]
        if not host:
            host = "{YOUR_DOMAIN}"
        configs = {
            "cloudflare": {
                "worker_name": "schema-inject-worker",
                "route_pattern": f"{host}/{inputs.get('url_path', '*')}",
                "kv_namespace": "SCHEMA_CACHE",
                "env_variables": {"SCHEMA_TTL": "3600"},
                "pages_config": {"build_command": "npm run build", "output_dir": "dist"}
            },
            "fastly": {
                "vcl_template": "schema_inject.vcl",
                "backend": "origin_server",
                "director": "round_robin",
                "conditions": ["req.url.path ~ /^\\/content\\//"],
                "rules": ["Set req.http.X-Inject-Schema = true"]
            },
            "akamai": {
                "edge_worker_name": "schema-injection",
                "event_handler": "onClientRequest",
                "property_manager": {"rules": [{"name": "Schema Injection", "behavior": "edgeWorker"}]}
            },
            "cloudfront": {
                "function_name": "schema-injection-function",
                "event_type": "viewer-request",
                "runtime": "cloudfront-js-2.0",
                "cache_policy": "CachingOptimized"
            }
        }
        if cdn == "not_detected":
            return {
                "cdn_provider": "not_detected",
                "status": "NOT_CONFIGURED - CDN provider not detected from response headers",
                "note": "Set your CDN provider via the cdn_provider input or expose it in Server/Via headers for auto-detection.",
                "available_provider_templates": list(configs.keys()),
            }
        return configs.get(cdn, configs["cloudflare"])

    def _create_deployment_guide(self, cdn: str, worker: Dict) -> Dict[str, Any]:
        """Create deployment guide."""
        if cdn == "not_detected":
            return {
                "cdn_provider": "not_detected",
                "status": "NOT_CONFIGURED - no CDN detected",
                "deployment_steps": [
                    "1. Identify your current CDN or hosting edge provider",
                    "2. Re-run analysis after configuring cdn_provider input",
                    "3. Follow provider-specific deployment steps once detected"
                ]
            }
        return {
            "cdn_provider": cdn,
            "deployment_steps": [
                f"1. Access {cdn} dashboard and navigate to Workers/Edge Functions",
                "2. Create new worker with the generated snippet",
                "3. Configure route patterns to match content URLs",
                "4. Set environment variables for schema TTL",
                "5. Deploy to staging and test with search bot user agents",
                "6. Verify schema appears in Google Rich Results Test",
                "7. Deploy to production",
                "8. Monitor worker execution logs for errors"
            ],
            "testing_checklist": [
                "Verify schema in page source (curl with Googlebot UA)",
                "Test with Google Rich Results Test",
                "Validate with Schema.org validator",
                "Check HTTP headers in browser dev tools",
                "Verify cache behavior (multiple requests)",
                "Test on mobile device (check rendering)"
            ],
            "rollback_plan": "Disable worker route to immediately revert to origin response"
        }

    def _generate_recommendations(self, cdn: str, worker: Dict, headers: Dict) -> List[Dict[str, str]]:
        """Generate CDN recommendations."""
        recs = []
        if headers.get("critical_issues", 0) > 0:
            recs.append({
                "priority": "HIGH",
                "action": "Fix critical header issues",
                "detail": f"{headers['critical_issues']} critical headers need correction"
            })
        recs.append({
            "priority": "MEDIUM",
            "action": f"Deploy edge worker for schema injection via {cdn}",
            "detail": "Edge injection bypasses CMS deployment cycles"
        })
        recs.append({
            "priority": "LOW",
            "action": "Configure CDN caching rules for search bots",
            "detail": "Separate cache policies for bots vs users"
        })
        return recs
