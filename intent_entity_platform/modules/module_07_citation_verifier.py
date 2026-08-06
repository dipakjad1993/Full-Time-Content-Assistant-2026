"""
Module 7: Real-Time Citation & Source Verifier (Anti-Hallucination)
Verifies claims, checks sources, and ensures citation integrity.
"""
import re
from typing import List, Dict, Any, Optional
from ..utils.text_analytics import tokenize_words, extract_entities_simple
from ..utils.web_data import verify_url as _verify_url


class CitationSourceVerifier:
    """Module 7: Real-Time Citation & Source Verifier (Anti-Hallucination)"""

    def __init__(self):
        self.module_id = "M07"
        self.module_name = "Real-Time Citation & Source Verifier (Anti-Hallucination)"

    def analyze(self, text: str, existing_sources: List[Dict] = None, url_data: Dict = None) -> Dict[str, Any]:
        """Full citation and source verification pipeline."""
        if not text.strip():
            return {"module": self.module_id, "module_name": self.module_name, "error": "No text provided"}

        claims = self._extract_claims(text)
        statistics = self._extract_statistics(text)
        sources = self._extract_source_references(text)
        fact_check = self._verify_claims(claims, statistics)
        source_quality = self._assess_source_quality(sources)
        hallucination_risk = self._assess_hallucination_risk(text, claims, statistics)
        citation_optimization = self._optimize_citations(text, sources)

        url_citation_analysis = self._analyze_url_citations(text, url_data) if url_data else None

        result = {
            "module": self.module_id,
            "module_name": self.module_name,
            "claims_extracted": claims,
            "statistics_extracted": statistics,
            "sources_identified": sources,
            "fact_check_results": fact_check,
            "source_quality_assessment": source_quality,
            "hallucination_risk_assessment": hallucination_risk,
            "citation_optimization": citation_optimization,
            "verification_summary": self._generate_verification_summary(claims, statistics, sources, fact_check),
            "recommendations": self._generate_recommendations(claims, statistics, sources, fact_check, hallucination_risk),
            "implementation_steps": self._generate_implementation_steps(claims, statistics, sources, hallucination_risk),
            "where_to_add": self._generate_where_to_add(claims, statistics, citation_optimization),
            "detailed_analysis": self._generate_detailed_analysis(claims, statistics, sources, fact_check, hallucination_risk, source_quality)
        }

        if url_citation_analysis:
            result["url_citation_analysis"] = url_citation_analysis
            result["recommendations"] = self._merge_citation_url_recommendations(result["recommendations"], url_citation_analysis)
            result["detailed_analysis"]["url_citation_insights"] = url_citation_analysis

        return result

    def _analyze_url_citations(self, text: str, url_data: Dict) -> Dict[str, Any]:
        """Deep analysis of actual URL content for citations, statistics, and factual claims."""
        word_count = url_data.get("word_count", 0)
        title = url_data.get("title", "")
        h2s = url_data.get("h2s", [])

        all_statistics = re.findall(r'\d+(?:\.\d+)?%', text)
        dollar_amounts = re.findall(r'\$(\d+(?:,\d{3})*(?:\.\d+)?)\s*(million|billion|trillion|M|B|K)?', text)
        comparative_stats = re.findall(r'(\d+(?:,\d{3})*(?:\.\d+)?)\s*(?:times|x)\s+(?:more|less|faster|slower|better|worse)', text)
        population_stats = re.findall(r'(\d+(?:,\d{3})*(?:\.\d+)?)\s*(?:million|billion|trillion|M|B|K)\s+(?:users|companies|organizations|people|customers)', text)
        change_metrics = re.findall(r'(?:increase|decrease|growth|decline|improvement|reduction)\s+(?:of|by)\s+(\d+(?:\.\d+)?)%', text)

        total_statistics = len(all_statistics) + len(dollar_amounts) + len(comparative_stats) + len(population_stats) + len(change_metrics)

        stats_with_source = 0
        stats_without_source = 0
        stat_contexts = []
        for match in re.finditer(r'\d+(?:\.\d+)?%', text):
            context_start = max(0, match.start() - 80)
            context_end = min(len(text), match.end() + 80)
            context = text[context_start:context_end].strip()
            has_source = bool(re.search(r'according|source|study|research|survey|report|published|found by', context, re.IGNORECASE))
            if has_source:
                stats_with_source += 1
            else:
                stats_without_source += 1
            stat_contexts.append({
                "statistic": match.group(),
                "context": f"...{context}...",
                "has_source": has_source,
                "position": match.start()
            })

        for match in re.finditer(r'\$(\d+(?:,\d{3})*(?:\.\d+)?)\s*(million|billion|trillion|M|B|K)?', text):
            context_start = max(0, match.start() - 80)
            context_end = min(len(text), match.end() + 80)
            context = text[context_start:context_end].strip()
            has_source = bool(re.search(r'according|source|study|research|survey|report|published|found by', context, re.IGNORECASE))
            if has_source:
                stats_with_source += 1
            else:
                stats_without_source += 1
            stat_contexts.append({
                "statistic": match.group(),
                "context": f"...{context}...",
                "has_source": has_source,
                "position": match.start()
            })

        research_claims = re.findall(
            r'(?:studies?\s+(?:show|indicate|suggest|reveal|found|demonstrate))\s+([^.]+)',
            text, re.IGNORECASE
        )

        attributed_claims = re.findall(
            r'(?:according\s+to\s+([^,]+),?\s*)([^.]+)',
            text, re.IGNORECASE
        )

        expert_claims = re.findall(
            r'(?:experts?\s+(?:say|agree|believe|suggest|recommend|note))\s+([^.]+)',
            text, re.IGNORECASE
        )

        established_claims = re.findall(
            r'(?:it\s+(?:is|has\s+been)\s+(?:proven|demonstrated|shown|established))\s+that\s+([^.]+)',
            text, re.IGNORECASE
        )

        predictive_claims = re.findall(
            r'([^.]+(?:will|would|could|should|might)\s+(?:increase|decrease|improve|reduce|enhance|lead\s+to))',
            text, re.IGNORECASE
        )

        total_claims = len(research_claims) + len(attributed_claims) + len(expert_claims) + len(established_claims) + len(predictive_claims)

        claims_with_source = len(attributed_claims)
        claims_without_source = len(research_claims) + len(expert_claims) + len(established_claims)

        source_references = re.findall(
            r'(?:according\s+to\s+([^,\.]+))|(?:source:\s*(.+?)(?:\.|$))|(?:published\s+(?:in|by)\s+([^,\.]+))|(?:as\s+(?:reported|shown|found|demonstrated)\s+by\s+([^,\.]+))|((?:https?://|www\.)[^\s<>"]+)',
            text, re.IGNORECASE
        )
        unique_sources = set()
        for s in source_references:
            for part in s:
                if part and len(part.strip()) > 3:
                    unique_sources.add(part.strip()[:100])

        high_authority_sources = 0
        for source in unique_sources:
            source_lower = source.lower()
            if any(auth in source_lower for auth in ["gartner", "forrester", "idc", "mckinsey", "harvard", "mit", "stanford", "google", "microsoft", "ieee", "nature", "science"]):
                high_authority_sources += 1
            elif any(auth in source_lower for auth in [".gov", ".edu", ".org"]):
                high_authority_sources += 1

        factual_claims = re.findall(
            r'(?:is the|is a|is an|are the|are the most|is the largest|is the first|was founded in|was established in|has \d+|serves \d+|used by \d+)',
            text, re.IGNORECASE
        )

        unsourced_assertions = 0
        for match in re.finditer(r'(?:is the|is a|are the)', text, re.IGNORECASE):
            context_start = max(0, match.start() - 40)
            context = text[context_start:match.end() + 100].strip()
            if not re.search(r'according|source|study|research|survey|report|published|cited|found', context, re.IGNORECASE):
                unsourced_assertions += 1

        citation_density = len(unique_sources) / max(1, word_count / 200)
        stat_density = total_statistics / max(1, len(h2s))

        hallucination_score = 0.0
        if total_claims > 0:
            hallucination_score += (claims_without_source / total_claims) * 0.4
        if total_statistics > 0:
            hallucination_score += (stats_without_source / total_statistics) * 0.3
        if unsourced_assertions > 5:
            hallucination_score += min(0.3, unsourced_assertions * 0.02)

        citation_issues = []
        if total_statistics > 0 and stats_without_source > 0:
            citation_issues.append(f"{stats_without_source} of {total_statistics} statistics lack source attribution. Add 'According to [Source]' format.")
        if claims_without_source > 0:
            citation_issues.append(f"{claims_without_source} research/expert claims lack attribution. Add named sources.")
        if len(unique_sources) < 3:
            citation_issues.append(f"Only {len(unique_sources)} unique source(s) found. Add 5+ authoritative sources.")
        if high_authority_sources < 2:
            citation_issues.append(f"Only {high_authority_sources} high-authority source(s) (.gov, .edu, Gartner, Forrester). Add 2-3 more.")
        if citation_density < 1:
            citation_issues.append(f"Citation density is {citation_density:.2f} per 200 words. Target: 1-2 citations per 200 words.")
        if stat_density < 2:
            citation_issues.append(f"Only {stat_density:.1f} statistics per H2 section. Target: 2-3 statistics per section.")
        if unsourced_assertions > 5:
            citation_issues.append(f"{unsourced_assertions} factual assertions lack source attribution. Verify or cite sources.")
        if len(factual_claims) > 0 and len(unique_sources) < 5:
            citation_issues.append(f"Factual claims made without sufficient supporting sources.")

        # REAL URL verification: actually resolve every URL found in the content
        url_verification = self._verify_cited_urls(text)

        return {
            "total_statistics": total_statistics,
            "percentage_statistics": len(all_statistics),
            "dollar_amounts": len(dollar_amounts),
            "comparative_statistics": len(comparative_stats),
            "population_statistics": len(population_stats),
            "change_metrics": len(change_metrics),
            "statistics_with_source": stats_with_source,
            "statistics_without_source": stats_without_source,
            "stat_source_coverage_rate": round(stats_with_source / max(1, total_statistics), 3),
            "stat_source_coverage_benchmark": "Target: 100% of statistics should have source attribution",
            "stat_density_per_h2": round(stat_density, 1),
            "stat_density_benchmark": "Target: 2-3 statistics per H2 section",
            "research_claims": len(research_claims),
            "attributed_claims": len(attributed_claims),
            "expert_claims": len(expert_claims),
            "established_claims": len(established_claims),
            "predictive_claims": len(predictive_claims),
            "total_claims": total_claims,
            "claims_with_source": claims_with_source,
            "claims_without_source": claims_without_source,
            "claim_source_coverage_rate": round(claims_with_source / max(1, total_claims), 3),
            "unique_sources_found": len(unique_sources),
            "unique_source_list": list(unique_sources)[:10],
            "high_authority_sources": high_authority_sources,
            "high_authority_benchmark": "Target: 3+ high-authority sources (Gartner, Forrester, academic)",
            "citation_density_per_200_words": round(citation_density, 2),
            "citation_density_benchmark": "Target: 1-2 citations per 200 words",
            "factual_claims_count": len(factual_claims),
            "unsourced_assertions": unsourced_assertions,
            "unsourced_assertions_benchmark": "Target: <3 unsourced assertions",
            "hallucination_risk_score": round(min(1.0, hallucination_score), 3),
            "hallucination_risk_level": (
                "CRITICAL" if hallucination_score > 0.7 else
                "HIGH" if hallucination_score > 0.5 else
                "MODERATE" if hallucination_score > 0.3 else
                "LOW" if hallucination_score > 0.1 else
                "MINIMAL"
            ),
            "statistic_details": stat_contexts[:15],
            "citation_issues": citation_issues,
            "citation_issues_count": len(citation_issues),
            "citation_quality_tier": (
                "EXCELLENT - All claims and statistics properly sourced" if len(citation_issues) == 0 else
                "GOOD - Minor citation improvements needed" if len(citation_issues) <= 2 else
                "NEEDS_WORK - Multiple citation issues" if len(citation_issues) <= 5 else
                "POOR - Major citation restructuring required"
            ),
            "specific_recommendations": self._generate_citation_url_recommendations(text, url_data),
            "url_verification": url_verification
        }

    def _verify_cited_urls(self, text: str) -> Dict[str, Any]:
        """Actually verify every URL found in the content via live HTTP checks."""
        urls = []
        for m in re.finditer(r'(?:https?://|www\.)[^\s<>"\')\]]+', text):
            u = m.group().rstrip('.,;:')
            if u and u not in [x["url"] for x in urls]:
                urls.append({"url": u, "position": m.start()})
        urls = urls[:12]
        statuses = []
        broken = []
        reachable = 0
        for item in urls:
            check = _verify_url(item["url"], timeout=10)
            entry = {
                "url": item["url"],
                "reachable": bool(check.get("reachable")),
                "status_code": check.get("status_code"),
                "final_url": check.get("final_url"),
            }
            statuses.append(entry)
            if check.get("reachable"):
                reachable += 1
            else:
                broken.append(entry)
        return {
            "urls_checked": len(statuses),
            "reachable_count": reachable,
            "broken_count": len(broken),
            "live_check_performed": len(statuses) > 0,
            "source_url_status": statuses,
            "broken_urls": broken,
            "summary": (
                f"Verified {reachable} of {len(statuses)} cited URLs are live."
                if statuses else "No URLs found in content to verify."
            )
        }

    def _generate_citation_url_recommendations(self, text: str, url_data: Dict) -> List[Dict[str, str]]:
        """Generate specific citation recommendations based on actual URL content."""
        recs = []

        total_statistics = len(re.findall(r'\d+(?:\.\d+)?%', text))
        stats_without_source = 0
        for match in re.finditer(r'\d+(?:\.\d+)?%', text):
            context_start = max(0, match.start() - 80)
            context = text[context_start:match.end() + 80].strip()
            if not re.search(r'according|source|study|research|survey|report|published|found by', context, re.IGNORECASE):
                stats_without_source += 1

        if stats_without_source > 0:
            recs.append({
                "priority": "CRITICAL",
                "action": f"Add source citations for {stats_without_source} unsourced statistics",
                "detail": f"Found {stats_without_source} statistics without source attribution. Use 'According to [Source], [statistic]' format. Unsourced statistics reduce E-E-A-T by 40-60%."
            })

        research_claims = re.findall(r'(?:studies?\s+(?:show|indicate|suggest|reveal|found|demonstrate))\s+([^.]+)', text, re.IGNORECASE)
        attributed_claims = re.findall(r'(?:according\s+to\s+([^,]+))', text, re.IGNORECASE)
        if len(research_claims) > len(attributed_claims):
            unsourced_research = len(research_claims) - len(attributed_claims)
            recs.append({
                "priority": "HIGH",
                "action": f"Add specific attribution for {unsourced_research} research claims",
                "detail": "Replace 'Studies show...' with 'A 2025 Gartner study found...' or similar specific attribution."
            })

        unique_sources = set()
        for match in re.finditer(r'(?:according\s+to\s+([^,\.]+))|((?:https?://|www\.)[^\s<>"]+)', text, re.IGNORECASE):
            for part in match.groups():
                if part and len(part.strip()) > 3:
                    unique_sources.add(part.strip()[:100])

        if len(unique_sources) < 5:
            recs.append({
                "priority": "HIGH",
                "action": f"Add {5 - len(unique_sources)}+ more authoritative source citations",
                "detail": f"Only {len(unique_sources)} unique source(s) found. Target: 5+ sources from Tier 1 (Gartner, Forrester, academic) and Tier 2 (industry publications)."
            })

        high_authority = sum(1 for s in unique_sources if any(a in s.lower() for a in ["gartner", "forrester", "idc", "mckinsey", "harvard", ".gov", ".edu"]))
        if high_authority < 2:
            recs.append({
                "priority": "HIGH",
                "action": f"Add {2 - high_authority}+ high-authority sources (.gov, .edu, Gartner, Forrester)",
                "detail": f"Only {high_authority} high-authority source(s) found. These provide strongest trust signals for E-E-A-T."
            })

        expert_claims = re.findall(r'(?:experts?\s+(?:say|agree|believe|suggest|recommend|note))\s+([^.]+)', text, re.IGNORECASE)
        if len(expert_claims) > 0:
            named_experts = re.findall(r'(?:according\s+to\s+([A-Z][a-z]+\s+[A-Z][a-z]+))', text)
            if len(named_experts) < len(expert_claims):
                recs.append({
                    "priority": "MEDIUM",
                    "action": f"Add named expert attribution for {len(expert_claims) - len(named_experts)} expert claims",
                    "detail": "Replace 'experts say...' with 'Dr. Jane Smith, VP at Gartner, says...' for verifiable credentials."
                })

        urls = re.findall(r'(?:https?://|www\.)[^\s<>"]+', text)
        broken_url_check = f"Verify {len(urls)} URL(s) are live and accessible"
        if len(urls) > 0:
            recs.append({
                "priority": "MEDIUM",
                "action": broken_url_check,
                "detail": f"Found {len(urls)} URLs in content. Verify each is accessible and links to the intended destination."
            })

        word_count = url_data.get("word_count", 0) if url_data else len(tokenize_words(text))
        citation_density = len(unique_sources) / max(1, word_count / 200)
        if citation_density < 1:
            recs.append({
                "priority": "MEDIUM",
                "action": f"Increase citation density from {citation_density:.2f} to 1-2 per 200 words",
                "detail": f"Current citation density is below optimal. Add more inline citations throughout the content."
            })

        return recs

    def _merge_citation_url_recommendations(self, existing_recs: List[Dict], url_analysis: Dict) -> List[Dict[str, str]]:
        """Merge URL-specific citation recommendations with existing recommendations."""
        url_recs = url_analysis.get("specific_recommendations", [])
        merged = list(existing_recs)
        for url_rec in url_recs:
            already_covered = False
            for existing in merged:
                if url_rec["action"][:30] in existing.get("action", ""):
                    already_covered = True
                    break
            if not already_covered:
                merged.append(url_rec)
        return merged

    def _extract_claims(self, text: str) -> List[Dict[str, Any]]:
        """Extract factual claims from text."""
        claim_patterns = [
            (r'(?:studies?\s+(?:show|indicate|suggest|reveal|found|demonstrate))\s+([^.]+)', "research_claim"),
            (r'(?:research\s+(?:shows|indicates|suggests|reveals))\s+([^.]+)', "research_claim"),
            (r'(?:according\s+to\s+([^,]+),?\s*)([^.]+)', "attributed_claim"),
            (r'(?:data\s+(?:shows|indicates|suggests|reveals))\s+([^.]+)', "data_claim"),
            (r'(?:\d+(?:\.\d+)?%\s+of\s+[^.]+(?:are|is|have|has|report|indicate|use|prefer|choose))', "statistical_claim"),
            (r'(?:experts?\s+(?:say|agree|believe|suggest|recommend|note))\s+([^.]+)', "expert_claim"),
            (r'(?:it\s+(?:is|has\s+been)\s+(?:proven|demonstrated|shown|established))\s+that\s+([^.]+)', "established_claim"),
            (r'([^.]+(?:will|would|could|should|might)\s+(?:increase|decrease|improve|reduce|enhance|lead\s+to))', "predictive_claim"),
        ]
        claims = []
        seen = set()
        for pattern, claim_type in claim_patterns:
            for m in re.finditer(pattern, text, re.IGNORECASE):
                claim_text = m.group().strip()
                if claim_text not in seen and len(claim_text) > 20:
                    seen.add(claim_text)
                    claims.append({
                        "claim_text": claim_text[:300],
                        "claim_type": claim_type,
                        "position": m.start(),
                        "verifiable": claim_type in ["research_claim", "attributed_claim", "statistical_claim", "data_claim"],
                        "requires_source": claim_type in ["research_claim", "attributed_claim", "established_claim"],
                        "priority": "HIGH" if claim_type in ["research_claim", "attributed_claim"] else "MEDIUM",
                        "verification_status": "UNVERIFIED",
                        "suggested_source_type": self._suggest_source_type(claim_type)
                    })
        return claims[:20]

    def _suggest_source_type(self, claim_type: str) -> str:
        """Suggest appropriate source type for claim type."""
        suggestions = {
            "research_claim": "Peer-reviewed journal or industry research report",
            "attributed_claim": "Named expert with verifiable credentials and profile",
            "statistical_claim": "Primary research source with methodology disclosure",
            "data_claim": "Official dataset, report, or platform analytics",
            "expert_claim": "Named expert with LinkedIn/Wikipedia verification",
            "established_claim": "Multiple corroborating authoritative sources",
            "predictive_claim": "Industry analyst report with track record"
        }
        return suggestions.get(claim_type, "Reputable industry publication")

    def _extract_statistics(self, text: str) -> List[Dict[str, Any]]:
        """Extract all statistics from text."""
        stat_patterns = [
            (r'(\d+(?:\.\d+)?)%', "percentage"),
            (r'\$(\d+(?:,\d{3})*(?:\.\d+)?)\s*(million|billion|trillion|M|B|K)?', "monetary"),
            (r'(\d+(?:,\d{3})*(?:\.\d+)?)\s*(times|x)\s+(?:more|less|faster|slower|better|worse)', "comparative"),
            (r'(\d+(?:,\d{3})*(?:\.\d+)?)\s*(million|billion|trillion|M|B|K)\s+(?:users|companies|organizations|people|customers)', "population"),
            (r'(?:increase|decrease|growth|decline|improvement|reduction)\s+(?:of|by)\s+(\d+(?:\.\d+)?)%', "change_metric"),
            (r'(\d+(?:\.\d+)?)\s*(?:hours|minutes|seconds|days|weeks|months|years)\s+(?:per|on\s+average|faster|slower)', "time_metric"),
        ]
        statistics = []
        seen = set()
        for pattern, stat_type in stat_patterns:
            for m in re.finditer(pattern, text, re.IGNORECASE):
                stat_text = m.group().strip()
                if stat_text not in seen:
                    seen.add(stat_text)
                    context_start = max(0, m.start() - 60)
                    context_end = min(len(text), m.end() + 60)
                    context = text[context_start:context_end].strip()
                    statistics.append({
                        "statistic": stat_text,
                        "type": stat_type,
                        "position": m.start(),
                        "context": f"...{context}...",
                        "has_source": bool(re.search(r'according|source|study|research|survey|report', context, re.IGNORECASE)),
                        "source_mentioned": self._extract_inline_source(context),
                        "verification_priority": "HIGH" if not re.search(r'according|source|study|research', context, re.IGNORECASE) else "MEDIUM",
                        "needs_primary_source": not bool(re.search(r'according|source|study|research|published|survey', context, re.IGNORECASE))
                    })
        return statistics[:20]

    def _extract_inline_source(self, context: str) -> str:
        """Extract inline source attribution from context."""
        patterns = [
            r'according\s+to\s+([^,\.]+)',
            r'(?:source|study|research|survey|report)\s*(?:by|from)\s+([^,\.]+)',
            r'(?:published|found|conducted)\s+(?:by|in)\s+([^,\.]+)',
        ]
        for pattern in patterns:
            m = re.search(pattern, context, re.IGNORECASE)
            if m:
                return m.group(1).strip()
        return ""

    def _extract_source_references(self, text: str) -> List[Dict[str, Any]]:
        """Extract source references from text."""
        source_patterns = [
            (r'(?:according\s+to\s+([^,\.]+(?:,\s*[^,\.]+)?))', "text_attribution"),
            (r'(?:source:\s*(.+?)(?:\.|$))', "explicit_source"),
            (r'(?:published\s+(?:in|by)\s+([^,\.]+))', "publication"),
            (r'(?:as\s+(?:reported|shown|found|demonstrated)\s+by\s+([^,\.]+))', "reporting"),
            (r'((?:https?://|www\.)[^\s<>"]+)', "url"),
        ]
        sources = []
        seen = set()
        for pattern, source_type in source_patterns:
            for m in re.finditer(pattern, text, re.IGNORECASE):
                source_text = m.group(1).strip() if m.lastindex else m.group().strip()
                if source_text not in seen and len(source_text) > 3:
                    seen.add(source_text)
                    sources.append({
                        "source": source_text[:200],
                        "type": source_type,
                        "position": m.start(),
                        "authority_score": self._estimate_authority(source_text, source_type),
                        "is_url": source_type == "url",
                        "needs_verification": source_type == "text_attribution"
                    })
        return sources[:15]

    def _estimate_authority(self, source_text: str, source_type: str) -> float:
        """Estimate source authority score."""
        high_authority = [
            "gartner", "forrester", "idc", "mckinsey", "bain", "deloitte", "pwc", "accenture",
            "harvard", "mit", "stanford", "oxford", "cambridge", "google", "microsoft", "apple",
            "amazon", "ieee", "acm", "nature", "science", "lancet", "nejm",
            "sec", "fda", "nist", "iso", "w3c", "iso"
        ]
        medium_authority = [
            "techcrunch", "venturebeat", "zdnet", "forbes", "bloomberg", "reuters",
            "hbr", "economist", "wired", "ars technica", "the verge", "mit technology review"
        ]
        source_lower = source_text.lower()
        for authority in high_authority:
            if authority in source_lower:
                return 0.9
        for authority in medium_authority:
            if authority in source_lower:
                return 0.7
        if source_type == "url":
            if any(tld in source_lower for tld in [".gov", ".edu", ".org"]):
                return 0.85
        return 0.5

    def _verify_claims(self, claims: List[Dict], statistics: List[Dict]) -> Dict[str, Any]:
        """Verify claims against available evidence."""
        unverifiable = [c for c in claims if not c["verifiable"]]
        needs_source = [c for c in claims if c["requires_source"]]
        stats_without_source = [s for s in statistics if not s["has_source"]]
        return {
            "total_claims": len(claims),
            "verifiable_claims": sum(1 for c in claims if c["verifiable"]),
            "unverifiable_claims": len(unverifiable),
            "claims_needing_sources": len(needs_source),
            "statistics_without_sources": len(stats_without_source),
            "verification_rate": round(sum(1 for c in claims if c["verifiable"]) / max(1, len(claims)), 3),
            "source_coverage_rate": round(
                sum(1 for s in statistics if s["has_source"]) / max(1, len(statistics)), 3
            ),
            "unverifiable_details": [{"claim": c["claim_text"][:100], "type": c["claim_type"]} for c in unverifiable[:5]],
            "unourced_statistics": [{"stat": s["statistic"], "context": s["context"][:100]} for s in stats_without_source[:5]],
            "overall_verification_status": (
                "FULLY_VERIFIED" if len(needs_source) == 0 and len(stats_without_source) == 0 else
                "MOSTLY_VERIFIED" if len(needs_source) <= 2 and len(stats_without_source) <= 2 else
                "PARTIALLY_VERIFIED" if len(needs_source) <= 5 else
                "SIGNIFICANT_GAPS" if len(needs_source) <= 10 else
                "CRITICAL_VERIFICATION_NEEDED"
            )
        }

    def _assess_source_quality(self, sources: List[Dict]) -> Dict[str, Any]:
        """Assess overall source quality."""
        if not sources:
            return {"average_authority": 0, "quality_tier": "NO_SOURCES", "high_authority_count": 0}

        avg_authority = sum(s["authority_score"] for s in sources) / len(sources)
        high_authority = sum(1 for s in sources if s["authority_score"] >= 0.8)
        medium_authority = sum(1 for s in sources if 0.5 <= s["authority_score"] < 0.8)
        low_authority = sum(1 for s in sources if s["authority_score"] < 0.5)

        return {
            "total_sources": len(sources),
            "average_authority_score": round(avg_authority, 3),
            "authority_distribution": {
                "high_authority_0.8_plus": high_authority,
                "medium_authority_0.5_to_0.8": medium_authority,
                "low_authority_below_0.5": low_authority
            },
            "quality_tier": (
                "EXCELLENT" if avg_authority > 0.8 else
                "GOOD" if avg_authority > 0.65 else
                "MODERATE" if avg_authority > 0.5 else
                "BELOW_AVERAGE" if avg_authority > 0.3 else
                "POOR"
            ),
            "source_diversity_score": round(min(1.0, len(set(s["type"] for s in sources)) / 4), 3),
            "recommended_additions": max(0, 5 - high_authority),
            "sources_detail": sources[:10]
        }

    def _assess_hallucination_risk(self, text: str, claims: List[Dict], statistics: List[Dict]) -> Dict[str, Any]:
        """Assess overall hallucination risk."""
        unsourced_claims = sum(1 for c in claims if c["requires_source"] and not c.get("source_mentioned"))
        unsourced_stats = sum(1 for s in statistics if s["needs_primary_source"])
        total_assertions = len(claims) + len(statistics)
        hallucination_score = (unsourced_claims + unsourced_stats) / max(1, total_assertions)
        specific_numbers = re.findall(r'\b\d+(?:\.\d+)?%?\b', text)
        specific_entities = extract_entities_simple(text)
        number_density = len(specific_numbers) / max(1, len(tokenize_words(text)))
        entity_count = sum(len(v) for v in specific_entities.values())

        return {
            "hallucination_risk_score": round(min(1.0, hallucination_score), 3),
            "risk_level": (
                "CRITICAL" if hallucination_score > 0.7 else
                "HIGH" if hallucination_score > 0.5 else
                "MODERATE" if hallucination_score > 0.3 else
                "LOW" if hallucination_score > 0.1 else
                "MINIMAL"
            ),
            "unsourced_claims_count": unsourced_claims,
            "unsourced_statistics_count": unsourced_stats,
            "specificity_metrics": {
                "specific_numbers_used": len(specific_numbers),
                "number_density": round(number_density, 4),
                "entities_mentioned": entity_count,
                "specificity_assessment": (
                    "HIGH_SPECIFICITY" if number_density > 0.03 and entity_count > 10 else
                    "MODERATE_SPECIFICITY" if number_density > 0.01 or entity_count > 5 else
                    "LOW_SPECIFICITY - Add more specific data points"
                )
            },
            "verification_actions_needed": self._prioritize_verification_actions(claims, statistics)
        }

    def _prioritize_verification_actions(self, claims: List[Dict], statistics: List[Dict]) -> List[Dict[str, str]]:
        """Prioritize verification actions."""
        actions = []
        unsourced_stats = [s for s in statistics if s["needs_primary_source"]]
        if unsourced_stats:
            actions.append({
                "priority": "CRITICAL",
                "action": f"Add primary source citations for {len(unsourced_stats)} statistics",
                "detail": "Statistics without sources undermine credibility and E-E-A-T"
            })
        unsourced_claims = [c for c in claims if c["requires_source"] and not c.get("source_mentioned")]
        if unsourced_claims:
            actions.append({
                "priority": "HIGH",
                "action": f"Add source attribution for {len(unsourced_claims)} research/expert claims",
                "detail": "Claims requiring attribution must cite named sources"
            })
        if len(claims) + len(statistics) > 0 and sum(1 for c in claims if c["verifiable"]) / max(1, len(claims)) < 0.5:
            actions.append({
                "priority": "MEDIUM",
                "action": "Increase verifiable claim ratio",
                "detail": "More than half of claims are currently unverifiable"
            })
        return actions

    def _optimize_citations(self, text: str, sources: List[Dict]) -> Dict[str, Any]:
        """Optimize citation placement and format."""
        return {
            "optimal_citation_density": "1-2 citations per 200 words",
            "current_citation_density": f"{len(sources)} citations in {len(tokenize_words(text))} words ({len(sources) / max(1, len(tokenize_words(text)) / 200):.2f} per 200 words)",
            "citation_placement_recommendations": [
                "Place primary citation immediately after statistical claims",
                "Use inline attribution for expert quotes: '[Expert Name], [Title] at [Company]'",
                "Include full source details in methodology section or footnotes",
                "Link to primary sources (not secondary reporting) where possible",
                "Use rel='nofollow' for external commercial links"
            ],
            "citation_format_recommendations": [
                "Statistics: 'According to [Source], [statistic].'",
                "Expert quotes: 'Quote from Expert Name, Title, Organization.'",
                "Research: 'A [Year] study by [Institution] found that [finding].'",
                "Data: 'Internal data from [Platform] shows [metric] [trend].'"
            ],
            "missing_citation_types": self._identify_missing_citation_types(sources)
        }

    def _identify_missing_citation_types(self, sources: List[Dict]) -> List[str]:
        """Identify missing citation types."""
        source_types = set(s["type"] for s in sources)
        missing = []
        if "url" not in source_types:
            missing.append("Direct URL citations")
        if "text_attribution" not in source_types:
            missing.append("Named source attributions")
        if "publication" not in source_types:
            missing.append("Publication references")
        return missing

    def _generate_verification_summary(self, claims: List, statistics: List, sources: List, fact_check: Dict) -> Dict[str, Any]:
        """Generate verification summary."""
        return {
            "total_claims": len(claims),
            "total_statistics": len(statistics),
            "total_sources": len(sources),
            "verification_rate": fact_check.get("verification_rate", 0),
            "source_coverage_rate": fact_check.get("source_coverage_rate", 0),
            "overall_status": fact_check.get("overall_verification_status", "UNKNOWN"),
            "critical_gaps": fact_check.get("claims_needing_sources", 0) + fact_check.get("statistics_without_sources", 0)
        }

    def _generate_recommendations(self, claims: List, statistics: List, sources: List,
                                    fact_check: Dict, hallucination_risk: Dict) -> List[Dict[str, str]]:
        """Generate verification recommendations."""
        recs = []
        if hallucination_risk.get("risk_level") in ["CRITICAL", "HIGH"]:
            recs.append({
                "priority": "CRITICAL",
                "action": "Address high hallucination risk",
                "detail": f"{hallucination_risk.get('unsourced_claims_count', 0)} unsourced claims, {hallucination_risk.get('unsourced_statistics_count', 0)} unsourced statistics"
            })
        if fact_check.get("source_coverage_rate", 0) < 0.5:
            recs.append({
                "priority": "HIGH",
                "action": "Add source citations for statistics",
                "detail": f"Only {fact_check.get('source_coverage_rate', 0) * 100:.0f}% of statistics have sources"
            })
        if len(sources) < 5:
            recs.append({
                "priority": "MEDIUM",
                "action": "Increase source diversity",
                "detail": f"Only {len(sources)} sources identified - aim for 5+ authoritative sources"
            })
        return recs

    def _generate_implementation_steps(self, claims: List, statistics: List,
                                        sources: List, hallucination_risk: Dict) -> List[str]:
        steps = []
        steps.append("Step 1: Add primary source citations for ALL statistics currently lacking source attribution")
        steps.append("Step 2: Replace unsourced research claims with specific attributions (e.g., 'A 2025 Gartner study found that...')")
        steps.append("Step 3: Add named expert attributions with verifiable credentials for all expert claims")
        steps.append("Step 4: Verify all URLs in source references are live and accessible")
        steps.append("Step 5: Replace any secondary reporting citations with links to primary sources where possible")
        steps.append("Step 6: Add methodology disclosures for all proprietary statistics (sample size, date, methodology)")
        steps.append("Step 7: Include publication dates for all cited research and reports")
        steps.append("Step 8: Add 2-3 additional Tier 1 authoritative sources (Gartner, Forrester, academic institutions)")
        steps.append("Step 9: Place statistical citations immediately after the statistic in the format 'According to [Source], [statistic]'")
        steps.append("Step 10: Add rel='nofollow' for all external commercial links to maintain trust signals")
        steps.append("Step 11: Create a 'Sources' or 'References' section at the article end with full citation details")
        steps.append("Step 12: Re-run citation verification to confirm all claims now meet minimum verification standards")
        return steps

    def _generate_where_to_add(self, claims: List, statistics: List,
                                citation_optimization: Dict) -> List[str]:
        locations = []
        locations.append("Add source citations immediately after each statistical claim within the body paragraph")
        locations.append("Place expert attributions as inline text following the quote: '[Expert Name], [Title] at [Company]'")
        locations.append("Add primary source links directly after statistics using the 'According to [Source]' format")
        locations.append("Include a dedicated 'Sources' or 'References' section at the bottom of the article")
        locations.append("Place methodology disclosures as footnotes or within a 'Methodology' subsection at the article end")
        locations.append("Add full citation details in footnotes or endnotes for academic and research references")
        locations.append("Include publication dates for all cited sources within the inline citation text")
        locations.append("Place verifiable claim links (Wikipedia, LinkedIn, official docs) within the body text as hyperlinks")
        locations.append("Add a 'Data Sources' subsection within the Expert Insights H2 section for research citations")
        locations.append("Place rel='nofollow' on external commercial links in the body content and references section")
        return locations

    def _generate_detailed_analysis(self, claims: List, statistics: List, sources: List,
                                     fact_check: Dict, hallucination_risk: Dict,
                                     source_quality: Dict) -> Dict[str, Any]:
        return {
            "claims_insights": {
                "total_claims": len(claims),
                "verifiable_claims": fact_check.get("verifiable_claims", 0),
                "claims_needing_sources": fact_check.get("claims_needing_sources", 0),
                "verification_rate": fact_check.get("verification_rate", 0),
                "benchmark": "Professional content has 90%+ verifiable claims; below 70% indicates significant trust issues",
                "statistical_range": f"Verification rate: {fact_check.get('verification_rate', 0)*100:.0f}% (target: 90%+)",
                "expert_recommendation": "Every research claim, attributed claim, and statistical claim must have a verifiable source",
                "common_mistakes": ["Making claims without source attribution", "Using vague attributions ('experts say')", "Not verifying URLs are accessible"],
                "success_metrics": ["Verification rate > 90%", "Zero unverifiable claims", "All research claims attributed"]
            },
            "statistics_insights": {
                "total_statistics": len(statistics),
                "statistics_without_sources": fact_check.get("statistics_without_sources", 0),
                "source_coverage_rate": fact_check.get("source_coverage_rate", 0),
                "benchmark": "All statistics must have source attribution; unsourced statistics reduce E-E-A-T by 40-60%",
                "statistical_range": f"Source coverage: {fact_check.get('source_coverage_rate', 0)*100:.0f}% (target: 100%)",
                "expert_recommendation": "Add inline source attribution for every statistic using 'According to [Source]' format",
                "common_mistakes": ["Presenting statistics without sources", "Citing secondary sources instead of primary", "Missing methodology disclosures"],
                "success_metrics": ["100% statistics sourced", "Primary sources for 80%+ of statistics", "Methodology disclosed for proprietary data"]
            },
            "source_quality_insights": {
                "average_authority": source_quality.get("average_authority_score", 0),
                "quality_tier": source_quality.get("quality_tier", "UNKNOWN"),
                "high_authority_count": source_quality.get("authority_distribution", {}).get("high_authority_0.8_plus", 0),
                "source_diversity_score": source_quality.get("source_diversity_score", 0),
                "benchmark": "Top content cites sources from 3+ tiers with average authority >0.7; 3+ Tier 1 sources required",
                "statistical_range": f"Source quality: {source_quality.get('quality_tier', 'UNKNOWN')} (avg authority: {source_quality.get('average_authority_score', 0):.2f})",
                "expert_recommendation": "Add 2-3 Tier 1 authoritative sources (academic, government, standards bodies) for maximum credibility",
                "common_mistakes": ["Relying only on medium-authority industry publications", "Missing government and academic sources", "Not diversifying source types"],
                "success_metrics": ["Average authority > 0.7", "3+ Tier 1 sources", "Source diversity > 75%"]
            },
            "hallucination_risk_insights": {
                "risk_score": hallucination_risk.get("hallucination_risk_score", 0),
                "risk_level": hallucination_risk.get("risk_level", "UNKNOWN"),
                "unsourced_claims": hallucination_risk.get("unsourced_claims_count", 0),
                "unsourced_statistics": hallucination_risk.get("unsourced_statistics_count", 0),
                "specificity_assessment": hallucination_risk.get("specificity_metrics", {}).get("specificity_assessment", "UNKNOWN"),
                "benchmark": "Low hallucination risk requires <10% unsourced claims; HIGH or CRITICAL risk content should not be published",
                "statistical_range": f"Hallucination risk: {hallucination_risk.get('hallucination_risk_score', 0)*100:.0f}% ({hallucination_risk.get('risk_level', 'UNKNOWN')})",
                "expert_recommendation": f"Address {hallucination_risk.get('unsourced_claims_count', 0)} unsourced claims and {hallucination_risk.get('unsourced_statistics_count', 0)} unsourced statistics before publishing",
                "common_mistakes": ["Publishing content with HIGH or CRITICAL hallucination risk", "Not verifying specific numbers and percentages", "Missing entity verification for named sources"],
                "success_metrics": ["Risk level LOW or MINIMAL", "Unsourced claims < 2", "Specificity assessment HIGH"]
            },
            "verification_summary_insights": {
                "overall_status": fact_check.get("overall_verification_status", "UNKNOWN"),
                "critical_gaps": fact_check.get("claims_needing_sources", 0) + fact_check.get("statistics_without_sources", 0),
                "benchmark": "FULLY_VERIFIED or MOSTLY_VERIFIED status required before publishing; SIGNIFICANT_GAPS content must be revised",
                "statistical_range": f"Verification status: {fact_check.get('overall_verification_status', 'UNKNOWN')} (critical gaps: {fact_check.get('claims_needing_sources', 0) + fact_check.get('statistics_without_sources', 0)})",
                "expert_recommendation": "Achieve MOSTLY_VERIFIED or FULLY_VERIFIED status by addressing all critical gaps before publication",
                "common_mistakes": ["Publishing with SIGNIFICANT_GAPS status", "Not re-running verification after fixes", "Ignoring critical verification gaps"],
                "success_metrics": ["Status: MOSTLY_VERIFIED or FULLY_VERIFIED", "Critical gaps < 2", "Verification rate > 85%"]
            }
        }
