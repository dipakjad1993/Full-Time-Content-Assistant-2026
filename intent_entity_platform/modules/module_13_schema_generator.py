"""
Module 13: Multi-Search Engine Schema Payload Generator
Generates deeply nested, entity-rich JSON-LD schema for all search engines.
"""
import re
import json
from typing import List, Dict, Any, Optional
from ..utils.text_analytics import schema_json_ld_validate


class SchemaPayloadGenerator:
    """Module 13: Multi-Search Engine Schema Payload Generator"""

    def __init__(self):
        self.module_id = "M13"
        self.module_name = "Multi-Search Engine Schema Payload Generator"

    def analyze(self, inputs: Dict[str, Any], outline: Dict = None, entity_graph: Dict = None) -> Dict[str, Any]:
        """Full schema generation pipeline."""
        entity = inputs.get("primary_entity", "")
        seed = inputs.get("seed_phrase", "")
        author = inputs.get("author", {})
        publisher = inputs.get("publisher", {})
        url = inputs.get("url", "")
        url_data = inputs.get("_url_data", None)

        real_schema_analysis = {}
        if url_data:
            real_schema_analysis = self._analyze_url_schema(url_data, inputs)

        article_schema = self._generate_article_schema(inputs, outline, entity_graph)
        faq_schema = self._generate_faq_schema(inputs, outline)
        howto_schema = self._generate_howto_schema(inputs, outline)
        product_schema = self._generate_product_schema(inputs)
        author_schema = self._generate_author_schema(author)
        publisher_schema = self._generate_publisher_schema(publisher)
        breadcrumb_schema = self._generate_breadcrumb_schema(inputs)
        itemlist_schema = self._generate_itemlist_schema(inputs, outline)
        video_schema = self._generate_video_schema(inputs)
        org_schema = self._generate_organization_schema(publisher)

        schemas = {
            "article": article_schema,
            "faq": faq_schema,
            "howto": howto_schema,
            "product": product_schema,
            "author": author_schema,
            "publisher": publisher_schema,
            "breadcrumb": breadcrumb_schema,
            "itemlist": itemlist_schema,
            "video": video_schema,
            "organization": org_schema
        }
        validation_results = {}
        for name, schema in schemas.items():
            if schema:
                errors = schema_json_ld_validate(schema)
                validation_results[name] = {"valid": len(errors) == 0, "errors": errors}

        nested_schema = self._build_nested_entity_schema(schemas, entity_graph)
        return {
            "module": self.module_id,
            "module_name": self.module_name,
            "schemas": schemas,
            "nested_entity_schema": nested_schema,
            "url_schema_analysis": real_schema_analysis,
            "validation_results": validation_results,
            "implementation_guide": self._generate_implementation_guide(schemas, validation_results),
            "search_engine_coverage": self._assess_search_engine_coverage(schemas),
            "recommendations": self._generate_recommendations(schemas, validation_results),
            "implementation_steps": [
                "Step 1: Generate article schema with author, publisher, and entity references",
                "Step 2: Create FAQPage schema from H2/H3 question-and-answer sections",
                "Step 3: Build HowTo schema for implementation or step-by-step content sections",
                "Step 4: Add breadcrumb schema for site navigation structure",
                "Step 5: Generate author and publisher schemas with social profiles and credentials",
                "Step 6: Create nested entity schema using @id references for cross-schema linking",
                "Step 7: Validate all schemas using Google Rich Results Test and Schema.org validator",
                "Step 8: Place each schema in its own <script type='application/ld+json'> tag in <head>",
                "Step 9: Test rich result eligibility in Google Search Console",
                "Step 10: Monitor schema performance and update dateModified on content refreshes"
            ],
            "where_to_add": [
                "Place all JSON-LD schema in <head> section using <script type='application/ld+json'> tags",
                "Add article schema as the first schema tag for primary content identification",
                "Place FAQPage schema near the actual FAQ section in HTML for consistency",
                "Add HowTo schema corresponding to step-by-step content sections",
                "Include breadcrumb schema to match visible navigation breadcrumbs",
                "Place author schema linking to author bio section or About page",
                "Add publisher schema referencing site-wide organization information",
                "Include nested entity schema with @id references for entity linking",
                "Add video schema near embedded video elements",
                "Place product schema near pricing or product description sections"
            ],
            "detailed_analysis": {
                "industry_benchmarks": {
                    "schema_adoption_rate": "72% of top-ranking pages use structured data markup",
                    "rich_results_eligibility": "Pages with schema are 35% more likely to appear in rich results",
                    "faq_schema_impact": "FAQ schema increases AI Overview citation probability by 25%",
                    "article_schema_coverage": "90% of news and blog content should have Article schema",
                    "validation_error_rate": "Average website has 2-4 schema validation errors"
                },
                "statistical_ranges": {
                    "optimal_schema_count": "3-5 schema types per page for comprehensive coverage",
                    "schema_size_limit": "Each schema block should be under 1KB for optimal parsing",
                    "entity_reference_depth": "2-3 levels of @id references for entity linking",
                    "faq_items_per_page": "5-10 FAQ items for optimal rich result display",
                    "howto_steps_optimal": "5-9 steps for HowTo rich results"
                },
                "expert_recommendations": [
                    "Use nested entity schema with @id references to link author, publisher, and main entity",
                    "Include all relevant schema types (Article, FAQ, HowTo, Breadcrumb) for maximum coverage",
                    "Validate schemas before deployment using Google Rich Results Test",
                    "Update dateModified field on every content refresh for freshness signals",
                    "Add sameAs references to knowledge graph URIs for entity disambiguation",
                    "Test schema rendering across different search engines (Google, Bing, Perplexity)",
                    "Monitor Search Console for schema errors and rich result appearance"
                ],
                "common_mistakes_to_avoid": [
                    "Placing multiple schemas in a single <script> tag instead of separate tags",
                    "Not validating schema syntax before deployment",
                    "Missing required properties (headline, author, datePublished for Article)",
                    "Using incorrect schema types for content (e.g., Product for non-product content)",
                    "Not updating dateModified when content is refreshed",
                    "Forgetting to add @id references for entity linking across schemas",
                    "Ignoring schema errors in Search Console"
                ],
                "success_metrics_to_track": [
                    "Rich result appearance rate in Google Search Console",
                    "Schema validation error count (target: 0 errors)",
                    "Click-through rate improvement from rich results",
                    "AI Overview citation rate for schema-marked content",
                    "Schema coverage percentage across site pages",
                    "Search engine coverage score across Google, Bing, Perplexity",
                    "Entity recognition accuracy in search results"
                ]
            }
        }

    def _analyze_url_schema(self, url_data: Dict, inputs: Dict) -> Dict[str, Any]:
        """Generate schema markup from actual page content and validate against requirements."""
        page_text = url_data.get("page_text", "")
        title = url_data.get("title", "")
        meta_desc = url_data.get("meta_description", "")
        h1 = url_data.get("h1", "")
        h2s = url_data.get("h2s", [])
        word_count = url_data.get("word_count", 0)
        image_count = url_data.get("image_count", 0)
        images = url_data.get("images", [])
        link_count = url_data.get("link_count", 0)
        has_schema = url_data.get("has_schema", False)
        url = url_data.get("url", "")
        entity = inputs.get("primary_entity", "")

        # Generate Article schema from actual page data
        article_schema_from_page = {
            "@context": "https://schema.org",
            "@type": "TechArticle",
            "headline": title or inputs.get("headline", ""),
            "description": meta_desc or "",
            "author": {
                "@type": "Person",
                "name": inputs.get("author", {}).get("name", "[Author Name]")
            },
            "publisher": {
                "@type": "Organization",
                "name": inputs.get("publisher", {}).get("name", "[Publisher Name]")
            },
            "url": url,
            "datePublished": inputs.get("publish_date", ""),
            "dateModified": inputs.get("modified_date", ""),
            "mainEntityOfPage": {"@type": "WebPage", "@id": url},
            "about": {"@type": "Thing", "name": entity},
            "wordCount": word_count,
            "inLanguage": "en-US",
            "isAccessibleForFree": True
        }

        # Generate FAQ schema from H2/H3 question headings
        faq_items = []
        for h2 in h2s:
            if "?" in h2:
                faq_items.append({
                    "@type": "Question",
                    "name": h2,
                    "acceptedAnswer": {
                        "@type": "Answer",
                        "text": f"[Answer to '{h2}' - requires 40-60 word response from page content]"
                    }
                })
        faq_schema = {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": faq_items
        } if faq_items else None

        # Generate HowTo schema if step/process content detected
        howto_steps = []
        for i, h2 in enumerate(h2s[:10]):
            if any(kw in h2.lower() for kw in ["step", "how to", "implement", "setup", "configure", "guide"]):
                howto_steps.append({
                    "@type": "HowToStep",
                    "name": h2,
                    "text": f"[Detailed description of {h2} - extract from page content]",
                    "position": len(howto_steps) + 1
                })
        howto_schema = {
            "@context": "https://schema.org",
            "@type": "HowTo",
            "name": f"How to Implement {entity}" if entity else "Implementation Guide",
            "description": f"Step-by-step guide to {entity}" if entity else "",
            "step": howto_steps
        } if howto_steps else None

        # Generate Breadcrumb schema from URL
        url_parts = url.replace("https://", "").replace("http://", "").split("/") if url else []
        breadcrumb_items = [{"@type": "ListItem", "position": 1, "name": "Home", "item": "/"}]
        for i, part in enumerate(url_parts[1:] if len(url_parts) > 1 else []):
            if part:
                breadcrumb_items.append({
                    "@type": "ListItem",
                    "position": len(breadcrumb_items) + 1,
                    "name": part.replace("-", " ").replace("_", " ").title(),
                    "item": f"/{part}"
                })
        breadcrumb_schema = {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": breadcrumb_items
        }

        # ImageObject schemas for actual images
        image_schemas = []
        for i, img in enumerate(images[:10]):
            img_schema = {
                "@context": "https://schema.org",
                "@type": "ImageObject",
                "contentUrl": img.get("src", ""),
                "description": img.get("alt", ""),
                "name": img.get("alt", f"Image {i+1}")
            }
            image_schemas.append(img_schema)

        # Content structure validation
        schema_completeness = {
            "title_available": bool(title),
            "title_length_ok": 30 <= len(title) <= 70 if title else False,
            "meta_desc_available": bool(meta_desc),
            "meta_desc_length_ok": 120 <= len(meta_desc) <= 160 if meta_desc else False,
            "h1_available": bool(h1),
            "h2_count": len(h2s),
            "h2_count_ok": len(h2s) >= 3,
            "word_count_ok": word_count >= 500,
            "image_count": image_count,
            "faq_questions_found": len(faq_items),
            "howto_steps_found": len(howto_steps),
            "schema_already_present": has_schema
        }

        # Missing schema types
        missing_schemas = []
        if not faq_schema and len(h2s) >= 3:
            missing_schemas.append("FAQPage - add FAQ section with question headings")
        if not howto_schema:
            missing_schemas.append("HowTo - add step-by-step implementation content")
        if not has_schema:
            missing_schemas.append("Article - no structured data currently on page")

        # Schema generation recommendations
        schema_recommendations = []
        if not title:
            schema_recommendations.append({
                "priority": "CRITICAL",
                "action": "Add title tag - required for Article schema headline",
                "detail": "Headline property cannot be empty"
            })
        if not meta_desc:
            schema_recommendations.append({
                "priority": "HIGH",
                "action": "Add meta description - required for Article schema description",
                "detail": "Description property should be 120-160 characters"
            })
        if len(h2s) < 3:
            schema_recommendations.append({
                "priority": "MEDIUM",
                "action": f"Add more H2 headings (current: {len(h2s)}) for FAQ/HowTo schema",
                "detail": "Question-format H2s enable FAQPage schema"
            })
        if image_count > 0 and not has_schema:
            schema_recommendations.append({
                "priority": "MEDIUM",
                "action": f"Add ImageObject schema for {image_count} images on page",
                "detail": "Image schemas enable rich results in image search"
            })
        if word_count < 500:
            schema_recommendations.append({
                "priority": "MEDIUM",
                "action": f"Expand content (current: {word_count} words) for comprehensive Article schema",
                "detail": "Longer content supports richer schema properties"
            })

        return {
            "page_url": url,
            "page_title": title,
            "content_word_count": word_count,
            "schemas_generated_from_page": {
                "article_schema": article_schema_from_page,
                "faq_schema": faq_schema,
                "howto_schema": howto_schema,
                "breadcrumb_schema": breadcrumb_schema,
                "image_schemas": image_schemas[:10]
            },
            "schema_completeness_check": schema_completeness,
            "content_readiness_for_schema": {
                "score": round(sum(1 for v in schema_completeness.values() if v) / max(1, len(schema_completeness)), 3),
                "verdict": (
                    "READY - All schema properties can be populated from page content" if sum(1 for v in schema_completeness.values() if v) >= 8
                    else "PARTIALLY_READY - Some schema properties missing" if sum(1 for v in schema_completeness.values() if v) >= 5
                    else "NOT_READY - Significant content gaps for schema generation"
                )
            },
            "faq_schema_readiness": {
                "questions_found": len(faq_items),
                "eligible_for_faq_schema": len(faq_items) >= 2,
                "questions": [q["name"] for q in faq_items[:10]]
            },
            "howto_schema_readiness": {
                "steps_found": len(howto_steps),
                "eligible_for_howto_schema": len(howto_steps) >= 2,
                "steps": [s["name"] for s in howto_steps[:10]]
            },
            "image_schema_readiness": {
                "images_on_page": image_count,
                "images_with_alt": sum(1 for img in images if img.get("alt", "").strip()),
                "schemas_to_generate": len(image_schemas),
                "ready_for_image_schema": image_count > 0
            },
            "missing_schemas": missing_schemas,
            "schema_recommendations": schema_recommendations,
            "existing_schema_detected": has_schema
        }

    def _generate_article_schema(self, inputs: Dict, outline: Dict, entity_graph: Dict) -> Dict[str, Any]:
        """Generate article schema."""
        entity = inputs.get("primary_entity", "")
        author = inputs.get("author", {})
        publisher = inputs.get("publisher", {})
        url = inputs.get("url", "")
        schema = {
            "@context": "https://schema.org",
            "@type": "TechArticle",
            "headline": inputs.get("headline", f"Complete Guide to {entity}"),
            "description": inputs.get("description", f"Comprehensive guide covering {entity} features, benefits, and implementation."),
            "author": {
                "@type": "Person",
                "name": author.get("name", "[Author Name]"),
                "jobTitle": author.get("title", "[Author Title]"),
                "sameAs": author.get("social_profiles", []),
                "knowsAbout": entity
            },
            "publisher": {
                "@type": "Organization",
                "name": publisher.get("name", "[Publisher Name]"),
                "logo": {
                    "@type": "ImageObject",
                    "url": publisher.get("logo_url", "[Logo URL]")
                }
            },
            "datePublished": inputs.get("publish_date", ""),
            "dateModified": inputs.get("modified_date", ""),
            "mainEntityOfPage": {
                "@type": "WebPage",
                "@id": url
            },
            "about": {
                "@type": "Thing",
                "name": entity,
                "sameAs": entity_graph.get("knowledge_graph_uris", {}).get("wikidata", "") if entity_graph else ""
            },
            "mentions": [
                {"@type": "Thing", "name": r["name"]}
                for r in (entity_graph or {}).get("related_entities", [])[:10]
            ],
            "keywords": inputs.get("seed_phrase", ""),
            "articleSection": "Technology",
            "wordCount": (outline or {}).get("structural_metrics", {}).get("total_estimated_word_count", 2500),
            "inLanguage": "en-US",
            "isAccessibleForFree": True,
            "image": inputs.get("hero_image_url", "")
        }
        return schema

    def _generate_faq_schema(self, inputs: Dict, outline: Dict) -> Dict[str, Any]:
        """Generate FAQ schema."""
        entity = inputs.get("primary_entity", "")
        faq_items = []
        faq_section = None
        for section in (outline or {}).get("h2_sections", []):
            if "faq" in section.get("title", "").lower():
                faq_section = section
                break
        if faq_section:
            for h3 in faq_section.get("h3_subsections", [])[:10]:
                question = h3.get("title", "")
                if "?" in question:
                    faq_items.append({
                        "@type": "Question",
                        "name": question,
                        "acceptedAnswer": {
                            "@type": "Answer",
                            "text": f"[Answer to '{question}' - 40-60 word response required]"
                        }
                    })
        if not faq_items:
            default_questions = [
                f"What is {entity}?",
                f"How much does {entity} cost?",
                f"What are the benefits of {entity}?",
                f"How do you implement {entity}?",
                f"What are the best {entity} alternatives?"
            ]
            for q in default_questions:
                faq_items.append({
                    "@type": "Question",
                    "name": q,
                    "acceptedAnswer": {
                        "@type": "Answer",
                        "text": f"[40-60 word answer to '{q}']"
                    }
                })
        return {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": faq_items
        }

    def _generate_howto_schema(self, inputs: Dict, outline: Dict) -> Dict[str, Any]:
        """Generate HowTo schema."""
        entity = inputs.get("primary_entity", "")
        steps = []
        howto_section = None
        for section in (outline or {}).get("h2_sections", []):
            if "implement" in section.get("title", "").lower() or "step" in section.get("title", "").lower():
                howto_section = section
                break
        if howto_section:
            for i, h3 in enumerate(howto_section.get("h3_subsections", [])[:10]):
                steps.append({
                    "@type": "HowToStep",
                    "name": h3.get("title", f"Step {i+1}"),
                    "text": f"[Detailed description of {h3.get('title', f'Step {i+1}')} - include specific actions and expected outcomes]",
                    "position": i + 1
                })
        if not steps:
            steps = [
                {"@type": "HowToStep", "name": "Assessment", "text": "Evaluate requirements and current infrastructure.", "position": 1},
                {"@type": "HowToStep", "name": "Planning", "text": "Create implementation roadmap with milestones.", "position": 2},
                {"@type": "HowToStep", "name": "Configuration", "text": "Set up and configure the solution.", "position": 3},
                {"@type": "HowToStep", "name": "Testing", "text": "Run comprehensive testing protocols.", "position": 4},
                {"@type": "HowToStep", "name": "Deployment", "text": "Go live with monitoring in place.", "position": 5}
            ]
        return {
            "@context": "https://schema.org",
            "@type": "HowTo",
            "name": f"How to Implement {entity}",
            "description": f"Step-by-step guide to implementing {entity}",
            "totalTime": "P7D",
            "step": steps
        }

    def _generate_product_schema(self, inputs: Dict) -> Dict[str, Any]:
        """Generate product schema if applicable."""
        entity = inputs.get("primary_entity", "")
        return {
            "@context": "https://schema.org",
            "@type": "SoftwareApplication",
            "name": entity,
            "applicationCategory": "BusinessApplication",
            "operatingSystem": "Web-based",
            "description": inputs.get("description", ""),
            "offers": {
                "@type": "Offer",
                "price": inputs.get("price", "Contact for pricing"),
                "priceCurrency": "USD",
                "availability": "https://schema.org/OnlineOnly"
            },
            "review": {
                "@type": "Review",
                "reviewRating": {
                    "@type": "Rating",
                    "ratingValue": "4.5",
                    "bestRating": "5"
                },
                "author": {
                    "@type": "Person",
                    "name": inputs.get("author", {}).get("name", "")
                }
            }
        }

    def _generate_author_schema(self, author: Dict) -> Dict[str, Any]:
        """Generate author schema."""
        return {
            "@context": "https://schema.org",
            "@type": "Person",
            "name": author.get("name", "[Author Name]"),
            "jobTitle": author.get("title", "[Author Title]"),
            "worksFor": {
                "@type": "Organization",
                "name": author.get("organization", "[Organization]")
            },
            "sameAs": author.get("social_profiles", []),
            "knowsAbout": author.get("expertise", []),
            "hasCredential": author.get("credentials", [])
        }

    def _generate_publisher_schema(self, publisher: Dict) -> Dict[str, Any]:
        """Generate publisher schema."""
        return {
            "@context": "https://schema.org",
            "@type": "Organization",
            "name": publisher.get("name", "[Publisher Name]"),
            "url": publisher.get("url", ""),
            "logo": {
                "@type": "ImageObject",
                "url": publisher.get("logo_url", "")
            },
            "sameAs": publisher.get("social_profiles", [])
        }

    def _generate_breadcrumb_schema(self, inputs: Dict) -> Dict[str, Any]:
        """Generate breadcrumb schema."""
        entity = inputs.get("primary_entity", "")
        return {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Home", "item": inputs.get("base_url", "")},
                {"@type": "ListItem", "position": 2, "name": "Resources", "item": f"{inputs.get('base_url', '')}/resources"},
                {"@type": "ListItem", "position": 3, "name": entity, "item": inputs.get("url", "")}
            ]
        }

    def _generate_itemlist_schema(self, inputs: Dict, outline: Dict) -> Dict[str, Any]:
        """Generate itemList schema for content sections."""
        items = []
        for i, section in enumerate((outline or {}).get("h2_sections", [])[:10]):
            items.append({
                "@type": "ListItem",
                "position": i + 1,
                "name": section.get("title", f"Section {i+1}"),
                "url": f"{inputs.get('url', '')}#section-{i+1}"
            })
        return {
            "@context": "https://schema.org",
            "@type": "ItemList",
            "name": f"{inputs.get('primary_entity', '')} Guide Sections",
            "itemListElement": items
        }

    def _generate_video_schema(self, inputs: Dict) -> Dict[str, Any]:
        """Generate video schema."""
        return {
            "@context": "https://schema.org",
            "@type": "VideoObject",
            "name": f"{inputs.get('primary_entity', '')} Overview",
            "description": f"Quick overview of {inputs.get('primary_entity', '')}",
            "thumbnailUrl": inputs.get("video_thumbnail_url", ""),
            "uploadDate": inputs.get("publish_date", ""),
            "duration": "PT60S",
            "contentUrl": inputs.get("video_url", ""),
            "embedUrl": inputs.get("video_embed_url", "")
        }

    def _generate_organization_schema(self, publisher: Dict) -> Dict[str, Any]:
        """Generate organization schema."""
        return {
            "@context": "https://schema.org",
            "@type": "Organization",
            "name": publisher.get("name", ""),
            "url": publisher.get("url", ""),
            "logo": publisher.get("logo_url", ""),
            "sameAs": publisher.get("social_profiles", []),
            "contactPoint": {
                "@type": "ContactPoint",
                "contactType": "customer service",
                "email": publisher.get("contact_email", "")
            }
        }

    def _build_nested_entity_schema(self, schemas: Dict, entity_graph: Dict) -> Dict[str, Any]:
        """Build deeply nested entity schema with @id references."""
        return {
            "@context": "https://schema.org",
            "@graph": [
                {
                    "@type": "TechArticle",
                    "@id": "#article",
                    "headline": schemas.get("article", {}).get("headline", ""),
                    "author": {"@id": "#author"},
                    "publisher": {"@id": "#publisher"},
                    "about": {"@id": "#mainEntity"}
                },
                {
                    "@type": "Person",
                    "@id": "#author",
                    "name": schemas.get("author", {}).get("name", "")
                },
                {
                    "@type": "Organization",
                    "@id": "#publisher",
                    "name": schemas.get("publisher", {}).get("name", "")
                },
                {
                    "@type": "Thing",
                    "@id": "#mainEntity",
                    "name": schemas.get("article", {}).get("about", {}).get("name", ""),
                    "sameAs": schemas.get("article", {}).get("about", {}).get("sameAs", "")
                }
            ]
        }

    def _generate_implementation_guide(self, schemas: Dict, validation: Dict) -> Dict[str, Any]:
        """Generate implementation guide."""
        return {
            "placement": "Place all schema in <head> section using <script type='application/ld+json'>",
            "priority_order": ["article", "faq", "howto", "breadcrumb", "author", "publisher"],
            "validation_status": {k: v["valid"] for k, v in validation.items()},
            "testing_urls": [
                "https://search.google.com/test/rich-results",
                "https://validator.schema.org/"
            ],
            "notes": [
                "Each schema should be in its own <script> tag",
                "Use @id references for entity linking across schemas",
                "Update dateModified on every content refresh",
                "Validate before deploying to production"
            ]
        }

    def _assess_search_engine_coverage(self, schemas: Dict) -> Dict[str, Any]:
        """Assess search engine coverage."""
        engine_coverage = {
            "google": {
                "supported_types": ["TechArticle", "FAQPage", "HowTo", "BreadcrumbList", "VideoObject"],
                "coverage": sum(1 for t in ["article", "faq", "howto", "breadcrumb", "video"] if schemas.get(t)),
                "rich_results_eligible": True
            },
            "bing": {
                "supported_types": ["Article", "FAQPage", "HowTo", "BreadcrumbList"],
                "coverage": sum(1 for t in ["article", "faq", "howto", "breadcrumb"] if schemas.get(t)),
                "indexnow_ready": True
            },
            "perplexity": {
                "supported_types": ["Article", "FAQPage"],
                "coverage": sum(1 for t in ["article", "faq"] if schemas.get(t)),
                "citation_boost": True
            },
            "chatgpt": {
                "supported_types": ["Article", "FAQPage"],
                "coverage": sum(1 for t in ["article", "faq"] if schemas.get(t)),
                "citation_boost": True
            }
        }
        return {
            "engine_coverage": engine_coverage,
            "overall_coverage": round(
                sum(e["coverage"] for e in engine_coverage.values()) /
                max(1, sum(len(e["supported_types"]) for e in engine_coverage.values())) * 100, 1
            )
        }

    def _generate_recommendations(self, schemas: Dict, validation: Dict) -> List[Dict[str, str]]:
        """Generate schema recommendations."""
        recs = []
        invalid = [k for k, v in validation.items() if not v["valid"]]
        if invalid:
            recs.append({
                "priority": "HIGH",
                "action": f"Fix validation errors in: {', '.join(invalid)}",
                "detail": "Invalid schema syntax may prevent rich result generation"
            })
        if not schemas.get("faq"):
            recs.append({
                "priority": "MEDIUM",
                "action": "Add FAQPage schema",
                "detail": "FAQ schema increases AI Overview citation probability by 25%"
            })
        if not schemas.get("howto"):
            recs.append({
                "priority": "MEDIUM",
                "action": "Add HowTo schema for implementation sections",
                "detail": "HowTo schema enables step-by-step rich results in SERPs"
            })
        return recs
