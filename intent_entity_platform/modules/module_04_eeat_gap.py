"""
Module 4: The Experience & Gap Profiler (E-E-A-T Engine)
Identifies consensus, information gaps, and SME quote placement opportunities.
"""
import re
from typing import List, Dict, Any, Optional
from ..utils.text_analytics import (
    extract_keyphrases, tokenize_words, cosine_similarity,
    tf_idf_vectorize, text_statistics, calculate_information_gain
)


class EEATGapProfiler:
    """Module 4: The Experience & Gap Profiler (E-E-A-T Engine)"""

    def __init__(self):
        self.module_id = "M04"
        self.module_name = "The Experience & Gap Profiler (E-E-A-T Engine)"

    def analyze(self, inputs: Dict[str, Any], serp_data: Dict, existing_content: Optional[str] = None) -> Dict[str, Any]:
        """Full E-E-A-T and gap analysis pipeline with REAL competitor data."""
        seed_phrase = inputs.get("seed_phrase", "")
        primary_entity = inputs.get("primary_entity", "")
        competitor_content = inputs.get("competitor_content", [])
        sme_assets = inputs.get("sme_assets", [])
        proprietary_data = inputs.get("proprietary_data", [])
        url_data = inputs.get("_url_data", None)
        
        # NEW: Use real competitor data from live fetches
        real_competitor_pages = inputs.get("real_competitor_pages", [])
        real_content_analysis = inputs.get("real_content_analysis", {})
        real_competitor_entities = inputs.get("real_competitor_entities", {})
        real_content_gaps = inputs.get("real_content_gaps", {})
        
        # Build enhanced competitor content from real data
        enhanced_competitor_content = list(competitor_content)
        for page in real_competitor_pages:
            if page.get("fetch_success"):
                enhanced_competitor_content.append(page.get("page_text", ""))
                enhanced_competitor_content.extend(page.get("h2s", []))
                enhanced_competitor_content.extend(page.get("h3s", []))

        consensus_map = self._detect_consensus(seed_phrase, primary_entity, enhanced_competitor_content)
        information_gain = self._calculate_information_gaps(seed_phrase, primary_entity, enhanced_competitor_content)
        sme_placement = self._optimize_sme_placement(seed_phrase, primary_entity, sme_assets, enhanced_competitor_content)
        eeat_assessment = self._assess_eEat_signals(seed_phrase, primary_entity, enhanced_competitor_content, sme_assets)
        unique_value = self._identify_unique_value_propositions(enhanced_competitor_content, proprietary_data, sme_assets)
        content_differentiation = self._score_content_differentiation(seed_phrase, enhanced_competitor_content, proprietary_data)
        
        # NEW: Analyze real competitor E-E-A-T signals
        real_competitor_eeat = self._analyze_real_competitor_eeat(real_competitor_pages, real_content_analysis, real_competitor_entities, real_content_gaps)

        url_eeat_analysis = self._analyze_url_eeat(url_data, seed_phrase, primary_entity) if url_data else None

        result = {
            "module": self.module_id,
            "module_name": self.module_name,
            "consensus_detection": consensus_map,
            "information_gain_analysis": information_gain,
            "sme_placement_optimization": sme_placement,
            "eeat_assessment": eeat_assessment,
            "unique_value_identification": unique_value,
            "content_differentiation_score": content_differentiation,
            "gap_priority_matrix": self._build_gap_priority_matrix(consensus_map, information_gain, sme_placement),
            "recommendations": self._generate_recommendations(consensus_map, information_gain, eeat_assessment, sme_placement),
            "implementation_steps": self._generate_implementation_steps(consensus_map, information_gain, sme_placement, eeat_assessment),
            "where_to_add": self._generate_where_to_add(sme_placement, information_gain),
            "detailed_analysis": self._generate_detailed_analysis(consensus_map, information_gain, sme_placement, eeat_assessment, content_differentiation),
            "real_competitor_eeat_analysis": real_competitor_eeat,
            "data_source": "real_time_competitor_analysis",
            "competitors_analyzed": len([p for p in real_competitor_pages if p.get("fetch_success")])
        }

        if url_data and url_eeat_analysis:
            result["url_eeat_analysis"] = url_eeat_analysis
            result["recommendations"] = self._merge_eeat_url_recommendations(result["recommendations"], url_eeat_analysis)
            result["detailed_analysis"]["url_eeat_insights"] = url_eeat_analysis

        return result

    def _analyze_real_competitor_eeat(self, competitor_pages: List[Dict], content_analysis: Dict, competitor_entities: Dict, content_gaps: Dict) -> Dict[str, Any]:
        """Analyze real competitor E-E-A-T signals from live data."""
        if not competitor_pages:
            return {"error": "No competitor data available", "source": "N/A"}
        
        successful_pages = [p for p in competitor_pages if p.get("fetch_success")]
        if not successful_pages:
            return {"error": "No successful competitor fetches", "source": "N/A"}
        
        eeat_analysis = []
        for page in competitor_pages:
            if not page.get("fetch_success"):
                continue
            page_text = page.get("page_text", "")
            
            # Count E-E-A-T signals in real competitor content
            author_signals = len(re.findall(r'(?:by|author|written by|contributor|editor)', page_text, re.IGNORECASE))
            credential_signals = len(re.findall(r'(?:PhD|MD|MBA|certified|expert|specialist|years of experience|decade)', page_text, re.IGNORECASE))
            citation_signals = len(re.findall(r'(?:according to|source:|cited by|based on|research by|study by|published by|report by)', page_text, re.IGNORECASE))
            expertise_signals = len(re.findall(r'(?:industry|market|research|analysis|data|study|survey|benchmark|statistic)', page_text, re.IGNORECASE))
            trust_signals = len(re.findall(r'(?:guarantee|warranty|secure|verified|certified|trusted|proven|tested)', page_text, re.IGNORECASE))
            
            eeat_analysis.append({
                "url": page.get("url", ""),
                "position": page.get("position", 0),
                "eeat_signals": {
                    "author_signals": author_signals,
                    "credential_signals": credential_signals,
                    "citation_signals": citation_signals,
                    "expertise_signals": expertise_signals,
                    "trust_signals": trust_signals,
                    "total_signals": author_signals + credential_signals + citation_signals + expertise_signals + trust_signals
                },
                "has_schema": page.get("has_schema", False),
                "word_count": page.get("word_count", 0)
            })
        
        # Calculate E-E-A-T benchmarks
        avg_author_signals = sum(c["eeat_signals"]["author_signals"] for c in eeat_analysis) / len(eeat_analysis) if eeat_analysis else 0
        avg_credential_signals = sum(c["eeat_signals"]["credential_signals"] for c in eeat_analysis) / len(eeat_analysis) if eeat_analysis else 0
        avg_citation_signals = sum(c["eeat_signals"]["citation_signals"] for c in eeat_analysis) / len(eeat_analysis) if eeat_analysis else 0
        avg_expertise_signals = sum(c["eeat_signals"]["expertise_signals"] for c in eeat_analysis) / len(eeat_analysis) if eeat_analysis else 0
        avg_trust_signals = sum(c["eeat_signals"]["trust_signals"] for c in eeat_analysis) / len(eeat_analysis) if eeat_analysis else 0
        
        # Get content gaps from real data
        gaps = content_gaps.get("content_gaps", [])
        coverage = content_gaps.get("coverage_percentage", 0)
        
        return {
            "competitors_analyzed": len(eeat_analysis),
            "eeat_details": eeat_analysis,
            "benchmarks_from_real_data": {
                "avg_author_signals": round(avg_author_signals, 1),
                "avg_credential_signals": round(avg_credential_signals, 1),
                "avg_citation_signals": round(avg_citation_signals, 1),
                "avg_expertise_signals": round(avg_expertise_signals, 1),
                "avg_trust_signals": round(avg_trust_signals, 1)
            },
            "content_gaps_from_real_competitors": {
                "total_gaps_identified": len(gaps),
                "coverage_percentage": coverage,
                "top_missing_topics": gaps[:15],
                "recommendation": f"Create content for {len(gaps)} topics competitors cover that you don't"
            },
            "recommendations": [
                f"Add {max(0, 3 - int(avg_author_signals))} author attribution signals (competitors average {avg_author_signals:.1f})",
                f"Add {max(0, 5 - int(avg_credential_signals))} credential signals (competitors average {avg_credential_signals:.1f})",
                f"Add {max(0, 5 - int(avg_citation_signals))} citation signals (competitors average {avg_citation_signals:.1f})",
                f"Add {max(0, 8 - int(avg_expertise_signals))} expertise signals (competitors average {avg_expertise_signals:.1f})",
                f"Add {max(0, 3 - int(avg_trust_signals))} trust signals (competitors average {avg_trust_signals:.1f})",
                f"Create content for {len(gaps)} missing topics identified from competitor analysis"
            ],
            "data_source": "live_competitor_page_analysis"
        }

    def _analyze_url_eeat(self, url_data: Dict, seed_phrase: str, primary_entity: str) -> Dict[str, Any]:
        """Deep analysis of actual URL content for E-E-A-T signals."""
        page_text = url_data.get("page_text", "")
        title = url_data.get("title", "")
        url = url_data.get("url", "")
        word_count = url_data.get("word_count", 0)

        first_person_patterns = re.findall(r'\b(?:we|our|I|my|us|me)\b', page_text, re.IGNORECASE)
        first_person_count = len(first_person_patterns)

        specific_results = re.findall(r'\d+(?:\.\d+)?%|\$\d+[\d,.]*|\d+x|\d+\s+times', page_text)

        case_study_patterns = re.findall(r'case\s+study|client\s+story|customer\s+story|implementation\s+result|measurable\s+outcome', page_text, re.IGNORECASE)
        case_study_count = len(case_study_patterns)

        personal_experience = re.findall(
            r'in\s+my\s+experience|from\s+what\s+I\'?ve\s+seen|we\'?ve\s+found|we\s+have\s+seen|our\s+team\s+has|I\'?ve\s+worked|our\s+clients\s+have|we\s+tested|we\s+analyzed|our\s+research\s+shows',
            page_text, re.IGNORECASE
        )

        technical_terms = re.findall(r'\b(?:API|SDK|SaaS|aaS|ROI|TCO|KPI|SLA|NPS|SOC\s*2|GDPR|HIPAA|ISO\s*27001|CI\/CD|RBAC|SSO|EHR|FP&A)\b', page_text)

        research_citations = re.findall(
            r'according\s+to\s+([^,]+)|research\s+shows|study\s+finds|data\s+suggests|published\s+(?:in|by)|peer[\s-]reviewed',
            page_text, re.IGNORECASE
        )

        detailed_explanations = re.findall(
            r'(?:for\s+example|such\s+as|specifically|in\s+particular|to\s+illustrate|for\s+instance|this\s+means\s+that|this\s+includes)',
            page_text, re.IGNORECASE
        )

        process_descriptions = re.findall(
            r'(?:step\s+\d|first|second|third|fourth|fifth|finally|next|subsequently|initially|following\s+this)',
            page_text, re.IGNORECASE
        )

        authority_mentions = re.findall(
            r'(?:leading|top|recognized|award[\s-]winning|industry[\s-]leading|best[\s-]in[\s-]class|world[\s-]class|Gartner|Forrester|IDC|G2|Capterra|TrustRadius)',
            page_text, re.IGNORECASE
        )

        external_citations = re.findall(
            r'according\s+to|source:|reference:|published\s+in|cited\s+by|as\s+reported\s+by',
            page_text, re.IGNORECASE
        )

        brand_mentions = re.findall(
            r'(?:Microsoft|Google|Amazon|Apple|Salesforce|HubSpot|SAP|Oracle|Adobe|ServiceNow)',
            page_text
        )

        data_transparency = re.findall(
            r'(?:methodology|sample\s+size|survey\s+of|data\s+from|based\s+on|analysis\s+of)',
            page_text, re.IGNORECASE
        )

        date_references = re.findall(r'202[0-9]', page_text)

        author_credentials = re.findall(
            r'(?:CEO|CTO|VP|Director|Analyst|Researcher|Professor|PhD|MD|MBA|Certified|Licensed)',
            page_text
        )

        expert_quotes = re.findall(
            r'["\u201c][^"\u201d]{20,}["\u201d]\s*[-—]\s*[A-Z][a-z]+',
            page_text
        )

        trust_signals = data_transparency + external_citations + author_credentials

        experience_score = min(1.0, (first_person_count * 0.02 + len(specific_results) * 0.03 + case_study_count * 0.1 + len(personal_experience) * 0.08))
        expertise_score = min(1.0, (len(technical_terms) * 0.05 + len(research_citations) * 0.06 + len(detailed_explanations) * 0.03 + len(process_descriptions) * 0.02))
        authoritativeness_score = min(1.0, (len(authority_mentions) * 0.08 + len(external_citations) * 0.06 + len(brand_mentions) * 0.03))
        trustworthiness_score = min(1.0, (len(data_transparency) * 0.08 + len(date_references) * 0.02 + len(author_credentials) * 0.06 + len(expert_quotes) * 0.04))

        overall_eeat = experience_score * 0.25 + expertise_score * 0.30 + authoritativeness_score * 0.25 + trustworthiness_score * 0.20

        eeat_issues = []
        if experience_score < 0.3:
            eeat_issues.append(f"Weak Experience signals (score: {experience_score:.2f}). Add first-person narratives, case studies, and specific results.")
        if expertise_score < 0.3:
            eeat_issues.append(f"Weak Expertise signals (score: {expertise_score:.2f}). Add technical depth, research citations, and detailed explanations.")
        if authoritativeness_score < 0.3:
            eeat_issues.append(f"Weak Authoritativeness signals (score: {authoritativeness_score:.2f}). Add industry analyst references and external citations.")
        if trustworthiness_score < 0.3:
            eeat_issues.append(f"Weak Trustworthiness signals (score: {trustworthiness_score:.2f}). Add methodology disclosures, dates, and author credentials.")
        if first_person_count < 3:
            eeat_issues.append(f"Only {first_person_count} first-person reference(s) found. Add 5-10 first-person narratives for Experience signals.")
        if len(specific_results) < 3:
            eeat_issues.append(f"Only {len(specific_results)} specific result(s) found. Add 3+ measurable outcomes with percentage or dollar amounts.")
        if case_study_count == 0:
            eeat_issues.append("No case studies found. Include 1-2 case studies with measurable outcomes.")
        if len(research_citations) < 2:
            eeat_issues.append(f"Only {len(research_citations)} research citation(s). Add 3+ citations to peer-reviewed or authoritative sources.")
        if len(author_credentials) == 0:
            eeat_issues.append("No author credentials found. Add byline with verifiable credentials and LinkedIn profile.")
        if len(expert_quotes) == 0:
            eeat_issues.append("No expert quotes found. Add 2-3 named expert quotes with verifiable credentials.")
        if len(date_references) == 0:
            eeat_issues.append("No date references found. Add publication date and last-updated date for freshness signals.")
        if word_count < 2000:
            eeat_issues.append(f"Word count {word_count} is low. In-depth content (3000+ words) signals expertise.")

        return {
            "url": url,
            "page_title": title,
            "word_count": word_count,
            "eeat_scores": {
                "experience": round(experience_score, 3),
                "expertise": round(expertise_score, 3),
                "authoritativeness": round(authoritativeness_score, 3),
                "trustworthiness": round(trustworthiness_score, 3),
                "overall": round(overall_eeat, 3)
            },
            "eeat_tier": (
                "EXCELLENT (Top 5%)" if overall_eeat > 0.8 else
                "STRONG (Top 20%)" if overall_eeat > 0.6 else
                "MODERATE (Average)" if overall_eeat > 0.4 else
                "WEAK (Below Average)" if overall_eeat > 0.2 else
                "CRITICAL (Needs Major Improvement)"
            ),
            "signal_counts": {
                "first_person_references": first_person_count,
                "first_person_benchmark": "(General industry guidance, unverified): 5-10 first-person references per article",
                "specific_results": len(specific_results),
                "specific_results_benchmark": "(General industry guidance, unverified): 3+ measurable outcomes per article",
                "case_studies": case_study_count,
                "case_study_benchmark": "(General industry guidance, unverified): 1-2 case studies with measurable outcomes",
                "personal_experience_statements": len(personal_experience),
                "technical_terms": len(technical_terms),
                "technical_term_benchmark": "(General industry guidance, unverified): 10-20 technical terms for industry content",
                "research_citations": len(research_citations),
                "research_citation_benchmark": "(General industry guidance, unverified): 3+ citations to authoritative sources",
                "detailed_explanations": len(detailed_explanations),
                "process_descriptions": len(process_descriptions),
                "authority_mentions": len(authority_mentions),
                "external_citations": len(external_citations),
                "external_citation_benchmark": "(General industry guidance, unverified): 5+ external citations per article",
                "brand_mentions": len(brand_mentions),
                "data_transparency_signals": len(data_transparency),
                "date_references": len(date_references),
                "author_credentials": len(author_credentials),
                "expert_quotes": len(expert_quotes),
                "expert_quote_benchmark": "(General industry guidance, unverified): 2-3 named expert quotes per article"
            },
            "weakest_signal": min(
                {"experience": experience_score, "expertise": expertise_score, "authoritativeness": authoritativeness_score, "trustworthiness": trustworthiness_score},
                key=lambda k: {"experience": experience_score, "expertise": expertise_score, "authoritativeness": authoritativeness_score, "trustworthiness": trustworthiness_score}[k]
            ),
            "strongest_signal": max(
                {"experience": experience_score, "expertise": expertise_score, "authoritativeness": authoritativeness_score, "trustworthiness": trustworthiness_score},
                key=lambda k: {"experience": experience_score, "expertise": expertise_score, "authoritativeness": authoritativeness_score, "trustworthiness": trustworthiness_score}[k]
            ),
            "eeat_issues": eeat_issues,
            "eeat_issues_count": len(eeat_issues),
            "url_trust_indicators": {
                "has_https": url.startswith("https://") if url else False,
                "has_author_profile": len(author_credentials) > 0,
                "has_publication_date": len(date_references) > 0,
                "has_methodology": len(data_transparency) > 0,
                "has_expert_quotes": len(expert_quotes) > 0,
                "has_case_studies": case_study_count > 0,
                "has_research_citations": len(research_citations) > 0
            },
            "specific_recommendations": self._generate_eeat_url_recommendations(url_data, seed_phrase, primary_entity)
        }

    def _generate_eeat_url_recommendations(self, url_data: Dict, seed_phrase: str, primary_entity: str) -> List[Dict[str, str]]:
        """Generate specific E-E-A-T recommendations based on actual URL content."""
        recs = []
        page_text = url_data.get("page_text", "")
        word_count = url_data.get("word_count", 0)

        first_person_count = len(re.findall(r'\b(?:we|our|I|my|us)\b', page_text, re.IGNORECASE))
        if first_person_count < 5:
            recs.append({
                "priority": "HIGH",
                "action": f"Add {5 - first_person_count}+ more first-person references for Experience signals",
                "detail": f"Only {first_person_count} first-person reference(s) found. Add 'In our experience', 'We found that', 'Our team discovered' throughout content."
            })

        specific_results = re.findall(r'\d+(?:\.\d+)?%|\$\d+[\d,.]*', page_text)
        if len(specific_results) < 3:
            recs.append({
                "priority": "HIGH",
                "action": f"Add {3 - len(specific_results)}+ specific measurable results with percentage or dollar amounts",
                "detail": f"Only {len(specific_results)} specific result(s) found. Include 'increased by 45%', 'reduced costs by $50K', etc."
            })

        case_studies = re.findall(r'case\s+study|client\s+story|customer\s+story', page_text, re.IGNORECASE)
        if len(case_studies) == 0:
            recs.append({
                "priority": "MEDIUM",
                "action": "Add 1-2 case studies with measurable outcomes",
                "detail": "No case studies found. Include 'Client X achieved Y% improvement in Z months' format."
            })

        research_citations = re.findall(r'according\s+to|research\s+shows|study\s+finds', page_text, re.IGNORECASE)
        if len(research_citations) < 3:
            recs.append({
                "priority": "HIGH",
                "action": f"Add {3 - len(research_citations)}+ research citations from authoritative sources",
                "detail": f"Only {len(research_citations)} research citation(s). Use 'According to Gartner/Forrester/study by...' format."
            })

        author_creds = re.findall(r'(?:CEO|CTO|VP|Director|Analyst|Researcher|Professor|PhD)', page_text)
        if len(author_creds) == 0:
            recs.append({
                "priority": "HIGH",
                "action": "Add author byline with verifiable credentials and LinkedIn profile",
                "detail": "No author credentials found. Include 'Written by [Name], [Title] at [Company]' with sameAs schema link."
            })

        expert_quotes = re.findall(r'["\u201c][^"\u201d]{20,}["\u201d]', page_text)
        if len(expert_quotes) < 2:
            recs.append({
                "priority": "MEDIUM",
                "action": f"Add {2 - len(expert_quotes)}+ named expert quotes with verifiable credentials",
                "detail": "Include quotes from named experts with LinkedIn profiles and organization affiliations."
            })

        date_refs = re.findall(r'202[0-9]', page_text)
        if len(date_refs) == 0:
            recs.append({
                "priority": "MEDIUM",
                "action": "Add publication date and last-updated date prominently",
                "detail": "No date references found. Add 'Published: [Date] | Last Updated: [Date]' for freshness signals."
            })

        if word_count < 2500:
            recs.append({
                "priority": "MEDIUM",
                "action": f"Expand content from {word_count} to 2500-4000 words for deeper expertise signals",
                "detail": "In-depth content (3000+ words) signals expertise and authority to search engines."
            })

        return recs

    def _merge_eeat_url_recommendations(self, existing_recs: List[Dict], url_analysis: Dict) -> List[Dict[str, str]]:
        """Merge URL-specific E-E-A-T recommendations with existing recommendations."""
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

    def _detect_consensus(self, seed: str, entity: str, competitor_content: List[str]) -> Dict[str, Any]:
        """Identify what all competitors agree on (consensus detection)."""
        if not competitor_content:
            return {"consensus_points": [], "unique_angles": [], "consensus_score": 0}

        all_sentences = []
        for content in competitor_content:
            sentences = [s.strip() for s in re.split(r'[.!?]+', content) if len(s.strip()) > 20]
            all_sentences.extend(sentences)

        keyphrase_docs = []
        for content in competitor_content:
            kps = extract_keyphrases(content, top_n=30)
            keyphrase_docs.append(set(kp for kp, _ in kps))

        if len(keyphrase_docs) >= 2:
            all_kps = set()
            for kp_set in keyphrase_docs:
                all_kps.update(kp_set)
            kp_frequency = {}
            for kp in all_kps:
                count = sum(1 for kp_set in keyphrase_docs if kp in kp_set)
                kp_frequency[kp] = count
            consensus_kps = {kp: count for kp, count in kp_frequency.items() if count >= len(competitor_content) * 0.6}
            unique_kps = {kp: count for kp, count in kp_frequency.items() if count == 1}
        else:
            consensus_kps = {}
            unique_kps = {}

        topic_coverage = {}
        common_topics = [
            "definition", "features", "benefits", "pricing", "comparison",
            "implementation", "use_cases", "integration", "security", "support",
            "scalability", "performance", "compliance", "roi", "alternatives"
        ]
        for topic in common_topics:
            coverage_count = 0
            for content in competitor_content:
                if any(term in content.lower() for term in [topic.replace("_", " "), topic]):
                    coverage_count += 1
            topic_coverage[topic] = {
                "coverage_count": coverage_count,
                "coverage_percentage": round(coverage_count / max(1, len(competitor_content)) * 100, 1),
                "consensus_level": "universal" if coverage_count >= len(competitor_content) * 0.8 else
                                  "majority" if coverage_count >= len(competitor_content) * 0.5 else
                                  "minority" if coverage_count >= len(competitor_content) * 0.2 else "rare"
            }

        consensus_statements = self._extract_consensus_statements(all_sentences, len(competitor_content))

        return {
            "consensus_keyphrases": [{"phrase": k, "frequency": v, "competitor_count": v, "total_competitors": len(competitor_content)} for k, v in sorted(consensus_kps.items(), key=lambda x: x[1], reverse=True)[:20]],
            "unique_keyphrases": [{"phrase": k, "frequency": v} for k, v in sorted(unique_kps.items(), key=lambda x: x[1], reverse=True)[:15]],
            "topic_coverage": topic_coverage,
            "consensus_statements": consensus_statements,
            "consensus_score": round(len(consensus_kps) / max(1, len(list(set().union(*keyphrase_docs))) if keyphrase_docs else 1), 3),
            "differentiation_opportunities": len(unique_kps),
            "total_competitors_analyzed": len(competitor_content),
            "insight": f"{len(consensus_kps)} keyphrases appear across 60%+ of competitors. {len(unique_kps)} unique angles identified for differentiation."
        }

    def _extract_consensus_statements(self, sentences: List[str], num_competitors: int) -> List[Dict[str, Any]]:
        """Extract statements that appear across multiple competitors."""
        if len(sentences) < 10:
            return []

        vectors, feature_names = tf_idf_vectorize(sentences[:200], max_features=200)
        if len(vectors) < 2:
            return []

        consensus_groups = []
        processed = set()
        for i, vec_a in enumerate(vectors):
            if i in processed:
                continue
            group = [i]
            for j, vec_b in enumerate(vectors[i+1:], start=i+1):
                if j in processed:
                    continue
                sim = cosine_similarity(vec_a, vec_b)
                if sim > 0.6:
                    group.append(j)
                    processed.add(j)
            if len(group) >= 2:
                processed.add(i)
                consensus_groups.append({
                    "statement": sentences[group[0]][:200],
                    "occurrence_count": len(group),
                    "similarity_score": round(cosine_similarity(vectors[group[0]], vectors[group[1]]), 3) if len(group) > 1 else 1.0,
                    "recommendation": "REPEAT for trust signal" if len(group) >= num_competitors * 0.5 else "Consider including"
                })

        return sorted(consensus_groups, key=lambda x: x["occurrence_count"], reverse=True)[:10]

    def _calculate_information_gaps(self, seed: str, entity: str, competitor_content: List[str]) -> Dict[str, Any]:
        """Calculate information gaps and unique value opportunities."""
        if not competitor_content:
            return {"gaps": [], "gain_score": 1.0, "unique_opportunities": []}

        combined_competitor = ' '.join(competitor_content)
        gap_categories = {
            "missing_statistics": {
                "description": "Statistics and data points that no competitor provides",
                "check_patterns": [
                    r'\d+(?:\.\d+)?%', r'\$\d+', r'\d+x', r'\d+\s+times',
                    r'increase\s+of\s+\d+', r'decrease\s+of\s+\d+'
                ]
            },
            "missing_expert_perspectives": {
                "description": "Expert quotes, insights, or original research",
                "check_patterns": [
                    r'according\s+to\s+\w+\s+\w+', r'says\s+\w+\s+\w+',
                    r'expert', r'research\s+shows', r'study\s+finds'
                ]
            },
            "missing_use_cases": {
                "description": "Specific industry or scenario use cases",
                "check_patterns": [
                    r'use\s+case', r'example', r'case\s+study',
                    r'industry', r'scenario', r'situation'
                ]
            },
            "missing_comparisons": {
                "description": "Head-to-head comparisons with alternatives",
                "check_patterns": [
                    r'vs\.?', r'compared?\s+to', r'alternatives?',
                    r'better\s+than', r'worse\s+than', r'difference\s+between'
                ]
            },
            "missing_future_insights": {
                "description": "Forward-looking trends and predictions",
                "check_patterns": [
                    r'future', r'2026', r'2027', r'trend',
                    r'prediction', r'forecast', r'will\s+become'
                ]
            },
            "missing_pricing_data": {
                "description": "Specific pricing information and cost analysis",
                "check_patterns": [
                    r'price', r'cost', r'\$\d+', r'per\s+month',
                    r'annual', r'free\s+trial', r'enterprise\s+plan'
                ]
            }
        }

        gaps_found = []
        for category, config in gap_categories.items():
            mention_count = 0
            for pattern in config["check_patterns"]:
                mention_count += len(re.findall(pattern, combined_competitor, re.IGNORECASE))
            coverage_level = "well_covered" if mention_count > 20 else "partially_covered" if mention_count > 5 else "gap_opportunity"
            if coverage_level == "gap_opportunity":
                gaps_found.append({
                    "category": category,
                    "description": config["description"],
                    "competitor_mention_count": mention_count,
                    "opportunity_level": "HIGH" if mention_count == 0 else "MEDIUM",
                    "recommended_action": f"Add comprehensive {category.replace('missing_', '')} section"
                })

        unique_opportunities = []
        proprietary_signals = ["original research", "internal data", "proprietary", "our analysis", "we found", "our data"]
        has_proprietary = any(signal in combined_competitor.lower() for signal in proprietary_signals)
        if not has_proprietary:
            unique_opportunities.append({
                "opportunity": "Original Research",
                "description": "No competitor includes original research data",
                "impact": "VERY_HIGH",
                "action": "Conduct and publish proprietary survey or benchmark study"
            })

        expert_signals = ["according to dr", "professor", "phd", "researcher at", "study by"]
        expert_count = sum(1 for s in expert_signals if s in combined_competitor.lower())
        if expert_count < 3:
            unique_opportunities.append({
                "opportunity": "Named Expert Attribution",
                "description": "Limited named expert citations in competitor content",
                "impact": "HIGH",
                "action": "Include quotes from 3+ named industry experts with credentials"
            })

        unique_opportunities.append({
            "opportunity": "Interactive Content",
            "description": "Most competitors use static text only",
            "impact": "MEDIUM",
            "action": "Add calculators, comparison tools, or interactive charts"
        })

        return {
            "gaps": gaps_found,
            "total_gaps": len(gaps_found),
            "high_priority_gaps": [g for g in gaps_found if g["opportunity_level"] == "HIGH"],
            "unique_opportunities": unique_opportunities,
            "information_gain_potential": round(min(1.0, len(gaps_found) * 0.15 + len(unique_opportunities) * 0.1), 3),
            "recommended_priority": "Address HIGH opportunity gaps first, then differentiate with unique opportunities"
        }

    def _optimize_sme_placement(self, seed: str, entity: str, sme_assets: List[Dict],
                                  competitor_content: List[str]) -> Dict[str, Any]:
        """Optimize placement of SME quotes and insights within the content outline."""
        if not sme_assets:
            return {
                "placements": [],
                "sme_count": 0,
                "recommendation": "Collect at least 3 SME quotes/insights before content creation"
            }

        placements = []
        section_suggestions = [
            {"section": "Definition/Overview", "placement_type": "expert_definition", "priority": "HIGH",
             "sme_role": "Industry veteran who can validate the core definition",
             "quote_format": "Expert validates or expands on the entity definition"},
            {"section": "Benefits/Value Proposition", "placement_type": "expert_benefit_validation", "priority": "HIGH",
             "sme_role": "Practitioner who has experienced the benefits firsthand",
             "quote_format": "Expert shares specific results or outcomes"},
            {"section": "Comparison/Alternatives", "placement_type": "expert_comparison", "priority": "MEDIUM",
             "sme_role": "Analyst or consultant who has evaluated multiple options",
             "quote_format": "Expert provides nuanced comparison perspective"},
            {"section": "Implementation Guide", "placement_type": "expert_implementation", "priority": "HIGH",
             "sme_role": "Technical implementer who has deployed the solution",
             "quote_format": "Expert shares implementation tips and pitfalls"},
            {"section": "Challenges/Limitations", "placement_type": "expert_caveat", "priority": "MEDIUM",
             "sme_role": "Honest practitioner who acknowledges trade-offs",
             "quote_format": "Expert provides balanced perspective on limitations"},
            {"section": "Future Outlook", "placement_type": "expert_prediction", "priority": "MEDIUM",
             "sme_role": "Industry visionary or researcher",
             "quote_format": "Expert shares forward-looking insights"},
            {"section": "Expert Insights Section", "placement_type": "featured_expert", "priority": "CRITICAL",
             "sme_role": "Primary subject matter expert",
             "quote_format": "Extended expert perspective with credentials"}
        ]

        for i, asset in enumerate(sme_assets[:7]):
            if i < len(section_suggestions):
                suggestion = section_suggestions[i]
                placements.append({
                    "sme_name": asset.get("expert_name", f"SME_{i+1}"),
                    "sme_title": asset.get("expert_title", "Industry Expert"),
                    "target_section": suggestion["section"],
                    "placement_type": suggestion["placement_type"],
                    "priority": suggestion["priority"],
                    "sme_role": suggestion["sme_role"],
                    "quote_format": suggestion["quote_format"],
                    "content_snippet": asset.get("content", "")[:200],
                    "eEat_enhancement": "Increases Experience and Expertise signals",
                    "schema_recommendation": "Add author schema with sameAs linking to expert profile"
                })

        return {
            "placements": placements,
            "sme_count": len(sme_assets),
            "total_sections_covered": len(placements),
            "eeat_boost_estimate": round(min(1.0, len(placements) * 0.12), 3),
            "recommendation": f"Place {len(placements)} SME insights across content sections for maximum E-E-A-T impact"
        }

    def _assess_eEat_signals(self, seed: str, entity: str, competitor_content: List[str],
                               sme_assets: List[Dict]) -> Dict[str, Any]:
        """Comprehensive E-E-A-T signal assessment."""
        combined_competitor = ' '.join(competitor_content) if competitor_content else ""

        experience_signals = {
            "first_person_narrative": len(re.findall(r'\b(?:we|our|I|my|us)\b', combined_competitor, re.IGNORECASE)),
            "specific_results": len(re.findall(r'\d+(?:\.\d+)?%|\$\d+|\d+x|\d+\s+times', combined_competitor)),
            "case_study_references": len(re.findall(r'case\s+study|client\s+story|customer\s+story', combined_competitor, re.IGNORECASE)),
            "personal_experience": len(re.findall(r'in\s+my\s+experience|from\s+what\s+I\'?ve\s+seen|we\'?ve\s+found', combined_competitor, re.IGNORECASE)),
        }

        expertise_signals = {
            "technical_terminology": len(re.findall(r'\b(?:API|SDK|SaaS|aaS|ROI|TCO|KPI|SLA|NPS)\b', combined_competitor)),
            "citations_to_research": len(re.findall(r'according\s+to|research\s+shows|study\s+finds|data\s+suggests', combined_competitor, re.IGNORECASE)),
            "detailed_explanations": len(re.findall(r'(?:for\s+example|such\s+as|specifically|in\s+particular)', combined_competitor, re.IGNORECASE)),
            "process_descriptions": len(re.findall(r'(?:step\s+\d|first|second|third|finally|next)', combined_competitor, re.IGNORECASE)),
        }

        authoritativeness_signals = {
            "domain_authority_mentions": len(re.findall(r'(?:leading|top|recognized|award-winning|industry-leading)', combined_competitor, re.IGNORECASE)),
            "external_citations": len(re.findall(r'(?:according\s+to|source:|reference:|published\s+in)', combined_competitor, re.IGNORECASE)),
            "brand_mentions": len(re.findall(r'(?:Microsoft|Google|Amazon|Apple|Salesforce|HubSpot|SAP|Oracle)', combined_competitor)),
            "industry_recognition": len(re.findall(r'(?:Gartner|Forrester|IDC|G2|Capterra|TrustRadius)', combined_competitor)),
        }

        trust_signals = {
            "data_transparency": len(re.findall(r'(?:methodology|sample\s+size|survey\s+of|data\s+from)', combined_competitor, re.IGNORECASE)),
            "date_freshness": len(re.findall(r'2024|2025|2026', combined_competitor)),
            "source_attribution": len(re.findall(r'(?:source:|according\s+to|as\s+reported\s+by|published\s+by)', combined_competitor, re.IGNORECASE)),
            "author_credentials": len(re.findall(r'(?:CEO|CTO|VP|Director|Analyst|Researcher|Professor|PhD)', combined_competitor)),
        }

        scores = {
            "experience": min(1.0, sum(experience_signals.values()) * 0.05),
            "expertise": min(1.0, sum(expertise_signals.values()) * 0.04),
            "authoritativeness": min(1.0, sum(authoritativeness_signals.values()) * 0.06),
            "trustworthiness": min(1.0, sum(trust_signals.values()) * 0.05)
        }
        overall_eEat = (scores["experience"] * 0.25 + scores["expertise"] * 0.30 +
                       scores["authoritativeness"] * 0.25 + scores["trustworthiness"] * 0.20)

        sme_count = len(sme_assets)
        sme_boost = min(0.3, sme_count * 0.05)

        return {
            "component_scores": scores,
            "overall_eEat_score": round(min(1.0, overall_eEat + sme_boost), 3),
            "sme_boost_applied": round(sme_boost, 3),
            "signal_counts": {
                "experience": experience_signals,
                "expertise": expertise_signals,
                "authoritativeness": authoritativeness_signals,
                "trust": trust_signals
            },
            "weakest_signal": min(scores, key=scores.get),
            "strongest_signal": max(scores, key=scores.get),
            "eeat_tier": (
                "EXCELLENT (Top 5%)" if overall_eEat + sme_boost > 0.8 else
                "STRONG (Top 20%)" if overall_eEat + sme_boost > 0.6 else
                "MODERATE (Average)" if overall_eEat + sme_boost > 0.4 else
                "WEAK (Below Average)" if overall_eEat + sme_boost > 0.2 else
                "CRITICAL (Needs Major Improvement)"
            ),
            "improvement_recommendations": self._get_eeat_improvements(scores, sme_count)
        }

    def _get_eeat_improvements(self, scores: Dict, sme_count: int) -> List[str]:
        """Get specific E-E-A-T improvement recommendations."""
        improvements = []
        if scores["experience"] < 0.5:
            improvements.append("Add first-person narratives and specific implementation results")
            improvements.append("Include real case studies with measurable outcomes")
        if scores["expertise"] < 0.5:
            improvements.append("Increase technical depth with detailed process explanations")
            improvements.append("Cite peer-reviewed research and industry studies")
        if scores["authoritativeness"] < 0.5:
            improvements.append("Reference industry analysts (Gartner, Forrester, IDC)")
            improvements.append("Include author biographical credentials and external profiles")
        if scores["trustworthiness"] < 0.5:
            improvements.append("Add methodology disclosures for any statistics cited")
            improvements.append("Include publication and last-updated dates prominently")
        if sme_count < 3:
            improvements.append("Collect at least 3 expert quotes from named SMEs")
        return improvements

    def _identify_unique_value_propositions(self, competitor_content: List[str],
                                              proprietary_data: List[Dict], sme_assets: List[Dict]) -> Dict[str, Any]:
        """Identify unique value propositions that differentiate from competitors."""
        uvps = []
        if proprietary_data:
            uvps.append({
                "uvp_type": "proprietary_data",
                "description": f"{len(proprietary_data)} proprietary data points available",
                "differentiation_score": 0.9,
                "recommendation": "Feature prominently with source attribution for maximum E-E-A-T"
            })
        if sme_assets:
            verified_experts = [a for a in sme_assets if a.get("verified", False)]
            uvps.append({
                "uvp_type": "expert_attribution",
                "description": f"{len(sme_assets)} SME insights, {len(verified_experts)} verified experts",
                "differentiation_score": 0.85 if verified_experts else 0.6,
                "recommendation": "Link expert quotes to LinkedIn/Wikipedia profiles for entity verification"
            })
        uvps.append({
            "uvp_type": "original_research",
            "description": "Opportunity to publish original benchmark data",
            "differentiation_score": 0.95,
            "recommendation": "Conduct survey or analysis that no competitor has published"
        })
        uvps.append({
            "uvp_type": "interactive_content",
            "description": "Opportunity to add calculators, tools, or interactive comparisons",
            "differentiation_score": 0.7,
            "recommendation": "Build comparison calculator or ROI estimator widget"
        })
        return {
            "unique_value_propositions": uvps,
            "total_uvp_count": len(uvps),
            "avg_differentiation_score": round(sum(u["differentiation_score"] for u in uvps) / max(1, len(uvps)), 3),
            "top_recommendation": uvps[0] if uvps else None
        }

    def _score_content_differentiation(self, seed: str, competitor_content: List[str],
                                         proprietary_data: List[Dict]) -> Dict[str, Any]:
        """Score potential content differentiation."""
        combined = ' '.join(competitor_content) if competitor_content else ""
        base_keywords = set(tokenize_words(seed))
        competitor_words = set(tokenize_words(combined))
        keyword_saturation = len(base_keywords & competitor_words) / max(1, len(base_keywords))
        has_proprietary = len(proprietary_data) > 0
        differentiation_score = max(0, 1.0 - keyword_saturation * 0.5 + (0.2 if has_proprietary else 0))
        return {
            "differentiation_score": round(min(1.0, differentiation_score), 3),
            "keyword_saturation": round(keyword_saturation, 3),
            "has_proprietary_data": has_proprietary,
            "differentiation_tier": (
                "HIGHLY_DIFFERENTIATED" if differentiation_score > 0.7 else
                "MODERATELY_DIFFERENTIATED" if differentiation_score > 0.4 else
                "LOW_DIFFERENTIATION - Significant unique value needed"
            )
        }

    def _build_gap_priority_matrix(self, consensus: Dict, info_gain: Dict, sme_placement: Dict) -> Dict[str, Any]:
        """Build prioritized matrix of content gaps."""
        matrix = []
        for gap in info_gain.get("gaps", []):
            matrix.append({
                "gap": gap["category"],
                "priority": gap["opportunity_level"],
                "effort": "medium",
                "impact": gap["opportunity_level"],
                "action": gap["recommended_action"]
            })
        for opp in info_gain.get("unique_opportunities", []):
            matrix.append({
                "gap": opp["opportunity"],
                "priority": opp["impact"],
                "effort": "high",
                "impact": opp["impact"],
                "action": opp["action"]
            })
        priority_order = {"VERY_HIGH": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
        matrix.sort(key=lambda x: priority_order.get(x["priority"], 4))
        return {
            "priority_matrix": matrix,
            "total_items": len(matrix),
            "high_priority_count": sum(1 for m in matrix if m["priority"] in ["VERY_HIGH", "HIGH"])
        }

    def _generate_recommendations(self, consensus: Dict, info_gain: Dict, eeat: Dict, sme: Dict) -> List[Dict[str, str]]:
        """Generate E-E-A-T and gap recommendations."""
        recs = []
        if consensus.get("consensus_score", 0) > 0.6:
            recs.append({
                "priority": "HIGH",
                "action": "Match consensus points for trust signal",
                "detail": f"{consensus.get('consensus_score', 0) * 100:.0f}% of competitors cover similar points - include these for baseline credibility"
            })
        for gap in info_gain.get("high_priority_gaps", [])[:3]:
            recs.append({
                "priority": "HIGH",
                "action": gap["recommended_action"],
                "detail": f"Opportunity level: {gap['opportunity_level']} - competitor mention count: {gap['competitor_mention_count']}"
            })
        if eeat.get("weakest_signal") == "experience":
            recs.append({
                "priority": "CRITICAL",
                "action": "Strengthen Experience signals",
                "detail": "Add first-person narratives, case studies, and specific implementation results"
            })
        if sme.get("sme_count", 0) < 3:
            recs.append({
                "priority": "HIGH",
                "action": "Collect more SME insights",
                "detail": f"Currently {sme.get('sme_count', 0)} SME assets - need minimum 3 for strong E-E-A-T"
            })
        return recs

    def _generate_implementation_steps(self, consensus: Dict, info_gain: Dict,
                                        sme_placement: Dict, eeat: Dict) -> List[str]:
        steps = []
        steps.append("Step 1: Include all consensus keyphrases that appear in 60%+ of competitor content for baseline trust signals")
        steps.append("Step 2: Add first-person narratives and specific implementation results to strengthen Experience signals")
        steps.append("Step 3: Place SME expert quotes in the designated sections (Definition, Benefits, Implementation, Expert Insights)")
        steps.append("Step 4: Add author byline with credentials, LinkedIn profile, and sameAs schema links")
        steps.append("Step 5: Include 3+ named expert quotes with verifiable credentials (CEO, CTO, PhD, Analyst titles)")
        steps.append("Step 6: Add original research data or proprietary benchmark statistics not found in competitor content")
        steps.append("Step 7: Include specific case studies with measurable outcomes (percentage improvements, ROI metrics)")
        steps.append("Step 8: Add methodology disclosures for any statistics cited to strengthen Trustworthiness signals")
        steps.append("Step 9: Reference industry analysts (Gartner, Forrester, IDC) for Authoritativeness signals")
        steps.append("Step 10: Include publication date and last-updated date prominently near the article title")
        steps.append("Step 11: Fill all HIGH opportunity information gaps identified in the analysis")
        steps.append("Step 12: Add interactive content elements (calculators, comparison tools) for differentiation")
        return steps

    def _generate_where_to_add(self, sme_placement: Dict, info_gain: Dict) -> List[str]:
        locations = []
        locations.append("Add expert quotes as blockquotes within each designated H2 section per SME placement plan")
        locations.append("Place author byline with credentials and sameAs links immediately below the H1 heading")
        locations.append("Include first-person narratives and case studies within 'Implementation Guide' and 'Benefits' H2 sections")
        locations.append("Add original research data and proprietary statistics within 'Expert Insights' or 'Research Findings' H2 section")
        locations.append("Place methodology disclosures as footnotes or a 'Methodology' subsection at the article end")
        locations.append("Add publication date and last-updated date in the article metadata area below H1")
        locations.append("Include industry analyst references (Gartner, Forrester) within 'Comparison' and 'Best Practices' H2 sections")
        locations.append("Add case studies with measurable outcomes within 'Benefits' or dedicated 'Case Studies' H2 section")
        locations.append("Place interactive content elements (calculators, comparison tools) within 'Comparison' H2 section")
        locations.append("Add consensus statements from competitor analysis as trust-signal paragraphs within relevant H2 sections")
        return locations

    def _generate_detailed_analysis(self, consensus: Dict, info_gain: Dict,
                                     sme_placement: Dict, eeat: Dict,
                                     content_differentiation: Dict) -> Dict[str, Any]:
        return {
            "consensus_insights": {
                "consensus_score": consensus.get("consensus_score", 0),
                "total_competitors_analyzed": consensus.get("total_competitors_analyzed", 0),
                "differentiation_opportunities": consensus.get("differentiation_opportunities", 0),
                "benchmark": "(General industry guidance, unverified): Pages matching 70-80% of competitor consensus points while adding 20-30% unique value achieve highest rankings",
                "statistical_range": f"Consensus coverage: {consensus.get('consensus_score', 0)*100:.0f}% (unverified heuristic target: match 70-80%)",
                "expert_recommendation": "Match all consensus points for baseline credibility, then differentiate with unique data and expert perspectives",
                "common_mistakes": ["Ignoring consensus points and losing baseline trust", "Only copying competitors without adding unique value", "Missing key consensus topics entirely"],
                "success_metrics": ["Consensus coverage > 75%", "20-30% unique differentiating content", "E-E-A-T score > 0.7"],
                "data_origin": "unverified_industry_heuristic - not measured for this page"
            },
            "information_gain_insights": {
                "total_gaps": info_gain.get("total_gaps", 0),
                "high_priority_gaps": len(info_gain.get("high_priority_gaps", [])),
                "gain_potential": info_gain.get("information_gain_potential", 0),
                "benchmark": "(General industry guidance, unverified): Content with 3+ unique information gaps filled achieves 40-60% higher engagement than competitor average",
                "statistical_range": f"Information gain potential: {info_gain.get('information_gain_potential', 0)*100:.0f}% (unverified heuristic target: 50%+)",
                "expert_recommendation": "Address HIGH opportunity gaps first, then differentiate with unique opportunities like original research",
                "common_mistakes": ["Filling all gaps equally instead of prioritizing HIGH opportunities", "Missing original research opportunities", "Not leveraging proprietary data for differentiation"],
                "success_metrics": ["3+ HIGH priority gaps filled", "Original research published", "Unique value propositions > 3"],
                "data_origin": "unverified_industry_heuristic - not measured for this page"
            },
            "sme_placement_insights": {
                "sme_count": sme_placement.get("sme_count", 0),
                "sections_covered": sme_placement.get("total_sections_covered", 0),
                "eeat_boost_estimate": sme_placement.get("eeat_boost_estimate", 0),
                "benchmark": "(General industry guidance, unverified): Content with 3-5 named expert quotes sees 30-50% improvement in E-E-A-T signals and trustworthiness",
                "statistical_range": f"SME boost estimate: +{sme_placement.get('eeat_boost_estimate', 0)*100:.0f}% E-E-A-T improvement (unverified heuristic target: 25%+)",
                "expert_recommendation": "Place SME quotes in Definition, Benefits, Implementation, and Expert Insights sections for maximum impact",
                "common_mistakes": ["Using generic expert quotes without credentials", "Placing all quotes in one section", "Missing LinkedIn/profile verification links"],
                "success_metrics": ["3+ verified expert quotes", "Expert quotes in 4+ sections", "E-E-A-T boost > 20%"],
                "data_origin": "unverified_industry_heuristic - not measured for this page"
            },
            "eeat_assessment_insights": {
                "overall_score": eeat.get("overall_eEat_score", 0),
                "eeat_tier": eeat.get("eeat_tier", "UNKNOWN"),
                "weakest_signal": eeat.get("weakest_signal", "unknown"),
                "strongest_signal": eeat.get("strongest_signal", "unknown"),
                "benchmark": "(General industry guidance, unverified): Top 5% content scores 0.8+ on E-E-A-T; average is 0.4-0.6; below 0.2 needs critical improvement",
                "statistical_range": f"Current E-E-A-T: {eeat.get('overall_eEat_score', 0)*100:.0f}% ({eeat.get('eeat_tier', 'UNKNOWN')})",
                "expert_recommendation": f"Focus on improving {eeat.get('weakest_signal', 'unknown')} signals - currently the lowest scoring component",
                "common_mistakes": ["Ignoring the weakest E-E-A-T signal", "Adding credentials without expertise evidence", "Missing source attributions for all claims"],
                "success_metrics": ["E-E-A-T score > 0.7", "All 4 signals above 0.5", "No signal below 0.3", "Tier upgrade within 90 days"],
                "data_origin": "unverified_industry_heuristic - not measured for this page"
            },
            "content_differentiation_insights": {
                "differentiation_score": content_differentiation.get("differentiation_score", 0),
                "differentiation_tier": content_differentiation.get("differentiation_tier", "UNKNOWN"),
                "keyword_saturation": content_differentiation.get("keyword_saturation", 0),
                "benchmark": "(General industry guidance, unverified): Highly differentiated content (>0.7 score) achieves 50-80% higher engagement and backlink rates",
                "statistical_range": f"Differentiation score: {content_differentiation.get('differentiation_score', 0)*100:.0f}% ({content_differentiation.get('differentiation_tier', 'UNKNOWN')})",
                "expert_recommendation": "Add proprietary data, original research, and interactive elements to push differentiation above 70%",
                "common_mistakes": ["Producing content identical to competitors", "Ignoring proprietary data opportunities", "Missing interactive content elements"],
                "success_metrics": ["Differentiation score > 0.7", "Backlink growth > 25%", "Unique visitor increase > 30%"],
                "data_origin": "unverified_industry_heuristic - not measured for this page"
            }
        }
