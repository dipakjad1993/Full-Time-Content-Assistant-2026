"""
Module 11: Synthetic RAG (Retrieval-Augmented Generation) Tester
Tests content for RAG retrieval optimization across vector databases.
"""
import re
import math
from typing import List, Dict, Any
from ..utils.text_analytics import (
    chunk_text_semantic, tokenize_words, tokenize_sentences,
    cosine_similarity, tf_idf_vectorize, extract_keyphrases
)


class RAGTester:
    """Module 11: Synthetic RAG (Retrieval-Augmented Generation) Tester"""

    def __init__(self):
        self.module_id = "M11"
        self.module_name = "Synthetic RAG (Retrieval-Augmented Generation) Tester"

    def analyze(self, text: str = "", target_queries: List[str] = None, inputs: Dict[str, Any] = None) -> Dict[str, Any]:
        """Full RAG testing pipeline."""
        inputs = inputs or {}
        url_data = inputs.get("_url_data", None)

        real_rag_analysis = {}
        if url_data:
            real_rag_analysis = self._analyze_url_rag_compatibility(url_data, target_queries)

        if not text.strip() and not url_data:
            return {"module": self.module_id, "module_name": self.module_name, "error": "No text provided"}

        target_queries = target_queries or []
        use_text = text if text.strip() else url_data.get("page_text", "") if url_data else ""
        chunks = chunk_text_semantic(use_text, max_tokens=400)
        chunk_analysis = self._analyze_chunks(chunks)
        query_alignment = self._test_query_alignment(chunks, target_queries)
        standalone_test = self._test_standalone_context(chunks)
        embedding_readiness = self._assess_embedding_readiness(chunks)
        retrieval_simulation = self._simulate_retrieval(chunks, target_queries)
        optimization_report = self._generate_optimization_report(chunks, chunk_analysis, query_alignment)

        return {
            "module": self.module_id,
            "module_name": self.module_name,
            "chunk_analysis": chunk_analysis,
            "query_alignment": query_alignment,
            "standalone_context_test": standalone_test,
            "embedding_readiness": embedding_readiness,
            "retrieval_simulation": retrieval_simulation,
            "optimization_report": optimization_report,
            "url_rag_analysis": real_rag_analysis,
            "overall_rag_score": self._calculate_overall_rag_score(chunk_analysis, query_alignment, standalone_test),
            "recommendations": self._generate_recommendations(chunk_analysis, query_alignment, standalone_test, embedding_readiness),
            "implementation_steps": [
                "Step 1: Restructure content into semantic chunks of 200-500 tokens each",
                "Step 2: Ensure each chunk starts with a clear topic sentence or definition",
                "Step 3: Replace ambiguous pronouns (this, it, they) with explicit entity names at chunk boundaries",
                "Step 4: Add explicit entity mentions at the start of each chunk for better embedding",
                "Step 5: Split content at natural paragraph boundaries, not mid-sentence",
                "Step 6: Create a content hierarchy with H2/H3 headings where each section is independently retrievable",
                "Step 7: Test chunk standalone context by reading each chunk in isolation",
                "Step 8: Validate chunk sizes using token counting (target: 200-500 tokens)",
                "Step 9: Run query alignment tests against target search queries",
                "Step 10: Monitor retrieval performance across vector databases (Pinecone, Weaviate, Chroma)"
            ],
            "where_to_add": [
                "Place topic sentences at the beginning of each paragraph for chunk start",
                "Add entity names in parentheses after pronouns at chunk boundaries",
                "Include definition statements ('X is a...') at the start of new concept sections",
                "Add transitional phrases between chunks to maintain context flow",
                "Place key terms and entities in H2/H3 headings for better chunk identification",
                "Include summary statements at the end of major sections for context",
                "Add metadata tags (topic, entity, intent) to each chunk for vector database filtering",
                "Place cross-reference links between related chunks for context enrichment"
            ],
            "detailed_analysis": {
                "industry_benchmarks": {
                    "data_origin": "unverified_industry_heuristic - not measured for this page",
                    "optimal_chunk_size": "200-500 tokens (OpenAI/Anthropic standard for embedding)",
                    "self_contained_chunk_ratio": "Top-performing RAG content achieves 90%+ self-contained chunks",
                    "query_alignment_score": "Excellent alignment: >0.7 cosine similarity with target queries",
                    "definition_start_ratio": ">50% of chunks should start with clear definitions",
                    "retrieval_accuracy": "Well-optimized content achieves 80%+ retrieval accuracy in RAG systems"
                },
                "statistical_ranges": {
                    "data_origin": "unverified_industry_heuristic - not measured for this page",
                    "chunk_token_range": "200-500 tokens per chunk (optimal for embedding windows)",
                    "sentence_count_per_chunk": "3-8 sentences for adequate context without noise",
                    "entity_mentions_per_chunk": "2-3 explicit entity mentions for embedding clarity",
                    "pronoun_resolution_rate": ">95% of pronouns should have clear antecedents",
                    "standalone_context_score": ">0.7 for chunks to be useful in isolation"
                },
                "expert_recommendations": [
                    "Structure content with clear H2/H3 hierarchy where each section is independently retrievable",
                    "Use the 'inverted pyramid' approach - put key information first in each chunk",
                    "Include entity names, numbers, and specific data points for embedding richness",
                    "Test chunks by reading them in isolation - they should make sense without surrounding context",
                    "Add metadata (topic tags, entity labels) to chunks for vector database filtering",
                    "Monitor retrieval performance across different vector databases and embedding models",
                    "Update chunk structure based on actual query patterns from analytics"
                ],
                "common_mistakes_to_avoid": [
                    "Creating chunks that are too large (>500 tokens) causing information dilution",
                    "Splitting content mid-sentence or mid-concept breaking context",
                    "Using ambiguous pronouns without clear antecedents at chunk starts",
                    "Not including enough context in each chunk for standalone understanding",
                    "Ignoring chunk boundary effects where context is lost between chunks",
                    "Creating chunks that are too small (<200 tokens) lacking sufficient context",
                    "Not testing chunk retrieval performance with actual queries"
                ],
                "success_metrics_to_track": [
                    "Chunk size compliance percentage (target: >80% within 200-500 tokens)",
                    "Self-contained chunk ratio (target: >90%)",
                    "Query alignment scores across target queries",
                    "Retrieval accuracy in vector database testing",
                    "Embedding readiness score (target: >0.8)",
                    "RAG answer quality ratings from user testing",
                    "Citation accuracy when content is used in AI responses"
                ]
            },
            "data_source": "real_time_analysis"
        }

    def _analyze_url_rag_compatibility(self, url_data: Dict, target_queries: List[str] = None) -> Dict[str, Any]:
        """Test RAG compatibility using actual page content for vector database retrieval."""
        page_text = url_data.get("page_text", "")
        title = url_data.get("title", "")
        h1 = url_data.get("h1", "")
        h2s = url_data.get("h2s", [])
        word_count = url_data.get("word_count", 0)
        url = url_data.get("url", "")
        target_queries = target_queries or []

        use_text = page_text or ""
        actual_word_count = len(use_text.split()) if use_text else word_count

        # Analyze chunk quality from actual content
        sentences = re.split(r'[.!?]+', use_text) if use_text else []
        sentences = [s.strip() for s in sentences if len(s.strip()) > 10]

        # Split into approximate chunks
        chunk_size = 400  # tokens
        words = use_text.split() if use_text else []
        approx_chunks = []
        chunk_words = []
        for w in words:
            chunk_words.append(w)
            if len(chunk_words) >= 280:  # ~400 tokens
                approx_chunks.append(" ".join(chunk_words))
                chunk_words = []
        if chunk_words:
            approx_chunks.append(" ".join(chunk_words))

        # Analyze each chunk for RAG readiness
        chunk_quality_scores = []
        for i, chunk in enumerate(approx_chunks):
            chunk_words_list = chunk.split()
            chunk_sentences = re.split(r'[.!?]+', chunk)
            chunk_sentences = [s.strip() for s in chunk_sentences if len(s.strip()) > 10]

            # Check if chunk starts with a definition
            starts_with_def = bool(re.search(
                r'^(?:[A-Z][^.]*?\s+(?:is|are|refers to|means|involves|includes|provides|offers))',
                chunk, re.IGNORECASE
            ))
            # Check for ambiguous pronouns at start
            starts_with_pronoun = bool(re.search(
                r'^(?:It|This|That|These|Those|They|He|She)\s',
                chunk
            ))
            # Check for entity mentions
            entity_mentions = len(re.findall(r'[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*', chunk))
            # Check for specific data
            has_data = bool(re.search(r'\d+(?:\.\d+)?%|\$\d+|\d{4}|\d+x', chunk))

            chunk_score = 0
            if starts_with_def:
                chunk_score += 0.3
            if not starts_with_pronoun:
                chunk_score += 0.2
            if entity_mentions >= 2:
                chunk_score += 0.2
            if has_data:
                chunk_score += 0.15
            if len(chunk_words_list) >= 50:
                chunk_score += 0.15

            chunk_quality_scores.append({
                "chunk_id": i + 1,
                "word_count": len(chunk_words_list),
                "sentence_count": len(chunk_sentences),
                "starts_with_definition": starts_with_def,
                "starts_with_pronoun": starts_with_pronoun,
                "entity_mentions": entity_mentions,
                "has_data": has_data,
                "quality_score": round(chunk_score, 3),
                "quality_tier": (
                    "EXCELLENT" if chunk_score >= 0.7 else
                    "GOOD" if chunk_score >= 0.5 else
                    "NEEDS_WORK" if chunk_score >= 0.3 else
                    "POOR"
                ),
                "preview": chunk[:120]
            })

        # Query alignment analysis
        query_alignment_results = []
        for query in target_queries[:10]:
            query_words = set(query.lower().split())
            text_lower = use_text.lower()
            # Check how well the content covers this query
            query_word_coverage = sum(1 for w in query_words if w in text_lower) / max(1, len(query_words))
            # Find best matching section
            best_section_match = None
            best_score = 0
            for h2 in h2s:
                h2_words = set(h2.lower().split())
                overlap = len(query_words & h2_words) / max(1, len(query_words))
                if overlap > best_score:
                    best_score = overlap
                    best_section_match = h2
            query_alignment_results.append({
                "query": query[:80],
                "word_coverage": round(query_word_coverage, 3),
                "best_matching_section": best_section_match or "No direct section match",
                "alignment_tier": (
                    "STRONG" if query_word_coverage >= 0.7 else
                    "MODERATE" if query_word_coverage >= 0.4 else
                    "WEAK"
                )
            })

        avg_alignment = sum(q["word_coverage"] for q in query_alignment_results) / max(1, len(query_alignment_results))

        # RAG retrieval simulation
        avg_chunk_quality = sum(c["quality_score"] for c in chunk_quality_scores) / max(1, len(chunk_quality_scores))
        definition_chunks = sum(1 for c in chunk_quality_scores if c["starts_with_definition"])
        standalone_chunks = sum(1 for c in chunk_quality_scores if not c["starts_with_pronoun"])

        # Vector database readiness assessment
        vector_readiness = {
            "chunk_count": len(approx_chunks),
            "avg_chunk_words": round(actual_word_count / max(1, len(approx_chunks))),
            "optimal_chunk_size": "200-500 words (~280-400 tokens)",
            "chunks_in_optimal_range": sum(1 for c in chunk_quality_scores if 100 <= c["word_count"] <= 500),
            "chunk_size_compliance": round(sum(1 for c in chunk_quality_scores if 100 <= c["word_count"] <= 500) / max(1, len(chunk_quality_scores)) * 100, 1),
            "definition_start_rate": round(definition_chunks / max(1, len(chunk_quality_scores)) * 100, 1),
            "standalone_chunk_rate": round(standalone_chunks / max(1, len(chunk_quality_scores)) * 100, 1),
            "estimated_embedding_quality": "HIGH" if avg_chunk_quality >= 0.6 else "MODERATE" if avg_chunk_quality >= 0.4 else "LOW"
        }

        # RAG-specific recommendations
        rag_recommendations = []
        total_chunks = len(approx_chunks)
        if definition_chunks / max(1, total_chunks) < 0.3:
            rag_recommendations.append({
                "priority": "HIGH",
                "action": f"Add definition sentences at the start of chunks (only {definition_chunks}/{total_chunks} have definitions)",
                "impact": "(General industry guidance, unverified): Definition-led chunks increase retrieval relevance by 30-45%"
            })
        if standalone_chunks / max(1, total_chunks) < 0.7:
            rag_recommendations.append({
                "priority": "HIGH",
                "action": "Replace ambiguous pronouns with explicit entity names at chunk boundaries",
                "impact": "Reduces context loss in isolated retrieval"
            })
        if actual_word_count < 500:
            rag_recommendations.append({
                "priority": "HIGH",
                "action": f"Expand content depth (current: {actual_word_count} words, target: 500+ for RAG)",
                "impact": "More content provides richer embeddings and better retrieval"
            })
        if len(h2s) < 3:
            rag_recommendations.append({
                "priority": "MEDIUM",
                "action": f"Add more H2 headings for chunk boundaries (current: {len(h2s)}, target: 5+)",
                "impact": "H2 headings create natural chunk boundaries for embedding"
            })
        if avg_alignment < 0.4:
            rag_recommendations.append({
                "priority": "MEDIUM",
                "action": "Improve query alignment - use target query terms in headings and body text",
                "impact": "Better term overlap improves cosine similarity in vector retrieval"
            })

        return {
            "page_url": url,
            "page_title": title,
            "content_word_count": actual_word_count,
            "chunk_analysis_from_actual_content": {
                "total_chunks": total_chunks,
                "avg_chunk_words": round(actual_word_count / max(1, total_chunks)),
                "chunk_quality_scores": chunk_quality_scores[:10],
                "avg_chunk_quality": round(avg_chunk_quality, 3),
                "definition_starting_chunks": definition_chunks,
                "standalone_chunks": standalone_chunks
            },
            "query_alignment_from_content": {
                "queries_tested": len(query_alignment_results),
                "avg_alignment_score": round(avg_alignment, 3),
                "results": query_alignment_results,
                "overall_alignment_tier": (
                    "STRONG" if avg_alignment >= 0.7 else
                    "MODERATE" if avg_alignment >= 0.4 else
                    "WEAK"
                )
            },
            "vector_database_readiness": vector_readiness,
            "rag_retrieval_simulation": {
                "estimated_retrieval_accuracy": round(avg_chunk_quality * 100, 1),
                "context_quality_for_llm": "HIGH" if avg_chunk_quality >= 0.6 else "MODERATE" if avg_chunk_quality >= 0.4 else "LOW",
                "estimated_answer_quality": "STRONG" if avg_chunk_quality >= 0.6 and avg_alignment >= 0.5 else "MODERATE" if avg_chunk_quality >= 0.4 else "WEAK",
                "citation_potential": "HIGH" if definition_chunks >= total_chunks * 0.4 else "MODERATE" if definition_chunks >= total_chunks * 0.2 else "LOW"
            },
            "rag_recommendations": rag_recommendations,
            "heading_structure_for_rag": {
                "h2_count": len(h2s),
                "h2_headings": h2s[:15],
                "h2_with_definitions": sum(1 for h in h2s if any(kw in h.lower() for kw in ["what is", "how to", "guide", "overview"])),
                "chunk_boundary_quality": "GOOD" if len(h2s) >= 4 else "NEEDS_MORE"
            }
        }

    def _analyze_chunks(self, chunks: List[Dict]) -> Dict[str, Any]:
        """Analyze chunk quality and characteristics."""
        if not chunks:
            return {"total_chunks": 0, "average_tokens": 0}

        token_counts = [c["token_estimate"] for c in chunks]
        word_counts = [c["word_count"] for c in chunks]
        sentence_counts = [c["sentence_count"] for c in chunks]
        self_contained = sum(1 for c in chunks if c["is_self_contained"])
        definition_starts = sum(1 for c in chunks if c["starts_with_definition"])
        ambiguous = sum(1 for c in chunks if c["has_ambiguous_pronouns"])

        return {
            "total_chunks": len(chunks),
            "token_statistics": {
                "min_tokens": min(token_counts),
                "max_tokens": max(token_counts),
                "avg_tokens": round(sum(token_counts) / len(token_counts), 2),
                "median_tokens": sorted(token_counts)[len(token_counts) // 2],
                "token_range": f"{min(token_counts)}-{max(token_counts)}"
            },
            "word_statistics": {
                "min_words": min(word_counts),
                "max_words": max(word_counts),
                "avg_words": round(sum(word_counts) / len(word_counts), 2)
            },
            "sentence_statistics": {
                "min_sentences": min(sentence_counts),
                "max_sentences": max(sentence_counts),
                "avg_sentences": round(sum(sentence_counts) / len(sentence_counts), 2)
            },
            "quality_metrics": {
                "self_contained_ratio": round(self_contained / max(1, len(chunks)), 3),
                "definition_start_ratio": round(definition_starts / max(1, len(chunks)), 3),
                "ambiguous_pronoun_ratio": round(ambiguous / max(1, len(chunks)), 3),
                "ideal_chunk_size": "200-500 tokens (OpenAI/Anthropic standard)"
            },
            "chunks": [{k: v for k, v in c.items() if k != "text"} for c in chunks],
            "chunk_size_compliance": sum(1 for c in chunks if 200 <= c["token_estimate"] <= 500) / max(1, len(chunks))
        }

    def _test_query_alignment(self, chunks: List[Dict], queries: List[str]) -> Dict[str, Any]:
        """Test how well chunks align with target queries."""
        if not chunks or not queries:
            return {"alignment_scores": [], "average_alignment": 0}

        chunk_texts = [c["text"] for c in chunks]
        all_texts = chunk_texts + queries
        vectors, feature_names = tf_idf_vectorize(all_texts, max_features=300)

        alignment_scores = []
        for i, chunk_vec in enumerate(vectors[:len(chunk_texts)]):
            chunk_similarities = []
            for j, query_vec in enumerate(vectors[len(chunk_texts):]):
                sim = cosine_similarity(chunk_vec, query_vec)
                chunk_similarities.append({
                    "query": queries[j][:80],
                    "similarity": round(sim, 4)
                })
            best_match = max(chunk_similarities, key=lambda x: x["similarity"]) if chunk_similarities else {"similarity": 0}
            alignment_scores.append({
                "chunk_id": chunks[i]["chunk_id"],
                "best_query_match": best_match["query"],
                "best_similarity": best_match["similarity"],
                "query_similarities": sorted(chunk_similarities, key=lambda x: x["similarity"], reverse=True)[:3],
                "alignment_tier": (
                    "EXCELLENT" if best_match["similarity"] > 0.7 else
                    "GOOD" if best_match["similarity"] > 0.5 else
                    "MODERATE" if best_match["similarity"] > 0.3 else
                    "POOR" if best_match["similarity"] > 0.1 else
                    "NOT_ALIGNED"
                )
            })

        avg_alignment = sum(a["best_similarity"] for a in alignment_scores) / max(1, len(alignment_scores))
        return {
            "alignment_scores": alignment_scores,
            "average_alignment": round(avg_alignment, 4),
            "excellent_alignment_count": sum(1 for a in alignment_scores if a["alignment_tier"] == "EXCELLENT"),
            "good_alignment_count": sum(1 for a in alignment_scores if a["alignment_tier"] == "GOOD"),
            "poor_alignment_count": sum(1 for a in alignment_scores if a["alignment_tier"] in ["POOR", "NOT_ALIGNED"]),
            "alignment_distribution": {
                "excellent": sum(1 for a in alignment_scores if a["alignment_tier"] == "EXCELLENT"),
                "good": sum(1 for a in alignment_scores if a["alignment_tier"] == "GOOD"),
                "moderate": sum(1 for a in alignment_scores if a["alignment_tier"] == "MODERATE"),
                "poor": sum(1 for a in alignment_scores if a["alignment_tier"] in ["POOR", "NOT_ALIGNED"])
            }
        }

    def _test_standalone_context(self, chunks: List[Dict]) -> Dict[str, Any]:
        """Test if each chunk makes sense standalone."""
        standalone_results = []
        for chunk in chunks:
            text = chunk["text"]
            sentences = tokenize_sentences(text)
            first_sentence = sentences[0] if sentences else ""
            has_pronoun_issue = chunk.get("has_ambiguous_pronouns", False)
            has_definition = chunk.get("starts_with_definition", False)
            is_self_contained = chunk.get("is_self_contained", False)
            standalone_score = 0
            if has_definition:
                standalone_score += 0.3
            if is_self_contained:
                standalone_score += 0.3
            if not has_pronoun_issue:
                standalone_score += 0.2
            if len(sentences) >= 2:
                standalone_score += 0.1
            if len(text.split()) >= 50:
                standalone_score += 0.1
            standalone_results.append({
                "chunk_id": chunk["chunk_id"],
                "standalone_score": round(standalone_score, 3),
                "issues": (
                    ["Begins with ambiguous pronouns - add context"] if has_pronoun_issue else []
                ) + (
                    ["Does not start with definition - add introductory context"] if not has_definition else []
                ),
                "first_sentence_preview": first_sentence[:100],
                "verdict": (
                    "STANDALONE_READY" if standalone_score > 0.7 else
                    "MOSTLY_READY" if standalone_score > 0.5 else
                    "NEEDS_WORK" if standalone_score > 0.3 else
                    "REQUIRES_REWRITE"
                )
            })

        ready_count = sum(1 for r in standalone_results if r["verdict"] == "STANDALONE_READY")
        return {
            "chunk_results": standalone_results,
            "standalone_ready_count": ready_count,
            "standalone_ready_ratio": round(ready_count / max(1, len(standalone_results)), 3),
            "average_standalone_score": round(
                sum(r["standalone_score"] for r in standalone_results) / max(1, len(standalone_results)), 3
            ),
            "chunks_needing_work": [r for r in standalone_results if r["verdict"] in ["NEEDS_WORK", "REQUIRES_REWRITE"]]
        }

    def _assess_embedding_readiness(self, chunks: List[Dict]) -> Dict[str, Any]:
        """Assess how well content will embed in vector databases."""
        if not chunks:
            return {"readiness_score": 0}

        optimal_size_count = sum(1 for c in chunks if 200 <= c["token_estimate"] <= 500)
        self_contained_count = sum(1 for c in chunks if c["is_self_contained"])
        definition_count = sum(1 for c in chunks if c["starts_with_definition"])

        size_score = optimal_size_count / max(1, len(chunks))
        context_score = self_contained_count / max(1, len(chunks))
        clarity_score = definition_count / max(1, len(chunks))
        overall = (size_score * 0.35 + context_score * 0.35 + clarity_score * 0.30)

        return {
            "readiness_score": round(overall, 3),
            "readiness_tier": (
                "VECTOR_READY" if overall > 0.8 else
                "MOSTLY_READY" if overall > 0.6 else
                "NEEDS_OPTIMIZATION" if overall > 0.4 else
                "NOT_READY"
            ),
            "component_scores": {
                "chunk_size_optimization": round(size_score, 3),
                "context_independence": round(context_score, 3),
                "definition_clarity": round(clarity_score, 3)
            },
            "embedding_recommendations": [
                f"Optimal chunk size: {optimal_size_count}/{len(chunks)} chunks (target: 200-500 tokens)",
                f"Self-contained chunks: {self_contained_count}/{len(chunks)} (target: 100%)",
                f"Definition-led chunks: {definition_count}/{len(chunks)} (target: >50%)"
            ]
        }

    def _simulate_retrieval(self, chunks: List[Dict], queries: List[str]) -> Dict[str, Any]:
        """Simulate how an LLM would retrieve and use chunks."""
        if not chunks or not queries:
            return {"simulations": []}

        simulations = []
        for query in queries[:5]:
            chunk_texts = [c["text"] for c in chunks]
            all_texts = chunk_texts + [query]
            vectors, _ = tf_idf_vectorize(all_texts, max_features=200)
            query_vec = vectors[-1]
            chunk_sims = []
            for i, chunk_vec in enumerate(vectors[:-1]):
                sim = cosine_similarity(chunk_vec, query_vec)
                chunk_sims.append({"chunk_id": chunks[i]["chunk_id"], "similarity": round(sim, 4)})
            chunk_sims.sort(key=lambda x: x["similarity"], reverse=True)
            top_chunks = chunk_sims[:3]
            simulations.append({
                "query": query[:100],
                "retrieved_chunks": top_chunks,
                "top_similarity": top_chunks[0]["similarity"] if top_chunks else 0,
                "context_quality": (
                    "HIGH" if top_chunks and top_chunks[0]["similarity"] > 0.5 else
                    "MODERATE" if top_chunks and top_chunks[0]["similarity"] > 0.3 else
                    "LOW"
                ),
                "expected_answer_quality": (
                    "STRONG - Retrieved chunks contain relevant information" if top_chunks and top_chunks[0]["similarity"] > 0.5 else
                    "MODERATE - Some relevant context available" if top_chunks and top_chunks[0]["similarity"] > 0.3 else
                    "WEAK - Insufficient relevant chunks for high-quality answer"
                )
            })
        return {
            "simulations": simulations,
            "average_top_similarity": round(
                sum(s["top_similarity"] for s in simulations) / max(1, len(simulations)), 4
            ),
            "retrieval_quality": (
                "EXCELLENT" if all(s["top_similarity"] > 0.5 for s in simulations) else
                "GOOD" if all(s["top_similarity"] > 0.3 for s in simulations) else
                "MIXED" if any(s["top_similarity"] > 0.3 for s in simulations) else
                "POOR"
            )
        }

    def _generate_optimization_report(self, chunks: List[Dict], analysis: Dict, alignment: Dict) -> Dict[str, Any]:
        """Generate RAG optimization report."""
        return {
            "optimization_actions": [
                {
                    "action": "Ensure each chunk starts with a clear topic sentence",
                    "priority": "HIGH",
                    "affected_chunks": sum(1 for c in chunks if not c.get("starts_with_definition")),
                    "impact": "(General industry guidance, unverified): Increases retrieval relevance by 20-35%"
                },
                {
                    "action": "Fix ambiguous pronouns in chunk openings",
                    "priority": "HIGH",
                    "affected_chunks": sum(1 for c in chunks if c.get("has_ambiguous_pronouns")),
                    "impact": "Prevents context loss in isolated retrieval"
                },
                {
                    "action": "Rebalance chunk sizes to 200-500 token range",
                    "priority": "MEDIUM",
                    "affected_chunks": sum(1 for c in chunks if c["token_estimate"] < 200 or c["token_estimate"] > 500),
                    "impact": "Optimizes for vector database storage windows"
                },
                {
                    "action": "Add explicit entity mentions at chunk boundaries",
                    "priority": "MEDIUM",
                    "affected_chunks": len(chunks),
                    "impact": "Improves entity-based retrieval accuracy"
                }
            ],
            "content_structure_for_rag": {
                "recommendation": "Structure content with clear H2/H3 hierarchy where each section is independently retrievable",
                "chunk_boundary_strategy": "Split at natural paragraph boundaries, not mid-sentence",
                "entity_annotation": "Include entity names at the start of each chunk for better embedding"
            }
        }

    def _calculate_overall_rag_score(self, analysis: Dict, alignment: Dict, standalone: Dict) -> Dict[str, Any]:
        """Calculate overall RAG readiness score."""
        size_compliance = analysis.get("chunk_size_compliance", 0)
        avg_alignment = alignment.get("average_alignment", 0)
        standalone_ratio = standalone.get("standalone_ready_ratio", 0)
        overall = (size_compliance * 0.3 + avg_alignment * 0.4 + standalone_ratio * 0.3)
        return {
            "overall_score": round(overall, 3),
            "size_compliance_score": round(size_compliance, 3),
            "query_alignment_score": round(avg_alignment, 3),
            "standalone_context_score": round(standalone_ratio, 3),
            "rag_readiness_tier": (
                "EXCELLENT - Fully optimized for RAG retrieval" if overall > 0.8 else
                "GOOD - Minor optimizations needed" if overall > 0.6 else
                "MODERATE - Several improvements required" if overall > 0.4 else
                "POOR - Significant RAG optimization needed"
            )
        }

    def _generate_recommendations(self, analysis: Dict, alignment: Dict, standalone: Dict, embedding: Dict) -> List[Dict[str, str]]:
        """Generate RAG optimization recommendations."""
        recs = []
        if analysis.get("chunk_size_compliance", 0) < 0.7:
            recs.append({
                "priority": "HIGH",
                "action": "Adjust chunk sizes to 200-500 token range",
                "detail": f"Only {analysis.get('chunk_size_compliance', 0) * 100:.0f}% of chunks are within optimal size"
            })
        if alignment.get("poor_alignment_count", 0) > 0:
            recs.append({
                "priority": "HIGH",
                "action": "Improve query alignment for poorly-aligned chunks",
                "detail": f"{alignment['poor_alignment_count']} chunks have poor query alignment"
            })
        if standalone.get("chunks_needing_work"):
            recs.append({
                "priority": "MEDIUM",
                "action": "Make chunks more self-contained",
                "detail": f"{len(standalone['chunks_needing_work'])} chunks need standalone context improvement"
            })
        if embedding.get("readiness_score", 0) < 0.6:
            recs.append({
                "priority": "MEDIUM",
                "action": "Improve embedding readiness",
                "detail": f"Current readiness score: {embedding.get('readiness_score', 0)} - add definitions at chunk starts"
            })
        return recs
