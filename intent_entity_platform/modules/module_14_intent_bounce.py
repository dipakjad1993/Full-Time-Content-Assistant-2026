"""
Module 14: Audience Intent & Bounce-Risk Predictor
Predicts bounce risk and aligns content with audience intent.
"""
import re
from typing import List, Dict, Any
from ..utils.text_analytics import (
    flesch_kincaid_grade, flesch_reading_ease, gunning_fog_index,
    tokenize_words, tokenize_sentences, compute_readability_for_level
)


class IntentBouncePredictor:
    """Module 14: Audience Intent & Bounce-Risk Predictor"""

    def __init__(self):
        self.module_id = "M14"
        self.module_name = "Audience Intent & Bounce-Risk Predictor"

    def analyze(self, text: str = "", outline: Dict = None, audience_config: Dict = None, inputs: Dict[str, Any] = None) -> Dict[str, Any]:
        """Full intent and bounce-risk analysis pipeline."""
        inputs = inputs or {}
        url_data = inputs.get("_url_data", None)

        real_intent_analysis = {}
        if url_data:
            real_intent_analysis = self._analyze_url_intent_bounce(url_data, audience_config)

        audience_config = audience_config or {}
        if not text or not text.strip():
            text = url_data.get("page_text", "") if url_data else ""

        if not text or not text.strip():
            no_content = True
            text = ""
        else:
            no_content = False

        if no_content:
            return {
                "module": self.module_id,
                "module_name": self.module_name,
                "status": "NO_CONTENT",
                "message": "No real content text was provided or fetched. Intent and bounce-risk analysis requires the actual article text.",
                "url_intent_analysis": real_intent_analysis,
                "content_depth_analysis": {
                    "total_words": 0,
                    "total_sentences": 0,
                    "paragraph_count": 0,
                    "avg_paragraph_length": 0.0,
                    "reading_time_minutes": 0.0,
                    "content_depth_tier": "NO_CONTENT"
                },
                "recommendations": [
                    "Provide the article content (paste text or analyze a URL) to run real intent and bounce-risk analysis.",
                    "Analyze a live URL with /api/analyze-url to get real page content for this module."
                ]
            }

        above_fold = self._analyze_above_fold(text, outline)
        readability = self._assess_readability_alignment(text, audience_config)
        scanability = self._evaluate_scanability(text, outline)
        bounce_risk = self._predict_bounce_risk(text, outline, audience_config)
        intent_match = self._assess_intent_alignment(text, audience_config)
        engagement_signals = self._analyze_engagement_signals(text)

        return {
            "module": self.module_id,
            "module_name": self.module_name,
            "above_fold_analysis": above_fold,
            "readability_alignment": readability,
            "scanability_index": scanability,
            "bounce_risk_prediction": bounce_risk,
            "intent_alignment": intent_match,
            "engagement_signal_analysis": engagement_signals,
            "url_intent_analysis": real_intent_analysis,
            "overall_bounce_risk_score": self._calculate_overall_bounce_risk(above_fold, readability, scanability, bounce_risk),
            "recommendations": self._generate_recommendations(above_fold, readability, scanability, bounce_risk, intent_match),
            "content_depth_analysis": {
                "total_words": len(tokenize_words(text)),
                "total_sentences": len(tokenize_sentences(text)),
                "paragraph_count": len([p for p in text.split('\n\n') if p.strip()]),
                "avg_paragraph_length": round(len(tokenize_words(text)) / max(1, len([p for p in text.split('\n\n') if p.strip()])), 1),
                "reading_time_minutes": round(len(tokenize_words(text)) / 250, 1),
                "content_depth_tier": "COMPREHENSIVE" if len(tokenize_words(text)) > 2000 else "MODERATE" if len(tokenize_words(text)) > 1000 else "BRIEF"
            },
            "user_journey_alignment": {
                "opening_hook_effectiveness": "MODERATE" if bounce_risk.get("has_immediate_value") else "LOW - Add direct value statement",
                "progressive_disclosure": "GOOD" if scanability.get("scanability_score", 0) > 0.5 else "NEEDS_WORK",
                "conversion_readiness": intent_match.get("alignment_tier", "UNKNOWN"),
                "trust_signals_present": engagement_signals.get("elements_present", 0),
                "trust_signal_target": 7,
                "trust_signal_target_origin": "heuristic, not measured",
                "content_freshness_signal": "Include current year (2026) data for freshness"
            },
            "competitor_bounce_comparison": {
                "data_origin": "unverified_industry_heuristic - not measured for this page",
                "industry_avg_bounce_rate": "40-60% for informational content",
                "target_bounce_rate": "< 45% for well-optimized content",
                "your_estimated_bounce_risk": bounce_risk.get("bounce_risk_level", "UNKNOWN"),
                "improvement_potential": "HIGH" if bounce_risk.get("bounce_risk_score", 0) > 0.3 else "MODERATE"
            },
            "implementation_steps": [
                "Step 1: Add direct answer or definition in the first paragraph (under 50 words)",
                "Step 2: Include key statistics and data points within the first 800 pixels of content",
                "Step 3: Restructure headings to use action-oriented language (What, How, Why, Best)",
                "Step 4: Add bullet lists and bold emphasis for quick scanning opportunities",
                "Step 5: Include examples, case studies, and real-world applications for engagement",
                "Step 6: Reduce average sentence length to under 20 words for better readability",
                "Step 7: Add visual breaks (lists, code blocks, images) every 200-300 words",
                "Step 8: Include expert quotes and data statistics to build trust signals",
                "Step 9: Align content intent with target funnel stage (informational, comparative, transactional)",
                "Step 10: Add current year (2026) references and recent data for freshness signals"
            ],
            "where_to_add": [
                "Place direct answer definition in the first paragraph before H2 sections",
                "Add key statistics and percentages in the introductory section above the fold",
                "Include bullet lists within H2 sections for feature/benefit breakdowns",
                "Place expert quotes as blockquotes within relevant H2 sections",
                "Add comparison tables in 'Comparison' or 'Alternatives' H2 sections",
                "Include call-to-action buttons after providing value (not before)",
                "Place trust signals (testimonials, case studies) near conversion points",
                "Add images and visuals within corresponding H2 sections for context",
                "Include internal links to related content within body paragraphs",
                "Place FAQ sections at the end for long-tail query capture"
            ],
            "detailed_analysis": {
                "industry_benchmarks": {
                    "data_origin": "unverified_industry_heuristic - not measured for this page",
                    "average_bounce_rate": "40-60% for informational content, 20-40% for transactional",
                    "optimal_dwell_time": "2-3 minutes for comprehensive guides, 1-2 minutes for listicles",
                    "above_fold_value_delivery": "Top pages deliver value within first 100 words",
                    "scanability_score": "Leading content achieves 0.7+ scanability score",
                    "engagement_signal_count": "5-7 engagement elements per 1000 words optimal"
                },
                "statistical_ranges": {
                    "data_origin": "unverified_industry_heuristic - not measured for this page",
                    "optimal_paragraph_length": "50-100 words per paragraph for readability",
                    "heading_density": "1 heading per 200-300 words for scanability",
                    "list_usage": "3-5 bullet lists per 2000-word article",
                    "image_frequency": "1 image per 300-400 words for visual break",
                    "internal_link_density": "2-3 internal links per 1000 words"
                },
                "expert_recommendations": [
                    "Front-load value: answer the reader's question in the first paragraph",
                    "Use the inverted pyramid structure - most important information first",
                    "Create 'scannable' content with clear headings, lists, and bold keywords",
                    "Include specific examples and data to support every major claim",
                    "Match content format to user intent (comparison tables for 'best' queries)",
                    "Add interactive elements (calculators, quizzes) for engagement signals",
                    "Test content with real users to identify bounce risk points"
                ],
                "common_mistakes_to_avoid": [
                    "Long introductions that delay value delivery (bore readers before they find value)",
                    "Using passive voice and complex sentences that reduce readability",
                    "Missing headings or using non-descriptive headings (Introduction, Conclusion)",
                    "No visual breaks - walls of text without lists, images, or bold emphasis",
                    "Generic content that doesn't match user intent (informational content for transactional queries)",
                    "Missing trust signals (expert quotes, data, case studies)",
                    "Not including current data or year references for freshness"
                ],
                "success_metrics_to_track": [
                    "(General industry guidance, unverified): Bounce rate percentage (target: <45% for informational content)",
                    "(General industry guidance, unverified): Average dwell time (target: >2 minutes for comprehensive content)",
                    "(General industry guidance, unverified): Pages per session (target: >1.5 pages)",
                    "(General industry guidance, unverified): Scroll depth percentage (target: >70% reach bottom)",
                    "(General industry guidance, unverified): Click-through rate from SERPs (target: >3% average)",
                    "(General industry guidance, unverified): Engagement signal count per article (target: 5-7 elements)",
                    "Readability score alignment with target audience level"
                ]
            },
            "data_source": "real_time_analysis"
        }

    def _analyze_url_intent_bounce(self, url_data: Dict, audience_config: Dict = None) -> Dict[str, Any]:
        """Deep intent alignment and bounce risk analysis using actual page content."""
        page_text = url_data.get("page_text", "")
        title = url_data.get("title", "")
        h1 = url_data.get("h1", "")
        h2s = url_data.get("h2s", [])
        word_count = url_data.get("word_count", 0)
        url = url_data.get("url", "")
        link_count = url_data.get("link_count", 0)
        image_count = url_data.get("image_count", 0)
        audience_config = audience_config or {}

        use_text = page_text or ""
        actual_word_count = len(use_text.split()) if use_text else word_count
        funnel_stage = audience_config.get("funnel_stage", "middle")

        # User intent detection from actual content
        intent_signals = {
            "informational": bool(re.search(r'(?:what is|definition|means|refers to|introduction|overview|explained)', use_text, re.IGNORECASE)),
            "educational": bool(re.search(r'(?:how to|guide|tutorial|step|learn|understand|explanation)', use_text, re.IGNORECASE)),
            "comparative": bool(re.search(r'(?:vs|versus|compared|comparison|alternative|better|worse|top\s+\d+)', use_text, re.IGNORECASE)),
            "transactional": bool(re.search(r'(?:price|cost|buy|purchase|demo|trial|sign up|get started|free)', use_text, re.IGNORECASE)),
            "navigational": bool(re.search(r'(?:official|website|homepage|contact|support|login)', use_text, re.IGNORECASE)),
            "investigational": bool(re.search(r'(?:review|analysis|research|study|data|survey|findings)', use_text, re.IGNORECASE))
        }
        detected_intents = [k for k, v in intent_signals.items() if v]

        # Bounce risk signals from actual content structure
        bounce_risk_factors = []
        bounce_score = 0

        # Factor 1: Content depth vs bounce risk
        if actual_word_count < 300:
            bounce_risk_factors.append(f"Thin content ({actual_word_count} words) - high bounce risk for comprehensive queries")
            bounce_score += 0.25
        elif actual_word_count < 600:
            bounce_risk_factors.append(f"Moderate content ({actual_word_count} words) - may not satisfy deep research intent")
            bounce_score += 0.10

        # Factor 2: First paragraph value delivery
        paragraphs = [p.strip() for p in use_text.split('\n\n') if p.strip()]
        first_para = paragraphs[0] if paragraphs else ""
        first_para_words = len(first_para.split())
        has_immediate_value = bool(re.search(
            r'(?:is a|refers to|here\'?s|the answer|in short|tl;?dr|definition)',
            first_para, re.IGNORECASE
        ))
        if not has_immediate_value and first_para_words > 50:
            bounce_risk_factors.append("First paragraph lacks immediate value statement")
            bounce_score += 0.15

        # Factor 3: Heading scanability
        h2_with_value = sum(1 for h in h2s if any(kw in h.lower() for kw in ["what", "how", "why", "benefit", "feature", "best", "guide", "comparison", "step"]))
        if len(h2s) < 3:
            bounce_risk_factors.append(f"Only {len(h2s)} H2 headings - poor scanability")
            bounce_score += 0.10
        if h2_with_value < 3 and len(h2s) >= 3:
            bounce_risk_factors.append("Headings lack action-oriented or value-driven language")
            bounce_score += 0.05

        # Factor 4: Engagement elements
        has_lists = bool(re.search(r'(?:^|\n)\s*[-•*]\s+|(?:^|\n)\s*\d+[\.\)]\s+', use_text))
        has_bold = bool(re.search(r'\*\*[^*]+\*\*|<strong>|<b>', use_text))
        has_statistics = len(re.findall(r'\d+(?:\.\d+)?%', use_text))
        has_examples = bool(re.search(r'(?:for example|for instance|such as|e\.g\.|case study|real-world)', use_text, re.IGNORECASE))
        engagement_elements = sum([has_lists, has_bold, has_statistics >= 2, has_examples])

        if engagement_elements < 2:
            bounce_risk_factors.append("Limited engagement elements (lists, bold, statistics, examples)")
            bounce_score += 0.10

        # Factor 5: Visual content
        if actual_word_count > 500 and image_count == 0:
            bounce_risk_factors.append("No visual content in substantial text - wall of text")
            bounce_score += 0.10

        # Factor 6: Internal linking
        if actual_word_count > 800 and link_count < 3:
            bounce_risk_factors.append("Limited internal links - readers have no next-step paths")
            bounce_score += 0.05

        # Intent alignment scoring
        expected_intents = {
            "top": ["informational", "educational"],
            "middle": ["comparative", "educational", "informational"],
            "bottom": ["transactional", "comparative"]
        }
        target_intents = expected_intents.get(funnel_stage, ["informational"])
        matched_intents = [i for i in target_intents if intent_signals.get(i, False)]
        intent_alignment = len(matched_intents) / max(1, len(target_intents))

        # Engagement signal analysis from actual content
        engagement_analysis = {
            "has_examples": has_examples,
            "has_statistics": has_statistics >= 2,
            "statistics_count": has_statistics,
            "has_lists": has_lists,
            "has_bold_emphasis": has_bold,
            "has_questions": use_text.count('?') >= 3,
            "has_internal_links": link_count > 3,
            "has_images": image_count > 0,
            "engagement_score": round(engagement_elements / 6, 3)
        }

        # Content depth classification
        content_depth = (
            "COMPREHENSIVE" if actual_word_count > 2000 else
            "DETAILED" if actual_word_count > 1000 else
            "MODERATE" if actual_word_count > 500 else
            "BRIEF" if actual_word_count > 200 else
            "MINIMAL"
        )

        # Reading time and dwell time estimation
        reading_time_minutes = round(actual_word_count / 250, 1)
        estimated_dwell_time = (
            "3+ minutes" if actual_word_count > 1500 else
            "2-3 minutes" if actual_word_count > 800 else
            "1-2 minutes" if actual_word_count > 400 else
            "< 1 minute"
        )

        # Specific recommendations based on actual content
        intent_recommendations = []
        if actual_word_count < 500:
            intent_recommendations.append({
                "priority": "HIGH",
                "action": f"Expand content to 500+ words (current: {actual_word_count})",
                "impact": "Thin content has highest bounce rates and lowest dwell time"
            })
        if not has_immediate_value:
            intent_recommendations.append({
                "priority": "HIGH",
                "action": "Add direct answer/definition in first paragraph",
                "impact": "(General industry guidance, unverified): Immediate value delivery reduces bounce by 20-35%"
            })
        if len(h2s) < 3:
            intent_recommendations.append({
                "priority": "MEDIUM",
                "action": f"Add more H2 headings for scanability (current: {len(h2s)})",
                "impact": "(General industry guidance, unverified): Good heading structure improves dwell time by 15-25%"
            })
        if engagement_elements < 3:
            intent_recommendations.append({
                "priority": "MEDIUM",
                "action": "Add more engagement elements (lists, bold, examples, statistics)",
                "impact": "(General industry guidance, unverified): Engagement elements increase dwell time by 20-40%"
            })
        if image_count == 0 and actual_word_count > 500:
            intent_recommendations.append({
                "priority": "MEDIUM",
                "action": "Add visual content (images, charts) for visual breaks",
                "impact": "(General industry guidance, unverified): Visual content reduces bounce by 15-25%"
            })
        if not intent_signals.get("informational") and funnel_stage == "top":
            intent_recommendations.append({
                "priority": "HIGH",
                "action": "Add informational content (definitions, explanations) for top-funnel audience",
                "impact": "Intent mismatch is primary cause of high bounce rates"
            })
        if not intent_signals.get("transactional") and funnel_stage == "bottom":
            intent_recommendations.append({
                "priority": "HIGH",
                "action": "Add transactional elements (pricing, demos, CTAs) for bottom-funnel audience",
                "impact": "Bottom-funnel content needs clear conversion paths"
            })

        # Overall bounce risk
        bounce_risk_level = (
            "CRITICAL" if bounce_score > 0.6 else
            "HIGH" if bounce_score > 0.4 else
            "MODERATE" if bounce_score > 0.2 else
            "LOW"
        )

        return {
            "page_url": url,
            "page_title": title,
            "content_word_count": actual_word_count,
            "content_depth": content_depth,
            "reading_time_minutes": reading_time_minutes,
            "estimated_dwell_time": estimated_dwell_time,
            "user_intent_detection": {
                "detected_intents": detected_intents,
                "target_intents": target_intents,
                "matched_intents": matched_intents,
                "intent_alignment_score": round(intent_alignment, 3),
                "intent_alignment_tier": (
                    "STRONG" if intent_alignment >= 0.7 else
                    "MODERATE" if intent_alignment >= 0.4 else
                    "WEAK"
                ),
                "intent_signals": intent_signals
            },
            "bounce_risk_assessment": {
                "bounce_risk_score": round(bounce_score, 3),
                "bounce_risk_level": bounce_risk_level,
                "risk_factors": bounce_risk_factors,
                "expected_bounce_rate": (
                    "(General industry guidance, unverified): 25-35%" if bounce_score < 0.2 else
                    "(General industry guidance, unverified): 35-50%" if bounce_score < 0.4 else
                    "(General industry guidance, unverified): 50-65%" if bounce_score < 0.6 else
                    "(General industry guidance, unverified): 65%+"
                ),
                "improvement_potential": "HIGH" if bounce_score > 0.3 else "MODERATE"
            },
            "engagement_signal_analysis": {
                "engagement_elements_present": engagement_elements,
                "engagement_score": round(engagement_elements / 6, 3),
                "engagement_tier": (
                    "HIGHLY_ENGAGING" if engagement_elements >= 5 else
                    "MODERATELY_ENGAGING" if engagement_elements >= 3 else
                    "NEEDS_MORE_ENGAGEMENT"
                ),
                "details": engagement_analysis
            },
            "content_structure_for_engagement": {
                "heading_count": len(h2s),
                "headings_with_value_keywords": h2_with_value,
                "has_lists": has_lists,
                "has_bold": has_bold,
                "has_statistics": has_statistics >= 2,
                "statistics_count": has_statistics,
                "has_examples": has_examples,
                "image_count": image_count,
                "link_count": link_count
            },
            "above_fold_prediction": {
                "first_paragraph_words": first_para_words,
                "has_immediate_value": has_immediate_value,
                "estimated_above_fold_value": "HIGH" if has_immediate_value and first_para_words <= 100 else "MODERATE" if has_immediate_value else "LOW"
            },
            "intent_recommendations": intent_recommendations,
            "competitor_comparison_benchmarks": {
                "data_origin": "unverified_industry_heuristic - not measured for this page",
                "industry_avg_bounce": "40-60%",
                "your_estimated_bounce": f"{int(25 + bounce_score * 40)}-{int(35 + bounce_score * 40)}%",
                "target_bounce": "< 45%",
                "gap_analysis": "ABOVE_TARGET" if bounce_score > 0.3 else "ON_TARGET"
            }
        }

    def _analyze_above_fold(self, text: str, outline: Dict) -> Dict[str, Any]:
        """Analyze what users see in the top 800px of the screen."""
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        first_800px_content = paragraphs[:3] if paragraphs else []
        content_800px = ' '.join(first_800px_content)
        words_in_800px = len(tokenize_words(content_800px))
        has_direct_answer = bool(re.search(
            r'(?:is a|refers to|means|is defined as|can be described as)',
            content_800px, re.IGNORECASE
        ))
        has_statistics = bool(re.search(r'\d+(?:\.\d+)?%', content_800px))
        has_entity_mention = bool(re.search(r'[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*', content_800px))
        has_cta = bool(re.search(r'(?:learn more|discover|find out|see how|get started)', content_800px, re.IGNORECASE))
        has_image = bool(re.search(r'!\[.*\]\(|<img', text[:2000], re.IGNORECASE))
        friction_score = 0
        if words_in_800px < 30:
            friction_score += 0.3
        if not has_direct_answer:
            friction_score += 0.25
        if has_image:
            friction_score += 0.1
        return {
            "estimated_words_above_fold": words_in_800px,
            "has_direct_answer": has_direct_answer,
            "has_statistics": has_statistics,
            "has_entity_mention": has_entity_mention,
            "has_cta": has_cta,
            "has_image": has_image,
            "friction_score": round(min(1.0, friction_score), 3),
            "friction_level": (
                "HIGH - Users may bounce before finding value" if friction_score > 0.5 else
                "MODERATE - Some friction in initial content" if friction_score > 0.3 else
                "LOW - Content delivers value quickly"
            ),
            "above_fold_recommendation": (
                "Add direct answer or definition block in first paragraph" if not has_direct_answer else
                "Content is well-structured for quick value delivery"
            )
        }

    def _assess_readability_alignment(self, text: str, audience: Dict) -> Dict[str, Any]:
        """Assess if readability matches target audience."""
        target_level = audience.get("knowledge_floor", "intermediate")
        funnel_stage = audience.get("funnel_stage", "middle")
        if funnel_stage == "top":
            adjusted_level = "beginner"
        elif funnel_stage == "bottom":
            adjusted_level = "advanced"
        else:
            adjusted_level = target_level
        alignment = compute_readability_for_level(text, adjusted_level)
        return {
            "target_audience_level": adjusted_level,
            "actual_flesch_kincaid_grade": alignment["flesch_kincaid_grade"],
            "actual_flesch_reading_ease": alignment["flesch_reading_ease"],
            "actual_gunning_fog": alignment["gunning_fog_index"],
            "alignment_score": alignment["alignment_score"],
            "alignment_verdict": alignment["verdict"],
            "issues": alignment["issues"],
            "readability_recommendation": (
                "Simplify language - use shorter sentences and common words" if alignment["flesch_kincaid_grade"] > alignment.get("target_grade_max", 12) else
                "Content readability is well-matched to audience" if alignment["alignment_score"] > 0.7 else
                "Consider adjusting complexity for target audience"
            )
        }

    def _evaluate_scanability(self, text: str, outline: Dict) -> Dict[str, Any]:
        """Evaluate if user can get 80% value from scanning headings."""
        headings = re.findall(r'^#{1,3}\s+(.+)$', text, re.MULTILINE)
        if not headings:
            headings = re.findall(r'<h[1-3][^>]*>(.+?)</h[1-3]>', text, re.IGNORECASE)
        if not headings and outline:
            headings = [s.get("title", "") for s in outline.get("h2_sections", [])]
        key_value_headings = sum(1 for h in headings if any(
            term in h.lower() for term in ["what", "how", "why", "benefit", "feature", "best", "comparison", "step", "guide"]
        ))
        heading_count = len(headings)
        has_lists = bool(re.search(r'(?:^|\n)\s*[-•*]\s+|(?:^|\n)\s*\d+[\.\)]\s+', text))
        has_tables = bool(re.search(r'\|.*\|.*\|', text))
        has_bold = bool(re.search(r'\*\*[^*]+\*\*|<strong>|<b>', text))
        scanability_score = (
            (min(1.0, key_value_headings / max(1, heading_count)) * 0.3) +
            (0.2 if heading_count >= 8 else heading_count / 8 * 0.2) +
            (0.15 if has_lists else 0) +
            (0.15 if has_tables else 0) +
            (0.1 if has_bold else 0) +
            (0.1 if key_value_headings >= 5 else 0)
        )
        return {
            "total_headings": heading_count,
            "key_value_headings": key_value_headings,
            "key_value_ratio": round(key_value_headings / max(1, heading_count), 3),
            "has_lists": has_lists,
            "has_tables": has_tables,
            "has_bold_emphasis": has_bold,
            "scanability_score": round(scanability_score, 3),
            "scanability_tier": (
                "EXCELLENT - Users can extract 80%+ value from scanning" if scanability_score > 0.7 else
                "GOOD - Most value accessible via scanning" if scanability_score > 0.5 else
                "MODERATE - Some scanning value, but reading required" if scanability_score > 0.3 else
                "POOR - Full reading required to extract value"
            ),
            "heading_quality": [
                {"heading": h, "is_key_value": any(
                    term in h.lower() for term in ["what", "how", "why", "benefit", "feature", "best"]
                )} for h in headings[:15]
            ],
            "scanability_recommendation": (
                "Excellent scanability - maintain current heading structure" if scanability_score > 0.7 else
                "Add more action-oriented headings (What, How, Why, Best)" if key_value_headings < 5 else
                "Add bullet lists and bold emphasis for quick scanning"
            )
        }

    def _predict_bounce_risk(self, text: str, outline: Dict, audience: Dict) -> Dict[str, Any]:
        """Predict bounce risk based on content characteristics."""
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        total_words = len(tokenize_words(text))
        first_paragraph_words = len(tokenize_words(paragraphs[0])) if paragraphs else 0
        has_immediate_value = bool(re.search(
            r'(?:is a|refers to|here\'?s|the answer|short answer|in short|tl;?dr)',
            paragraphs[0] if paragraphs else "", re.IGNORECASE
        ))
        intro_to_value_ratio = first_paragraph_words / max(1, total_words) * 100
        sentences = tokenize_sentences(text)
        avg_sentence_length = total_words / max(1, len(sentences))
        has_engagement_elements = bool(re.search(
            r'(?:for example|such as|case study|real-world|in practice|here\'?s how)',
            text, re.IGNORECASE
        ))
        has_visual_breaks = bool(re.search(r'(?:^|\n)\s*[-•*]\s+|(?:^|\n)\s*\d+[\.\)]\s+|```\n', text))
        bounce_risk_factors = []
        bounce_score = 0
        if first_paragraph_words > 150:
            bounce_risk_factors.append("Long introduction before reaching main topic")
            bounce_score += 0.2
        if not has_immediate_value:
            bounce_risk_factors.append("No immediate value signal in opening paragraph")
            bounce_score += 0.25
        if intro_to_value_ratio > 20:
            bounce_risk_factors.append(f"Introduction is {intro_to_value_ratio:.0f}% of total content")
            bounce_score += 0.15
        if avg_sentence_length > 25:
            bounce_risk_factors.append("Average sentence length may deter scanning")
            bounce_score += 0.1
        if not has_engagement_elements:
            bounce_risk_factors.append("Lacks engagement elements (examples, case studies)")
            bounce_score += 0.1
        if not has_visual_breaks:
            bounce_risk_factors.append("No visual breaks (lists, code blocks)")
            bounce_score += 0.1
        return {
            "bounce_risk_score": round(min(1.0, bounce_score), 3),
            "bounce_risk_level": (
                "CRITICAL" if bounce_score > 0.6 else
                "HIGH" if bounce_score > 0.4 else
                "MODERATE" if bounce_score > 0.2 else
                "LOW"
            ),
            "risk_factors": bounce_risk_factors,
            "first_paragraph_words": first_paragraph_words,
            "intro_to_value_ratio": round(intro_to_value_ratio, 1),
            "has_immediate_value": has_immediate_value,
            "has_engagement_elements": has_engagement_elements,
            "expected_dwell_time_impact": (
                "NEGATIVE - Users likely to bounce quickly" if bounce_score > 0.5 else
                "NEUTRAL - Average expected dwell time" if bounce_score > 0.2 else
                "POSITIVE - Strong engagement expected"
            )
        }

    def _assess_intent_alignment(self, text: str, audience: Dict) -> Dict[str, Any]:
        """Assess how well content aligns with user intent."""
        funnel_stage = audience.get("funnel_stage", "middle")
        intent_signals = {
            "informational": bool(re.search(r'(?:what is|definition|means|refers to|introduction|overview)', text, re.IGNORECASE)),
            "comparative": bool(re.search(r'(?:vs|versus|compared|comparison|alternative|better|worse)', text, re.IGNORECASE)),
            "transactional": bool(re.search(r'(?:price|cost|buy|purchase|demo|trial|sign up|get started)', text, re.IGNORECASE)),
            "navigational": bool(re.search(r'(?:official|website|homepage|contact|support)', text, re.IGNORECASE)),
            "educational": bool(re.search(r'(?:how to|guide|tutorial|step|learn|understand)', text, re.IGNORECASE)),
        }
        expected_intents = {
            "top": ["informational", "educational"],
            "middle": ["comparative", "educational", "informational"],
            "bottom": ["transactional", "comparative"]
        }
        target_intents = expected_intents.get(funnel_stage, ["informational"])
        matched_intents = [i for i in target_intents if intent_signals.get(i, False)]
        alignment_score = len(matched_intents) / max(1, len(target_intents))
        return {
            "detected_intents": [k for k, v in intent_signals.items() if v],
            "target_intents": target_intents,
            "matched_intents": matched_intents,
            "alignment_score": round(alignment_score, 3),
            "alignment_tier": (
                "STRONG - Content matches user intent" if alignment_score > 0.7 else
                "MODERATE - Partial intent alignment" if alignment_score > 0.4 else
                "WEAK - Significant intent mismatch"
            ),
            "missing_intents": [i for i in target_intents if i not in matched_intents],
            "intent_recommendation": (
                f"Add {', '.join([i for i in target_intents if i not in matched_intents])} content blocks" if alignment_score < 0.7 else
                "Content intent alignment is strong"
            )
        }

    def _analyze_engagement_signals(self, text: str) -> Dict[str, Any]:
        """Analyze engagement signals in content."""
        has_examples = bool(re.search(r'(?:for example|for instance|such as|e\.g\.|like)', text, re.IGNORECASE))
        has_questions = text.count('?') >= 3
        has_data = bool(re.search(r'\d+(?:\.\d+)?%', text))
        has_quotes = bool(re.search(r'["\u201c][^"\u201d]{20,}["\u201d]', text))
        has_lists = bool(re.search(r'(?:^|\n)\s*[-•*]\s+|(?:^|\n)\s*\d+[\.\)]\s+', text))
        has_bold = bool(re.search(r'\*\*[^*]+\*\*|<strong>|<b>', text))
        has_transitions = bool(re.search(r'(?:however|therefore|consequently|moreover|furthermore)', text, re.IGNORECASE))
        engagement_score = sum([has_examples, has_questions, has_data, has_quotes, has_lists, has_bold, has_transitions]) / 7
        return {
            "engagement_elements": {
                "examples": has_examples,
                "questions": has_questions,
                "data_statistics": has_data,
                "expert_quotes": has_quotes,
                "lists": has_lists,
                "bold_emphasis": has_bold,
                "transitions": has_transitions
            },
            "elements_present": sum([has_examples, has_questions, has_data, has_quotes, has_lists, has_bold, has_transitions]),
            "engagement_score": round(engagement_score, 3),
            "engagement_tier": (
                "HIGHLY_ENGAGING" if engagement_score > 0.7 else
                "MODERATELY_ENGAGING" if engagement_score > 0.4 else
                "NEEDS_MORE_ENGAGEMENT"
            ),
            "missing_elements": [
                e for e, present in [
                    ("examples", has_examples), ("questions", has_questions),
                    ("data_statistics", has_data), ("expert_quotes", has_quotes),
                    ("lists", has_lists), ("bold_emphasis", has_bold)
                ] if not present
            ]
        }

    def _calculate_overall_bounce_risk(self, above_fold: Dict, readability: Dict, scanability: Dict, bounce: Dict) -> Dict[str, Any]:
        """Calculate overall bounce risk score."""
        above_fold_penalty = above_fold.get("friction_score", 0) * 0.25
        readability_penalty = max(0, (1 - readability.get("alignment_score", 0.5))) * 0.25
        scanability_penalty = max(0, (1 - scanability.get("scanability_score", 0.5))) * 0.25
        bounce_penalty = bounce.get("bounce_risk_score", 0) * 0.25
        overall_risk = above_fold_penalty + readability_penalty + scanability_penalty + bounce_penalty
        return {
            "overall_bounce_risk": round(overall_risk, 3),
            "risk_level": (
                "CRITICAL" if overall_risk > 0.6 else
                "HIGH" if overall_risk > 0.4 else
                "MODERATE" if overall_risk > 0.2 else
                "LOW"
            ),
            "component_risks": {
                "above_fold_friction": round(above_fold_penalty, 3),
                "readability_misalignment": round(readability_penalty, 3),
                "scanability_issues": round(scanability_penalty, 3),
                "content_structure_risk": round(bounce_penalty, 3)
            },
            "expected_impact": (
                "Significant ranking and engagement loss expected" if overall_risk > 0.6 else
                "Moderate impact on user engagement" if overall_risk > 0.3 else
                "Minimal bounce risk - content is well-optimized"
            )
        }

    def _generate_recommendations(self, above_fold: Dict, readability: Dict, scanability: Dict,
                                    bounce: Dict, intent: Dict) -> List[Dict[str, str]]:
        """Generate bounce-risk reduction recommendations."""
        recs = []
        if above_fold.get("friction_score", 0) > 0.3:
            recs.append({
                "priority": "HIGH",
                "action": "Reduce above-fold friction",
                "detail": f"Friction score: {above_fold['friction_score']} - add direct answer in first paragraph"
            })
        if readability.get("alignment_score", 0) < 0.5:
            recs.append({
                "priority": "HIGH",
                "action": f"Adjust readability for {readability.get('target_audience_level', 'intermediate')} audience",
                "detail": f"Grade level: {readability.get('actual_flesch_kincaid_grade', 0)} - target audience: {readability.get('target_audience_level', 'intermediate')}"
            })
        if scanability.get("scanability_score", 0) < 0.5:
            recs.append({
                "priority": "MEDIUM",
                "action": "Improve content scanability",
                "detail": f"Key-value heading ratio: {scanability.get('key_value_ratio', 0)} - add more action-oriented headings"
            })
        if bounce.get("bounce_risk_score", 0) > 0.3:
            recs.append({
                "priority": "HIGH",
                "action": "Reduce bounce risk factors",
                "detail": f"{len(bounce.get('risk_factors', []))} risk factors identified"
            })
        if intent.get("alignment_score", 0) < 0.5:
            recs.append({
                "priority": "MEDIUM",
                "action": f"Add missing intent content: {', '.join(intent.get('missing_intents', []))}",
                "detail": f"Content aligned with {intent.get('matched_intents', [])} but missing {intent.get('missing_intents', [])}"
            })
        return recs
