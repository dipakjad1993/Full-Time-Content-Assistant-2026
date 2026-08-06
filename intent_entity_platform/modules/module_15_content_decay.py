"""
Module 15: Post-Publish Delta & Content Decay Engine
Monitors content performance decay and generates refresh briefs.
"""
import re
from typing import List, Dict, Any
from datetime import datetime, timedelta
from ..utils.web_data import wayback_snapshots


class ContentDecayEngine:
    """Module 15: Post-Publish Delta & Content Decay Engine"""

    def __init__(self):
        self.module_id = "M15"
        self.module_name = "Post-Publish Delta & Content Decay Engine"

    def analyze(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Full content decay analysis pipeline."""
        url = inputs.get("url", "")
        publish_date = inputs.get("publish_date", "")
        entity = inputs.get("primary_entity", "content strategy")
        gsc_data = inputs.get("gsc_data", {})
        competitor_data = inputs.get("competitor_data", [])

        _url_data = inputs.get("_url_data", {})
        url_page_text = _url_data.get("page_text", "")
        url_title = _url_data.get("title", "")
        url_h1 = _url_data.get("h1", "")
        url_h2s = _url_data.get("h2s", [])
        url_word_count = _url_data.get("word_count", 0)
        url_has_schema = _url_data.get("has_schema", False)
        url_image_count = _url_data.get("image_count", 0)
        url_link_count = _url_data.get("link_count", 0)
        url_url = _url_data.get("url", url)

        url_freshness_analysis = self._analyze_url_freshness_signals(_url_data) if _url_data else {}

        decay_indicators = self._detect_decay_indicators(inputs)
        gsc_impairments = self._analyze_gsc_impairments(gsc_data)
        competitor_monitoring = self._monitor_competitor_gains(competitor_data, entity)
        refresh_brief = self._generate_refresh_brief(inputs, decay_indicators, gsc_impairments)
        content_freshness = self._assess_content_freshness(inputs, publish_date)
        decay_prediction = self._predict_decay_trajectory(inputs, decay_indicators)
        health_score = self._calculate_health_score(decay_indicators, gsc_impairments, content_freshness)
        recommendations = self._generate_recommendations(decay_indicators, gsc_impairments, refresh_brief)

        refresh_brief["priority_actions"] = self._generate_priority_actions(decay_indicators, content_freshness)
        refresh_brief["content_gap_opportunities"] = self._identify_content_gaps(entity, inputs)
        refresh_brief["internal_link_refresh"] = self._suggest_internal_link_updates(inputs)

        result = {
            "module": self.module_id,
            "module_name": self.module_name,
            "url_analyzed": url_url or url or "Not provided - using sample analysis",
            "analysis_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "decay_indicators": decay_indicators,
            "gsc_impairments": gsc_impairments,
            "competitor_monitoring": competitor_monitoring,
            "refresh_brief": refresh_brief,
            "content_freshness": content_freshness,
            "decay_prediction": decay_prediction,
            "overall_health_score": health_score,
            "recommendations": recommendations,
            "url_content_analysis": url_freshness_analysis if _url_data else {
                "status": "NO_URL_DATA",
                "message": "Provide _url_data for real content decay analysis"
            },
            "content_lifecycle": {
                "current_phase": content_freshness.get("freshness_status", "UNKNOWN"),
                "estimated_remaining_shelf_life": self._estimate_shelf_life(decay_indicators, content_freshness),
                "optimal_refresh_frequency": "Every 3-6 months for competitive niches, 6-12 for evergreen",
                "last_significant_update": publish_date or "Unknown",
                "days_since_publish": self._calculate_days_since(publish_date),
                "content_half_life_estimate": f"{self._estimate_half_life(decay_indicators)} days"
            },
            "seasonal_patterns": {
                "seasonal_sensitivity": "MODERATE" if not gsc_data else "HIGH - Analyze GSC trends",
                "recommended_update_windows": ["Q1 (January-March)", "Q3 (July-September)"],
                "holiday_impact": "Monitor for 2-4 weeks before major holidays",
                "industry_trend_alignment": "Regular review against current best practices"
            },
            "recovery_strategy": {
                "immediate_actions": [
                    "Update statistics and data points to current year",
                    "Add recent case studies and examples",
                    "Refresh meta descriptions with current year",
                    "Review and update internal links"
                ],
                "short_term_actions": [
                    "Add new sections addressing emerging subtopics",
                    "Include current expert quotes and opinions",
                    "Update screenshots and visual assets",
                    "Refresh FAQ schema with current questions"
                ],
                "long_term_strategy": [
                    "Monitor competitor content for 90 days",
                    "Track ranking changes weekly",
                    "Conduct quarterly content audits",
                    "Build topical authority through content clusters"
                ]
            },
            "implementation_steps": [
                "Step 1: Export current GSC performance data (last 90 days) for the URL and compare against the prior 90-day window to quantify decay",
                "Step 2: Audit every statistic, percentage, and data point in the article - replace any data older than 12 months with 2026 figures from authoritative sources",
                "Step 3: Add or update the dateModified field in the page's JSON-LD Article schema to today's date",
                "Step 4: Rewrite the meta description to include the current year and a compelling value proposition that differentiates from competitors",
                "Step 5: Add 2-3 new expert quotes or citations from recognized authorities published within the last 6 months",
                "Step 6: Insert a new H2 section covering emerging subtopics or recent developments identified in competitor gap analysis",
                "Step 7: Update all internal links to point to the most current and relevant pillar/cluster pages on your site",
                "Step 8: Add fresh screenshots, charts, or visual assets that reflect the latest data or UI changes",
                "Step 9: Refresh FAQ schema markup by adding 2-3 new questions sourced from People Also Ask and recent user queries",
                "Step 10: Submit the updated URL to Google Indexing API and Bing IndexNow for immediate re-crawl",
                "Step 11: Monitor GSC performance daily for 14 days post-refresh to track recovery trajectory",
                "Step 12: Schedule a follow-up content audit in 90 days to prevent future decay"
            ],
            "where_to_add": [
                "Place updated JSON-LD Article schema with new dateModified in the <head> via <script type='application/ld+json'> tag",
                "Insert expert quotes as blockquotes within relevant H2 sections of the article body",
                "Add the refreshed meta description in the <head> <meta name='description'> tag",
                "Place new H2 subsections after the most relevant existing section to maintain logical flow",
                "Update internal links inline within body paragraphs using descriptive anchor text",
                "Replace hero/intro statistics within the first 100 words of the article",
                "Add FAQ schema in a dedicated <script type='application/ld+json'> block in <head>",
                "Place updated screenshots in <figure> tags with descriptive <figcaption> elements",
                "Update hreflang tags in <head> if localized versions exist",
                "Add refreshed open graph and Twitter card meta tags in <head> for social sharing"
            ],
            "detailed_analysis": {
                "decay_statistics": {
                    "average_content_half_life": "180-365 days depending on niche competitiveness",
                    "competitive_niche_decay_rate": "Content in SaaS/tech niches decays 40% faster than average",
                    "typical_ctr_decline_without_refresh": "15-35% over 12 months for evergreen content",
                    "position_drop_pattern": "Average position drops 2-5 positions per quarter without updates",
                    "impression_loss_compound_rate": "Cumulative 10-20% impression loss per quarter when decay is unchecked"
                },
                "industry_benchmarks": {
                    "healthy_freshness_score": "Above 0.6 (content updated within 90 days)",
                    "optimal_refresh_frequency": "Every 90-180 days for competitive topics, 180-365 for evergreen",
                    "target_health_score": "Above 0.8 for top-3 ranking content",
                    "gsc_ctr_benchmark": "Average CTR varies by position: Pos 1 = 28-35%, Pos 2-3 = 12-18%, Pos 4-10 = 3-8%",
                    "competitor_monitoring_frequency": "Weekly for top 5 competitors, monthly for broader market"
                },
                "expert_recommendations": [
                    "Treat content as a living asset - schedule quarterly reviews for all URLs ranking in top 20",
                    "Prioritize refreshes for URLs with high impressions but declining CTR (low-hanging fruit)",
                    "Add unique data or research findings that competitors cannot easily replicate",
                    "Build content clusters where refreshed pillar pages link to updated cluster content",
                    "Monitor Google algorithm updates and align refresh timing to avoid turbulence"
                ],
                "common_mistakes": [
                    "Only refreshing the title without updating body content signals neglect to search engines",
                    "Adding thin content (a few sentences) does not reset decay - provide substantial value",
                    "Ignoring internal link equity flow when refreshing - broken or outdated links compound decay",
                    "Refreshing too frequently (weekly) can trigger re-evaluation volatility - space updates 30+ days apart",
                    "Forgetting to update schema dateModified and datePublished when making significant changes"
                ],
                "success_metrics": [
                    "Track CTR recovery within 14-30 days post-refresh (target: 10%+ improvement)",
                    "Monitor average position improvement within 30-60 days",
                    "Measure impression growth week-over-week for 4 weeks post-update",
                    "Track returning visitor rate as a signal of renewed content relevance",
                    "Monitor featured snippet and AI Overview inclusion after refresh"
                ]
            }
        }
        return result

    def _analyze_url_freshness_signals(self, url_data: Dict) -> Dict[str, Any]:
        """Deeply analyze actual page content for freshness signals and decay indicators."""
        page_text = url_data.get("page_text", "")
        title = url_data.get("title", "")
        h1 = url_data.get("h1", "")
        h2s = url_data.get("h2s", [])
        word_count = url_data.get("word_count", 0)
        has_schema = url_data.get("has_schema", False)
        images = url_data.get("images", [])
        links = url_data.get("links", [])
        url = url_data.get("url", "")

        # REAL historical data from the Wayback Machine
        wayback = wayback_snapshots(url, limit=8)
        snapshots = wayback.get("snapshots", [])
        first_snapshot_ts = snapshots[0]["timestamp"] if snapshots else None
        last_snapshot_ts = snapshots[-1]["timestamp"] if snapshots else None
        wayback_age_days = None
        if last_snapshot_ts and first_snapshot_ts:
            try:
                from datetime import datetime as _dt
                def _parse_ts(t):
                    return _dt.strptime(t, "%Y%m%d%H%M%S")
                wayback_age_days = max(0, (_parse_ts(last_snapshot_ts) - _parse_ts(first_snapshot_ts)).days)
            except Exception:
                wayback_age_days = None
        wayback_available = wayback.get("ok", False)
        last_snapshot_recency_days = None
        if last_snapshot_ts:
            try:
                from datetime import datetime as _dt
                last_dt = _dt.strptime(last_snapshot_ts, "%Y%m%d%H%M%S")
                last_snapshot_recency_days = max(0, (_dt.utcnow() - last_dt).days)
            except Exception:
                last_snapshot_recency_days = None

        date_patterns = [
            r'January\s+\d{4}', r'February\s+\d{4}', r'March\s+\d{4}',
            r'April\s+\d{4}', r'May\s+\d{4}', r'June\s+\d{4}',
            r'July\s+\d{4}', r'August\s+\d{4}', r'September\s+\d{4}',
            r'October\s+\d{4}', r'November\s+\d{4}', r'December\s+\d{4}',
            r'\d{4}-\d{2}-\d{2}', r'\d{2}/\d{2}/\d{4}',
            r'Updated\s+\w+\s+\d{4}', r'Last updated[:\s]+',
            r'Published\s+\w+\s+\d{4}', r'As of\s+\w+\s+\d{4}'
        ]
        date_mentions = []
        for pattern in date_patterns:
            matches = re.findall(pattern, page_text)
            date_mentions.extend(matches)
        current_year_mentions = len(re.findall(r'202[5-6]', page_text))
        outdated_year_mentions = len(re.findall(r'202[0-3]', page_text))
        outdated_data_patterns = [
            r'(?:according to|data from|report from|study from|research from)\s+(?:20[0-2]\d)',
            r'\d{4}\s+(?:survey|study|report|research|analysis)',
            r'(?:last year|previous year|this year)'
        ]
        outdated_data_found = []
        for pattern in outdated_data_patterns:
            matches = re.findall(pattern, page_text, re.IGNORECASE)
            outdated_data_found.extend(matches)

        stale_content_signals = []
        if wayback_available and wayback_age_days is not None and wayback_age_days > 730:
            stale_content_signals.append(
                f"Wayback Machine shows first capture {first_snapshot_ts} and no newer significant change in {wayback_age_days} days")
        if last_snapshot_recency_days is not None and last_snapshot_recency_days > 365:
            stale_content_signals.append(
                f"Wayback Machine's most recent snapshot is {last_snapshot_recency_days} days old - content may not be updated")
        if outdated_year_mentions > 0:
            stale_content_signals.append(f"Found {outdated_year_mentions} references to outdated years (2020-2023)")
        if outdated_data_found:
            stale_content_signals.append(f"Found {len(outdated_data_found)} references to potentially outdated data sources")
        if word_count < 300:
            stale_content_signals.append(f"Thin content: only {word_count} words (target 1500+ for competitive topics)")
        if word_count > 5000:
            stale_content_signals.append(f"Very long content ({word_count} words) - may need pruning or restructuring")

        refresh_indicators = []
        if current_year_mentions == 0 and word_count > 200:
            refresh_indicators.append("No current year (2025-2026) mentions - content appears outdated")
        if not has_schema:
            refresh_indicators.append("Missing structured data schema - add Article or BlogPosting schema")
        if len(h2s) < 2 and word_count > 1000:
            refresh_indicators.append(f"Only {len(h2s)} H2 sections for {word_count} words - needs better content structure")
        if len(images) < 2 and word_count > 800:
            refresh_indicators.append(f"Only {len(images)} images for {word_count} words - add visual assets")
        if len(links) < 3 and word_count > 500:
            refresh_indicators.append(f"Only {len(links)} links found - add internal and external links")
        if len(date_mentions) == 0:
            refresh_indicators.append("No date mentions found - add temporal signals for freshness")

        freshness_score = 1.0
        if wayback_available and wayback_age_days is not None and wayback_age_days > 730:
            freshness_score -= 0.2
        if last_snapshot_recency_days is not None and last_snapshot_recency_days > 365:
            freshness_score -= 0.25
        if outdated_year_mentions > 3:
            freshness_score -= 0.3
        elif outdated_year_mentions > 0:
            freshness_score -= 0.15
        if current_year_mentions == 0:
            freshness_score -= 0.2
        if not has_schema:
            freshness_score -= 0.1
        if len(date_mentions) == 0:
            freshness_score -= 0.1
        if word_count < 300:
            freshness_score -= 0.2
        freshness_score = max(0.0, freshness_score)

        refresh_actions = []
        if outdated_year_mentions > 0:
            refresh_actions.append({
                "action": "Update outdated year references",
                "detail": f"Replace {outdated_year_mentions} outdated year mentions with current data",
                "priority": "HIGH"
            })
        if current_year_mentions == 0 and word_count > 200:
            refresh_actions.append({
                "action": "Add current year references",
                "detail": "Include 2025/2026 dates to signal freshness",
                "priority": "HIGH"
            })
        if not has_schema:
            refresh_actions.append({
                "action": "Add structured data schema",
                "detail": "Implement Article or BlogPosting JSON-LD schema with dateModified",
                "priority": "MEDIUM"
            })
        if len(images) < 2 and word_count > 800:
            refresh_actions.append({
                "action": "Add visual assets",
                "detail": f"Page has {len(images)} images for {word_count} words - add charts, screenshots, or diagrams",
                "priority": "MEDIUM"
            })
        if len(links) < 3 and word_count > 500:
            refresh_actions.append({
                "action": "Add internal and external links",
                "detail": f"Only {len(links)} links found - target 5-8 contextual links",
                "priority": "MEDIUM"
            })

        return {
            "url_analyzed": url,
            "page_word_count": word_count,
            "page_title": title,
            "page_h1": h1,
            "h2_section_count": len(h2s),
            "h2_headings": h2s,
            "date_mentions_found": date_mentions,
            "date_mention_count": len(date_mentions),
            "current_year_references": current_year_mentions,
            "outdated_year_references": outdated_year_mentions,
            "outdated_data_sources": outdated_data_found,
            "stale_content_signals": stale_content_signals,
            "stale_signal_count": len(stale_content_signals),
            "freshness_indicators": refresh_indicators,
            "freshness_indicator_count": len(refresh_indicators),
            "computed_freshness_score": round(freshness_score, 3),
            "freshness_tier": (
                "FRESH" if freshness_score > 0.8 else
                "AGING" if freshness_score > 0.5 else
                "STALE" if freshness_score > 0.3 else
                "OUTDATED"
            ),
            "refresh_actions": refresh_actions,
            "schema_present": has_schema,
            "image_count": len(images),
            "link_count": len(links),
            "content_structure_score": round(min(1.0, len(h2s) / max(1, word_count / 500)), 3),
            "temporal_signal_strength": (
                "STRONG" if len(date_mentions) >= 3 else
                "MODERATE" if len(date_mentions) >= 1 else
                "WEAK - No dates detected"
            ),
            "detailed_findings": {
                "freshness_summary": f"Page has {current_year_mentions} current-year references, {outdated_year_mentions} outdated year mentions, {len(date_mentions)} date mentions, and {'structured data' if has_schema else 'no structured data'}",
                "content_age_estimate": (
                    f"Wayback Machine first capture: {first_snapshot_ts}" if wayback_available else
                    "Cannot determine exact publish date from content alone"
                ),
                "recommended_refresh_priority": "HIGH" if freshness_score < 0.4 else "MEDIUM" if freshness_score < 0.7 else "LOW",
                "content_quality_signal": f"{word_count} words, {len(h2s)} sections, {len(images)} images, {len(links)} links",
                "freshness_risk_factors": stale_content_signals + refresh_indicators
            },
            "wayback_archive_analysis": {
                "archive_checked": wayback_available,
                "archive_error": wayback.get("error"),
                "snapshot_count": len(snapshots),
                "first_snapshot": first_snapshot_ts,
                "last_snapshot": last_snapshot_ts,
                "archive_age_days": wayback_age_days,
                "last_snapshot_recency_days": last_snapshot_recency_days,
                "snapshots": snapshots,
            }
        }

    def _detect_decay_indicators(self, inputs: Dict) -> Dict[str, Any]:
        """Detect content decay indicators."""
        gsc_data = inputs.get("gsc_data", {})
        indicators = []
        ctr_trend = gsc_data.get("ctr_trend", [])
        if len(ctr_trend) >= 2:
            recent_ctr = sum(ctr_trend[-7:]) / max(1, len(ctr_trend[-7:]))
            older_ctr = sum(ctr_trend[:7]) / max(1, len(ctr_trend[:7])) if len(ctr_trend) >= 14 else recent_ctr
            if recent_ctr < older_ctr * 0.85:
                indicators.append({
                    "indicator": "CTR_DECLINE",
                    "severity": "HIGH",
                    "detail": f"CTR dropped {((older_ctr - recent_ctr) / max(0.001, older_ctr) * 100):.1f}%",
                    "metric": f"Recent CTR: {recent_ctr:.2f}% vs Previous: {older_ctr:.2f}%"
                })
        impressions_trend = gsc_data.get("impressions_trend", [])
        if len(impressions_trend) >= 2:
            recent_imp = sum(impressions_trend[-7:]) / max(1, len(impressions_trend[-7:]))
            older_imp = sum(impressions_trend[:7]) / max(1, len(impressions_trend[:7])) if len(impressions_trend) >= 14 else recent_imp
            if recent_imp < older_imp * 0.8:
                indicators.append({
                    "indicator": "IMPRESSION_DECLINE",
                    "severity": "HIGH",
                    "detail": f"Impressions dropped {((older_imp - recent_imp) / max(1, older_imp) * 100):.1f}%",
                    "metric": f"Recent: {recent_imp:.0f} vs Previous: {older_imp:.0f}"
                })
        position_trend = gsc_data.get("position_trend", [])
        if len(position_trend) >= 2:
            recent_pos = sum(position_trend[-7:]) / max(1, len(position_trend[-7:]))
            older_pos = sum(position_trend[:7]) / max(1, len(position_trend[:7])) if len(position_trend) >= 14 else recent_pos
            if recent_pos > older_pos * 1.2:
                indicators.append({
                    "indicator": "POSITION_DROP",
                    "severity": "CRITICAL",
                    "detail": f"Average position dropped from {older_pos:.1f} to {recent_pos:.1f}",
                    "metric": f"Position change: +{(recent_pos - older_pos):.1f} positions"
                })
        if not indicators:
            indicators.append({
                "indicator": "NO_DECAY_DETECTED",
                "severity": "POSITIVE",
                "detail": "No significant decay indicators detected",
                "metric": "Content performing within expected parameters"
            })
        return {
            "indicators": indicators,
            "total_indicators": len(indicators),
            "critical_count": sum(1 for i in indicators if i["severity"] == "CRITICAL"),
            "high_count": sum(1 for i in indicators if i["severity"] == "HIGH"),
            "decay_status": (
                "NO_DECAY" if all(i["severity"] == "POSITIVE" for i in indicators) else
                "CRITICAL_DECAY" if any(i["severity"] == "CRITICAL" for i in indicators) else
                "HIGH_DECAY" if any(i["severity"] == "HIGH" for i in indicators) else
                "MODERATE_DECAY"
            )
        }

    def _analyze_gsc_impairments(self, gsc_data: Dict) -> Dict[str, Any]:
        """Analyze Google Search Console impairments."""
        if not gsc_data:
            return {"impairments": [], "status": "NO_DATA"}
        impairments = []
        queries = gsc_data.get("queries", [])
        for query_data in queries:
            if query_data.get("position", 0) > 10 and query_data.get("impressions", 0) > 100:
                impairments.append({
                    "type": "LOW_POSITION_HIGH_IMPRESSION",
                    "query": query_data.get("query", ""),
                    "position": query_data.get("position", 0),
                    "impressions": query_data.get("impressions", 0),
                    "clicks": query_data.get("clicks", 0),
                    "ctr": query_data.get("ctr", 0),
                    "recommendation": "Optimize for this query - high impressions indicate demand but low position limits clicks"
                })
        pages = gsc_data.get("pages", [])
        for page_data in pages:
            ctr = page_data.get("ctr", 0)
            position = page_data.get("position", 0)
            if position < 5 and ctr < 0.02:
                impairments.append({
                    "type": "LOW_CTR_HIGH_POSITION",
                    "url": page_data.get("url", ""),
                    "position": position,
                    "ctr": ctr,
                    "impressions": page_data.get("impressions", 0),
                    "recommendation": "Optimize title tag and meta description for higher CTR"
                })
        return {
            "impairments": impairments,
            "total_impairments": len(impairments),
            "high_priority_impairments": sum(1 for i in impairments if i["type"] == "LOW_POSITION_HIGH_IMPRESSION")
        }

    def _monitor_competitor_gains(self, competitor_data: List[Dict], entity: str) -> Dict[str, Any]:
        """Monitor competitor content gains."""
        gains = []
        for comp in competitor_data:
            if comp.get("new_content"):
                gains.append({
                    "competitor": comp.get("domain", ""),
                    "new_url": comp.get("url", ""),
                    "title": comp.get("title", ""),
                    "detected_date": comp.get("publish_date", ""),
                    "potential_impact": "Monitor for ranking changes"
                })
            if comp.get("updated_content"):
                gains.append({
                    "competitor": comp.get("domain", ""),
                    "updated_url": comp.get("url", ""),
                    "changes": comp.get("changes", []),
                    "detected_date": comp.get("update_date", ""),
                    "potential_impact": "May outrank if they added unique value"
                })
        return {
            "competitor_gains": gains,
            "total_gains": len(gains),
            "monitoring_priority": "HIGH" if len(gains) > 3 else "MEDIUM" if gains else "LOW"
        }

    def _generate_refresh_brief(self, inputs: Dict, decay: Dict, impairments: Dict) -> Dict[str, Any]:
        """Generate detailed content refresh brief."""
        entity = inputs.get("primary_entity", "")
        sections_to_update = []
        if decay.get("decay_status") == "CRITICAL_DECAY":
            sections_to_update.append({
                "section": "Hero/Introduction",
                "action": "Update statistics and add current year data",
                "priority": "CRITICAL",
                "estimated_effort": "2 hours"
            })
            sections_to_update.append({
                "section": "Features/Comparison",
                "action": "Add new features and competitor data from 2026",
                "priority": "CRITICAL",
                "estimated_effort": "4 hours"
            })
        for impairment in impairments.get("impairments", [])[:3]:
            if impairment["type"] == "LOW_POSITION_HIGH_IMPRESSION":
                sections_to_update.append({
                    "section": f"Content for query: {impairment.get('query', '')}",
                    "action": f"Add dedicated section targeting '{impairment.get('query', '')}'",
                    "priority": "HIGH",
                    "estimated_effort": "3 hours"
                })
        sections_to_update.extend([
            {
                "section": "Statistics and Data Points",
                "action": "Refresh all statistics with 2026 data",
                "priority": "HIGH",
                "estimated_effort": "2 hours"
            },
            {
                "section": "Expert Quotes",
                "action": "Add 2-3 new expert perspectives",
                "priority": "MEDIUM",
                "estimated_effort": "3 hours"
            },
            {
                "section": "Schema Markup",
                "action": "Update dateModified, add new FAQ items",
                "priority": "MEDIUM",
                "estimated_effort": "1 hour"
            }
        ])
        return {
            "refresh_brief": sections_to_update,
            "total_sections": len(sections_to_update),
            "estimated_total_effort": "15-20 hours",
            "recommended_timeline": "Complete within 2 weeks",
            "expected_outcome": "Restore/improve rankings and CTR"
        }

    def _assess_content_freshness(self, inputs: Dict, publish_date: str) -> Dict[str, Any]:
        """Assess content freshness."""
        if not publish_date:
            return {"freshness_score": 0.5, "status": "UNKNOWN"}
        try:
            pub_date = datetime.strptime(publish_date[:10], "%Y-%m-%d")
            days_old = (datetime.now() - pub_date).days
        except:
            days_old = 90
        if days_old <= 30:
            freshness_score = 1.0
            status = "FRESH"
        elif days_old <= 90:
            freshness_score = 0.8
            status = "RECENT"
        elif days_old <= 180:
            freshness_score = 0.6
            status = "AGING"
        elif days_old <= 365:
            freshness_score = 0.4
            status = "STALE"
        else:
            freshness_score = 0.2
            status = "OUTDATED"
        return {
            "days_since_publish": days_old,
            "freshness_score": freshness_score,
            "freshness_status": status,
            "refresh_recommended": days_old > 90,
            "urgent_refresh_needed": days_old > 180
        }

    def _predict_decay_trajectory(self, inputs: Dict, decay: Dict) -> Dict[str, Any]:
        """Predict content decay trajectory."""
        status = decay.get("decay_status", "NO_DECAY")
        trajectory = {
            "NO_DECAY": {
                "predicted_30_days": "Stable performance expected",
                "predicted_90_days": "Monitor for seasonal fluctuations",
                "predicted_180_days": "Schedule proactive refresh",
                "action": "Continue monitoring, no immediate action needed"
            },
            "MODERATE_DECAY": {
                "predicted_30_days": "Continued gradual decline if no action taken",
                "predicted_90_days": "10-20% impression loss expected without intervention",
                "predicted_180_days": "Significant ranking loss likely",
                "action": "Schedule content refresh within 30 days"
            },
            "HIGH_DECAY": {
                "predicted_30_days": "15-30% impression/CTR loss expected",
                "predicted_90_days": "Potential page 2 ranking drop",
                "predicted_180_days": "Page may become invisible for target queries",
                "action": "Initiate content refresh immediately"
            },
            "CRITICAL_DECAY": {
                "predicted_30_days": "25-50% impression loss, position drop likely",
                "predicted_90_days": "Page may drop off first 3 pages entirely",
                "predicted_180_days": "Content may need complete rewrite",
                "action": "Emergency content refresh required within 7 days"
            }
        }
        return trajectory.get(status, trajectory["NO_DECAY"])

    def _calculate_health_score(self, decay: Dict, impairments: Dict, freshness: Dict) -> Dict[str, Any]:
        """Calculate overall content health score."""
        decay_penalty = {"NO_DECAY": 0, "MODERATE_DECAY": 0.2, "HIGH_DECAY": 0.4, "CRITICAL_DECAY": 0.6}.get(
            decay.get("decay_status", "NO_DECAY"), 0
        )
        impairment_penalty = min(0.3, impairments.get("total_impairments", 0) * 0.05)
        freshness_penalty = max(0, (1 - freshness.get("freshness_score", 0.5))) * 0.2
        health_score = max(0, 1.0 - decay_penalty - impairment_penalty - freshness_penalty)
        return {
            "health_score": round(health_score, 3),
            "health_tier": (
                "EXCELLENT" if health_score > 0.8 else
                "GOOD" if health_score > 0.6 else
                "NEEDS_ATTENTION" if health_score > 0.4 else
                "CRITICAL"
            ),
            "component_scores": {
                "decay_penalty": round(decay_penalty, 3),
                "impairment_penalty": round(impairment_penalty, 3),
                "freshness_penalty": round(freshness_penalty, 3)
            }
        }

    def _generate_recommendations(self, decay: Dict, impairments: Dict, refresh: Dict) -> List[Dict[str, str]]:
        """Generate decay mitigation recommendations."""
        recs = []
        if decay.get("decay_status") == "CRITICAL_DECAY":
            recs.append({
                "priority": "CRITICAL",
                "action": "Emergency content refresh",
                "detail": "Critical decay detected - immediate refresh required"
            })
        if decay.get("decay_status") == "HIGH_DECAY":
            recs.append({
                "priority": "HIGH",
                "action": "Schedule urgent content refresh",
                "detail": "High decay detected - refresh within 2 weeks"
            })
        if impairments.get("high_priority_impairments", 0) > 0:
            recs.append({
                "priority": "HIGH",
                "action": f"Optimize for {impairments['high_priority_impairments']} high-impression queries",
                "detail": "Queries with high impressions but low positions represent easy wins"
            })
        if refresh.get("total_sections", 0) > 0:
            recs.append({
                "priority": "MEDIUM",
                "action": f"Update {refresh['total_sections']} sections per refresh brief",
                "detail": f"Estimated effort: {refresh.get('estimated_total_effort', 'unknown')}"
            })
        return recs

    def _generate_priority_actions(self, decay_indicators: Dict, content_freshness: Dict) -> List[Dict]:
        """Generate priority actions based on decay analysis."""
        actions = []
        status = decay_indicators.get("decay_status", "NO_DECAY")
        if status == "CRITICAL_DECAY":
            actions.append({"priority": "P0", "action": "Emergency content refresh", "timeline": "Immediate", "impact": "Prevent continued ranking loss"})
            actions.append({"priority": "P0", "action": "Update all statistics and data", "timeline": "Within 24 hours", "impact": "Restore factual accuracy signals"})
        elif status == "HIGH_DECAY":
            actions.append({"priority": "P1", "action": "Schedule content refresh", "timeline": "Within 7 days", "impact": "Prevent further impression decline"})
            actions.append({"priority": "P1", "action": "Add new expert quotes", "timeline": "Within 14 days", "impact": "Improve E-E-A-T signals"})
        else:
            actions.append({"priority": "P2", "action": "Schedule routine content audit", "timeline": "Within 30 days", "impact": "Maintain competitive positioning"})
            actions.append({"priority": "P2", "action": "Update year references", "timeline": "Within 30 days", "impact": "Maintain freshness signals"})

        freshness = content_freshness.get("freshness_score", 0.5)
        if freshness < 0.3:
            actions.append({"priority": "P1", "action": "Complete content overhaul recommended", "timeline": "Within 14 days", "impact": "Content below freshness threshold"})
        actions.append({"priority": "P2", "action": "Review and update internal links", "timeline": "Within 30 days", "impact": "Maintain link equity flow"})
        actions.append({"priority": "P3", "action": "Monitor competitor updates", "timeline": "Ongoing weekly", "impact": "Stay ahead of competitive changes"})
        return actions

    def _identify_content_gaps(self, entity: str, inputs: Dict) -> List[Dict]:
        """Identify content gap opportunities."""
        gaps = [
            {"gap_type": "EMERGING_SUBTOPICS", "detail": f"New developments in {entity} from 2025-2026", "opportunity": "HIGH", "action": "Research and add new section"},
            {"gap_type": "USER_QUESTIONS", "detail": "Common questions not addressed in current content", "opportunity": "MEDIUM", "action": "Add FAQ section with schema markup"},
            {"gap_type": "VISUAL_CONTENT", "detail": "Infographics, charts, or diagrams", "opportunity": "HIGH", "action": "Create custom visual assets"},
            {"gap_type": "VIDEO_CONTENT", "detail": "Embedded video explanation or tutorial", "opportunity": "MEDIUM", "action": "Create or embed relevant video"},
            {"gap_type": "COMPARISON_CONTENT", "detail": "Comparison tables or vs. content", "opportunity": "MEDIUM", "action": "Add comparison matrix"},
            {"gap_type": "CASE_STUDIES", "detail": "Real-world implementation examples", "opportunity": "HIGH", "action": "Add 2-3 relevant case studies"},
            {"gap_type": "TOOLS_RESOURCES", "detail": "Calculators, templates, or downloadable resources", "opportunity": "HIGH", "action": "Create interactive tool or template"}
        ]
        return gaps

    def _suggest_internal_link_updates(self, inputs: Dict) -> Dict:
        """Suggest internal link updates."""
        return {
            "current_internal_links": inputs.get("internal_links_count", 0),
            "target_internal_links": "5-8 for comprehensive content",
            "suggested_additions": [
                "Link to related pillar content",
                "Link to supporting cluster content",
                "Link to recent case studies or examples",
                "Link to pricing or product pages",
                "Link to FAQ or glossary sections"
            ],
            "link_anchor_optimization": "Use descriptive, keyword-rich anchor text (varied, not exact match)",
            "priority_level": "MEDIUM"
        }

    def _estimate_shelf_life(self, decay_indicators: Dict, content_freshness: Dict) -> str:
        """Estimate remaining content shelf life."""
        status = decay_indicators.get("decay_status", "NO_DECAY")
        freshness = content_freshness.get("freshness_score", 0.5)
        if status == "CRITICAL_DECAY" or freshness < 0.2:
            return "URGENT - Content needs immediate refresh"
        elif status == "HIGH_DECAY" or freshness < 0.4:
            return "1-2 weeks before significant ranking impact"
        elif status == "MODERATE_DECAY" or freshness < 0.6:
            return "30-60 days before noticeable decline"
        else:
            return "90+ days - content is healthy"

    def _estimate_half_life(self, decay_indicators: Dict) -> int:
        """Estimate content half-life in days."""
        status = decay_indicators.get("decay_status", "NO_DECAY")
        if status == "CRITICAL_DECAY":
            return 30
        elif status == "HIGH_DECAY":
            return 60
        elif status == "MODERATE_DECAY":
            return 120
        return 180

    def _calculate_days_since(self, publish_date: str) -> int:
        """Calculate days since publish date."""
        if not publish_date:
            return 0
        try:
            pub = datetime.strptime(publish_date, "%Y-%m-%d")
            return (datetime.now() - pub).days
        except:
            return 0
