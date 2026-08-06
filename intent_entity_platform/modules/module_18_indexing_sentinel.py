"""
Module 18: Indexing Pipeline & Server Log Sentinel
Monitors indexing status and server log errors for search bots.
"""
from typing import List, Dict, Any
from ..utils.web_data import fetch_robots_txt, fetch_sitemap_url, verify_url


class IndexingLogSentinel:
    """Module 18: Indexing Pipeline & Server Log Sentinel"""

    def __init__(self):
        self.module_id = "M18"
        self.module_name = "Indexing Pipeline & Server Log Sentinel"

    def analyze(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Full indexing and log analysis pipeline."""
        url = inputs.get("url", "")
        log_data = inputs.get("server_logs", [])
        sitemap_data = inputs.get("sitemap_data", {})

        _url_data = inputs.get("_url_data", {})
        url_from_data = _url_data.get("url", "")
        url_title = _url_data.get("title", "")
        url_has_schema = _url_data.get("has_schema", False)
        url_word_count = _url_data.get("word_count", 0)
        url_image_count = _url_data.get("image_count", 0)
        url_link_count = _url_data.get("link_count", 0)
        url_h1 = _url_data.get("h1", "")
        url_h2s = _url_data.get("h2s", [])

        url_indexing_analysis = self._analyze_url_indexing_readiness(_url_data) if _url_data else {}

        indexing_status = self._check_indexing_status(inputs)
        log_analysis = self._analyze_server_logs(log_data)
        crawl_budget = self._assess_crawl_budget(inputs, log_data)
        api_push_config = self._configure_api_push(inputs)
        bot_activity = self._analyze_bot_activity(log_data)
        error_analysis = self._analyze_errors(log_data)

        return {
            "module": self.module_id,
            "module_name": self.module_name,
            "url_analyzed": url_from_data or url,
            "url_indexing_readiness_analysis": url_indexing_analysis if _url_data else {
                "status": "NO_URL_DATA",
                "message": "Provide _url_data for URL-specific indexing analysis"
            },
            "indexing_status": indexing_status,
            "server_log_analysis": log_analysis,
            "crawl_budget_assessment": crawl_budget,
            "api_push_configuration": api_push_config,
            "bot_activity_analysis": bot_activity,
            "error_analysis": error_analysis,
            "recommendations": self._generate_recommendations(indexing_status, log_analysis, error_analysis),
            "implementation_steps": [
                "Step 1: Verify the target URL is included in your XML sitemap and the sitemap is submitted in GSC",
                "Step 2: Confirm the canonical URL is correctly set using <link rel='canonical'> in the <head>",
                "Step 3: Ensure robots.txt does not block the URL or its parent directory from Googlebot",
                "Step 4: Remove any noindex meta tags or X-Robots-Tag headers if the page should be indexed",
                "Step 5: Submit the URL to Google Indexing API using the provided endpoint and payload",
                "Step 6: Submit the URL to Bing IndexNow for instant indexing across Bing and partner engines",
                "Step 7: Collect at least 7 days of server log data to analyze bot crawling patterns",
                "Step 8: Analyze server logs to identify 4xx/5xx errors affecting crawl budget",
                "Step 9: Fix all 5xx server errors immediately - these block indexing and waste crawl budget",
                "Step 10: Redirect any 404 URLs with a 301 to the most relevant live page",
                "Step 11: Verify the page returns a 200 status code and full HTML content to Googlebot UA",
                "Step 12: Set up automated monitoring alerts for server errors and indexing status changes"
            ],
            "where_to_add": [
                "Place canonical URL in <head> via <link rel='canonical' href='...'> tag",
                "Add or verify XML sitemap location in robots.txt with Sitemap: directive",
                "Submit sitemap in GSC under Sitemaps section and Indexing API for instant push",
                "Configure server log monitoring in your server/CDN analytics or a log analyzer tool",
                "Set up IndexNow API key in your server configuration or CDN Worker",
                "Add X-Robots-Tag headers in server configuration or CDN rules for non-HTML content",
                "Place noindex directives in <head> meta tags or HTTP headers as appropriate",
                "Configure 301 redirects in server config (.htaccess, nginx.conf, or CDN rules)",
                "Set up GSC URL Inspection API integration for automated indexing verification",
                "Add structured data in <script type='application/ld+json'> in <head> for rich results eligibility"
            ],
            "detailed_analysis": {
                "indexing_benchmarks": {
                    "google_indexing_api_response_time": "Minutes to hours for URL_UPDATED type",
                    "bing_indexnow_response_time": "Within 24 hours for most submissions",
                    "typical_crawl_budget_per_site": "Small sites: 50-200 pages/day; Large sites: 1000-10000+ pages/day",
                    "time_to_first_index": "New pages: 2-14 days without API push; Minutes with Indexing API",
                    "crawl_frequency_for_important_pages": "Daily to weekly depending on authority and update frequency"
                },
                "server_log_analysis_benchmarks": {
                    "healthy_googlebot_crawl_rate": "10-50% of total bot traffic for established sites",
                    "acceptable_error_rate": "Under 1% of total requests",
                    "critical_5xx_threshold": "Any 5xx error on important pages requires immediate attention",
                    "redirect_chain_max_hops": "3 or fewer hops to preserve crawl budget",
                    "target_ttfb_for_bots": "Under 200ms to ensure full crawl within budget"
                },
                "expert_recommendations": [
                    "Always use Googlebot User-Agent in log analysis - filter out spoofed bots",
                    "Set up daily automated IndexNow submissions for new/updated content",
                    "Monitor crawl stats in GSC weekly to track Googlebot's crawl behavior on your site",
                    "Prioritize fixing 5xx errors on high-value URLs - they waste the most crawl budget",
                    "Implement server-side rendering or pre-rendering for JavaScript-heavy pages"
                ],
                "common_mistakes": [
                    "Forgetting to verify robots.txt changes don't accidentally block important pages",
                    "Using 302 temporary redirects instead of 301 permanent redirects (loses link equity)",
                    "Not monitoring server logs means crawl issues go undetected for weeks or months",
                    "Submitting too many URLs to Indexing API at once exceeds the 200/day quota",
                    "Ignoring crawl budget waste from 404 errors on deleted or moved content"
                ],
                "success_metrics": [
                    "Track Googlebot crawl frequency via GSC Crawl Stats report (target: daily for key pages)",
                    "Monitor indexing coverage in GSC - aim for 95%+ of important URLs indexed",
                    "Measure server error rate from logs (target: <0.1% of total requests)",
                    "Track time from publish to first Googlebot crawl (target: <48 hours with API push)",
                    "Monitor IndexNow submission success rate (target: 100% accepted responses)"
                ]
            }
        }

    def _analyze_url_indexing_readiness(self, url_data: Dict) -> Dict[str, Any]:
        """Analyze actual URL content for indexing readiness and crawlability."""
        url = url_data.get("url", "")
        title = url_data.get("title", "")
        has_schema = url_data.get("has_schema", False)
        word_count = url_data.get("word_count", 0)
        image_count = url_data.get("image_count", 0)
        link_count = url_data.get("link_count", 0)
        h1 = url_data.get("h1", "")
        h2s = url_data.get("h2s", [])
        meta_description = url_data.get("meta_description", "")
        page_text = url_data.get("page_text", "")

        indexing_checks = []
        indexing_score = 0

        if title:
            indexing_score += 15
            indexing_checks.append({
                "check": "Title Tag Present",
                "status": "PASS",
                "detail": f"Title tag found: '{title}' ({len(title)} chars)",
                "recommendation": "Title is within optimal range" if 30 <= len(title) <= 60 else f"Title is {len(title)} chars - aim for 30-60 characters"
            })
        else:
            indexing_checks.append({
                "check": "Title Tag Present",
                "status": "FAIL",
                "detail": "No title tag detected",
                "recommendation": "Add a descriptive title tag (30-60 characters)"
            })

        if h1:
            indexing_score += 15
            indexing_checks.append({
                "check": "H1 Tag Present",
                "status": "PASS",
                "detail": f"H1 found: '{h1}'",
                "recommendation": "H1 tag is present and descriptive"
            })
        else:
            indexing_checks.append({
                "check": "H1 Tag Present",
                "status": "FAIL",
                "detail": "No H1 tag detected",
                "recommendation": "Add a single H1 tag that matches the page intent"
            })

        if has_schema:
            indexing_score += 20
            indexing_checks.append({
                "check": "Structured Data Schema",
                "status": "PASS",
                "detail": "Structured data schema detected on page",
                "recommendation": "Schema present - verify with Google Rich Results Test"
            })
        else:
            indexing_checks.append({
                "check": "Structured Data Schema",
                "status": "FAIL",
                "detail": "No structured data schema detected",
                "recommendation": "Add Article, BlogPosting, or appropriate JSON-LD schema"
            })

        if word_count >= 300:
            indexing_score += 10
            indexing_checks.append({
                "check": "Content Depth",
                "status": "PASS" if word_count >= 800 else "WARNING",
                "detail": f"Page has {word_count} words of content",
                "recommendation": f"{'Adequate' if word_count >= 800 else 'Consider expanding to'} 800+ words for competitive topics"
            })
        else:
            indexing_checks.append({
                "check": "Content Depth",
                "status": "FAIL",
                "detail": f"Page has only {word_count} words - very thin content",
                "recommendation": "Expand content to 800+ words for better indexing potential"
            })

        if len(h2s) >= 2:
            indexing_score += 10
            indexing_checks.append({
                "check": "Content Structure (H2s)",
                "status": "PASS",
                "detail": f"Page has {len(h2s)} H2 sections for content organization",
                "recommendation": "Good content structure with multiple H2 sections"
            })
        else:
            indexing_checks.append({
                "check": "Content Structure (H2s)",
                "status": "WARNING",
                "detail": f"Page has only {len(h2s)} H2 sections",
                "recommendation": "Add 3-5 H2 sections to improve content structure and crawlability"
            })

        if link_count >= 3:
            indexing_score += 10
            indexing_checks.append({
                "check": "Internal/External Links",
                "status": "PASS",
                "detail": f"Page has {link_count} links",
                "recommendation": "Good link density for crawlability"
            })
        else:
            indexing_checks.append({
                "check": "Internal/External Links",
                "status": "WARNING",
                "detail": f"Page has only {link_count} links",
                "recommendation": "Add 5-8 contextual internal and external links"
            })

        if meta_description:
            indexing_score += 10
            indexing_checks.append({
                "check": "Meta Description",
                "status": "PASS",
                "detail": f"Meta description present ({len(meta_description)} chars)",
                "recommendation": "Meta description is set"
            })
        else:
            indexing_checks.append({
                "check": "Meta Description",
                "status": "WARNING",
                "detail": "No meta description detected",
                "recommendation": "Add a compelling meta description (150-160 characters)"
            })

        if image_count > 0:
            indexing_score += 5
            indexing_checks.append({
                "check": "Visual Content",
                "status": "PASS",
                "detail": f"Page has {image_count} images",
                "recommendation": "Images present - ensure all have descriptive alt text"
            })
        else:
            indexing_checks.append({
                "check": "Visual Content",
                "status": "WARNING",
                "detail": "No images detected on page",
                "recommendation": "Add relevant images with descriptive alt text"
            })

        indexing_score = min(100, indexing_score)

        sitemap_recommendations = []
        parsed_url = url.split("/") if url else []
        if len(parsed_url) > 3:
            sitemap_recommendations.append(f"Add URL to XML sitemap: {url}")
        sitemap_recommendations.extend([
            "Submit sitemap in Google Search Console",
            "Include lastmod date in sitemap entry",
            "Set changefreq to 'weekly' for frequently updated content",
            "Set priority based on content importance (0.5-1.0)"
        ])

        crawl_budget_recommendations = []
        if word_count > 2000:
            crawl_budget_recommendations.append("Long-form content - ensure server responds within 200ms TTFB")
        if image_count > 10:
            crawl_budget_recommendations.append(f"Many images ({image_count}) - optimize file sizes to reduce load time")
        crawl_budget_recommendations.extend([
            "Ensure URL returns 200 status code",
            "Verify canonical URL is self-referencing",
            "Check robots.txt allows Googlebot to crawl this URL",
            "Implement proper 301 redirects if URL has changed"
        ])

        return {
            "url": url,
            "page_title": title,
            "page_h1": h1,
            "page_word_count": word_count,
            "page_image_count": image_count,
            "page_link_count": link_count,
            "has_schema": has_schema,
            "h2_section_count": len(h2s),
            "meta_description_present": bool(meta_description),
            "indexing_readiness_checks": indexing_checks,
            "total_checks_passed": sum(1 for c in indexing_checks if c["status"] == "PASS"),
            "total_checks_failed": sum(1 for c in indexing_checks if c["status"] == "FAIL"),
            "total_checks_warning": sum(1 for c in indexing_checks if c["status"] == "WARNING"),
            "indexing_readiness_score": round(indexing_score / 100, 3),
            "indexing_readiness_tier": (
                "READY" if indexing_score >= 80 else
                "MOSTLY_READY" if indexing_score >= 60 else
                "NEEDS_WORK" if indexing_score >= 40 else
                "NOT_READY"
            ),
            "sitemap_recommendations": sitemap_recommendations,
            "crawl_budget_recommendations": crawl_budget_recommendations,
            "api_push_payload": {
                "google_indexing_api": {
                    "url": url,
                    "type": "URL_UPDATED"
                },
                "bing_indexnow": {
                    "host": "/".join(url.split("/")[:3]) if url else "",
                    "urlList": [url]
                }
            },
            "blocking_issues": [
                c for c in indexing_checks if c["status"] == "FAIL"
            ],
            "warnings": [
                c for c in indexing_checks if c["status"] == "WARNING"
            ],
            "content_quality_for_indexing": {
                "word_count_sufficient": word_count >= 300,
                "word_count_target": "800+ words for competitive topics",
                "structure_sufficient": len(h2s) >= 2,
                "link_density_sufficient": link_count >= 3,
                "schema_present": has_schema,
                "title_optimal": 30 <= len(title) <= 60 if title else False,
                "overall_content_quality_score": round(indexing_score / 100, 3)
            }
        }

    def _check_indexing_status(self, inputs: Dict) -> Dict[str, Any]:
        """Check indexing status of target URL with REAL robots.txt/sitemap verification."""
        _url_data = inputs.get("_url_data", {}) or {}
        url = _url_data.get("url", "") or inputs.get("url", "")

        # REAL robots.txt check
        robots_check = self._check_robots_allowance(url)
        # REAL sitemap check
        sitemap_check = self._check_sitemap_inclusion(url)
        # REAL page status check
        live_check = self._check_page_status(url)

        return {
            "target_url": url,
            "indexing_checks": {
                "google_indexed": "Requires GSC API verification (not configured)",
                "bing_indexed": "Requires IndexNow verification (not configured)",
                "sitemap_included": sitemap_check.get("found_in_sitemap", False),
                "robots_allow": robots_check.get("allowed", None),
                "canonical_set": bool(_url_data.get("canonical") or inputs.get("canonical_url")),
                "page_reachable": live_check.get("reachable"),
                "page_http_status": live_check.get("status_code"),
                "mobile_friendly": "Not tested (requires emulation)",
                "page_experience": "Not configured (requires Core Web Vitals data)"
            },
            "live_checks_performed": True,
            "robots_txt_analysis": robots_check,
            "sitemap_analysis": sitemap_check,
            "page_status_check": live_check,
            "indexing_readiness_score": self._compute_indexing_readiness(robots_check, sitemap_check, live_check),
            "blocking_issues": self._collect_blocking_issues(robots_check, sitemap_check, live_check),
            "recommended_actions": [
                "Submit URL to Google Indexing API",
                "Submit to Bing IndexNow",
                "Verify robots.txt allows crawling",
                "Ensure canonical URL is correct"
            ]
        }

    def _check_robots_allowance(self, url: str) -> Dict[str, Any]:
        """Fetch the real robots.txt and determine whether the URL is allowed."""
        if not url:
            return {"allowed": None, "status": "NO_URL", "error": "No URL provided"}
        robots = fetch_robots_txt(url)
        content = robots.get("content", "") or ""
        allowed = None
        reason = ""
        path = ""
        try:
            from urllib.parse import urlparse
            path = urlparse(url).path or "/"
        except Exception:
            pass
        lines = [ln.strip() for ln in content.splitlines() if ln.strip()]
        user_agent = None
        for ln in lines:
            low = ln.lower()
            if low.startswith("user-agent"):
                user_agent = ln.split(":", 1)[1].strip().lower()
                continue
            if low.startswith("allow") or low.startswith("disallow"):
                if user_agent is not None and user_agent not in ("*", "googlebot"):
                    continue
                rule = low.split(":", 1)[1].strip()
                if low.startswith("allow"):
                    pass
                else:
                    if rule in ("/", "") and path.startswith("/"):
                        allowed = False
                        reason = f"robots.txt Disallow: / blocks the URL path"
                        break
                    if rule and rule != "/" and path.startswith(rule):
                        allowed = False
                        reason = f"robots.txt Disallow: {rule} matches path {path}"
                        break
        if allowed is None and not reason:
            if not content.strip():
                allowed = True
                reason = "No robots.txt found (treated as allow-all)"
            else:
                allowed = True
                reason = "No disallow rule matched the URL path"
        return {
            "allowed": bool(allowed),
            "status": "CHECKED" if robots.get("ok") else "UNAVAILABLE",
            "robots_url": robots.get("url", ""),
            "robots_fetch_error": robots.get("error"),
            "path_checked": path,
            "reason": reason,
            "robots_snippet": content[:500],
        }

    def _check_sitemap_inclusion(self, url: str) -> Dict[str, Any]:
        """Fetch the real sitemap and check whether the URL is present."""
        if not url:
            return {"found_in_sitemap": None, "status": "NO_URL"}
        sitemap = fetch_sitemap_url(url)
        in_sitemap = url in sitemap.get("sitemap_urls", [])
        return {
            "found_in_sitemap": bool(in_sitemap),
            "status": "CHECKED" if sitemap.get("ok") else "UNAVAILABLE",
            "sitemap_url": sitemap.get("url", ""),
            "total_urls_in_sitemap": len(sitemap.get("sitemap_urls", [])),
            "error": sitemap.get("error"),
        }

    def _check_page_status(self, url: str) -> Dict[str, Any]:
        """Verify the target URL actually returns a 200."""
        if not url:
            return {"reachable": None, "status_code": None}
        check = verify_url(url, timeout=10)
        return {
            "reachable": bool(check.get("reachable")),
            "status_code": check.get("status_code"),
            "final_url": check.get("final_url"),
            "error": check.get("error"),
        }

    def _compute_indexing_readiness(self, robots: Dict, sitemap: Dict, live: Dict) -> float:
        score = 0.0
        if robots.get("allowed") is True:
            score += 0.4
        if sitemap.get("found_in_sitemap"):
            score += 0.3
        if live.get("reachable") and live.get("status_code") == 200:
            score += 0.3
        return round(min(1.0, score), 3)

    def _collect_blocking_issues(self, robots: Dict, sitemap: Dict, live: Dict) -> List[str]:
        issues = []
        if robots.get("allowed") is False:
            issues.append("robots.txt disallows crawling this URL")
        if sitemap.get("status") == "CHECKED" and not sitemap.get("found_in_sitemap"):
            issues.append("URL is not present in the site sitemap")
        if live.get("reachable") is False:
            issues.append(f"URL returned HTTP {live.get('status_code')} (not 200)")
        return issues

    def _analyze_server_logs(self, log_data: List[Dict]) -> Dict[str, Any]:
        """Analyze server access logs."""
        if not log_data:
            return {"status": "NO_LOG_DATA", "analysis": "Provide server log data for analysis"}
        bot_requests = {}
        status_codes = {}
        for entry in log_data:
            user_agent = entry.get("user_agent", "unknown")
            status = entry.get("status_code", 200)
            if "googlebot" in user_agent.lower():
                bot_requests["googlebot"] = bot_requests.get("googlebot", 0) + 1
            elif "bingbot" in user_agent.lower():
                bot_requests["bingbot"] = bot_requests.get("bingbot", 0) + 1
            elif "perplexitybot" in user_agent.lower():
                bot_requests["perplexitybot"] = bot_requests.get("perplexitybot", 0) + 1
            elif "gptbot" in user_agent.lower():
                bot_requests["gptbot"] = bot_requests.get("gptbot", 0) + 1
            status_codes[status] = status_codes.get(status, 0) + 1
        return {
            "total_requests": len(log_data),
            "bot_requests": bot_requests,
            "status_code_distribution": status_codes,
            "error_rate": round(sum(v for k, v in status_codes.items() if k >= 400) / max(1, len(log_data)) * 100, 2),
            "googlebot_hits": bot_requests.get("googlebot", 0),
            "crawl_frequency": "Analyze over 7-day window for patterns"
        }

    def _assess_crawl_budget(self, inputs: Dict, log_data: List[Dict]) -> Dict[str, Any]:
        """Assess crawl budget allocation."""
        return {
            "crawl_budget_status": "Requires server log data for accurate assessment",
            "optimization_recommendations": [
                "Fix 4xx/5xx errors to preserve crawl budget",
                "Implement proper redirects (301, not 302)",
                "Reduce redirect chains to < 3 hops",
                "Minimize thin/duplicate content pages",
                "Optimize server response time (< 200ms TTFB)"
            ],
            "crawl_efficiency_score": "Calculate from log data: (successful_crawls / total_crawl_attempts)"
        }

    def _configure_api_push(self, inputs: Dict) -> Dict[str, Any]:
        """Configure instant API push for indexing (honest about required credentials)."""
        has_indexnow_key = bool(inputs.get("indexnow_key"))
        has_gsc_creds = bool(inputs.get("indexing_api_credentials", {}).get("service_account_json"))
        _url_data = inputs.get("_url_data", {}) or {}
        url = _url_data.get("url", "") or inputs.get("url", "")
        try:
            from urllib.parse import urlparse
            domain = urlparse(url).netloc
        except Exception:
            domain = inputs.get("domain", "")
        return {
            "google_indexing_api": {
                "available": has_gsc_creds,
                "status": "NOT_CONFIGURED - requires Google service account JSON (indexing_api_credentials)",
                "endpoint": "https://indexing.googleapis.com/v3/urlNotifications:publish",
                "quota": "200 URLs per day",
                "payload": {
                    "url": url,
                    "type": "URL_UPDATED"
                }
            },
            "bing_indexnow": {
                "available": has_indexnow_key,
                "status": "CONFIGURED" if has_indexnow_key else "NOT_CONFIGURED - requires indexnow_key",
                "endpoint": "https://api.indexnow.org/indexnow",
                "key": inputs.get("indexnow_key", "[PENDING_INDEXNOW_KEY]"),
                "payload": {
                    "host": domain,
                    "urlList": [url]
                }
            },
            "instant_push_enabled": has_gsc_creds or has_indexnow_key,
            "push_triggers": ["on_publish", "on_update", "on_canonical_change"],
            "verification_steps": [
                "Submit URL and verify 200 response from API",
                "Check GSC URL Inspection tool after 24 hours",
                "Monitor server logs for bot visits within 48 hours"
            ]
        }

    def _analyze_bot_activity(self, log_data: List[Dict]) -> Dict[str, Any]:
        """Analyze search bot activity patterns."""
        if not log_data:
            return {"status": "NO_DATA"}
        return {
            "bot_visits_summary": "Analyze log data for bot visit patterns",
            "frequency_assessment": "Check if high-priority pages are crawled within 24h of publish",
            "render_check": "Verify bots receive fully rendered HTML, not JavaScript shell",
            "recommendation": "Monitor bot visits for 7 days after publish to verify crawl patterns"
        }

    def _analyze_errors(self, log_data: List[Dict]) -> Dict[str, Any]:
        """Analyze server errors from logs."""
        if not log_data:
            return {"errors": [], "status": "NO_DATA"}
        errors = []
        for entry in log_data:
            status = entry.get("status_code", 200)
            if status >= 400:
                errors.append({
                    "url": entry.get("url", ""),
                    "status_code": status,
                    "user_agent": entry.get("user_agent", ""),
                    "timestamp": entry.get("timestamp", ""),
                    "severity": "CRITICAL" if status >= 500 else "HIGH" if status == 404 else "MEDIUM",
                    "fix": "Check URL availability and server configuration" if status >= 500 else
                           "Verify URL exists and is properly linked" if status == 404 else
                           "Check access permissions"
                })
        return {
            "total_errors": len(errors),
            "critical_errors": sum(1 for e in errors if e["severity"] == "CRITICAL"),
            "high_errors": sum(1 for e in errors if e["severity"] == "HIGH"),
            "errors": errors[:20],
            "error_rate": round(len(errors) / max(1, len(log_data)) * 100, 2)
        }

    def _generate_recommendations(self, indexing: Dict, logs: Dict, errors: Dict) -> List[Dict[str, str]]:
        """Generate indexing recommendations."""
        recs = []
        if errors.get("critical_errors", 0) > 0:
            recs.append({
                "priority": "CRITICAL",
                "action": f"Fix {errors['critical_errors']} server errors (5xx)",
                "detail": "Server errors waste crawl budget and prevent indexing"
            })
        if errors.get("high_errors", 0) > 0:
            recs.append({
                "priority": "HIGH",
                "action": f"Resolve {errors['high_errors']} client errors (4xx)",
                "detail": "404 errors indicate broken links or missing content"
            })
        recs.append({
            "priority": "HIGH",
            "action": "Submit URL to Google Indexing API and Bing IndexNow",
            "detail": "Instant push ensures immediate crawl consideration"
        })
        return recs
