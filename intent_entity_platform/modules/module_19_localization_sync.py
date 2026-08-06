"""
Module 19: Internationalization & Localization Sync Engine
Analyzes hreflang needs, locale targeting, and entity mapping for multi-language SEO.
"""
import re
from typing import List, Dict, Any


class LocalizationSyncEngine:
    """Module 19: Internationalization & Localization Sync Engine"""

    def __init__(self):
        self.module_id = "M19"
        self.module_name = "Internationalization & Localization Sync Engine"

    def analyze(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Full localization and hreflang analysis pipeline."""
        url = inputs.get("url", "")
        target_locales = inputs.get("target_locales", [])
        content = inputs.get("content", "")
        existing_hreflang = inputs.get("existing_hreflang", [])

        _url_data = inputs.get("_url_data", {})
        url_from_data = _url_data.get("url", "")
        url_title = _url_data.get("title", "")
        url_page_text = _url_data.get("page_text", "")
        url_h1 = _url_data.get("h1", "")
        url_h2s = _url_data.get("h2s", [])
        url_word_count = _url_data.get("word_count", 0)
        url_has_schema = _url_data.get("has_schema", False)
        url_meta_description = _url_data.get("meta_description", "")

        url_localization_analysis = self._analyze_url_localization_needs(_url_data) if _url_data else {}

        hreflang_analysis = self._analyze_hreflang(existing_hreflang, url)
        locale_targeting = self._assess_locale_targeting(target_locales, url)
        entity_mapping = self._map_entities_for_localization(content or url_page_text, url_title)
        translation_priorities = self._prioritize_translation(content or url_page_text, url_title)
        international_seo_config = self._configure_international_seo(url, target_locales)

        return {
            "module": self.module_id,
            "module_name": self.module_name,
            "url_analyzed": url_from_data or url,
            "url_localization_analysis": url_localization_analysis if _url_data else {
                "status": "NO_URL_DATA",
                "message": "Provide _url_data for URL-specific localization analysis"
            },
            "hreflang_analysis": hreflang_analysis,
            "locale_targeting_assessment": locale_targeting,
            "entity_mapping": entity_mapping,
            "translation_priorities": translation_priorities,
            "international_seo_configuration": international_seo_config,
            "recommendations": self._generate_recommendations(hreflang_analysis, locale_targeting, entity_mapping),
            "implementation_steps": [
                "Step 1: Identify all target locales and language variants for the content",
                "Step 2: Add hreflang tags in <head> for each locale variant (e.g., en-us, en-gb, fr-fr, de-de)",
                "Step 3: Implement x-default hreflang tag pointing to the primary language version",
                "Step 4: Add lang attribute to <html> tag (e.g., <html lang='en-US'>)",
                "Step 5: Translate title tags and meta descriptions for each locale (not just body content)",
                "Step 6: Localize date formats, currency, measurements, and number formats in content",
                "Step 7: Add Geo-Targeting meta tags or CDN-based geo-redirects for country-specific content",
                "Step 8: Create locale-specific XML sitemaps or include hreflang in existing sitemap",
                "Step 9: Implement structured data with inLanguage and contentLocale properties",
                "Step 10: Set up CDN edge rules to serve correct locale based on Accept-Language header",
                "Step 11: Verify hreflang implementation with Google's hreflang testing tool",
                "Step 12: Monitor international targeting in GSC for each locale version"
            ],
            "where_to_add": [
                "Place hreflang tags in <head> via <link rel='alternate' hreflang='...' href='...'> tags",
                "Add lang attribute on <html> element: <html lang='en-US'>",
                "Place x-default hreflang tag in <head> for the primary language fallback",
                "Add inLanguage property to Article/BlogPosting JSON-LD schema in <head>",
                "Translate <title> and <meta name='description'> for each locale in <head>",
                "Add locale-specific Open Graph tags (og:locale, og:locale:alternate) in <head>",
                "Place localized content in separate URL structures (e.g., /en/, /fr/, /de/)",
                "Add hreflang entries in XML sitemap under <url> with <xhtml:link> elements",
                "Implement geo-redirects in CDN Worker or server config based on user location",
                "Add Content-Language HTTP header for locale identification"
            ],
            "detailed_analysis": {
                "hreflang_benchmarks": {
                    "minimum_locales_for_hreflang": "2+ language versions required",
                    "x_default_importance": "Critical - specifies fallback for unmatched locales",
                    "self_referencing_hreflang": "Required - each page must reference itself",
                    "reciprocal_hreflang": "All linked pages must have returning hreflang tags",
                    "typical_hreflang_error_rate": "30-40% of implementations have errors on first deploy"
                },
                "localization_benchmarks": {
                    "translation_quality_threshold": "Native speaker review required for YMYL content",
                    "localized_title_optimization": "Translate AND optimize for local search behavior",
                    "currency_localization_impact": "Localized pricing increases conversion by 20-40%",
                    "date_format_localization": "Critical for trust - US: MM/DD/YYYY vs EU: DD/MM/YYYY",
                    "rtl_language_support": "Required for Arabic, Hebrew, Farsi - affects entire layout"
                },
                "international_seo_benchmarks": {
                    "geo_targeting_accuracy": "CDN-based geo-detection is 95%+ accurate",
                    "hreflang_implementation_time": "2-4 weeks for first implementation, 1-2 days for updates",
                    "content_localization_cost": "30-50% of original content creation cost per locale",
                    "international_organic_traffic_uplift": "40-60% increase with proper hreflang implementation",
                    "local_search_volume_increase": "2-3x for locally-optimized content vs. translated-only content"
                },
                "expert_recommendations": [
                    "Never use machine translation alone for YMYL content - always have native speaker review",
                    "Localize content for cultural context, not just language - idioms, examples, and references differ",
                    "Use subdirectory structure (/en/, /fr/) over subdomains for simpler hreflang management",
                    "Implement hreflang before launching international content to prevent duplicate issues",
                    "Monitor each locale version separately in GSC for locale-specific performance insights"
                ],
                "common_mistakes": [
                    "Forgetting self-referencing hreflang tags causes indexing issues",
                    "Using machine-translated content without human review damages E-E-A-T signals",
                    "Not localizing meta descriptions means missed CTR opportunities in local SERPs",
                    "Using IP-based redirects without hreflang creates crawlability issues",
                    "Ignoring right-to-left (RTL) language layout requirements breaks page rendering"
                ],
                "success_metrics": [
                    "Track organic traffic per locale version (target: proportional to market size)",
                    "Monitor hreflang errors in GSC International Targeting report (target: 0 errors)",
                    "Measure conversion rate by locale (target: within 20% of primary locale)",
                    "Track local keyword rankings per locale (target: top 10 for target terms)",
                    "Monitor bounce rate by locale (target: consistent across all versions)"
                ]
            }
        }

    def _analyze_url_localization_needs(self, url_data: Dict) -> Dict[str, Any]:
        """Analyze actual URL content for localization requirements."""
        url = url_data.get("url", "")
        title = url_data.get("title", "")
        page_text = url_data.get("page_text", "")
        h1 = url_data.get("h1", "")
        h2s = url_data.get("h2s", [])
        word_count = url_data.get("word_count", 0)
        meta_description = url_data.get("meta_description", "")
        has_schema = url_data.get("has_schema", False)
        images = url_data.get("images", [])

        locale_indicators = []
        localization_score = 0

        lang_match = re.search(r'/(en|fr|de|es|it|pt|ja|ko|zh|ar|ru|nl|sv|da|fi|no|pl|tr|hi|th|vi|id|ms|cs|ro|hu|bg|hr|sk|sl|et|lv|lt|ga|mt|cy|is|mk|sq|bs|sr|me|sq|ka|hy|az|kk|uz|tg|tk|ky|mn|ne|si|bn|ta|te|mr|gu|pa|ur|fa|kn|ml|or|as|sa|my|km|lo|ka|am|ti|so|sw|yo|ig|ha|zu|af|st|tn|ts|ss|ve|nr|xh|rw|mg|ml', url)
        if lang_match:
            detected_lang = lang_match.group(1)
            locale_indicators.append(f"URL path contains language code: /{detected_lang}/")
            localization_score += 20
        else:
            locale_indicators.append("No language code detected in URL path")
            localization_score += 5

        tld_match = re.search(r'\.(com|co\.uk|fr|de|es|it|jp|cn|br|in|au|ca|mx|nl|se|no|dk|fi|pl|cz|ro|hu|bg|hr|sk|si|ee|lv|lt|ie|mt|cy|is|lu|be|at|ch)', url)
        if tld_match:
            tld = tld_match.group(1)
            locale_indicators.append(f"Country-code TLD detected: .{tld}")
            localization_score += 15

        text_indicators = {
            "en": [r'\bthe\b', r'\bis\b', r'\band\b', r'\bfor\b'],
            "fr": [r'\ble\b', r'\bla\b', r'\bdes\b', r'\bune\b'],
            "de": [r'\bder\b', r'\bdie\b', r'\bund\b', r'\bein\b'],
            "es": [r'\bel\b', r'\bla\b', r'\by\b', r'\bde\b'],
            "ja": [r'[\u3040-\u309f\u30a0-\u30ff]'],
            "zh": [r'[\u4e00-\u9fff]'],
            "ar": [r'[\u0600-\u06ff]'],
            "ru": [r'[\u0400-\u04ff]']
        }
        detected_content_lang = None
        for lang, patterns in text_indicators.items():
            matches = sum(len(re.findall(p, page_text, re.IGNORECASE)) for p in patterns)
            if matches >= 3:
                detected_content_lang = lang
                locale_indicators.append(f"Content language detected: {lang} ({matches} pattern matches)")
                localization_score += 25
                break

        if not detected_content_lang:
            locale_indicators.append("Could not detect content language from text patterns")
            localization_score += 5

        currency_patterns = [
            (r'\$[\d,]+', 'USD ($)'),
            (r'€[\d,]+', 'EUR (€)'),
            (r'£[\d,]+', 'GBP (£)'),
            (r'¥[\d,]+', 'JPY/CNY (¥)'),
            (r'₹[\d,]+', 'INR (₹)'),
            (r'R\$[\d,]+', 'BRL (R$)')
        ]
        currencies_found = []
        for pattern, name in currency_patterns:
            if re.search(pattern, page_text):
                currencies_found.append(name)
                localization_score += 5
        if currencies_found:
            locale_indicators.append(f"Currencies referenced: {', '.join(currencies_found)}")

        date_format_patterns = [
            (r'\d{1,2}/\d{1,2}/\d{4}', 'US format (MM/DD/YYYY)'),
            (r'\d{1,2}\.\d{1,2}\.\d{4}', 'EU format (DD.MM.YYYY)'),
            (r'\d{4}-\d{2}-\d{2}', 'ISO format (YYYY-MM-DD)'),
            (r'\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}', 'Written format')
        ]
        date_formats_found = []
        for pattern, name in date_format_patterns:
            if re.search(pattern, page_text):
                date_formats_found.append(name)
        if date_formats_found:
            locale_indicators.append(f"Date formats found: {', '.join(date_formats_found)}")

        measurement_patterns = [
            (r'\d+(?:\.\d+)?(?:km|kilometer)', 'Metric (km)'),
            (r'\d+(?:\.\d+)?(?:mi|miles)', 'Imperial (miles)'),
            (r'\d+(?:\.\d+)?(?:kg|kilogram)', 'Metric (kg)'),
            (r'\d+(?:\.\d+)?(?:lbs?|pounds?)', 'Imperial (lbs)'),
            (r'\d+(?:\.\d+)?(?:°C|°F)', 'Temperature')
        ]
        measurements_found = []
        for pattern, name in measurement_patterns:
            if re.search(pattern, page_text, re.IGNORECASE):
                measurements_found.append(name)
        if measurements_found:
            locale_indicators.append(f"Measurement systems found: {', '.join(measurements_found)}")

        localization_actions = []
        if not lang_match:
            localization_actions.append({
                "action": "Add language code to URL structure",
                "detail": "Implement /en/, /fr/, /de/ etc. in URL path for language targeting",
                "priority": "HIGH"
            })
        if not has_schema:
            localization_actions.append({
                "action": "Add schema with inLanguage property",
                "detail": "Implement Article/BlogPosting JSON-LD with inLanguage field",
                "priority": "MEDIUM"
            })
        if currencies_found and len(currencies_found) > 1:
            localization_actions.append({
                "action": "Localize currency display per locale",
                "detail": f"Multiple currencies detected ({', '.join(currencies_found)}) - show relevant currency per locale",
                "priority": "HIGH"
            })
        if measurements_found:
            localization_actions.append({
                "action": "Localize measurement units per locale",
                "detail": f"Measurement systems detected ({', '.join(measurements_found)}) - convert for target locale",
                "priority": "MEDIUM"
            })
        if date_formats_found and len(set(date_formats_found)) > 1:
            localization_actions.append({
                "action": "Standardize date format per locale",
                "detail": f"Multiple date formats detected - use locale-appropriate format",
                "priority": "MEDIUM"
            })

        return {
            "url": url,
            "page_title": title,
            "page_word_count": word_count,
            "locale_indicators": locale_indicators,
            "locale_indicator_count": len(locale_indicators),
            "detected_content_language": detected_content_lang or "UNKNOWN",
            "url_has_language_code": bool(lang_match),
            "detected_language_in_url": lang_match.group(1) if lang_match else None,
            "url_has_country_tld": bool(tld_match),
            "detected_country_tld": tld_match.group(1) if tld_match else None,
            "currencies_referenced": currencies_found,
            "date_formats_detected": date_formats_found,
            "measurement_systems_detected": measurements_found,
            "localization_score": round(min(1.0, localization_score / 100), 3),
            "localization_tier": (
                "FULLY_LOCALIZED" if localization_score >= 70 else
                "PARTIALLY_LOCALIZED" if localization_score >= 40 else
                "MINIMALLY_LOCALIZED" if localization_score >= 20 else
                "NOT_LOCALIZED"
            ),
            "localization_actions": localization_actions,
            "localization_action_count": len(localization_actions),
            "hreflang_implementation_needed": not lang_match or localization_score < 40,
            "recommended_locales": self._suggest_target_locales(url, detected_content_lang, title, page_text),
            "localization_complexity": {
                "currency_localization_needed": bool(currencies_found),
                "date_format_localization_needed": len(set(date_formats_found)) > 1,
                "measurement_localization_needed": bool(measurements_found),
                "rtl_support_needed": detected_content_lang in ["ar", "he", "fa", "ur"],
                "estimated_translation_effort": f"{max(1, word_count // 500)} hours per locale"
            }
        }

    def _suggest_target_locales(self, url: str, detected_lang: str, title: str, page_text: str) -> List[Dict]:
        """Suggest target locales based on content analysis."""
        suggestions = []
        if detected_lang == "en":
            suggestions.extend([
                {"locale": "en-US", "language": "English", "region": "United States", "priority": "PRIMARY"},
                {"locale": "en-GB", "language": "English", "region": "United Kingdom", "priority": "HIGH"},
                {"locale": "en-AU", "language": "English", "region": "Australia", "priority": "MEDIUM"},
                {"locale": "fr-FR", "language": "French", "region": "France", "priority": "HIGH"},
                {"locale": "de-DE", "language": "German", "region": "Germany", "priority": "HIGH"},
                {"locale": "es-ES", "language": "Spanish", "region": "Spain", "priority": "HIGH"},
                {"locale": "pt-BR", "language": "Portuguese", "region": "Brazil", "priority": "MEDIUM"},
                {"locale": "ja-JP", "language": "Japanese", "region": "Japan", "priority": "MEDIUM"}
            ])
        elif detected_lang == "fr":
            suggestions.extend([
                {"locale": "fr-FR", "language": "French", "region": "France", "priority": "PRIMARY"},
                {"locale": "fr-CA", "language": "French", "region": "Canada", "priority": "HIGH"},
                {"locale": "en-US", "language": "English", "region": "United States", "priority": "HIGH"}
            ])
        elif detected_lang == "de":
            suggestions.extend([
                {"locale": "de-DE", "language": "German", "region": "Germany", "priority": "PRIMARY"},
                {"locale": "de-AT", "language": "German", "region": "Austria", "priority": "HIGH"},
                {"locale": "de-CH", "language": "German", "region": "Switzerland", "priority": "HIGH"},
                {"locale": "en-US", "language": "English", "region": "United States", "priority": "HIGH"}
            ])
        elif detected_lang == "es":
            suggestions.extend([
                {"locale": "es-ES", "language": "Spanish", "region": "Spain", "priority": "PRIMARY"},
                {"locale": "es-MX", "language": "Spanish", "region": "Mexico", "priority": "HIGH"},
                {"locale": "es-AR", "language": "Spanish", "region": "Argentina", "priority": "MEDIUM"},
                {"locale": "en-US", "language": "English", "region": "United States", "priority": "HIGH"}
            ])
        else:
            suggestions.extend([
                {"locale": "en-US", "language": "English", "region": "United States", "priority": "PRIMARY"},
                {"locale": "en-GB", "language": "English", "region": "United Kingdom", "priority": "HIGH"}
            ])
        return suggestions

    def _analyze_hreflang(self, existing_hreflang: List[Dict], url: str) -> Dict[str, Any]:
        """Analyze existing hreflang implementation."""
        if not existing_hreflang:
            return {
                "status": "NO_HREFLANG_FOUND",
                "hreflang_tags": [],
                "issues": ["No hreflang tags found - implement for international targeting"],
                "recommendations": [
                    "Add hreflang tags for all language/locale variants",
                    "Include self-referencing hreflang tag",
                    "Add x-default hreflang for fallback"
                ]
            }

        issues = []
        locales_found = [h.get("locale", "") for h in existing_hreflang]
        has_self_referencing = any(url in h.get("url", "") for h in existing_hreflang)
        has_x_default = "x-default" in locales_found

        if not has_self_referencing:
            issues.append("Missing self-referencing hreflang tag")
        if not has_x_default:
            issues.append("Missing x-default hreflang tag for fallback")
        if len(locales_found) != len(set(locales_found)):
            issues.append("Duplicate hreflang locale tags found")

        return {
            "status": "HREFLANG_FOUND" if existing_hreflang else "NO_HREFLANG_FOUND",
            "hreflang_tags": existing_hreflang,
            "total_hreflang_tags": len(existing_hreflang),
            "locales_covered": locales_found,
            "has_self_referencing": has_self_referencing,
            "has_x_default": has_x_default,
            "issues": issues,
            "issue_count": len(issues),
            "implementation_quality": "GOOD" if not issues else "NEEDS_FIXES"
        }

    def _assess_locale_targeting(self, target_locales: List[Dict], url: str) -> Dict[str, Any]:
        """Assess locale targeting strategy."""
        return {
            "target_locales": target_locales,
            "total_target_locales": len(target_locales),
            "targeting_strategy": "subdirectory" if "/en/" in url or "/fr/" in url else "subdomain_or_tld",
            "geo_targeting_recommendation": "Use CDN-based geo-redirects with hreflang for best results",
            "locale_url_structure": {
                "recommended": "/{lang}/page-slug or /{lang}-{country}/page-slug",
                "alternative": "https://{subdomain}.{domain}/page-slug",
                "tld_approach": "https://{domain}.{tld}/page-slug"
            }
        }

    def _map_entities_for_localization(self, content: str, title: str) -> Dict[str, Any]:
        """Map entities that need localization."""
        brand_names = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', content or title or "")
        unique_brands = list(set(brand_names))[:20]
        return {
            "entities_detected": unique_brands,
            "entity_count": len(unique_brands),
            "localization_requirements": [
                "Brand names may need transliteration for non-Latin scripts",
                "Product names may need adaptation for local markets",
                "Technical terms may need translation or explanation",
                "Acronyms may need expansion in translation"
            ],
            "entity_consistency_check": "Verify brand name consistency across all locale versions"
        }

    def _prioritize_translation(self, content: str, title: str) -> Dict[str, Any]:
        """Prioritize content elements for translation."""
        word_count = len(content.split()) if content else 0
        return {
            "translation_priority_tiers": [
                {
                    "tier": "TIER_1_CRITICAL",
                    "elements": ["Title tag", "Meta description", "H1 heading", "First paragraph"],
                    "reason": "Most visible in SERPs and highest impact on CTR",
                    "estimated_effort": "1-2 hours per locale"
                },
                {
                    "tier": "TIER_2_HIGH",
                    "elements": ["H2 headings", "Image alt text", "Schema markup"],
                    "reason": "Important for SEO and accessibility",
                    "estimated_effort": "2-3 hours per locale"
                },
                {
                    "tier": "TIER_3_MEDIUM",
                    "elements": ["Body content", "Bullet points", "Internal link anchor text"],
                    "reason": "Core content that users read",
                    "estimated_effort": f"{max(1, word_count // 500)} hours per locale"
                },
                {
                    "tier": "TIER_4_LOW",
                    "elements": ["Footer content", "Sidebar widgets", "Comments section"],
                    "reason": "Lower priority but still relevant for full localization",
                    "estimated_effort": "1-2 hours per locale"
                }
            ],
            "total_word_count": word_count,
            "estimated_total_translation_time": f"{max(2, word_count // 250)} hours per locale"
        }

    def _configure_international_seo(self, url: str, target_locales: List[Dict]) -> Dict[str, Any]:
        """Configure international SEO settings."""
        return {
            "hreflang_implementation": {
                "method": "HTML link tags in <head> or XML sitemap",
                "self_referencing": "Required for each locale page",
                "reciprocal": "All pages must link back to each other",
                "x_default": "Required - specify fallback locale"
            },
            "cdn_locale_serving": {
                "method": "Accept-Language header detection",
                "fallback": "x-default hreflang locale",
                "override": "User can manually select locale",
                "cookie_persist": "Store locale preference in cookie"
            },
            "schema_localization": {
                "inLanguage": "Add to Article/BlogPosting schema",
                "contentLocale": "Specify content locale in schema",
                "availableLanguage": "List all available language versions"
            },
            "monitoring_per_locale": {
                "gsc_setup": "Add property for each locale subdomain/subdirectory",
                "tracking": "Monitor organic traffic, rankings, and conversions per locale",
                "reporting": "Compare locale performance monthly"
            }
        }

    def _generate_recommendations(self, hreflang: Dict, locale: Dict, entity: Dict) -> List[Dict[str, str]]:
        """Generate localization recommendations."""
        recs = []
        if hreflang.get("status") == "NO_HREFLANG_FOUND":
            recs.append({
                "priority": "HIGH",
                "action": "Implement hreflang tags for all locale variants",
                "detail": "No hreflang implementation found - critical for international SEO"
            })
        if hreflang.get("issue_count", 0) > 0:
            recs.append({
                "priority": "HIGH",
                "action": f"Fix {hreflang['issue_count']} hreflang implementation issues",
                "detail": "Hreflang errors can cause indexing issues across locales"
            })
        recs.append({
            "priority": "MEDIUM",
            "action": "Localize title tags and meta descriptions per locale",
            "detail": "Translation of body content alone is insufficient for local SEO"
        })
        recs.append({
            "priority": "MEDIUM",
            "action": "Add inLanguage property to structured data schema",
            "detail": "Schema localization helps search engines serve correct locale in results"
        })
        return recs
