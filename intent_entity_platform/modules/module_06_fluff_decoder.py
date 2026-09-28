"""
Module 6: Algorithmic Fluff & Cliche De-Coder
Detects and neutralizes AI-generated text patterns, enforces burstiness.
"""
import re
from typing import List, Dict, Any
from ..utils.text_analytics import (
    detect_ai_patterns, sentence_length_distribution, text_statistics,
    tokenize_words, tokenize_sentences, flesch_kincaid_grade
)


class FluffClicheDecoder:
    """Module 6: Algorithmic Fluff & Cliche De-Coder"""

    def __init__(self):
        self.module_id = "M06"
        self.module_name = "Algorithmic Fluff & Cliche De-Coder"

    def analyze(self, text: str, brand_blacklist: List[str] = None, url_data: Dict = None, inputs: Dict = None) -> Dict[str, Any]:
        """Full fluff and cliché analysis pipeline with REAL competitor comparison."""
        if not text.strip():
            return {"module": self.module_id, "module_name": self.module_name, "error": "No text provided"}

        ai_patterns = detect_ai_patterns(text)
        burstiness = sentence_length_distribution(text)
        stats = text_statistics(text)
        trope_analysis = self._analyze_tropes(text, brand_blacklist or [])
        sentence_quality = self._analyze_sentence_quality(text)
        transition_analysis = self._analyze_transitions(text)
        filler_words = self._detect_filler_words(text)
        readability = self._assess_readability_depth(text)
        overall_quality = self._calculate_overall_quality(ai_patterns, burstiness, trope_analysis, sentence_quality)
        
        # NEW: Compare against real competitor writing patterns
        real_competitor_fluff_analysis = None
        if inputs:
            real_competitor_pages = inputs.get("real_competitor_pages", [])
            real_readability_analysis = inputs.get("real_readability_analysis", {})
            real_competitor_fluff_analysis = self._analyze_real_competitor_fluff(real_competitor_pages, real_readability_analysis, text)

        url_fluff_analysis = self._analyze_url_fluff(text, url_data) if url_data else None

        result = {
            "module": self.module_id,
            "module_name": self.module_name,
            "ai_pattern_detection": ai_patterns,
            "burstiness_analysis": burstiness,
            "text_statistics": stats,
            "trope_analysis": trope_analysis,
            "sentence_quality": sentence_quality,
            "transition_analysis": transition_analysis,
            "filler_word_detection": filler_words,
            "readability_depth_assessment": readability,
            "overall_quality_score": overall_quality,
            "fluff_removal_priority": self._prioritize_fluff_removals(ai_patterns, trope_analysis, filler_words),
            "rewrite_recommendations": self._generate_rewrite_recommendations(ai_patterns, burstiness, trope_analysis),
            "implementation_steps": self._generate_implementation_steps(ai_patterns, trope_analysis, filler_words, burstiness, readability),
            "where_to_add": self._generate_where_to_add(trope_analysis, filler_words, sentence_quality),
            "detailed_analysis": self._generate_detailed_analysis(ai_patterns, trope_analysis, filler_words, burstiness, readability, overall_quality),
            "real_competitor_fluff_comparison": real_competitor_fluff_analysis,
            "data_source": "real_time_competitor_analysis" if real_competitor_fluff_analysis else "heuristic_analysis"
        }

        if url_fluff_analysis:
            result["url_fluff_analysis"] = url_fluff_analysis
            result["detailed_analysis"]["url_fluff_insights"] = url_fluff_analysis

        return result

    def _analyze_real_competitor_fluff(self, competitor_pages: List[Dict], readability_analysis: Dict, user_text: str) -> Dict[str, Any]:
        """Compare user text quality against REAL competitor writing patterns."""
        if not competitor_pages:
            return {"error": "No competitor data available"}
        
        successful_pages = [p for p in competitor_pages if p.get("fetch_success")]
        if not successful_pages:
            return {"error": "No successful competitor fetches"}
        
        competitor_readability = []
        competitor_burstiness = []
        competitor_tropes = []
        
        for page in competitor_pages:
            if not page.get("fetch_success"):
                continue
            page_text = page.get("page_text", "")
            
            # Analyze readability
            words = page_text.split()
            sentences = re.split(r'[.!?]+', page_text)
            sentences = [s.strip() for s in sentences if s.strip()]
            avg_sentence_len = len(words) / max(1, len(sentences))
            
            # Analyze burstiness (sentence length variance)
            sentence_lengths = [len(s.split()) for s in sentences if s.strip()]
            if sentence_lengths:
                mean_len = sum(sentence_lengths) / len(sentence_lengths)
                variance = sum((l - mean_len) ** 2 for l in sentence_lengths) / len(sentence_lengths)
                burstiness_score = min(1.0, variance / 100)
            else:
                burstiness_score = 0
            
            # Count AI-like patterns in competitor text
            ai_patterns_count = len(re.findall(r'(?:moreover|furthermore|additionally|consequently|nevertheless|however|therefore|thus|hence)', page_text, re.IGNORECASE))
            trope_count = len(re.findall(r'(?:game-changer|cutting-edge|leverage|synergy|paradigm|innovative|transformative|revolutionary|disruptive)', page_text, re.IGNORECASE))
            
            competitor_readability.append({
                "url": page.get("url", ""),
                "position": page.get("position", 0),
                "avg_sentence_length": round(avg_sentence_len, 1),
                "word_count": len(words),
                "sentence_count": len(sentences)
            })
            competitor_burstiness.append(burstiness_score)
            competitor_tropes.append(trope_count)
        
        # Calculate benchmarks
        avg_competitor_sentence_len = sum(r["avg_sentence_length"] for r in competitor_readability) / len(competitor_readability) if competitor_readability else 0
        avg_competitor_burstiness = sum(competitor_burstiness) / len(competitor_burstiness) if competitor_burstiness else 0
        avg_competitor_tropes = sum(competitor_tropes) / len(competitor_tropes) if competitor_tropes else 0
        
        # Analyze user text for comparison
        user_words = user_text.split()
        user_sentences = re.split(r'[.!?]+', user_text)
        user_sentences = [s.strip() for s in user_sentences if s.strip()]
        user_avg_sentence_len = len(user_words) / max(1, len(user_sentences))
        user_trope_count = len(re.findall(r'(?:game-changer|cutting-edge|leverage|synergy|paradigm|innovative|transformative|revolutionary|disruptive)', user_text, re.IGNORECASE))
        
        return {
            "competitors_analyzed": len(competitor_readability),
            "competitor_benchmarks": {
                "avg_sentence_length": round(avg_competitor_sentence_len, 1),
                "avg_burstiness_score": round(avg_competitor_burstiness, 3),
                "avg_trope_count": round(avg_competitor_tropes, 1)
            },
            "user_text_comparison": {
                "user_avg_sentence_length": round(user_avg_sentence_len, 1),
                "user_trope_count": user_trope_count,
                "sentence_length_vs_competitors": round(user_avg_sentence_len - avg_competitor_sentence_len, 1),
                "trope_usage_vs_competitors": round(user_trope_count - avg_competitor_tropes, 1)
            },
            "recommendations": [
                f"Adjust sentence length to match competitor average of {avg_competitor_sentence_len:.1f} words" if abs(user_avg_sentence_len - avg_competitor_sentence_len) > 5 else "Sentence length is competitive",
                f"Reduce trope usage (competitors average {avg_competitor_tropes:.1f}, you have {user_trope_count})" if user_trope_count > avg_competitor_tropes else "Trope usage is competitive",
                f"Increase burstiness to match competitor average of {avg_competitor_burstiness:.3f}" if avg_competitor_burstiness > 0.3 else "Burstiness is adequate"
            ],
            "competitor_readability_details": competitor_readability,
            "data_source": "live_competitor_page_analysis"
        }

    def _analyze_url_fluff(self, text: str, url_data: Dict) -> Dict[str, Any]:
        """Deep analysis of actual URL content for fluff, clichés, and content quality."""
        word_count = url_data.get("word_count", 0)
        title = url_data.get("title", "")
        h2s = url_data.get("h2s", [])
        page_text = url_data.get("page_text", "")

        sentences = tokenize_sentences(text)
        words = tokenize_words(text)

        total_words = len(words)
        total_sentences = len(sentences)

        sentences_over_40_words = sum(1 for s in sentences if len(tokenize_words(s)) > 40)
        sentences_under_5_words = sum(1 for s in sentences if len(tokenize_words(s)) < 5)
        avg_sentence_length = total_words / max(1, total_sentences)

        comma_heavy_sentences = sum(1 for s in sentences if s.count(',') > 3)
        passive_voice = len(re.findall(
            r'(?:is|are|was|were)\s+(?:considered|regarded|viewed|seen|known|believed|thought|made|done|used|required|expected)',
            text, re.IGNORECASE
        ))

        weak_intensifiers = re.findall(r'\b(?:very|really|quite|rather|somewhat|fairly|pretty much|extremely|absolutely|totally|completely)\b', text, re.IGNORECASE)
        hedge_words = re.findall(r'\b(?:just|simply|literally|actually|honestly|basically|essentially|perhaps|maybe|possibly|arguably)\b', text, re.IGNORECASE)

        empty_phrases = re.findall(
            r'(?:it goes without saying|needless to say|as a matter of fact|at the end of the day|the fact of the matter is|when all is said and done|in light of the fact that|with regard to|in terms of|due to the fact that|without further ado)',
            text, re.IGNORECASE
        )

        cliche_phrases = re.findall(
            r'(?:in today\'?s (?:fast-paced|digital|ever-changing|modern|rapidly evolving|competitive|dynamic)|game[\s-]changer|revolutionary|transformative|groundbreaking|paradigm shift|disruptive|next[\s-]generation|delve into|explore|unpack|embark on a journey|harness(?:ing)? the power|unlock(?:ing)? the potential|seamless(?:ly)?|robust|cutting[\s-]edge|state[\s-]of[\s-]the[\s-]art|best[\s-]in[\s-]class|world[\s-]class|industry[\s-]leading)',
            text, re.IGNORECASE
        )

        filler_transition_words = re.findall(
            r'\b(?:furthermore|moreover|additionally|in addition|also|likewise|similarly|consequently|that being said|with that being said|all things considered)\b',
            text, re.IGNORECASE
        )

        vague_quantifiers = re.findall(
            r'\b(?:many organizations|numerous companies|several studies|growing number|increasingly|significantly|substantially|numerous|myriad|plethora|a multitude of)\b',
            text, re.IGNORECASE
        )

        vague_nouns = re.findall(
            r'\b(?:stuff|things|aspects|elements|factors|issues|concerns|various|multiple|several)\b',
            text, re.IGNORECASE
        )

        total_issues = (len(weak_intensifiers) + len(hedge_words) + len(empty_phrases) +
                       len(cliche_phrases) + len(filler_transition_words) + len(vague_quantifiers) +
                       len(vague_nouns) + sentences_over_40_words + comma_heavy_sentences + passive_voice)

        issue_density = total_issues / max(1, total_words / 100)

        content_issues = []
        if len(weak_intensifiers) > 3:
            content_issues.append(f"{len(weak_intensifiers)} weak intensifiers found ('very', 'really', 'quite'). Replace with specific data.")
        if len(hedge_words) > 3:
            content_issues.append(f"{len(hedge_words)} hedge words found ('just', 'simply', 'actually'). Remove for directness.")
        if len(empty_phrases) > 0:
            content_issues.append(f"{len(empty_phrases)} empty phrases found ('it is important to note'). Remove all.")
        if len(cliche_phrases) > 3:
            content_issues.append(f"{len(cliche_phrases)} cliché/AI phrases found. Replace with specific, factual language.")
        if len(filler_transition_words) > 5:
            content_issues.append(f"{len(filler_transition_words)} filler transitions found ('furthermore', 'moreover'). Delete and start sentences directly.")
        if len(vague_quantifiers) > 3:
            content_issues.append(f"{len(vague_quantifiers)} vague quantifiers found ('many organizations'). Replace with specific data.")
        if sentences_over_40_words > 3:
            content_issues.append(f"{sentences_over_40_words} sentences over 40 words. Split at natural clause breaks.")
        if comma_heavy_sentences > 3:
            content_issues.append(f"{comma_heavy_sentences} comma-heavy sentences (3+ commas). Break into shorter sentences.")
        if passive_voice > 5:
            content_issues.append(f"{passive_voice} passive voice constructions. Convert to active voice.")
        if avg_sentence_length > 25:
            content_issues.append(f"Average sentence length is {avg_sentence_length:.1f} words. Aim for 15-20 for readability.")
        if sentences_under_5_words > total_sentences * 0.3:
            content_issues.append(f"{sentences_under_5_words} very short sentences ({sentences_under_5_words / max(1, total_sentences) * 100:.0f}%). Add substance or combine.")

        word_freq = {}
        for word in words:
            word_lower = word.lower()
            if len(word_lower) > 3:
                word_freq[word_lower] = word_freq.get(word_lower, 0) + 1
        overused_words = sorted([(w, c) for w, c in word_freq.items() if c >= 5], key=lambda x: x[1], reverse=True)[:10]

        unique_words = set(w.lower() for w in words if len(w) > 3)
        lexical_diversity = len(unique_words) / max(1, total_words)

        return {
            "total_words": total_words,
            "total_sentences": total_sentences,
            "avg_sentence_length": round(avg_sentence_length, 1),
            "avg_sentence_length_benchmark": "(General industry guidance, unverified): 15-20 words per sentence is a common target",
            "sentences_over_40_words": sentences_over_40_words,
            "sentences_under_5_words": sentences_under_5_words,
            "comma_heavy_sentences": comma_heavy_sentences,
            "passive_voice_count": passive_voice,
            "passive_voice_benchmark": "(General industry guidance, unverified): Reduce to <5% of sentences",
            "weak_intensifiers_count": len(weak_intensifiers),
            "weak_intensifier_examples": weak_intensifiers[:5],
            "hedge_words_count": len(hedge_words),
            "hedge_word_examples": hedge_words[:5],
            "empty_phrases_count": len(empty_phrases),
            "empty_phrase_examples": [p[:60] for p in empty_phrases[:3]],
            "cliche_phrases_count": len(cliche_phrases),
            "cliche_phrase_examples": [p[:60] for p in cliche_phrases[:5]],
            "filler_transitions_count": len(filler_transition_words),
            "filler_transition_examples": filler_transition_words[:5],
            "vague_quantifiers_count": len(vague_quantifiers),
            "vague_quantifier_examples": vague_quantifiers[:5],
            "vague_nouns_count": len(vague_nouns),
            "total_fluff_issues": total_issues,
            "issue_density_per_100_words": round(issue_density, 2),
            "issue_density_benchmark": "(General industry guidance, unverified): Target <2 issues per 100 words",
            "content_quality_tier": (
                "EXCELLENT - Clean, professional writing" if issue_density < 1 else
                "GOOD - Minor cleanup needed" if issue_density < 3 else
                "NEEDS_WORK - Multiple fluff issues" if issue_density < 6 else
                "POOR - Significant rewriting required"
            ),
            "lexical_diversity": round(lexical_diversity, 3),
            "lexical_diversity_benchmark": "(General industry guidance, unverified): 0.4-0.6 lexical diversity is typical of good content",
            "overused_words": [{"word": w, "count": c} for w, c in overused_words],
            "overused_words_benchmark": "(General industry guidance, unverified): No word should appear >5% of total words",
            "content_issues": content_issues,
            "content_issues_count": len(content_issues),
            "specific_recommendations": self._generate_fluff_url_recommendations(text, url_data)
        }

    def _generate_fluff_url_recommendations(self, text: str, url_data: Dict) -> List[Dict[str, str]]:
        """Generate specific fluff removal recommendations based on actual content."""
        recs = []
        word_count = url_data.get("word_count", 0)

        weak_intensifiers = re.findall(r'\b(?:very|really|quite|rather|somewhat|fairly|extremely|absolutely|totally|completely)\b', text, re.IGNORECASE)
        if len(weak_intensifiers) > 3:
            recs.append({
                "priority": "HIGH",
                "action": f"Remove {len(weak_intensifiers)} weak intensifiers ('very', 'really', 'quite', etc.)",
                "detail": f"Found {len(weak_intensifiers)} weak intensifiers. These add no informational value. Replace with specific data or remove entirely."
            })

        hedge_words = re.findall(r'\b(?:just|simply|literally|actually|honestly|basically|essentially)\b', text, re.IGNORECASE)
        if len(hedge_words) > 3:
            recs.append({
                "priority": "HIGH",
                "action": f"Remove {len(hedge_words)} hedge words ('just', 'simply', 'actually', etc.)",
                "detail": f"Found {len(hedge_words)} hedge words that weaken your assertions. State facts directly."
            })

        empty_phrases = re.findall(
            r'(?:it goes without saying|needless to say|as a matter of fact|at the end of the day|the fact of the matter is|when all is said and done|in light of the fact that|with regard to|in terms of|due to the fact that|without further ado|it is important to note|it should be noted|it is worth mentioning)',
            text, re.IGNORECASE
        )
        if len(empty_phrases) > 0:
            recs.append({
                "priority": "HIGH",
                "action": f"Remove {len(empty_phrases)} empty phrases ('it is important to note', 'at the end of the day', etc.)",
                "detail": "Empty phrases add zero informational value. Delete them and state the important fact directly."
            })

        cliche_phrases = re.findall(
            r'(?:in today\'?s (?:fast-paced|digital|ever-changing|modern|rapidly evolving)|game[\s-]changer|revolutionary|transformative|harness(?:ing)? the power|unlock(?:ing)? the potential|seamless(?:ly)?|robust|cutting[\s-]edge|delve into)',
            text, re.IGNORECASE
        )
        if len(cliche_phrases) > 3:
            recs.append({
                "priority": "HIGH",
                "action": f"Replace {len(cliche_phrases)} cliché/AI phrases with specific, factual language",
                "detail": f"Found {len(cliche_phrases)} clichés. Replace 'game-changer' with specific metrics, 'seamless' with measurable integrations."
            })

        filler_transitions = re.findall(r'\b(?:furthermore|moreover|additionally|in addition|that being said|with that being said)\b', text, re.IGNORECASE)
        if len(filler_transitions) > 5:
            recs.append({
                "priority": "MEDIUM",
                "action": f"Delete {len(filler_transitions)} filler transition words ('furthermore', 'moreover', 'additionally')",
                "detail": "Transition words are often unnecessary. Start sentences directly with the new point."
            })

        sentences = tokenize_sentences(text)
        long_sentences = [s for s in sentences if len(tokenize_words(s)) > 40]
        if len(long_sentences) > 3:
            recs.append({
                "priority": "MEDIUM",
                "action": f"Split {len(long_sentences)} sentences over 40 words into shorter, clearer sentences",
                "detail": f"Found {len(long_sentences)} overly long sentences. Break at natural clause breaks for readability."
            })

        passive_voice = len(re.findall(
            r'(?:is|are|was|were)\s+(?:considered|regarded|viewed|seen|known|believed|thought|made|done|used|required|expected)',
            text, re.IGNORECASE
        ))
        if passive_voice > 5:
            recs.append({
                "priority": "MEDIUM",
                "action": f"Convert {passive_voice} passive voice constructions to active voice",
                "detail": "Use '[Expert] found that...' instead of 'It is believed that...' for stronger, more direct writing."
            })

        vague_quantifiers = re.findall(r'\b(?:many organizations|numerous companies|several studies|growing number|increasingly|significantly|substantially|numerous|myriad|plethora|a multitude of)\b', text, re.IGNORECASE)
        if len(vague_quantifiers) > 3:
            recs.append({
                "priority": "MEDIUM",
                "action": f"Replace {len(vague_quantifiers)} vague quantifiers with specific data",
                "detail": "Replace 'many organizations' with '67% of organizations' (cite source). Specificity builds credibility."
            })

        return recs

    def _analyze_tropes(self, text: str, brand_blacklist: List[str]) -> Dict[str, Any]:
        """Analyze overused tropes and clichés."""
        COMMON_TROPES = {
            "in_todays": [
                r"in\s+today'?s\s+(?:fast-paced|digital|ever-changing|modern|rapidly\s+evolving|competitive|dynamic)",
                r"in\s+a\s+world\s+(?:of|where|wherein|that)",
                r"in\s+(?:the\s+)?(?:digital\s+age|modern\s+era|information\s+age|current\s+landscape)"
            ],
            "game_changer": [
                r"game[\s-]changer", r"revolutionary", r"transformative", r"groundbreaking",
                r"paradigm\s+shift", r"disruptive", r"next[\s-]generation"
            ],
            "delve_explorer": [
                r"delve\s+(?:into|deeper|deeper\s+into)", r"explore", r"unpack",
                r"embark\s+on\s+a\s+journey", r"dive\s+(?:into|deep|deeper)"
            ],
            "arness_power": [
                r"harness(?:ing)?\s+the\s+power", r"unlock(?:ing)?\s+the\s+potential",
                r"leverage(?:ing)?", r"tap\s+(?:into|the\s+power\s+of)",
                r"embrace(?:ing)?\s+(?:the\s+power|the\s+future)"
            ],
            "seamless_robust": [
                r"seamless(?:ly)?", r"robust", r"cutting[\s-]edge", r"state[\s-]of[\s-]the[\s-]art",
                r"best[\s-]in[\s-]class", r"world[\s-]class", r"industry[\s-]leading"
            ],
            "furthermore_additionally": [
                r"furthermore", r"moreover", r"additionally", r"in\s+addition",
                r"also", r"likewise", r"similarly", r"consequently"
            ],
            "it_is_important": [
                r"it\s+is\s+(?:important|crucial|essential|vital|imperative)\s+to\s+(?:note|mention|highlight)",
                r"it\s+(?:should|must)\s+be\s+noted",
                r"it\s+is\s+worth\s+(?:mentioning|noting|highlighting)",
                r"needless\s+to\s+say", r"obviously", r"of\s+course"
            ],
            "passive_constructions": [
                r"(?:is|are|was|were)\s+(?:considered|regarded|viewed|seen|known|believed|thought)",
                r"it\s+(?:is|was)\s+(?:widely|generally|commonly)\s+(?:recognized|accepted|known|believed)"
            ],
            "vague_quantifiers": [
                r"many\s+organizations", r"numerous\s+companies", r"several\s+studies",
                r"growing\s+number", r"increasingly", r"significantly", r"substantially",
                r"numerous", r"myriad", r"plethora", r"a\s+multitude\s+of"
            ],
            "filler_transitions": [
                r"at\s+the\s+end\s+of\s+the\s+day", r"when\s+all\s+(?:is\s+)?said\s+and\s+done",
                r"that\s+being\s+said", r"with\s+that\s+being\s+said",
                r"all\s+things\s+considered", r"in\s+conclusion", r"to\s+(?:sum\s+up|wrap\s+up)",
                r"without\s+further\s+ado", r"let'?s?\s+(?:dive|delve|explore|unpack|examine)"
            ]
        }
        combined_blacklist = list(set(
            brand_blacklist + [
                "in today's", "game-changer", "delve", "harness the power",
                "seamless", "robust", "cutting-edge", "furthermore", "moreover",
                "it is important to note", "needless to say", "at the end of the day"
            ]
        ))
        found_tropes = []
        all_flags = []
        for trope_name, patterns in COMMON_TROPES.items():
            trope_matches = []
            for pattern in patterns:
                for m in re.finditer(pattern, text, re.IGNORECASE):
                    context_start = max(0, m.start() - 40)
                    context_end = min(len(text), m.end() + 40)
                    context = text[context_start:context_end].strip()
                    severity = "HIGH" if trope_name in ["in_todays", "game_changer", "delve_explorer"] else "MEDIUM"
                    trope_matches.append({
                        "match": m.group(),
                        "position": m.start(),
                        "context": f"...{context}...",
                        "severity": severity,
                        "suggestion": self._suggest_trope_replacement(m.group(), trope_name)
                    })
            if trope_matches:
                found_tropes.append({
                    "trope_category": trope_name,
                    "occurrences": len(trope_matches),
                    "matches": trope_matches,
                    "severity": "HIGH" if len(trope_matches) > 3 else "MEDIUM" if len(trope_matches) > 1 else "LOW"
                })
                all_flags.extend(trope_matches)

        blacklist_flags = []
        for term in combined_blacklist:
            pattern = re.escape(term)
            for m in re.finditer(pattern, text, re.IGNORECASE):
                blacklist_flags.append({
                    "match": m.group(),
                    "position": m.start(),
                    "context": text[max(0, m.start()-30):min(len(text), m.end()+30)].strip(),
                    "severity": "CRITICAL",
                    "suggestion": f"Remove or replace blacklisted term: '{term}'"
                })

        return {
            "trope_categories_found": len(found_tropes),
            "total_trope_occurrences": sum(t["occurrences"] for t in found_tropes),
            "trope_details": found_tropes,
            "blacklist_violations": blacklist_flags,
            "trope_severity_score": min(1.0, (len(all_flags) + len(blacklist_flags)) * 0.08),
            "unique_tropes_detected": [t["trope_category"] for t in found_tropes],
            "cleanliness_grade": (
                "A - Professional Grade" if len(all_flags) + len(blacklist_flags) == 0 else
                "B - Minor Cleanup Needed" if len(all_flags) + len(blacklist_flags) <= 3 else
                "C - Moderate Revision Required" if len(all_flags) + len(blacklist_flags) <= 8 else
                "D - Significant Rewrite Needed" if len(all_flags) + len(blacklist_flags) <= 15 else
                "F - Complete Rewrite Recommended"
            )
        }

    def _suggest_trope_replacement(self, match: str, trope_category: str) -> str:
        """Suggest replacement for detected trope."""
        suggestions = {
            "in_todays": "Remove opening filler. Start directly with the subject or a specific fact.",
            "game_changer": "Replace with specific metric: 'increases X by Y%' or 'reduces Z by N hours'",
            "delve_explorer": "Remove and state the topic directly: '[Entity] operates by...'",
            "arness_power": "Replace with specific capability: '[Entity] enables [specific outcome]'",
            "seamless_robust": "Replace with measurable attribute: 'integrates with [X] systems in [timeframe]'",
            "furthermore_additionally": "Delete transition word. Start new sentence directly.",
            "it_is_important": "Remove filler. State the important fact directly.",
            "passive_constructions": "Convert to active voice: '[Expert] found that...' instead of 'It is believed that...'",
            "vague_quantifiers": "Replace with specific data: '67% of organizations' instead of 'many organizations'",
            "filler_transitions": "Delete transition. New paragraph should flow logically without it."
        }
        return suggestions.get(trope_category, "Review and replace with specific, factual language")

    def _analyze_sentence_quality(self, text: str) -> Dict[str, Any]:
        """Analyze individual sentence quality."""
        sentences = tokenize_sentences(text)
        if not sentences:
            return {"sentences": [], "issues": []}

        quality_issues = []
        sentence_details = []
        for i, sent in enumerate(sentences):
            words = tokenize_words(sent)
            word_count = len(words)
            details = {
                "index": i + 1,
                "text_preview": sent[:100] + "..." if len(sent) > 100 else sent,
                "word_count": word_count,
                "issues": []
            }
            if word_count > 40:
                details["issues"].append("TOO_LONG - Split into shorter sentences")
                quality_issues.append({"type": "overly_long", "sentence": i+1, "severity": "MEDIUM"})
            if word_count < 3 and i > 0:
                details["issues"].append("TOO_SHORT - May lack substance")
                quality_issues.append({"type": "too_short", "sentence": i+1, "severity": "LOW"})
            if sent.count(',') > 3:
                details["issues"].append("COMMA_HEAVY - Too many clauses")
                quality_issues.append({"type": "comma_heavy", "sentence": i+1, "severity": "MEDIUM"})
            if re.search(r'(?:very|really|quite|extremely|absolutely|totally|completely)\s+\w+', sent, re.IGNORECASE):
                details["issues"].append("WEAK_INTENSIFIER - Remove unnecessary intensifier")
                quality_issues.append({"type": "weak_intensifier", "sentence": i+1, "severity": "LOW"})
            if sent.startswith(('The ', 'A ', 'An ', 'This ', 'That ', 'These ', 'Those ')):
                details["issues"].append("STARTS_WITH_DETERMINER - Consider starting with subject or verb")
                quality_issues.append({"type": "determiner_start", "sentence": i+1, "severity": "LOW"})
            sentence_details.append(details)

        return {
            "total_sentences": len(sentences),
            "sentences_with_issues": sum(1 for s in sentence_details if s["issues"]),
            "quality_issues": quality_issues,
            "sentence_details": sentence_details[:30],
            "average_quality_score": round(
                1.0 - (len(quality_issues) / max(1, len(sentences) * 2)), 3
            )
        }

    def _analyze_transitions(self, text: str) -> Dict[str, Any]:
        """Analyze transition word usage."""
        sentences = tokenize_sentences(text)
        transitions = {
            "additive": ["furthermore", "moreover", "additionally", "also", "in addition", "likewise"],
            "contrast": ["however", "nevertheless", "nonetheless", "on the other hand", "conversely", "but"],
            "causal": ["therefore", "consequently", "thus", "hence", "as a result", "because"],
            "sequential": ["first", "second", "third", "next", "then", "finally", "subsequently"],
            "emphasis": ["indeed", "in fact", "particularly", "especially", "notably", "significantly"],
            "example": ["for example", "for instance", "such as", "specifically", "to illustrate"],
            "temporal": ["meanwhile", "subsequently", "previously", "currently", "initially"],
        }
        transition_usage = {}
        for category, words in transitions.items():
            count = 0
            found_words = []
            for word in words:
                occurrences = len(re.findall(r'\b' + re.escape(word) + r'\b', text, re.IGNORECASE))
                if occurrences > 0:
                    count += occurrences
                    found_words.append({"word": word, "count": occurrences})
            transition_usage[category] = {"count": count, "words_found": found_words}

        total_transitions = sum(t["count"] for t in transition_usage.values())
        sentences = tokenize_sentences(text)
        transition_density = total_transitions / max(1, len(sentences))

        overused = [cat for cat, data in transition_usage.items() if data["count"] > len(sentences) * 0.3]
        missing = [cat for cat, data in transition_usage.items() if data["count"] == 0]

        return {
            "transition_usage": transition_usage,
            "total_transitions": total_transitions,
            "transition_density": round(transition_density, 4),
            "density_assessment": (
                "TOO_DENSE - Reduce transition words" if transition_density > 0.4 else
                "OPTIMAL" if transition_density > 0.15 else
                "TOO_SPARSE - Add more variety" if transition_density > 0.05 else
                "MONOTONOUS - Significant variety needed"
            ),
            "overused_categories": overused,
            "missing_categories": missing,
            "recommendation": self._get_transition_recommendation(transition_usage, transition_density)
        }

    def _get_transition_recommendation(self, usage: Dict, density: float) -> str:
        """Get transition word recommendations."""
        if density > 0.4:
            return "Remove 50% of transition words - let content flow naturally between paragraphs"
        if density < 0.05:
            return "Add transitional phrases to improve readability - aim for 15-25% of sentences"
        overused = [cat for cat, data in usage.items() if data["count"] > 5]
        if overused:
            return f"Reduce {', '.join(overused)} transitions and vary with alternative phrases"
        return "Transition usage is within optimal range - maintain current balance"

    def _detect_filler_words(self, text: str) -> Dict[str, Any]:
        """Detect filler words and empty phrases."""
        filler_patterns = {
            "single_word_filler": [
                (r'\b(?:very|really|quite|rather|somewhat|fairly|pretty much)\b', "weak_intensifier"),
                (r'\b(?:just|simply|literally|actually|honestly|basically|essentially)\b', "hedge_word"),
                (r'\b(?:obviously|clearly|undoubtedly|certainly|definitely)\b', "false_emphasis"),
                (r'\b(?:perhaps|maybe|possibly|arguably)\b', "hedging"),
                (r'\b(?:stuff|things|aspects|elements|factors|issues|concerns)\b', "vague_noun"),
            ],
            "phrase_filler": [
                (r'(?:it\s+goes\s+without\s+saying)', "empty_phrase"),
                (r'(?:needless\s+to\s+say)', "empty_phrase"),
                (r'(?:as\s+a\s+matter\s+of\s+fact)', "empty_phrase"),
                (r'(?:at\s+the\s+end\s+of\s+the\s+day)', "empty_phrase"),
                (r'(?:the\s+fact\s+of\s+the\s+matter\s+is)', "empty_phrase"),
                (r'(?:when\s+all\s+(?:is\s+)?said\s+and\s+done)', "empty_phrase"),
                (r'(?:in\s+light\s+of\s+the\s+fact\s+that)', "empty_phrase"),
                (r'(?:with\s+regard\s+to)', "empty_phrase"),
                (r'(?:in\s+terms\s+of)', "empty_phrase"),
                (r'(?:due\s+to\s+the\s+fact\s+that)', "empty_phrase"),
            ]
        }
        filler_findings = []
        total_filler_count = 0
        for category, patterns in filler_patterns.items():
            for pattern, filler_type in patterns:
                matches = list(re.finditer(pattern, text, re.IGNORECASE))
                if matches:
                    for m in matches:
                        filler_findings.append({
                            "match": m.group(),
                            "type": filler_type,
                            "category": category,
                            "position": m.start(),
                            "context": text[max(0, m.start()-20):min(len(text), m.end()+20)].strip(),
                            "action": "REMOVE" if filler_type in ["empty_phrase", "weak_intensifier"] else "REPLACE"
                        })
                        total_filler_count += 1

        words = tokenize_words(text)
        filler_density = total_filler_count / max(1, len(words)) * 100

        return {
            "total_filler_count": total_filler_count,
            "filler_density_percentage": round(filler_density, 2),
            "filler_findings": filler_findings[:30],
            "filler_severity": (
                "CRITICAL" if filler_density > 5 else
                "HIGH" if filler_density > 3 else
                "MODERATE" if filler_density > 1.5 else
                "LOW" if filler_density > 0.5 else
                "MINIMAL"
            ),
            "words_removable": total_filler_count,
            "estimated_readability_improvement": f"Removing {total_filler_count} filler words could improve reading ease by {min(10, total_filler_count * 0.5):.1f} points"
        }

    def _assess_readability_depth(self, text: str) -> Dict[str, Any]:
        """Assess readability vs depth balance."""
        grade = flesch_kincaid_grade(text)
        words = tokenize_words(text)
        sentences = tokenize_sentences(text)
        avg_sentence_length = len(words) / max(1, len(sentences))
        complex_word_ratio = sum(1 for w in words if len(w) > 10) / max(1, len(words))
        return {
            "flesch_kincaid_grade": round(grade, 2),
            "average_sentence_length": round(avg_sentence_length, 2),
            "complex_word_ratio": round(complex_word_ratio, 4),
            "readability_tier": (
                "VERY_EASY (Grade 4-6)" if grade <= 6 else
                "EASY (Grade 6-8)" if grade <= 8 else
                "MODERATE (Grade 8-10)" if grade <= 10 else
                "DIFFICULT (Grade 10-14)" if grade <= 14 else
                "VERY_DIFFICULT (Grade 14+)"
            ),
            "depth_tier": (
                "SURFACE" if complex_word_ratio < 0.05 else
                "MODERATE" if complex_word_ratio < 0.12 else
                "DEEP" if complex_word_ratio < 0.2 else
                "EXPERT"
            ),
            "balance_assessment": self._assess_balance(grade, complex_word_ratio)
        }

    def _assess_balance(self, grade: float, complex_ratio: float) -> str:
        """Assess readability-depth balance."""
        if grade < 8 and complex_ratio < 0.05:
            return "TOO_SIMPLE - Content lacks depth for most audiences"
        if grade > 14 and complex_ratio > 0.2:
            return "TOO_COMPLEX - Content may be inaccessible to target audience"
        if 8 <= grade <= 12 and 0.05 <= complex_ratio <= 0.15:
            return "WELL_BALANCED - Good mix of accessibility and depth"
        if grade < 10 and complex_ratio > 0.1:
            return "ACCESSIBLE_WITH_DEPTH - Good for broad audiences"
        if grade > 12 and complex_ratio < 0.1:
            return "FORMAL_BUT_ACCESSIBLE - Suitable for professional audiences"
        return "ACCEPTABLE - Minor adjustments may improve engagement"

    def _calculate_overall_quality(self, ai_patterns: Dict, burstiness: Dict,
                                     tropes: Dict, sentence_quality: Dict) -> Dict[str, Any]:
        """Calculate overall content quality score."""
        ai_penalty = ai_patterns.get("ai_probability_score", 0) * 0.3
        burstiness_penalty = 0
        if burstiness.get("uniformity_risk") == "critical":
            burstiness_penalty = 0.25
        elif burstiness.get("uniformity_risk") == "high":
            burstiness_penalty = 0.15
        elif burstiness.get("uniformity_risk") == "moderate":
            burstiness_penalty = 0.08
        trope_penalty = tropes.get("trope_severity_score", 0) * 0.2
        sentence_penalty = max(0, (1 - sentence_quality.get("average_quality_score", 1)) * 0.15)
        overall = max(0, 1.0 - ai_penalty - burstiness_penalty - trope_penalty - sentence_penalty)
        return {
            "overall_score": round(overall, 3),
            "component_scores": {
                "ai_pattern_penalty": round(ai_penalty, 3),
                "burstiness_penalty": round(burstiness_penalty, 3),
                "trope_penalty": round(trope_penalty, 3),
                "sentence_quality_penalty": round(sentence_penalty, 3)
            },
            "quality_grade": (
                "A+ (Exceptional)" if overall > 0.9 else
                "A (Professional)" if overall > 0.8 else
                "B+ (Good)" if overall > 0.7 else
                "B (Acceptable)" if overall > 0.6 else
                "C (Needs Work)" if overall > 0.5 else
                "D (Poor)" if overall > 0.3 else
                "F (Rewrite Required)"
            ),
            "primary_improvement_areas": self._identify_primary_improvements(ai_patterns, burstiness, tropes)
        }

    def _identify_primary_improvements(self, ai_patterns: Dict, burstiness: Dict, tropes: Dict) -> List[str]:
        """Identify primary areas for improvement."""
        areas = []
        if ai_patterns.get("ai_probability_score", 0) > 0.5:
            areas.append("Reduce AI-generated text patterns - increase human-like variety")
        if burstiness.get("uniformity_risk") in ["critical", "high"]:
            areas.append("Increase sentence length variation - add short punchy sentences mixed with complex ones")
        if tropes.get("total_trope_occurrences", 0) > 5:
            areas.append("Remove overused industry clichés and AI filler phrases")
        if tropes.get("blacklist_violations"):
            areas.append("Remove all blacklisted terms immediately")
        return areas[:5]

    def _prioritize_fluff_removals(self, ai_patterns: Dict, tropes: Dict, fillers: Dict) -> List[Dict[str, str]]:
        """Prioritize fluff removal actions."""
        priorities = []
        if tropes.get("blacklist_violations"):
            priorities.append({
                "priority": "CRITICAL",
                "action": "Remove all blacklisted terms",
                "count": len(tropes["blacklist_violations"]),
                "impact": "Legal/brand compliance"
            })
        if tropes.get("total_trope_occurrences", 0) > 0:
            priorities.append({
                "priority": "HIGH",
                "action": "Replace detected AI clichés and tropes",
                "count": tropes["total_trope_occurrences"],
                "impact": "Content quality and uniqueness"
            })
        if ai_patterns.get("total_flags", 0) > 0:
            priorities.append({
                "priority": "HIGH",
                "action": "Remove AI-generated text patterns",
                "count": ai_patterns["total_flags"],
                "impact": "Human-like writing quality"
            })
        if fillers.get("total_filler_count", 0) > 0:
            priorities.append({
                "priority": "MEDIUM",
                "action": "Remove filler words and empty phrases",
                "count": fillers["total_filler_count"],
                "impact": "Readability and conciseness"
            })
        return priorities

    def _generate_rewrite_recommendations(self, ai_patterns: Dict, burstiness: Dict,
                                            tropes: Dict) -> List[Dict[str, str]]:
        """Generate specific rewrite recommendations."""
        recs = []
        for category, matches in ai_patterns.get("findings", {}).items():
            if matches:
                recs.append({
                    "priority": "HIGH" if category in ["opening_filler", "hyperbolic_claims"] else "MEDIUM",
                    "action": f"Remove {len(matches)} instances of {category.replace('_', ' ')}",
                    "detail": f"Example: '{matches[0]['match']}' at position {matches[0]['position']}"
                })
        if burstiness.get("uniformity_risk") in ["critical", "high"]:
            recs.append({
                "priority": "HIGH",
                "action": "Restructure sentences for varied rhythm",
                "detail": f"Burstiness score: {burstiness.get('burstiness_score', 0)} - need mix of 3-word and 40-word sentences"
            })
        return recs[:10]

    def _generate_implementation_steps(self, ai_patterns: Dict, trope_analysis: Dict,
                                        filler_words: Dict, burstiness: Dict,
                                        readability: Dict) -> List[str]:
        steps = []
        steps.append("Step 1: Remove all blacklisted terms identified in the trope analysis - these are critical compliance violations")
        steps.append("Step 2: Replace all 'in today's fast-paced/modern/digital world' opening phrases with direct subject or fact")
        steps.append("Step 3: Replace 'game-changer', 'revolutionary', 'transformative' with specific metrics and measurable outcomes")
        steps.append("Step 4: Remove 'delve into', 'explore', 'unpack' and state the topic directly in the first sentence")
        steps.append("Step 5: Replace 'harness the power', 'unlock the potential', 'leverage' with specific capability descriptions")
        steps.append("Step 6: Replace 'seamless', 'robust', 'cutting-edge' with measurable attributes and specific integrations")
        steps.append("Step 7: Delete all filler transitions ('furthermore', 'moreover', 'additionally') and start sentences directly")
        steps.append("Step 8: Remove 'it is important to note' and all empty phrases ('at the end of the day', 'needless to say')")
        steps.append("Step 9: Remove all filler words ('very', 'really', 'quite', 'just', 'simply', 'literally', 'actually')")
        steps.append("Step 10: Restructure sentences for varied length - mix 3-word punchy sentences with 30-40 word complex ones")
        steps.append("Step 11: Convert passive constructions to active voice ('[Expert] found that...' not 'It is believed that...')")
        steps.append("Step 12: Replace vague quantifiers ('many organizations', 'numerous companies') with specific data points")
        return steps

    def _generate_where_to_add(self, trope_analysis: Dict, filler_words: Dict,
                                sentence_quality: Dict) -> List[str]:
        locations = []
        locations.append("Review and replace all flagged tropes in the body paragraphs identified in trope_details")
        locations.append("Remove filler words from all H2 section opening paragraphs where they reduce directness")
        locations.append("Replace clichés in the article introduction (first 100 words) where they have highest visibility")
        locations.append("Fix overly long sentences (40+ words) by splitting at natural clause breaks within each H2 section")
        locations.append("Remove weak intensifiers ('very', 'really', 'quite') from throughout the body content")
        locations.append("Replace passive constructions in the Benefits and Implementation H2 sections with active voice")
        locations.append("Clean up comma-heavy sentences (3+ commas) by breaking into shorter, clearer sentences")
        locations.append("Remove empty phrases and filler transitions from paragraph openings throughout the article")
        locations.append("Replace vague nouns ('stuff', 'things', 'aspects') with specific terminology throughout the content")
        locations.append("Fix determiner-started sentences ('The', 'A', 'This') in high-visibility positions near H2 headings")
        return locations

    def _generate_detailed_analysis(self, ai_patterns: Dict, trope_analysis: Dict,
                                     filler_words: Dict, burstiness: Dict,
                                     readability: Dict, overall_quality: Dict) -> Dict[str, Any]:
        return {
            "ai_pattern_insights": {
                "ai_probability_score": ai_patterns.get("ai_probability_score", 0),
                "total_flags": ai_patterns.get("total_flags", 0),
                "benchmark": "(General industry guidance, unverified): Human-written content typically has AI probability <0.3; 0.5+ indicates likely AI generation patterns",
                "statistical_range": f"AI probability: {ai_patterns.get('ai_probability_score', 0)*100:.0f}% (unverified heuristic target: <30%)",
                "expert_recommendation": "Reduce AI probability below 30% by adding unique voice, specific examples, and personal experience",
                "common_mistakes": ["Not addressing AI patterns before publishing", "Only removing surface-level patterns without structural changes", "Ignoring opening filler that signals AI generation"],
                "success_metrics": ["AI probability < 30%", "No AI pattern flags in first paragraph", "Unique voice throughout content"],
                "data_origin": "unverified_industry_heuristic - not measured for this page"
            },
            "trope_analysis_insights": {
                "total_trope_occurrences": trope_analysis.get("total_trope_occurrences", 0),
                "trope_categories_found": trope_analysis.get("trope_categories_found", 0),
                "cleanliness_grade": trope_analysis.get("cleanliness_grade", "UNKNOWN"),
                "blacklist_violations": len(trope_analysis.get("blacklist_violations", [])),
                "benchmark": "(General industry guidance, unverified): Professional content has 0-2 trope occurrences; 5+ indicates significant AI cliché usage",
                "statistical_range": f"Trope occurrences: {trope_analysis.get('total_trope_occurrences', 0)} across {trope_analysis.get('trope_categories_found', 0)} categories",
                "expert_recommendation": "Eliminate all blacklist violations first, then replace HIGH severity tropes with specific, factual language",
                "common_mistakes": ["Not checking for blacklist violations before publishing", "Replacing one cliché with another", "Missing subtle AI patterns like 'furthermore' and 'moreover'"],
                "success_metrics": ["Cleanliness grade A or B", "Zero blacklist violations", "<3 total trope occurrences"],
                "data_origin": "unverified_industry_heuristic - not measured for this page"
            },
            "filler_word_insights": {
                "total_filler_count": filler_words.get("total_filler_count", 0),
                "filler_density_percentage": filler_words.get("filler_density_percentage", 0),
                "filler_severity": filler_words.get("filler_severity", "UNKNOWN"),
                "benchmark": "(General industry guidance, unverified): Professional content has <1% filler density; >3% significantly reduces readability and credibility",
                "statistical_range": f"Filler density: {filler_words.get('filler_density_percentage', 0):.1f}% (unverified heuristic target: <1%)",
                "expert_recommendation": "Remove all empty phrases and weak intensifiers - they add zero informational value",
                "common_mistakes": ["Keeping 'it is important to note' and similar empty phrases", "Using 'just', 'simply', 'actually' as hedges", "Not removing filler from high-visibility positions"],
                "success_metrics": ["Filler density < 1%", "Zero empty phrases", "Zero weak intensifiers in first 200 words"],
                "data_origin": "unverified_industry_heuristic - not measured for this page"
            },
            "burstiness_insights": {
                "burstiness_score": burstiness.get("burstiness_score", 0),
                "uniformity_risk": burstiness.get("uniformity_risk", "unknown"),
                "benchmark": "(General industry guidance, unverified): Natural writing has burstiness score 0.5-0.8; uniform sentence lengths (score <0.3) indicate AI patterns",
                "statistical_range": f"Burstiness: {burstiness.get('burstiness_score', 0):.2f} (uniformity risk: {burstiness.get('uniformity_risk', 'unknown')})",
                "expert_recommendation": "Create varied rhythm by mixing 3-word sentences with 30-40 word sentences throughout the content",
                "common_mistakes": ["Writing all sentences at similar length", "Not varying sentence structure between paragraphs", "Ignoring burstiness uniformity risk"],
                "success_metrics": ["Burstiness score > 0.5", "Uniformity risk < moderate", "Sentence length range from 5 to 45 words"],
                "data_origin": "unverified_industry_heuristic - not measured for this page"
            },
            "readability_insights": {
                "flesch_kincaid_grade": readability.get("flesch_kincaid_grade", 0),
                "readability_tier": readability.get("readability_tier", "UNKNOWN"),
                "depth_tier": readability.get("depth_tier", "UNKNOWN"),
                "balance_assessment": readability.get("balance_assessment", "UNKNOWN"),
                "benchmark": "(General industry guidance, unverified): Optimal readability for B2B content is Grade 8-12 with 5-15% complex word ratio",
                "statistical_range": f"Grade level: {readability.get('flesch_kincaid_grade', 0):.1f} ({readability.get('readability_tier', 'UNKNOWN')})",
                "expert_recommendation": "Aim for Grade 8-12 readability with DEEP complexity tier for professional audiences",
                "common_mistakes": ["Writing too simply for professional audiences", "Over-complicating without need", "Not balancing accessibility with depth"],
                "success_metrics": ["Grade 8-12 readability", "DEEP complexity tier", "WELL_BALANCED or ACCESSIBLE_WITH_DEPTH assessment"],
                "data_origin": "unverified_industry_heuristic - not measured for this page"
            },
            "overall_quality_insights": {
                "overall_score": overall_quality.get("overall_score", 0),
                "quality_grade": overall_quality.get("quality_grade", "UNKNOWN"),
                "primary_improvement_areas": overall_quality.get("primary_improvement_areas", []),
                "benchmark": "(General industry guidance, unverified): Grade A content scores 0.8+; Grade B is acceptable; Grade C or below requires revision",
                "statistical_range": f"Overall quality: {overall_quality.get('overall_score', 0)*100:.0f}% ({overall_quality.get('quality_grade', 'UNKNOWN')})",
                "expert_recommendation": "Address primary improvement areas in priority order: AI patterns first, then burstiness, then tropes",
                "common_mistakes": ["Not addressing the primary improvement area", "Making surface-level changes without structural rewriting", "Publishing content below Grade B quality"],
                "success_metrics": ["Quality grade B+ or higher", "Overall score > 0.7", "All penalties < 0.15"],
                "data_origin": "unverified_industry_heuristic - not measured for this page"
            }
        }
