"""
Module 19: Global Localization & Hreflang Entity Synchronizer
Handles localized transcreation and hreflang management.
"""
import re
from typing import List, Dict, Any


class LocalizationSync:
    """Module 19: Global Localization & Hreflang Entity Synchronizer"""

    def __init__(self):
        self.module_id = "M19"
        self.module_name = "Global Localization & Hreflang Entity Synchronizer"

    def analyze(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Full localization analysis pipeline."""
        content = inputs.get("content", "")
        source_locale = inputs.get("source_locale", "en-US")
        target_locales = inputs.get("target_locales", [])
        entity = inputs.get("primary_entity", "")

        entity_mapping = self._map_entities_for_locale(entity, target_locales)
        hreflang_config = self._generate_hreflang_config(inputs)
        currency_conversion = self._generate_currency_conversion(content, target_locales)
        regulatory_mapping = self._map_regulations(entity, target_locales)
        translation_guidelines = self._generate_translation_guidelines(inputs)
        localized_schema = self._generate_localized_schema(inputs, entity_mapping)

        return {
            "module": self.module_id,
            "module_name": self.module_name,
            "entity_mapping": entity_mapping,
            "hreflang_configuration": hreflang_config,
            "currency_conversion": currency_conversion,
            "regulatory_mapping": regulatory_mapping,
            "translation_guidelines": translation_guidelines,
            "localized_schema": localized_schema,
            "implementation_checklist": self._generate_checklist(hreflang_config, entity_mapping),
            "recommendations": self._generate_recommendations(entity_mapping, hreflang_config, regulatory_mapping),
            "implementation_steps": [
                "Step 1: Finalize target locale list and confirm URL structure (subdirectory /de/, /fr/ or subdomain de.example.com)",
                "Step 2: Generate hreflang XML sitemap using the provided configuration and validate with an hreflang testing tool",
                "Step 3: Insert hreflang link tags in the <head> of each localized page for each alternate version",
                "Step 4: Map all entity references (regulations, certifications, brand names) per locale using the entity mapping data",
                "Step 5: Replace U.S.-centric regulations with local equivalents (e.g., SEC to BaFin for de-DE, FCA for en-GB)",
                "Step 6: Convert all currency values to local formats using current exchange rates and locale-specific formatting",
                "Step 7: Adapt date formats, measurement systems (metric/imperial), and number formatting per locale",
                "Step 8: Configure localized JSON-LD schema markup with correct inLanguage and locale-specific keywords",
                "Step 9: Submit localized sitemaps to GSC and Bing Webmaster Tools for each language version",
                "Step 10: Have native speakers review all transcreated content for fluency and cultural accuracy",
                "Step 11: Test hreflang implementation using Aleyda Solis hreflang tag checker or similar tool",
                "Step 12: Set up monitoring for international ranking performance per locale in GSC"
            ],
            "where_to_add": [
                "Place hreflang link tags in <head> of each localized page via <link rel='alternate' hreflang='...'> tags",
                "Add localized JSON-LD schema in <head> via <script type='application/ld+json'> with inLanguage field",
                "Insert localized currency and date formats inline within body content",
                "Place localized regulatory references in relevant body sections (not just footnotes)",
                "Add x-default hreflang tag in <head> pointing to the primary language version",
                "Configure localized meta titles and descriptions in <head> for each locale version",
                "Place localized open graph tags in <head> for correct social sharing per region",
                "Add localized image alt text and file names for region-specific visual assets",
                "Configure locale-specific sitemaps and submit each to search engine webmaster tools",
                "Place culturally adapted internal links within body content pointing to locale-relevant pages"
            ],
            "detailed_analysis": {
                "localization_benchmarks": {
                    "hreflang_implementation_accuracy_target": "100% bi-directional tags with no orphan references",
                    "transcreation_vs_translation_success_rate": "Transcreated content outperforms literal translation by 30-50% in engagement",
                    "localized_content_ranking_lift": "Properly localized pages rank 20-40% better in local SERPs vs. untranslated",
                    "typical_international_traffic_increase": "50-200% organic traffic increase from proper hreflang implementation",
                    "localized_schema_rich_results_rate": "Localized schema increases rich results eligibility by 15-25% in target markets"
                },
                "regulatory_compliance_benchmarks": {
                    "eu_gdpr_equivalents": "DSGVO (de-DE), RGPD (fr-FR), UK GDPR (en-GB) - all require local language references",
                    "financial_regulatory_swaps": "SEC to BaFin/FCA/AMF depending on target market",
                    "data_privacy_localization": "CCPA becomes local privacy law equivalents - must be accurate per jurisdiction",
                    "certification_localization": "SOC 2 becomes ISO 27001, Cyber Essentials, or ISMAP depending on region",
                    "penalty_for_incorrect_regulatory_reference": "Loss of trust signals and potential legal exposure in regulated industries"
                },
                "expert_recommendations": [
                    "Use transcreation (meaning-based adaptation) rather than literal translation for marketing content",
                    "Always verify regulatory references with local legal counsel - automated mapping is a starting point only",
                    "Implement hreflang before launching localized content to prevent duplicate content penalties",
                    "Use dynamic currency conversion based on user geolocation for e-commerce content",
                    "Build locale-specific content clusters with internal linking between related localized pages"
                ],
                "common_mistakes": [
                    "Missing reciprocal hreflang tags (A references B, but B does not reference A back)",
                    "Using machine translation without native speaker review leads to unnatural, low-trust content",
                    "Forgetting to localize schema markup - inLanguage field and locale-specific keywords matter",
                    "Not including x-default hreflang tag which tells search engines which version to show globally",
                    "Ignoring cultural differences in formality, humor, and examples that affect user engagement"
                ],
                "success_metrics": [
                    "Track international organic traffic growth per locale in GSC (target: 50%+ increase)",
                    "Monitor hreflang implementation errors in GSC International Targeting report (target: 0 errors)",
                    "Measure bounce rate comparison between localized vs. non-localized pages (target: lower bounce)",
                    "Track local keyword rankings in each target market (target: top 10 for priority terms)",
                    "Monitor conversion rate per locale to validate localization effectiveness"
                ]
            }
        }

    def _map_entities_for_locale(self, entity: str, locales: List[str]) -> Dict[str, Any]:
        """Map entities to localized equivalents."""
        locale_entities = {}
        regulatory_swaps = {
            "en-GB": {"SEC": "FCA", "GDPR": "GDPR", "SOC 2": "Cyber Essentials"},
            "de-DE": {"SEC": "BaFin", "GDPR": "DSGVO", "SOC 2": "ISO 27001"},
            "fr-FR": {"SEC": "AMF", "GDPR": "RGPD", "SOC 2": "HDS"},
            "ja-JP": {"SEC": "FSA Japan", "GDPR": "APPI", "SOC 2": "ISMAP"},
            "en-AU": {"SEC": "ASIC", "GDPR": "Privacy Act", "SOC 2": "IRAP"},
        }
        for locale in locales:
            swaps = regulatory_swaps.get(locale, {})
            locale_entities[locale] = {
                "entity_name": entity,
                "localized_regulations": swaps,
                "currency": self._get_currency_for_locale(locale),
                "measurement_system": "metric" if locale not in ["en-US"] else "imperial",
                "date_format": self._get_date_format(locale),
                "formality_level": "formal" if locale in ["ja-JP", "de-DE", "fr-FR"] else "conversational"
            }
        return {
            "source_locale": "en-US",
            "target_locales": locales,
            "locale_entities": locale_entities,
            "total_locales": len(locales)
        }

    def _get_currency_for_locale(self, locale: str) -> Dict[str, str]:
        """Get currency for locale."""
        currencies = {
            "en-US": {"code": "USD", "symbol": "$", "format": "$X,XXX"},
            "en-GB": {"code": "GBP", "symbol": "\u00a3", "format": "\u00a3X,XXX"},
            "en-AU": {"code": "AUD", "symbol": "A$", "format": "A$X,XXX"},
            "en-CA": {"code": "CAD", "symbol": "C$", "format": "C$X,XXX"},
            "en-IN": {"code": "INR", "symbol": "\u20b9", "format": "\u20b9X,XXX"},
            "de-DE": {"code": "EUR", "symbol": "\u20ac", "format": "X.XXX\u20ac"},
            "fr-FR": {"code": "EUR", "symbol": "\u20ac", "format": "X XXX\u20ac"},
            "ja-JP": {"code": "JPY", "symbol": "\u00a5", "format": "\u00a5X,XXX"},
            "zh-CN": {"code": "CNY", "symbol": "\u00a5", "format": "\u00a5X,XXX"},
        }
        return currencies.get(locale, {"code": "USD", "symbol": "$", "format": "$X,XXX"})

    def _get_date_format(self, locale: str) -> str:
        """Get date format for locale."""
        formats = {
            "en-US": "MM/DD/YYYY",
            "en-GB": "DD/MM/YYYY",
            "de-DE": "DD.MM.YYYY",
            "fr-FR": "DD/MM/YYYY",
            "ja-JP": "YYYY年MM月DD日",
            "zh-CN": "YYYY年MM月DD日",
        }
        return formats.get(locale, "YYYY-MM-DD")

    def _generate_hreflang_config(self, inputs: Dict) -> Dict[str, Any]:
        """Generate hreflang XML configuration."""
        base_url = inputs.get("base_url", "")
        source_locale = inputs.get("source_locale", "en-US")
        target_locales = inputs.get("target_locales", [])
        url_path = inputs.get("url_path", "")
        hreflang_tags = []
        hreflang_tags.append({
            "locale": source_locale,
            "url": f"{base_url}/{url_path}",
            "rel": "alternate",
            "type": "hreflang"
        })
        for locale in target_locales:
            lang_code = locale.split("-")[0]
            hreflang_tags.append({
                "locale": locale,
                "url": f"{base_url}/{lang_code}/{url_path}",
                "rel": "alternate",
                "type": "hreflang"
            })
        hreflang_tags.append({
            "locale": "x-default",
            "url": f"{base_url}/{url_path}",
            "rel": "alternate",
            "type": "hreflang"
        })
        xml_content = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"\n  xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
        all_urls = [f"{base_url}/{url_path}"] + [f"{base_url}/{locale.split('-')[0]}/{url_path}" for locale in target_locales]
        for url in all_urls:
            xml_content += '  <url>\n'
            xml_content += f'    <loc>{url}</loc>\n'
            for tag in hreflang_tags:
                xml_content += f'    <xhtml:link rel="alternate" hreflang="{tag["locale"]}" href="{tag["url"]}"/>\n'
            xml_content += '  </url>\n'
        xml_content += '</urlset>'
        return {
            "hreflang_tags": hreflang_tags,
            "xml_content": xml_content,
            "total_tags": len(hreflang_tags),
            "bi_directional": True,
            "x_default_included": True,
            "validation": "Use hreflang tag checker tool before deployment"
        }

    def _generate_currency_conversion(self, content: str, locales: List[str]) -> Dict[str, Any]:
        """Generate currency conversion specifications."""
        price_patterns = re.findall(r'\$(\d+(?:,\d{3})*(?:\.\d+)?)', content)
        conversions = []
        for locale in locales:
            currency = self._get_currency_for_locale(locale)
            for price in price_patterns[:5]:
                conversions.append({
                    "locale": locale,
                    "original": f"${price}",
                    "currency_code": currency["code"],
                    "note": "Convert using current exchange rates at time of localization"
                })
        return {
            "prices_found": len(price_patterns),
            "conversions_needed": conversions,
            "recommendation": "Use dynamic currency conversion based on user geolocation"
        }

    def _map_regulations(self, entity: str, locales: List[str]) -> Dict[str, Any]:
        """Map regulations across locales."""
        regulation_map = {
            "en-US": ["SEC", "FTC", "SOC 2", "CCPA", "HIPAA"],
            "en-GB": ["FCA", "ICO", "Cyber Essentials", "UK GDPR"],
            "de-DE": ["BaFin", "DSGVO", "BSI", "EU GDPR"],
            "fr-FR": ["AMF", "CNIL", "RGPD", "HDS"],
            "ja-JP": ["FSA Japan", "APPI", "ISMAP", "PPC"],
            "en-AU": ["ASIC", "OAIC", "Privacy Act 1988", "IRAP"],
        }
        return {
            "regulation_map": {locale: regulation_map.get(locale, ["Local regulations apply"]) for locale in locales},
            "compliance_notes": "Replace U.S.-centric regulations with local equivalents during transcreation"
        }

    def _generate_translation_guidelines(self, inputs: Dict) -> Dict[str, Any]:
        """Generate transcreation guidelines."""
        return {
            "transcreation_approach": "Meaning-based, not word-for-word translation",
            "guidelines": [
                "Preserve SEO intent - translate keywords, not just words",
                "Adapt examples and statistics to local market",
                "Replace U.S.-centric references with local equivalents",
                "Maintain brand voice while adapting formality level",
                "Localize date, currency, and measurement formats",
                "Verify all regulatory references are locally accurate",
                "Test readability with native speakers in target market"
            ],
            "quality_checks": [
                "Native speaker review for fluency",
                "SEO keyword validation in target language",
                "Regulatory accuracy verification",
                "Cultural sensitivity review",
                "Brand consistency check"
            ]
        }

    def _generate_localized_schema(self, inputs: Dict, entity_mapping: Dict) -> Dict[str, Any]:
        """Generate localized schema markup."""
        schemas = {}
        for locale, data in entity_mapping.get("locale_entities", {}).items():
            lang = locale.split("-")[0]
            schemas[locale] = {
                "@context": "https://schema.org",
                "@type": "TechArticle",
                "inLanguage": locale,
                "keywords": f"{inputs.get('primary_entity', '')} {lang}",
                "about": {
                    "@type": "Thing",
                    "name": inputs.get("primary_entity", "")
                }
            }
        return {
            "localized_schemas": schemas,
            "total_schemas": len(schemas),
            "implementation": "Place in <head> of each localized page"
        }

    def _generate_checklist(self, hreflang: Dict, entities: Dict) -> List[Dict[str, str]]:
        """Generate implementation checklist."""
        return [
            {"task": f"Generate hreflang XML for {entities['total_locales']} locales", "priority": "HIGH", "deadline": "Day 1"},
            {"task": "Validate hreflang tags with testing tool", "priority": "HIGH", "deadline": "Day 1"},
            {"task": "Map all entity references per locale", "priority": "HIGH", "deadline": "Day 2"},
            {"task": "Configure localized schema markup", "priority": "MEDIUM", "deadline": "Day 3"},
            {"task": "Submit localized sitemaps to search engines", "priority": "HIGH", "deadline": "Day 5"},
            {"task": "Verify hreflang implementation across all locales", "priority": "HIGH", "deadline": "Week 1"}
        ]

    def _generate_recommendations(self, entities: Dict, hreflang: Dict, regulations: Dict) -> List[Dict[str, str]]:
        """Generate localization recommendations."""
        recs = []
        if entities.get("total_locales", 0) > 0:
            recs.append({
                "priority": "HIGH",
                "action": f"Implement hreflang for {entities['total_locales']} target locales",
                "detail": "Prevents duplicate content penalties across regional sites"
            })
        recs.append({
            "priority": "HIGH",
            "action": "Replace U.S.-centric regulations with local equivalents",
            "detail": "Regulatory mapping identified for all target locales"
        })
        recs.append({
            "priority": "MEDIUM",
            "action": "Use transcreation, not translation, for content localization",
            "detail": "Maintains SEO intent and cultural relevance"
        })
        return recs
