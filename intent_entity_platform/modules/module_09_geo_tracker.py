"""
Module 9: Post-Publish AI Overview / GEO Tracker
Tracks citation drift and monitors AI Overview inclusion.
"""
import re
from typing import List, Dict, Any, Optional
from datetime import datetime
from ..utils.web_data import web_search


class GEOTracker:
    """Module 9: Post-Publish AI Overview / GEO Tracker"""

    def __init__(self):
        self.module_id = "M09"
        self.module_name = "Post-Publish AI Overview / GEO Tracker"

    def analyze(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Generate post-publish tracking configuration."""
        url = inputs.get("url", "")
        target_queries = list(inputs.get("target_queries", []) or [])
        entity = inputs.get("primary_entity", "")
        seed = inputs.get("seed_phrase", "")
        locale = inputs.get("locale", "en-US")
        url_data = inputs.get("_url_data", None)

        if not target_queries:
            target_queries = [q for q in [seed] + list(inputs.get("secondary_keywords", []) or []) if q]
        if not target_queries and entity:
            target_queries = [entity]

        real_geo_analysis = {}
        if url_data:
            real_geo_analysis = self._analyze_url_geo_signals(url_data, target_queries)

        live_snapshot = self._capture_live_serp_snapshot(target_queries)

        tracking_config = self._build_tracking_config(url, target_queries, entity, locale)
        monitoring_dashboard = self._design_monitoring_dashboard(url, target_queries)
        alert_system = self._configure_alert_system(url, target_queries)
        reporting_framework = self._build_reporting_framework(url, target_queries)

        return {
            "module": self.module_id,
            "module_name": self.module_name,
            "live_serp_snapshot": live_snapshot,
            "tracking_configuration": tracking_config,
            "monitoring_dashboard": monitoring_dashboard,
            "alert_system": alert_system,
            "reporting_framework": reporting_framework,
            "url_geo_analysis": real_geo_analysis,
            "implementation_checklist": self._generate_implementation_checklist(tracking_config),
            "implementation_steps": [
                "Step 1: Set up daily SERP monitoring API (e.g., SERPAPI, SEMrush) for target queries",
                "Step 2: Configure AI Overview tracking for Google, Perplexity, ChatGPT, Gemini, and Copilot",
                "Step 3: Implement automated screenshot evidence collection for citation states",
                "Step 4: Set up alert notifications via email and Slack for citation changes",
                "Step 5: Create monitoring dashboard with citation status, position tracking, and competitor monitoring",
                "Step 6: Configure weekly competitor citation comparison reports",
                "Step 7: Establish response protocols for citation loss (48-hour update cycle)",
                "Step 8: Set up monthly reporting templates for executive stakeholders",
                "Step 9: Implement historical tracking with timestamped citation logs",
                "Step 10: Configure automated alerts for content decay (15%+ impression drop over 30 days)"
            ],
            "where_to_add": [
                "Add tracking pixels in <head> section for analytics attribution",
                "Place UTM parameters on internal links to track citation-driven traffic",
                "Add citation tracking scripts before closing </body> tag",
                "Include monitoring dashboard links in content team Slack channels",
                "Place weekly report templates in shared Google Drive/Notion workspace",
                "Add citation status widgets to existing SEO dashboards",
                "Configure alert webhooks to connect with existing notification systems",
                "Place competitor comparison data in monthly board presentation templates"
            ],
            "detailed_analysis": {
                "industry_benchmarks": {
                    "ai_overview_citation_rate": "Top-performing content achieves 15-25% citation rate in AI Overviews",
                    "perplexity_citation_frequency": "Optimized content appears in 10-20% of relevant Perplexity answers",
                    "citation_driven_traffic": "Citation-driven traffic converts 2-3x higher than organic search traffic",
                    "position_drop_response_time": "Best practice: respond to position drops within 48 hours",
                    "content_refresh_frequency": "Update cited content every 30-60 days to maintain citations"
                },
                "statistical_ranges": {
                    "optimal_query_count": "Track 5-10 primary queries per piece of content",
                    "citation_loss_recovery_time": "Average 7-14 days to recover lost citations with updates",
                    "competitor_citation_gap": "Top 3 competitors typically hold 60-80% of available citations",
                    "dashboard_refresh_rate": "Real-time for citation checks, daily for position tracking",
                    "alert_response_time": "CRITICAL alerts: 4-hour response, HIGH: 24-hour response"
                },
                "expert_recommendations": [
                    "Focus on obtaining citations in Google AI Overview first - highest traffic impact",
                    "Monitor competitor citation patterns to identify content gaps",
                    "Update cited sections with fresh data and examples monthly",
                    "Create citation-worthy content with unique data, expert quotes, and clear definitions",
                    "Track both direct citations and paraphrased mentions across AI platforms",
                    "Use structured data (FAQ, HowTo) to increase citation probability",
                    "Build topical authority through comprehensive coverage of subject matter"
                ],
                "common_mistakes_to_avoid": [
                    "Only tracking Google and ignoring Perplexity/ChatGPT citation opportunities",
                    "Not having a response protocol for citation loss (waiting too long to update)",
                    "Updating content without tracking what triggered the citation change",
                    "Focusing on quantity of tracked queries over quality (track most impactful queries)",
                    "Not benchmarking competitor citation performance",
                    "Ignoring citation context and sentiment analysis",
                    "Failing to document what content changes led to citation gains"
                ],
                "success_metrics_to_track": [
                    "AI Overview citation rate percentage over time",
                    "Citation-driven estimated traffic and conversions",
                    "Competitor citation share comparison",
                    "Content freshness score and update frequency",
                    "Position stability for target queries",
                    "Citation context quality (sentiment and accuracy)",
                    "ROI of GEO efforts vs traditional SEO"
                ]
            }
        }

    def _capture_live_serp_snapshot(self, queries: List[str]) -> Dict[str, Any]:
        """Capture a REAL live SERP snapshot for the target queries."""
        snapshots = []
        statuses = []
        for q in queries[:5]:
            serp = web_search(q, 8)
            snapshots.append({
                "query": q,
                "ok": serp.get("ok", False),
                "error": serp.get("error"),
                "results": serp.get("results", []),
            })
            statuses.append(serp.get("ok", False))
        return {
            "queries_monitored": len(snapshots),
            "captured_at": datetime.now().isoformat(),
            "live_capture_success": all(statuses),
            "partial_capture": any(statuses) and not all(statuses),
            "capture_error": "No live SERP results could be retrieved" if not any(statuses) else None,
            "queries": snapshots,
        }

    def _analyze_url_geo_signals(self, url_data: Dict, target_queries: List[str]) -> Dict[str, Any]:
        """Deep GEO signal analysis using actual page content."""
        page_text = url_data.get("page_text", "")
        title = url_data.get("title", "")
        meta_desc = url_data.get("meta_description", "")
        h1 = url_data.get("h1", "")
        h2s = url_data.get("h2s", [])
        word_count = url_data.get("word_count", 0)
        has_schema = url_data.get("has_schema", False)
        url = url_data.get("url", "")

        # Analyze content structure for AI citation readiness
        def has_definition_sentence(text_block):
            return bool(re.search(r'(?:is a|is an|refers to|means|is defined as|is the process|can be described as)', text_block, re.IGNORECASE))

        def has_statistical_evidence(text_block):
            return len(re.findall(r'\d+(?:\.\d+)?%', text_block)) + len(re.findall(r'\$\d+', text_block))

        def has_expert_attribution(text_block):
            return bool(re.search(r'(?:according to|research shows|studies indicate|experts suggest|data shows|a study|survey found)', text_block, re.IGNORECASE))

        def has_list_structure(text_block):
            return bool(re.search(r'(?:^|\n)\s*[-•*]\s+|(?:^|\n)\s*\d+[\.\)]\s+', text_block))

        def has_question_answer(text_block):
            return bool(re.search(r'#{1,3}\s+.*\?', text_block)) or text_block.count('?') >= 3

        def has_comparison_content(text_block):
            return bool(re.search(r'(?:vs\.?|versus|compared to|alternatives?|comparison|better than|worse than)', text_block, re.IGNORECASE))

        # AI Overview citation factors
        definition_sentences = len(re.findall(r'(?:is a|is an|refers to|means|is defined as)', page_text, re.IGNORECASE))
        statistical_evidence = has_statistical_evidence(page_text)
        expert_attribution = has_expert_attribution(page_text)
        list_structure = has_list_structure(page_text)
        question_answer = has_question_answer(page_text)
        comparison_content = has_comparison_content(page_text)

        # Content structure scoring for AI
        citation_readiness_score = 0
        citation_factors = []

        # Factor 1: Clear definitions (AI models prefer citing clear definitions)
        if definition_sentences >= 2:
            citation_readiness_score += 0.25
            citation_factors.append(f"Strong: {definition_sentences} definition sentences found - highly citeable")
        elif definition_sentences == 1:
            citation_readiness_score += 0.15
            citation_factors.append(f"Moderate: {definition_sentences} definition sentence found")
        else:
            citation_factors.append("Weak: No clear definition sentences - AI models cannot easily extract definitions")

        # Factor 2: Statistical evidence (increases citation probability)
        if statistical_evidence >= 5:
            citation_readiness_score += 0.25
            citation_factors.append(f"Strong: {statistical_evidence} statistical data points - highly citeable")
        elif statistical_evidence >= 2:
            citation_readiness_score += 0.15
            citation_factors.append(f"Moderate: {statistical_evidence} statistical data points")
        else:
            citation_factors.append("Weak: Limited statistical evidence - add more data for AI citation")

        # Factor 3: Expert attribution
        if expert_attribution:
            citation_readiness_score += 0.20
            citation_factors.append("Strong: Expert attributions and research citations present")
        else:
            citation_factors.append("Weak: No expert attributions - add research citations")

        # Factor 4: Structured content (lists, tables)
        if list_structure:
            citation_readiness_score += 0.10
            citation_factors.append("Good: List/bullet structure detected - easy for AI to parse")

        # Factor 5: Q&A format (highly citable)
        if question_answer:
            citation_readiness_score += 0.15
            citation_factors.append("Strong: Question-answer format detected - ideal for AI citation")

        # Factor 6: Comparison content
        if comparison_content:
            citation_readiness_score += 0.05
            citation_factors.append("Good: Comparison content present - useful for product queries")

        # AI platform-specific readiness
        ai_platform_readiness = {}
        # Google AI Overview prefers structured, concise answers
        ai_platform_readiness["google_ai_overview"] = {
            "readiness_score": round(min(1.0, citation_readiness_score * 1.1), 3),
            "factors": [
                "Content has clear definitions for extraction" if definition_sentences >= 2 else "Add more definition sentences",
                "Statistical evidence strengthens AI Overview inclusion" if statistical_evidence >= 3 else "Add more data points",
                "FAQ/Q&A structure increases citation probability" if question_answer else "Add FAQ section"
            ],
            "estimated_citation_probability": "High" if citation_readiness_score >= 0.7 else "Moderate" if citation_readiness_score >= 0.4 else "Low"
        }
        # Perplexity prefers well-sourced, factual content
        ai_platform_readiness["perplexity"] = {
            "readiness_score": round(min(1.0, citation_readiness_score * 1.0), 3),
            "factors": [
                "Research citations present for source verification" if expert_attribution else "Add source citations",
                f"Content length ({word_count} words) sufficient for comprehensive answers" if word_count >= 800 else "Content may be too brief",
                "Structured data (schema) present" if has_schema else "Add schema markup"
            ],
            "estimated_citation_probability": "High" if citation_readiness_score >= 0.6 else "Moderate" if citation_readiness_score >= 0.35 else "Low"
        }
        # ChatGPT/Copilot prefer authoritative, well-structured content
        ai_platform_readiness["chatgpt_copilot"] = {
            "readiness_score": round(min(1.0, citation_readiness_score * 0.95), 3),
            "factors": [
                "Authoritative tone with data support" if statistical_evidence >= 3 and expert_attribution else "Strengthen authority signals",
                "Clear heading structure for topic identification" if len(h2s) >= 3 else "Add more H2 headings for topic clarity",
                "Comprehensive coverage" if word_count >= 1000 else "Expand content depth"
            ],
            "estimated_citation_probability": "High" if citation_readiness_score >= 0.65 else "Moderate" if citation_readiness_score >= 0.4 else "Low"
        }

        # Content structure analysis for AI crawlers
        heading_analysis = {
            "h1_has_entity": bool(re.search(r'[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*', h1)) if h1 else False,
            "h2_count": len(h2s),
            "h2_with_questions": sum(1 for h in h2s if "?" in h),
            "h2_with_definitions": sum(1 for h in h2s if any(kw in h.lower() for kw in ["what is", "how to", "why", "guide", "comparison"])),
            "ai_friendly_headings": "Yes" if len(h2s) >= 4 else "Needs more headings"
        }

        # Recommendations specific to the actual content
        geo_recommendations = []
        if definition_sentences == 0:
            geo_recommendations.append({
                "priority": "CRITICAL",
                "action": "Add definition sentences ('X is a...' format) at the start of key sections",
                "impact": "Increases AI citation probability by 40-60%"
            })
        if statistical_evidence < 3:
            geo_recommendations.append({
                "priority": "HIGH",
                "action": f"Add more statistical evidence (current: {statistical_evidence} data points, target: 5+)",
                "impact": "Statistical content is cited 3x more often in AI responses"
            })
        if not expert_attribution:
            geo_recommendations.append({
                "priority": "HIGH",
                "action": "Add expert attributions, research citations, and source references",
                "impact": "Attributed content is 2.5x more likely to be cited by AI"
            })
        if not has_schema:
            geo_recommendations.append({
                "priority": "MEDIUM",
                "action": "Add structured data (Article, FAQ, HowTo schema) to improve AI parsing",
                "impact": "Schema-marked content has 25% higher AI citation rate"
            })
        if not question_answer:
            geo_recommendations.append({
                "priority": "MEDIUM",
                "action": "Add FAQ section or Q&A-formatted headings to capture question-based queries",
                "impact": "FAQ content is directly cited in AI Overviews"
            })
        if word_count < 800:
            geo_recommendations.append({
                "priority": "MEDIUM",
                "action": f"Expand content depth (current: {word_count} words, target: 800+)",
                "impact": "Comprehensive content is preferred by AI for authoritative answers"
            })

        return {
            "page_url": url,
            "page_title": title,
            "content_word_count": word_count,
            "citation_readiness_score": round(citation_readiness_score, 3),
            "citation_readiness_tier": (
                "EXCELLENT" if citation_readiness_score >= 0.8 else
                "GOOD" if citation_readiness_score >= 0.6 else
                "MODERATE" if citation_readiness_score >= 0.4 else
                "NEEDS_WORK" if citation_readiness_score >= 0.2 else
                "POOR"
            ),
            "citation_factors": citation_factors,
            "content_signals_for_ai": {
                "definition_sentences": definition_sentences,
                "statistical_data_points": statistical_evidence,
                "expert_attributions": expert_attribution,
                "list_structure": list_structure,
                "question_answer_format": question_answer,
                "comparison_content": comparison_content,
                "schema_present": has_schema
            },
            "ai_platform_readiness": ai_platform_readiness,
            "heading_analysis_for_ai": heading_analysis,
            "target_query_alignment": {
                "queries_provided": len(target_queries),
                "content_covers_queries": sum(1 for q in target_queries if q.lower() in page_text.lower()) if page_text else 0,
                "coverage_rate": round(sum(1 for q in target_queries if q.lower() in page_text.lower()) / max(1, len(target_queries)) * 100, 1) if page_text else 0
            },
            "geo_recommendations": geo_recommendations,
            "estimated_ai_citation_potential": {
                "google_ai_overview": ai_platform_readiness["google_ai_overview"]["estimated_citation_probability"],
                "perplexity": ai_platform_readiness["perplexity"]["estimated_citation_probability"],
                "chatgpt_copilot": ai_platform_readiness["chatgpt_copilot"]["estimated_citation_probability"]
            }
        }

    def _build_tracking_config(self, url: str, queries: List[str], entity: str, locale: str) -> Dict[str, Any]:
        """Build comprehensive tracking configuration."""
        return {
            "url": url,
            "entity": entity,
            "locale": locale,
            "monitoring_targets": {
                "google_ai_overview": {
                    "track": True,
                    "check_frequency": "daily",
                    "queries_to_monitor": queries[:10],
                    "metrics": ["citation_present", "citation_position", "citation_context", "competitor_citations"]
                },
                "perplexity": {
                    "track": True,
                    "check_frequency": "daily",
                    "queries_to_monitor": queries[:10],
                    "metrics": ["cited", "citation_position", "source_url", "answer_context"]
                },
                "chatgpt": {
                    "track": True,
                    "check_frequency": "weekly",
                    "queries_to_monitor": queries[:5],
                    "metrics": ["cited", "citation_context", "answer_quality"]
                },
                "gemini": {
                    "track": True,
                    "check_frequency": "daily",
                    "queries_to_monitor": queries[:10],
                    "metrics": ["knowledge_panel", "ai_overview_citation", "entity_association"]
                },
                "copilot": {
                    "track": True,
                    "check_frequency": "weekly",
                    "queries_to_monitor": queries[:5],
                    "metrics": ["cited", "citation_position", "bing_index_status"]
                }
            },
            "tracking_methods": [
                "Automated daily SERP checks via API",
                "Manual weekly verification for accuracy",
                "Competitor citation monitoring",
                "Citation context and sentiment analysis",
                "Historical tracking with screenshot evidence"
            ],
            "data_collection": {
                "screenshots": "Daily captures of AI Overview and citation states",
                "position_tracking": "Daily position monitoring for target queries",
                "citation_logs": "Timestamped records of all citation appearances",
                "competitor_benchmarks": "Weekly competitor citation comparison"
            }
        }

    def _design_monitoring_dashboard(self, url: str, queries: List[str]) -> Dict[str, Any]:
        """Design monitoring dashboard."""
        return {
            "dashboard_sections": [
                {
                    "section": "Citation Status Overview",
                    "widgets": [
                        "AI Overview citation status (present/absent)",
                        "Perplexity citation status",
                        "ChatGPT citation status",
                        "Gemini citation status",
                        "Overall citation health score"
                    ]
                },
                {
                    "section": "Position Tracking",
                    "widgets": [
                        "Daily position chart for each target query",
                        "Position change alerts",
                        "SERP feature ownership tracking",
                        "Competitor position comparison"
                    ]
                },
                {
                    "section": "Citation Context",
                    "widgets": [
                        "Citation snippet display",
                        "Surrounding text context",
                        "Competitor citation comparison",
                        "Citation sentiment analysis"
                    ]
                },
                {
                    "section": "Competitor Monitoring",
                    "widgets": [
                        "Competitor citation frequency",
                        "Content gap analysis",
                        "New competitor content alerts",
                        "Citation source comparison"
                    ]
                },
                {
                    "section": "Performance Metrics",
                    "widgets": [
                        "Impression trends from GSC",
                        "Click-through rate changes",
                        "Citation-driven traffic estimates",
                        "ROI tracking for GEO efforts"
                    ]
                }
            ],
            "refresh_frequency": "Real-time for citation checks, daily for position tracking",
            "access_control": "Role-based access for content, SEO, and dev teams"
        }

    def _configure_alert_system(self, url: str, queries: List[str]) -> Dict[str, Any]:
        """Configure alert system for citation changes."""
        return {
            "alert_types": [
                {
                    "alert": "Citation Lost",
                    "trigger": "URL removed from AI Overview or LLM citation",
                    "severity": "CRITICAL",
                    "notification": "Immediate email + Slack",
                    "response_protocol": "Review competitor content, update cited section within 48 hours"
                },
                {
                    "alert": "Citation Gained",
                    "trigger": "URL newly cited in AI Overview or LLM",
                    "severity": "POSITIVE",
                    "notification": "Daily digest email",
                    "response_protocol": "Document what triggered citation, replicate for other queries"
                },
                {
                    "alert": "Position Drop",
                    "trigger": "Organic position drops 3+ positions",
                    "severity": "HIGH",
                    "notification": "Daily email alert",
                    "response_protocol": "Review content freshness, competitor updates, algorithm changes"
                },
                {
                    "alert": "Competitor Citation",
                    "trigger": "Competitor gains citation for tracked query",
                    "severity": "MEDIUM",
                    "notification": "Weekly digest",
                    "response_protocol": "Analyze competitor content changes, identify new data/angles added"
                },
                {
                    "alert": "Content Decay",
                    "trigger": "Impressions drop 15%+ over 30 days",
                    "severity": "HIGH",
                    "notification": "Weekly report",
                    "response_protocol": "Generate refresh brief with specific sections to update"
                },
                {
                    "alert": "AI Overview Format Change",
                    "trigger": "AI Overview structure changes for tracked query",
                    "severity": "MEDIUM",
                    "notification": "Weekly digest",
                    "response_protocol": "Re-optimize content structure for new format"
                }
            ],
            "notification_channels": ["email", "slack", "webhook", "dashboard"],
            "escalation_policy": "CRITICAL alerts escalate to content lead within 4 hours"
        }

    def _build_reporting_framework(self, url: str, queries: List[str]) -> Dict[str, Any]:
        """Build reporting framework."""
        return {
            "report_types": [
                {
                    "report": "Daily Citation Snapshot",
                    "frequency": "daily",
                    "recipients": ["content_team", "seo_team"],
                    "contents": ["citation_status", "position_changes", "competitor_movements"]
                },
                {
                    "report": "Weekly Performance Summary",
                    "frequency": "weekly",
                    "recipients": ["marketing_lead", "content_lead"],
                    "contents": ["citation_trends", "position_trends", "traffic_impact", "competitor_analysis"]
                },
                {
                    "report": "Monthly GEO Impact Report",
                    "frequency": "monthly",
                    "recipients": ["executive_team", "marketing_lead"],
                    "contents": ["citation_growth", "traffic_from_ai", "roi_analysis", "strategic_recommendations"]
                },
                {
                    "report": "Quarterly Strategy Review",
                    "frequency": "quarterly",
                    "recipients": ["all_stakeholders"],
                    "contents": ["comprehensive_performance", "competitor_benchmarking", "strategy_adjustments", "resource_allocation"]
                }
            ],
            "kpi_tracking": {
                "primary_kpis": [
                    "AI Overview citation rate (%)",
                    "Perplexity citation frequency",
                    "Organic click-through rate",
                    "Citation-driven estimated traffic"
                ],
                "secondary_kpis": [
                    "Position for target queries",
                    "Impression volume",
                    "Content freshness score",
                    "Citation context quality"
                ]
            }
        }

    def _generate_implementation_checklist(self, tracking_config: Dict) -> List[Dict[str, str]]:
        """Generate implementation checklist."""
        return [
            {"task": "Set up daily SERP monitoring API", "priority": "CRITICAL", "deadline": "Day 1"},
            {"task": "Configure AI Overview tracking for all target queries", "priority": "CRITICAL", "deadline": "Day 1"},
            {"task": "Set up Perplexity citation monitoring", "priority": "HIGH", "deadline": "Day 2"},
            {"task": "Configure alert notifications (email + Slack)", "priority": "HIGH", "deadline": "Day 2"},
            {"task": "Set up weekly competitor comparison reports", "priority": "MEDIUM", "deadline": "Week 1"},
            {"task": "Create monitoring dashboard", "priority": "MEDIUM", "deadline": "Week 1"},
            {"task": "Configure monthly reporting templates", "priority": "LOW", "deadline": "Week 2"},
            {"task": "Set up automated screenshot evidence collection", "priority": "MEDIUM", "deadline": "Week 1"}
        ]
