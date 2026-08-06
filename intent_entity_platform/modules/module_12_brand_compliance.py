"""
Module 12: Brand Compliance & Legal Guardrail Engine
Scans for regulated claims, enforces brand style, and injects disclaimers.
"""
import re
from typing import List, Dict, Any


class BrandComplianceEngine:
    """Module 12: Brand Compliance & Legal Guardrail Engine"""

    def __init__(self):
        self.module_id = "M12"
        self.module_name = "Brand Compliance & Legal Guardrail Engine"

    def analyze(self, text: str = "", brand_config: Dict[str, Any] = None, inputs: Dict[str, Any] = None) -> Dict[str, Any]:
        """Full brand compliance analysis pipeline."""
        inputs = inputs or {}
        url_data = inputs.get("_url_data", None)

        real_brand_analysis = {}
        if url_data:
            real_brand_analysis = self._analyze_url_brand_compliance(url_data, brand_config)

        if not text.strip() and not url_data:
            return {"module": self.module_id, "module_name": self.module_name, "error": "No text provided"}

        brand_config = brand_config or {}
        use_text = text if text.strip() else url_data.get("page_text", "") if url_data else ""
        regulated_claims = self._scan_regulated_claims(use_text, brand_config)
        trademark_enforcement = self._enforce_trademarks(text, brand_config)
        anti_trope_compliance = self._check_anti_trope_compliance(text, brand_config)
        disclaimer_injection = self._suggest_disclaimers(text, brand_config)
        legal_risk_assessment = self._assess_legal_risk(text, regulated_claims)
        style_enforcement = self._enforce_brand_style(text, brand_config)

        return {
            "module": self.module_id,
            "module_name": self.module_name,
            "regulated_claims_scan": regulated_claims,
            "trademark_enforcement": trademark_enforcement,
            "anti_trope_compliance": anti_trope_compliance,
            "disclaimer_injection": disclaimer_injection,
            "legal_risk_assessment": legal_risk_assessment,
            "brand_style_enforcement": style_enforcement,
            "url_brand_analysis": real_brand_analysis,
            "compliance_score": self._calculate_compliance_score(regulated_claims, trademark_enforcement, anti_trope_compliance),
            "critical_violations": self._get_critical_violations(regulated_claims, trademark_enforcement, legal_risk_assessment),
            "recommendations": self._generate_recommendations(regulated_claims, trademark_enforcement, anti_trope_compliance, legal_risk_assessment),
            "implementation_steps": [
                "Step 1: Remove all CRITICAL regulated claims (absolute statements, financial guarantees, FDA/SEC claims)",
                "Step 2: Replace comparative claims with qualified, verifiable statements with source attribution",
                "Step 3: Fix trademark formatting violations (correct capitalization and symbols)",
                "Step 4: Remove anti-trope blacklist phrases and replace with brand-approved language",
                "Step 5: Add required disclaimers near relevant content sections (pricing, testimonials, forward-looking)",
                "Step 6: Reword superlative claims with specific data points and qualifying language",
                "Step 7: Add source attribution for all performance claims and statistics",
                "Step 8: Submit content for legal review if risk level is CRITICAL or HIGH",
                "Step 9: Update brand style guide compliance (formal voice, no casual language)",
                "Step 10: Implement automated compliance checking in content workflow"
            ],
            "where_to_add": [
                "Place pricing disclaimers immediately after pricing tables or cost discussions",
                "Add testimonial disclaimers below customer quotes or case study references",
                "Include forward-looking disclaimers near predictive content or forecasts",
                "Add ROI disclaimers near benefit claims and financial projections",
                "Place legal review notices at the top of content requiring approval",
                "Add trademark symbols (™ or ®) immediately after brand names on first mention",
                "Include source attribution links directly after statistics and data points",
                "Place compliance badges or certification logos in footer or sidebar areas"
            ],
            "detailed_analysis": {
                "industry_benchmarks": {
                    "compliance_violation_rate": "Average content has 3-7 compliance violations per 1000 words",
                    "legal_review_cycle_time": "Legal review typically adds 2-5 business days to publication timeline",
                    "trademark_violation_frequency": "15-20% of content contains trademark formatting errors",
                    "disclaimer_coverage": "Only 35% of content includes required disclaimers",
                    "anti_trope_compliance_rate": "Top brands achieve 90%+ anti-trope compliance"
                },
                "statistical_ranges": {
                    "critical_violations_per_article": "0-1 critical violations acceptable",
                    "high_violations_per_article": "0-3 high violations before requiring revision",
                    "disclaimer_placement_accuracy": "Disclaimers should be within 100 words of relevant content",
                    "trademark_symbol_usage": "100% compliance required for brand name formatting",
                    "legal_review_turnaround": "24-48 hours for standard content, 5-7 days for high-risk content"
                },
                "expert_recommendations": [
                    "Implement automated compliance scanning in content management workflow",
                    "Create a brand-approved vocabulary list to replace anti-trope blacklist terms",
                    "Establish clear escalation paths for different violation severity levels",
                    "Train content creators on FTC guidelines and industry-specific regulations",
                    "Maintain a living compliance checklist that updates with new regulations",
                    "Use version control for compliance reviews to track changes and approvals",
                    "Regularly audit published content for compliance drift over time"
                ],
                "common_mistakes_to_avoid": [
                    "Using absolute claims ('best', 'guaranteed', '100%') without qualifying data",
                    "Incorrect trademark formatting (wrong capitalization, missing symbols)",
                    "Adding disclaimers in footers instead of near relevant content sections",
                    "Ignoring industry-specific regulations (HIPAA, SOC 2, FDA claims)",
                    "Using casual language that contradicts brand voice profile",
                    "Not sourcing performance claims and statistics with credible references",
                    "Failing to update compliance when regulations change"
                ],
                "success_metrics_to_track": [
                    "Compliance score percentage over time (target: >95%)",
                    "Critical violations per article (target: 0)",
                    "Legal review turnaround time",
                    "Trademark formatting compliance rate (target: 100%)",
                    "Anti-trope compliance rate (target: >90%)",
                    "Disclaimer placement accuracy",
                    "Compliance training completion rate for content team"
                ]
            }
        }

    def _analyze_url_brand_compliance(self, url_data: Dict, brand_config: Dict = None) -> Dict[str, Any]:
        """Deep brand compliance analysis using actual page content."""
        page_text = url_data.get("page_text", "")
        title = url_data.get("title", "")
        meta_desc = url_data.get("meta_description", "")
        h1 = url_data.get("h1", "")
        h2s = url_data.get("h2s", [])
        word_count = url_data.get("word_count", 0)
        url = url_data.get("url", "")
        brand_config = brand_config or {}

        use_text = page_text or ""

        # Brand voice analysis from actual content
        voice_indicators = {
            "formal_language": len(re.findall(r'\b(?:therefore|furthermore|moreover|consequently|thus|hence)\b', use_text, re.IGNORECASE)),
            "casual_language": len(re.findall(r'\b(?:gonna|wanna|gotta|kinda|sorta|hey|cool|awesome)\b', use_text, re.IGNORECASE)),
            "technical_terms": len(re.findall(r'\b(?:API|SDK|SaaS|PaaS|IaaS|ROI|TCO|KPI|SLA)\b', use_text)),
            "industry_jargon": len(re.findall(r'\b(?:synergy|leverage|disrupt|scalable|ecosystem|paradigm)\b', use_text, re.IGNORECASE)),
            "action_words": len(re.findall(r'\b(?:implement|optimize|streamline|enhance|accelerate|transform)\b', use_text, re.IGNORECASE)),
            "hedging_language": len(re.findall(r'\b(?:may|might|could|possibly|potentially|arguably)\b', use_text, re.IGNORECASE)),
            "assertive_language": len(re.findall(r'\b(?:will|shall|must|definitely|certainly|always)\b', use_text, re.IGNORECASE))
        }

        total_words = len(use_text.split()) if use_text else 1
        voice_profile = "unknown"
        if voice_indicators["formal_language"] > voice_indicators["casual_language"] * 2:
            voice_profile = "formal"
        elif voice_indicators["casual_language"] > voice_indicators["formal_language"]:
            voice_profile = "casual"
        elif voice_indicators["technical_terms"] > 3:
            voice_profile = "technical"
        elif voice_indicators["action_words"] > 5:
            voice_profile = "action-oriented"

        # Detect brand-specific terminology
        brand_terms_found = []
        custom_terms = brand_config.get("brand_terms", [])
        for term in custom_terms:
            count = use_text.lower().count(term.lower())
            if count > 0:
                brand_terms_found.append({"term": term, "count": count})

        # Anti-trope analysis on actual content
        anti_trope_blacklist = brand_config.get("anti_trope_blacklist", [
            "in today's fast-paced", "game-changer", "delve", "harness the power",
            "seamless", "robust", "cutting-edge", "state-of-the-art", "best-in-class",
            "furthermore", "moreover", "it is important to note", "needless to say",
            "at the end of the day", "without further ado", "buckle up",
            "let's unpack", "paradigm shift", "unlock the potential"
        ])
        anti_trope_violations = []
        for term in anti_trope_blacklist:
            occurrences = [(m.start(), use_text[max(0, m.start()-20):min(len(use_text), m.end()+20)]) for m in re.finditer(re.escape(term), use_text, re.IGNORECASE)]
            for pos, context in occurrences:
                anti_trope_violations.append({
                    "term": term,
                    "position": pos,
                    "context": f"...{context.strip()}...",
                    "severity": "MEDIUM"
                })

        # Regulated claims scan on actual content
        regulated_findings = []
        absolute_claims = re.findall(r'\b(?:best|guaranteed|100%|always|never|proven|undeniable|unmatched|number one|#1|top-ranked|leading|most trusted)\b', use_text, re.IGNORECASE)
        for claim in absolute_claims:
            context_match = re.search(re.escape(claim), use_text, re.IGNORECASE)
            if context_match:
                ctx = use_text[max(0, context_match.start()-30):min(len(use_text), context_match.end()+30)]
                regulated_findings.append({
                    "claim": claim,
                    "type": "ABSOLUTE_CLAIM",
                    "severity": "HIGH",
                    "context": f"...{ctx.strip()}...",
                    "action": "REWORD with qualifying language"
                })

        financial_claims = re.findall(r'\b(?:guaranteed\s+(?:ROI|return|savings))\b|(?:will\s+(?:increase|reduce|save)\s+\$)', use_text, re.IGNORECASE)
        for claim in financial_claims:
            regulated_findings.append({
                "claim": claim,
                "type": "FINANCIAL_GUARANTEE",
                "severity": "CRITICAL",
                "action": "REMOVE or add disclaimer"
            })

        compliance_claims = re.findall(r'\b(?:SOC\s*2|HIPAA|GDPR|ISO\s*27001)\s+(?:compliant|certified)\b', use_text, re.IGNORECASE)
        for claim in compliance_claims:
            regulated_findings.append({
                "claim": claim,
                "type": "COMPLIANCE_CLAIM",
                "severity": "MEDIUM",
                "action": "Verify and add source attribution"
            })

        # Terminology consistency analysis
        terminology_issues = []
        # Check for inconsistent capitalization of key terms
        tech_terms = re.findall(r'\b[A-Za-z]{3,}\b', use_text)
        term_variants = {}
        for term in tech_terms:
            lower = term.lower()
            if lower not in term_variants:
                term_variants[lower] = set()
            term_variants[lower].add(term)
        for term, variants in term_variants.items():
            if len(variants) > 1 and len(term) > 3:
                terminology_issues.append({
                    "term": term,
                    "variants_found": list(variants),
                    "action": f"Standardize to one capitalization: '{list(variants)[0]}'"
                })

        # Style consistency
        style_issues = []
        sentence_lengths = [len(s.split()) for s in re.split(r'[.!?]+', use_text) if s.strip()]
        avg_sentence_length = sum(sentence_lengths) / max(1, len(sentence_lengths))
        long_sentences = sum(1 for l in sentence_lengths if l > 30)
        if long_sentences > len(sentence_lengths) * 0.2:
            style_issues.append(f"{long_sentences} sentences exceed 30 words - consider breaking for readability")

        # Disclaimers needed based on actual content
        disclaimers_needed = []
        if re.search(r'\b(?:price|cost|pricing|subscription)\b', use_text, re.IGNORECASE):
            disclaimers_needed.append("Pricing disclaimer - subject to change")
        if re.search(r'\b(?:testimonial|case study|customer story)\b', use_text, re.IGNORECASE):
            disclaimers_needed.append("Testimonial disclaimer - results may vary")
        if re.search(r'\b(?:prediction|forecast|future|estimate)\b', use_text, re.IGNORECASE):
            disclaimers_needed.append("Forward-looking disclaimer - risks and uncertainties")
        if re.search(r'\b(?:ROI|return|savings|revenue)\b', use_text, re.IGNORECASE):
            disclaimers_needed.append("Results disclaimer - specific use case dependent")

        # Overall compliance scoring
        total_violations = len(anti_trope_violations) + len(regulated_findings) + len(terminology_issues)
        compliance_score = max(0, 1.0 - (len(anti_trope_violations) * 0.03 + len(regulated_findings) * 0.05 + len(terminology_issues) * 0.02))

        return {
            "page_url": url,
            "page_title": title,
            "content_word_count": word_count,
            "brand_voice_analysis": {
                "detected_voice": voice_profile,
                "voice_indicators": voice_indicators,
                "formality_score": round(voice_indicators["formal_language"] / max(1, voice_indicators["formal_language"] + voice_indicators["casual_language"]), 3),
                "assertiveness_score": round(voice_indicators["assertive_language"] / max(1, voice_indicators["assertive_language"] + voice_indicators["hedging_language"]), 3),
                "technical_density": round(voice_indicators["technical_terms"] / max(1, total_words / 1000), 3),
                "voice_verdict": f"Detected: {voice_profile} voice"
            },
            "anti_trope_compliance": {
                "total_violations": len(anti_trope_violations),
                "violations": anti_trope_violations[:15],
                "compliance_rate": round((1 - len(anti_trope_violations) / max(1, total_words / 100)) * 100, 1),
                "status": "COMPLIANT" if len(anti_trope_violations) == 0 else "NON_COMPLIANT"
            },
            "regulated_claims_on_page": {
                "total_claims": len(regulated_findings),
                "critical_claims": sum(1 for f in regulated_findings if f.get("severity") == "CRITICAL"),
                "high_claims": sum(1 for f in regulated_findings if f.get("severity") == "HIGH"),
                "medium_claims": sum(1 for f in regulated_findings if f.get("severity") == "MEDIUM"),
                "findings": regulated_findings[:15],
                "legal_review_required": any(f.get("severity") == "CRITICAL" for f in regulated_findings)
            },
            "terminology_consistency": {
                "issues_found": len(terminology_issues),
                "issues": terminology_issues[:10],
                "brand_terms_detected": brand_terms_found,
                "consistency_score": round(max(0, 1.0 - len(terminology_issues) * 0.05), 3)
            },
            "style_analysis": {
                "avg_sentence_length": round(avg_sentence_length, 1),
                "long_sentences_count": long_sentences,
                "style_issues": style_issues,
                "readability_impact": "GOOD" if avg_sentence_length <= 20 else "NEEDS_IMPROVEMENT"
            },
            "disclaimers_recommended": disclaimers_needed,
            "overall_compliance_score": round(compliance_score, 3),
            "compliance_tier": (
                "FULLY_COMPLIANT" if compliance_score >= 0.95 else
                "MOSTLY_COMPLIANT" if compliance_score >= 0.85 else
                "PARTIALLY_COMPLIANT" if compliance_score >= 0.7 else
                "NON_COMPLIANT"
            ),
            "brand_recommendations": (
                [{"priority": "HIGH", "action": "Fix regulated claims", "detail": f"{len(regulated_findings)} claims need review"}] if regulated_findings else []
            ) + (
                [{"priority": "MEDIUM", "action": "Remove anti-trope violations", "detail": f"{len(anti_trope_violations)} banned phrases found"}] if anti_trope_violations else []
            ) + (
                [{"priority": "LOW", "action": "Standardize terminology", "detail": f"{len(terminology_issues)} inconsistencies found"}] if terminology_issues else []
            )
        }

    def _scan_regulated_claims(self, text: str, brand_config: Dict) -> Dict[str, Any]:
        """Scan for regulated and legally sensitive claims."""
        regulated_patterns = {
            "absolute_claims": [
                (r'\bbest\s+(?:in\s+class|overall|solution|platform|software|tool)\b', "COMPARATIVE_CLAIM"),
                (r'\b(?:100%|guaranteed|absolute|certain|definite|always|never)\b', "ABSOLUTE_CLAIM"),
                (r'\b(?:proven|undeniable|unmatched|unrivaled|unparalleled)\b', "SUPERLATIVE_CLAIM"),
                (r'\b(?:number\s+(?:one|1)|#1|top-ranked|leading)\b', "RANKING_CLAIM"),
                (r'\b(?:most\s+(?:trusted|reliable|secure|advanced|powerful))\b', "SUPERLATIVE_CLAIM"),
            ],
            "financial_claims": [
                (r'\b(?:guaranteed\s+(?:ROI|return|savings|revenue))\b', "FINANCIAL_GUARANTEE"),
                (r'\b(?:will\s+(?:increase|reduce|save|generate)\s+\$)\b', "FINANCIAL_PROJECTION"),
                (r'\b(?:free\s+(?:forever|for\s+life|trial))\b', "FREE_CLAIM"),
                (r'\b(?:no\s+(?:hidden\s+fees|contracts|commitments))\b', "NO_COMMITMENT_CLAIM"),
                (r'\b(?:\$0|\bcosts?\s+nothing)\b', "ZERO_COST_CLAIM"),
            ],
            "compliance_claims": [
                (r'\b(?:SOC\s*2|HIPAA|GDPR|FERPA|PCI\s*DSS|ISO\s*27001)\s+(?:compliant|certified|certification)\b', "COMPLIANCE_CLAIM"),
                (r'\b(?:FDA\s+(?:approved|cleared|certified))\b', "FDA_CLAIM"),
                (r'\b(?:SEC\s+(?:compliant|registered|approved))\b', "SEC_CLAIM"),
                (r'\b(?:meets?\s+(?:all|every)\s+(?:requirements|standards|regulations))\b', "COMPLIANCE_BROAD"),
            ],
            "performance_claims": [
                (r'\b(?:up\s+to\s+\d+%)\s+(?:faster|better|more\s+efficient|cheaper)\b', "PERFORMANCE_RANGE"),
                (r'\b(?:\d+x\s+(?:faster|better|more\s+efficient))\b', "MULTIPLIER_CLAIM"),
                (r'\b(?:reduces?\s+(?:costs?|time|errors?)\s+by\s+\d+%)\b', "SPECIFIC_BENEFIT"),
                (r'\b(?:eliminates?\s+(?:all|every|100%))\b', "ELIMINATION_CLAIM"),
            ],
            "testimonials_claims": [
                (r'\b(?:customers?\s+(?:report|say|claim|state))\s+["\u201c]([^"\u201d]+)["\u201d]', "TESTIMONIAL"),
                (r"\b(?:in\s+my\s+experience|we've\s+seen|our\s+clients)\b", "EXPERIENCE_CLAIM"),
            ]
        }
        findings = []
        for category, patterns in regulated_patterns.items():
            for pattern, claim_type in patterns:
                for m in re.finditer(pattern, text, re.IGNORECASE):
                    context = text[max(0, m.start()-40):min(len(text), m.end()+40)].strip()
                    severity = self._determine_claim_severity(claim_type, brand_config)
                    findings.append({
                        "claim": m.group()[:200],
                        "claim_type": claim_type,
                        "category": category,
                        "position": m.start(),
                        "context": f"...{context}...",
                        "severity": severity,
                        "regulation_reference": self._get_regulation_reference(claim_type),
                        "recommended_action": self._get_claim_action(claim_type, severity),
                        "requires_legal_review": severity in ["CRITICAL", "HIGH"]
                    })

        custom_blocked = brand_config.get("regulated_words", [])
        for term in custom_blocked:
            for m in re.finditer(re.escape(term), text, re.IGNORECASE):
                findings.append({
                    "claim": term,
                    "claim_type": "CUSTOM_BLOCKED_TERM",
                    "category": "brand_specific",
                    "position": m.start(),
                    "context": text[max(0, m.start()-30):min(len(text), m.end()+30)].strip(),
                    "severity": "CRITICAL",
                    "regulation_reference": "Brand compliance policy",
                    "recommended_action": "REMOVE immediately - violates brand guidelines",
                    "requires_legal_review": True
                })

        return {
            "total_violations": len(findings),
            "critical_violations": sum(1 for f in findings if f["severity"] == "CRITICAL"),
            "high_violations": sum(1 for f in findings if f["severity"] == "HIGH"),
            "medium_violations": sum(1 for f in findings if f["severity"] == "MEDIUM"),
            "findings": findings[:30],
            "violations_by_category": {cat: sum(1 for f in findings if f["category"] == cat)
                                       for cat in set(f["category"] for f in findings)},
            "compliance_status": (
                "COMPLIANT" if len(findings) == 0 else
                "MINOR_ISSUES" if sum(1 for f in findings if f["severity"] in ["CRITICAL", "HIGH"]) == 0 else
                "REQUIRES_REVIEW" if sum(1 for f in findings if f["severity"] == "CRITICAL") == 0 else
                "NON_COMPLIANT"
            )
        }

    def _determine_claim_severity(self, claim_type: str, brand_config: Dict) -> str:
        """Determine severity of a regulated claim."""
        critical_types = ["FDA_CLAIM", "SEC_CLAIM", "FINANCIAL_GUARANTEE", "CUSTOM_BLOCKED_TERM"]
        high_types = ["ABSOLUTE_CLAIM", "SUPERLATIVE_CLAIM", "COMPLIANCE_CLAIM", "COMPARATIVE_CLAIM"]
        medium_types = ["PERFORMANCE_RANGE", "MULTIPLIER_CLAIM", "TESTIMONIAL", "EXPERIENCE_CLAIM"]
        if claim_type in critical_types:
            return "CRITICAL"
        if claim_type in high_types:
            return "HIGH"
        if claim_type in medium_types:
            return "MEDIUM"
        return "LOW"

    def _get_regulation_reference(self, claim_type: str) -> str:
        """Get relevant regulation reference."""
        references = {
            "COMPARATIVE_CLAIM": "FTC Act Section 5 - Deceptive Practices",
            "ABSOLUTE_CLAIM": "FTC Guidelines on Advertising Claims",
            "SUPERLATIVE_CLAIM": "FTC Comparative Advertising Guidelines",
            "RANKING_CLAIM": "FTC Endorsement Guides",
            "FINANCIAL_GUARANTEE": "SEC Regulations on Financial Promises",
            "FINANCIAL_PROJECTION": "SEC Rule 10b-5 - Anti-Fraud Provisions",
            "FREE_CLAIM": "FTC Negative Option Rules",
            "FDA_CLAIM": "FDA 21 CFR Part 110 - Food and Drug Regulations",
            "SEC_CLAIM": "SEC Securities Act of 1933",
            "COMPLIANCE_CLAIM": "Industry-Specific Compliance Requirements",
            "TESTIMONIAL": "FTC Endorsement Guides (16 CFR Part 255)",
        }
        return references.get(claim_type, "General Advertising Standards")

    def _get_claim_action(self, claim_type: str, severity: str) -> str:
        """Get recommended action for claim."""
        if severity == "CRITICAL":
            return "REMOVE or REPLACE with qualified, verifiable claim"
        if severity == "HIGH":
            return "REWORD to remove absolute/comparative language, add qualifying data"
        if severity == "MEDIUM":
            return "ADD source attribution or qualifying language"
        return "MONITOR for potential issues"

    def _enforce_trademarks(self, text: str, brand_config: Dict) -> Dict[str, Any]:
        """Enforce trademark and naming conventions."""
        trademark_rules = brand_config.get("trademark_rules", {})
        default_rules = {
            "google": {"correct": "Google", "variations": ["google", "GOOGLE", "GoogLe"], "symbol": ""},
            "microsoft": {"correct": "Microsoft", "variations": ["microsoft", "MICROSOFT", "MicroSoft"], "symbol": ""},
            "apple": {"correct": "Apple", "variations": ["apple", "APPLE", "Aple"], "symbol": ""},
            "amazon": {"correct": "Amazon", "variations": ["amazon", "AMAZON", "Amazn"], "symbol": ""},
            "salesforce": {"correct": "Salesforce", "variations": ["salesforce", "SALESFORCE", "SalesForce"], "symbol": ""},
        }
        all_rules = {**default_rules, **trademark_rules}
        violations = []
        for brand_name, rule in all_rules.items():
            for variation in rule["variations"]:
                for m in re.finditer(re.escape(variation), text):
                    violations.append({
                        "found": variation,
                        "correct": rule["correct"],
                        "symbol": rule["symbol"],
                        "position": m.start(),
                        "action": f"Replace '{variation}' with '{rule['correct']}'"
                    })
        return {
            "trademark_violations": violations,
            "total_violations": len(violations),
            "brands_checked": len(all_rules),
            "compliance_rate": round(1 - len(violations) / max(1, len(text.split()) * 0.01), 3)
        }

    def _check_anti_trope_compliance(self, text: str, brand_config: Dict) -> Dict[str, Any]:
        """Check compliance with anti-trope blacklist."""
        anti_tropes = brand_config.get("anti_trope_blacklist", [])
        do_not_say = brand_config.get("do_not_say_terms", [])
        combined_blacklist = list(set(anti_tropes + do_not_say))
        if not combined_blacklist:
            combined_blacklist = [
                "in today's fast-paced", "game-changer", "delve", "harness the power",
                "seamless", "robust", "cutting-edge", "state-of-the-art", "best-in-class",
                "furthermore", "moreover", "it is important to note", "needless to say",
                "at the end of the day", "without further ado", "buckle up",
                "let's unpack", "paradigm shift", "unlock the potential"
            ]
        violations = []
        for term in combined_blacklist:
            for m in re.finditer(re.escape(term), text, re.IGNORECASE):
                violations.append({
                    "term": term,
                    "position": m.start(),
                    "context": text[max(0, m.start()-20):min(len(text), m.end()+20)].strip(),
                    "action": f"Remove or replace '{term}'"
                })
        return {
            "total_violations": len(violations),
            "unique_terms_violated": len(set(v["term"] for v in violations)),
            "violations": violations[:20],
            "compliance_rate": round(1 - len(violations) / max(1, len(text.split()) * 0.01), 3),
            "status": (
                "FULLY_COMPLIANT" if len(violations) == 0 else
                "PARTIALLY_COMPLIANT" if len(violations) < 5 else
                "NON_COMPLIANT"
            )
        }

    def _suggest_disclaimers(self, text: str, brand_config: Dict) -> Dict[str, Any]:
        """Suggest required disclaimers and legal notices."""
        required_disclaimers = brand_config.get("required_disclaimers", [])
        suggested = []
        if re.search(r'\b(?:price|cost|pricing|subscription|plan)\b', text, re.IGNORECASE):
            suggested.append({
                "disclaimer_type": "pricing_disclaimer",
                "text": "Pricing information is subject to change. Please visit the official website for current pricing.",
                "placement": "Near pricing section",
                "priority": "HIGH"
            })
        if re.search(r'\b(?:testimonial|case\s+study|customer\s+story)\b', text, re.IGNORECASE):
            suggested.append({
                "disclaimer_type": "testimonial_disclaimer",
                "text": "Results may vary. Testimonials reflect individual experiences.",
                "placement": "Near testimonial section",
                "priority": "MEDIUM"
            })
        if re.search(r'\b(?:prediction|forecast|future|estimate)\b', text, re.IGNORECASE):
            suggested.append({
                "disclaimer_type": "forward_looking_disclaimer",
                "text": "Forward-looking statements involve risks and uncertainties. Actual results may differ.",
                "placement": "Near predictive content",
                "priority": "HIGH"
            })
        if re.search(r'\b(?:ROI|return|savings|revenue)\b', text, re.IGNORECASE):
            suggested.append({
                "disclaimer_type": "results_disclaimer",
                "text": "Results and ROI figures are based on specific use cases and may not be representative of all implementations.",
                "placement": "Near ROI/benefit claims",
                "priority": "MEDIUM"
            })
        for disclaimer in required_disclaimers:
            suggested.append({
                "disclaimer_type": "brand_required",
                "text": disclaimer,
                "placement": "Footer or relevant section",
                "priority": "HIGH"
            })
        return {
            "suggested_disclaimers": suggested,
            "total_suggested": len(suggested),
            "must_have_count": sum(1 for d in suggested if d["priority"] == "HIGH")
        }

    def _assess_legal_risk(self, text: str, regulated_claims: Dict) -> Dict[str, Any]:
        """Assess overall legal risk."""
        critical = regulated_claims.get("critical_violations", 0)
        high = regulated_claims.get("high_violations", 0)
        medium = regulated_claims.get("medium_violations", 0)
        risk_score = (critical * 0.4 + high * 0.25 + medium * 0.1)
        risk_level = (
            "CRITICAL" if risk_score > 1.5 else
            "HIGH" if risk_score > 0.8 else
            "MODERATE" if risk_score > 0.3 else
            "LOW" if risk_score > 0.1 else
            "MINIMAL"
        )
        return {
            "risk_score": round(min(1.0, risk_score), 3),
            "risk_level": risk_level,
            "critical_claims": critical,
            "high_claims": high,
            "medium_claims": medium,
            "legal_review_required": risk_level in ["CRITICAL", "HIGH"],
            "liability_areas": self._identify_liability_areas(regulated_claims),
            "insurance_recommendation": "Professional liability review recommended" if risk_level in ["CRITICAL", "HIGH"] else "Standard review sufficient"
        }

    def _identify_liability_areas(self, regulated_claims: Dict) -> List[str]:
        """Identify areas of potential legal liability."""
        areas = []
        findings = regulated_claims.get("findings", [])
        for finding in findings:
            if finding.get("severity") == "CRITICAL":
                areas.append(f"{finding.get('claim_type', 'Unknown')}: {finding.get('claim', '')[:50]}")
        return list(set(areas))[:5]

    def _enforce_brand_style(self, text: str, brand_config: Dict) -> Dict[str, Any]:
        """Enforce brand style guidelines."""
        voice = brand_config.get("voice_profile", "authoritative")
        style_issues = []
        if voice == "authoritative":
            casual_patterns = [r'\bgonna\b', r'\bwanna\b', r'\bgotta\b', r'\bkinda\b', r'\bsorta\b']
            for pattern in casual_patterns:
                for m in re.finditer(pattern, text, re.IGNORECASE):
                    style_issues.append({
                        "issue": f"Casual language '{m.group()}' inconsistent with authoritative voice",
                        "position": m.start(),
                        "severity": "MEDIUM",
                        "action": "Replace with formal equivalent"
                    })
        return {
            "voice_profile": voice,
            "style_violations": style_issues,
            "total_violations": len(style_issues),
            "brand_consistency_score": round(max(0, 1.0 - len(style_issues) * 0.05), 3)
        }

    def _calculate_compliance_score(self, regulated: Dict, trademark: Dict, anti_trope: Dict) -> Dict[str, Any]:
        """Calculate overall compliance score."""
        reg_violations = regulated.get("total_violations", 0)
        tm_violations = trademark.get("total_violations", 0)
        at_violations = anti_trope.get("total_violations", 0)
        total_violations = reg_violations + tm_violations + at_violations
        score = max(0, 1.0 - total_violations * 0.05)
        return {
            "overall_score": round(score, 3),
            "regulatory_compliance": regulated.get("compliance_status", "UNKNOWN"),
            "trademark_compliance": "PASS" if tm_violations == 0 else f"FAIL ({tm_violations} violations)",
            "anti_trope_compliance": anti_trope.get("status", "UNKNOWN"),
            "total_violations": total_violations,
            "compliance_tier": (
                "FULLY_COMPLIANT" if total_violations == 0 else
                "MOSTLY_COMPLIANT" if total_violations < 5 else
                "PARTIALLY_COMPLIANT" if total_violations < 15 else
                "NON_COMPLIANT"
            )
        }

    def _get_critical_violations(self, regulated: Dict, trademark: Dict, legal: Dict) -> List[Dict[str, str]]:
        """Get all critical violations requiring immediate attention."""
        critical = []
        for finding in regulated.get("findings", []):
            if finding.get("severity") == "CRITICAL":
                critical.append({
                    "type": "REGULATED_CLAIM",
                    "claim": finding["claim"][:100],
                    "action": finding["recommended_action"]
                })
        for violation in trademark.get("trademark_violations", [])[:5]:
            critical.append({
                "type": "TRADEMARK",
                "claim": f"'{violation['found']}' should be '{violation['correct']}'",
                "action": violation["action"]
            })
        return critical

    def _generate_recommendations(self, regulated: Dict, trademark: Dict, anti_trope: Dict, legal: Dict) -> List[Dict[str, str]]:
        """Generate compliance recommendations."""
        recs = []
        if regulated.get("critical_violations", 0) > 0:
            recs.append({
                "priority": "CRITICAL",
                "action": "Remove all critical regulated claims",
                "detail": f"{regulated['critical_violations']} critical violations requiring legal review"
            })
        if trademark.get("total_violations", 0) > 0:
            recs.append({
                "priority": "HIGH",
                "action": "Fix trademark formatting violations",
                "detail": f"{trademark['total_violations']} trademark naming violations detected"
            })
        if anti_trope.get("total_violations", 0) > 0:
            recs.append({
                "priority": "MEDIUM",
                "action": "Remove anti-trope blacklist violations",
                "detail": f"{anti_trope['total_violations']} banned phrases detected"
            })
        if legal.get("legal_review_required"):
            recs.append({
                "priority": "CRITICAL",
                "action": "Submit content for legal review before publication",
                "detail": f"Risk level: {legal['risk_level']}"
            })
        return recs
