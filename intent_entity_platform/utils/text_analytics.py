"""
Utility functions for text analysis, NLP, scoring, and data processing.
"""
import re
import math
import hashlib
import json
from typing import List, Dict, Any, Tuple, Optional
from collections import Counter
from datetime import datetime


# ============================================================
# TEXT ANALYSIS UTILITIES
# ============================================================

def tokenize_sentences(text: str) -> List[str]:
    """Split text into sentences using regex-based sentence boundary detection."""
    if not text.strip():
        return []
    text = re.sub(r'\s+', ' ', text.strip())
    abbrevs = r'(?:Mr|Mrs|Ms|Dr|Prof|Sr|Jr|Inc|Ltd|Corp|etc|vs|approx|dept|est|vol|fig|al|e\.g|i\.e|a\.m|p\.m|U\.S|U\.K|U\.N)'
    protected = re.sub(abbrevs, lambda m: m.group().replace('.', '<<DOT>>'), text)
    sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z"\'])', protected)
    sentences = [s.replace('<<DOT>>', '.').strip() for s in sentences if s.strip()]
    if not sentences and text.strip():
        sentences = [text.strip()]
    return sentences


def tokenize_words(text: str) -> List[str]:
    """Extract words from text."""
    return re.findall(r'\b[a-zA-Z\'-]+\b', text.lower())


def count_syllables(word: str) -> int:
    """Estimate syllable count for a word."""
    word = word.lower().strip()
    if len(word) <= 3:
        return 1
    vowels = 'aeiouy'
    count = 0
    prev_vowel = False
    for char in word:
        is_vowel = char in vowels
        if is_vowel and not prev_vowel:
            count += 1
        prev_vowel = is_vowel
    if word.endswith('e') and count > 1:
        count -= 1
    if word.endswith('le') and len(word) > 2 and word[-3] not in vowels:
        count += 1
    return max(1, count)


def flesch_kincaid_grade(text: str) -> float:
    """Calculate Flesch-Kincaid Grade Level."""
    sentences = tokenize_sentences(text)
    words = tokenize_words(text)
    if not sentences or not words:
        return 0.0
    total_syllables = sum(count_syllables(w) for w in words)
    asl = len(words) / len(sentences)
    asw = total_syllables / len(words)
    return 0.39 * asl + 11.8 * asw - 15.59


def flesch_reading_ease(text: str) -> float:
    """Calculate Flesch Reading Ease score."""
    sentences = tokenize_sentences(text)
    words = tokenize_words(text)
    if not sentences or not words:
        return 0.0
    total_syllables = sum(count_syllables(w) for w in words)
    asl = len(words) / len(sentences)
    asw = total_syllables / len(words)
    score = 206.835 - 1.015 * asl - 84.6 * asw
    return max(0, min(100, score))


def coleman_liau_index(text: str) -> float:
    """Calculate Coleman-Liau Index."""
    sentences = tokenize_sentences(text)
    words = tokenize_words(text)
    if not words:
        return 0.0
    characters = sum(len(w) for w in tokenize_words(text))
    l = (characters / len(words)) * 100
    s = (len(sentences) / len(words)) * 100
    return 0.0588 * l - 0.296 * s - 15.8


def automated_readability_index(text: str) -> float:
    """Calculate Automated Readability Index."""
    sentences = tokenize_sentences(text)
    words = tokenize_words(text)
    if not sentences or not words:
        return 0.0
    characters = sum(len(w) for w in words)
    return 4.71 * (characters / len(words)) + 0.5 * (len(words) / len(sentences)) - 21.43


def gunning_fog_index(text: str) -> float:
    """Calculate Gunning Fog Index."""
    sentences = tokenize_sentences(text)
    words = tokenize_words(text)
    if not sentences or not words:
        return 0.0
    complex_words = sum(1 for w in words if count_syllables(w) >= 3)
    return 0.4 * ((len(words) / len(sentences)) + 100 * (complex_words / len(words)))


def text_statistics(text: str) -> Dict[str, Any]:
    """Compute comprehensive text statistics."""
    sentences = tokenize_sentences(text)
    words = tokenize_words(text)
    word_freq = Counter(words)
    char_count = len(text)
    word_count = len(words)
    sentence_count = len(sentences)
    avg_word_length = sum(len(w) for w in words) / max(1, word_count)
    avg_sentence_length = word_count / max(1, sentence_count)
    avg_syllables_per_word = sum(count_syllables(w) for w in words) / max(1, word_count)
    unique_word_ratio = len(set(words)) / max(1, word_count)
    type_token_ratio = unique_word_ratio
    hapax_legomena = sum(1 for w, c in word_freq.items() if c == 1)
    hapax_ratio = hapax_legomena / max(1, word_count)
    return {
        "character_count": char_count,
        "word_count": word_count,
        "sentence_count": sentence_count,
        "paragraph_count": len([p for p in text.split('\n\n') if p.strip()]),
        "avg_word_length": round(avg_word_length, 2),
        "avg_sentence_length_words": round(avg_sentence_length, 2),
        "avg_syllables_per_word": round(avg_syllables_per_word, 2),
        "unique_word_ratio": round(unique_word_ratio, 4),
        "type_token_ratio": round(type_token_ratio, 4),
        "hapax_legomena_ratio": round(hapax_ratio, 4),
        "flesch_kincaid_grade": round(flesch_kincaid_grade(text), 2),
        "flesch_reading_ease": round(flesch_reading_ease(text), 2),
        "coleman_liau_index": round(coleman_liau_index(text), 2),
        "automated_readability_index": round(automated_readability_index(text), 2),
        "gunning_fog_index": round(gunning_fog_index(text), 2),
        "top_words": word_freq.most_common(20),
        "word_length_distribution": dict(Counter(len(w) for w in words))
    }


def sentence_length_distribution(text: str) -> Dict[str, Any]:
    """Analyze sentence length distribution for burstiness analysis."""
    sentences = tokenize_sentences(text)
    if not sentences:
        return {"distribution": [], "burstiness_score": 0, "uniformity_risk": "low"}
    lengths = [len(tokenize_words(s)) for s in sentences]
    mean_len = sum(lengths) / len(lengths)
    variance = sum((l - mean_len) ** 2 for l in lengths) / len(lengths)
    std_dev = math.sqrt(variance) if variance > 0 else 0
    cv = std_dev / mean_len if mean_len > 0 else 0
    short = sum(1 for l in lengths if l <= 5)
    medium = sum(1 for l in lengths if 6 <= l <= 20)
    long_s = sum(1 for l in lengths if 21 <= l <= 40)
    very_long = sum(1 for l in lengths if l > 40)
    total = len(lengths)
    uniformity_score = 1.0 - cv
    if uniformity_score > 0.85:
        uniformity_risk = "critical"
    elif uniformity_score > 0.7:
        uniformity_risk = "high"
    elif uniformity_score > 0.5:
        uniformity_risk = "moderate"
    else:
        uniformity_risk = "low"
    burstiness_score = cv
    return {
        "sentence_count": total,
        "min_length": min(lengths) if lengths else 0,
        "max_length": max(lengths) if lengths else 0,
        "mean_length": round(mean_len, 2),
        "std_dev": round(std_dev, 2),
        "coefficient_of_variation": round(cv, 4),
        "burstiness_score": round(burstiness_score, 4),
        "uniformity_score": round(uniformity_score, 4),
        "uniformity_risk": uniformity_risk,
        "distribution": {
            "short_1_to_5_words": {"count": short, "percentage": round(short / max(1, total) * 100, 1)},
            "medium_6_to_20_words": {"count": medium, "percentage": round(medium / max(1, total) * 100, 1)},
            "long_21_to_40_words": {"count": long_s, "percentage": round(long_s / max(1, total) * 100, 1)},
            "very_long_40_plus_words": {"count": very_long, "percentage": round(very_long / max(1, total) * 100, 1)}
        },
        "lengths": lengths
    }


def detect_ai_patterns(text: str) -> Dict[str, Any]:
    """Detect common AI-generated text patterns and phrases."""
    AI_PATTERNS = {
        "opening_filler": [
            r"in today\'?s\s+(?:fast-paced|digital|ever-changing|modern|rapidly evolving)",
            r"in\s+(?:a|the)\s+world\s+(?:of|where|wherein)",
            r"as\s+(?:we|the|the world)\s+(?:move|navigate|transition|evolve)",
            r"with\s+the\s+(?:advent|rise|emergence|growing prevalence)",
            r"in\s+(?:recent|the\s+recent)\s+(?:years|times|months)",
            r"as\s+technology\s+(?:continues|evolves|advances)",
            r"the\s+(?:digital|modern)\s+(?:age|era|landscape|world)",
            r"in\s+(?:this|the)\s+(?:blog|article|guide|post)",
        ],
        "transition_phrases": [
            r"it\'?s?\s+worth\s+noticing?",
            r"needless\s+to\s+say",
            r"at\s+the\s+end\s+of\s+the\s+day",
            r"with\s+that\s+being\s+said",
            r"that\s+being\s+said",
            r"without\s+further\s+ado",
            r"let\'?s?\s+(?:dive|delve|explore|unpack|examine)",
            r"buckle\s+up",
            r"without\s+(?:further\s+ ado|more\s+ ado)",
            r"in\s+this\s+(?:article|blog|guide|post)\s+we\s+(?:will|\'?ll|are\s+going\s+to)",
            r"let\s+us\s+(?:dive|delve|explore|unpack)",
            r"first\s+and\s+foremost",
            r"last\s+but\s+not\s+least",
            r"more\s+importantly",
            r"on\s+the\s+other\s+hand",
            r"in\s+contrast",
            r"conversely",
            r"furthermore",
            r"moreover",
            r"additionally",
        ],
        "hyperbolic_claims": [
            r"(?:the\s+)?(?:best|worst|greatest|most\s+(?:powerful|effective|important))",
            r"(?:game[\s-]changer|revolutionary|transformative|groundbreaking)",
            r"(?:cutting[\s-]edge|state[\s-]of[\s-]the[\s-]art|best[\s-]in[\s-]class)",
            r"(?:unparalleled|unmatched|unrivaled|unprecedented)",
            r"(?:100%|guaranteed|absolute|proven|undeniable)",
            r"(?:will\s+definitely|absolutely\s+(?:will|can|does)|without\s+a\s+doubt)",
            r"(?:master(?:ing|ed)|unlock(?:ing|ed)|harness(?:ing|ed))\s+the\s+power",
            r"seamless(?:ly)?\s+(?:integrat|connect|blend|merge)",
        ],
        "vague_conclusions": [
            r"in\s+(?:conclusion|summary|essence|summary|closing)",
            r"to\s+(?:sum\s+up|wrap\s+up|conclude)",
            r"overall",
            r"all\s+things\s+considered",
            r"in\s+(?:the\s+)?(?:grand\s+scheme\s+of\s+things|final\s+analysis)",
            r"at\s+the\s+(?:end\s+of\s+the\s+day|core)",
            r"when\s+all\s+(?:is\s+)?said\s+and\s+done",
        ],
        "robotic_transitions": [
            r"with\s+regard\s+to",
            r"in\s+regard\s+s?",
            r"with\s+respect\s+to",
            r"in\s+terms\s+of",
            r"it\s+is\s+(?:important|crucial|essential|vital|imperative)\s+to\s+note",
            r"it\s+(?:should\s+be|must\s+be)\s+noted",
            r"it\s+is\s+worth\s+(?:mentioning|noting|highlighting)",
            r"as\s+mentioned\s+(?:previously|earlier|above|before)",
            r"as\s+we\s+(?:have|know|can\s+see)",
        ],
        "generic_definitions": [
            r"simply\s+put",
            r"in\s+(?:other\s+)?words",
            r"to\s+(?:put\s+it|be\s+frank|be\s+clear)",
            r"broadly\s+speaking",
            r"generally\s+speaking",
            r"technically\s+speaking",
        ],
        "passive_voice_markers": [
            r"(?:is|are|was|were|be|been|being)\s+(?:\w+ed|built|created|developed|designed|implemented)",
            r"it\s+(?:is|was)\s+(?:believed|thought|considered|assumed|widely\s+recognized)",
        ],
        "list_intros": [
            r"here\s+(?:is|are)\s+(?:a\s+list|the\s+following|some)",
            r"below\s+(?:is|are|you(?:'ll|\s+will)\s+find)",
            r"the\s+following\s+(?:is|are|are\s+some)",
            r"let(?:'s|\s+us)\s+(?:take\s+a\s+look|explore|examine|discuss)",
        ]
    }
    findings = {}
    all_flags = []
    for category, patterns in AI_PATTERNS.items():
        matches = []
        for pattern in patterns:
            for m in re.finditer(pattern, text, re.IGNORECASE):
                context_start = max(0, m.start() - 30)
                context_end = min(len(text), m.end() + 30)
                context = text[context_start:context_end].strip()
                matches.append({
                    "match": m.group(),
                    "position": m.start(),
                    "context": context,
                    "severity": "high" if category in ["opening_filler", "hyperbolic_claims"] else "medium"
                })
        if matches:
            findings[category] = matches
            all_flags.extend(matches)
    return {
        "total_flags": len(all_flags),
        "categories_flagged": len(findings),
        "findings": findings,
        "all_flags": all_flags,
        "ai_probability_score": min(1.0, len(all_flags) / 30),
        "recommendation": (
            "HIGH RISK" if len(all_flags) > 15 else
            "MODERATE RISK" if len(all_flags) > 8 else
            "LOW RISK" if len(all_flags) > 3 else
            "MINIMAL RISK"
        )
    }


def cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
    """Calculate cosine similarity between two vectors."""
    if not vec_a or not vec_b or len(vec_a) != len(vec_b):
        return 0.0
    dot_product = sum(a * b for a, b in zip(vec_a, vec_b))
    norm_a = math.sqrt(sum(a ** 2 for a in vec_a))
    norm_b = math.sqrt(sum(b ** 2 for b in vec_b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot_product / (norm_a * norm_b)


def tf_idf_vectorize(documents: List[str], max_features: int = 500) -> Tuple[List[List[float]], List[str]]:
    """Simple TF-IDF vectorizer for document comparison."""
    all_words = set()
    doc_word_lists = []
    for doc in documents:
        words = tokenize_words(doc)
        doc_word_lists.append(words)
        all_words.update(words)
    word_list = sorted(all_words)[:max_features]
    word_to_idx = {w: i for i, w in enumerate(word_list)}
    n_docs = len(documents)
    doc_freq = Counter()
    for words in doc_word_lists:
        unique = set(words)
        for w in unique:
            if w in word_to_idx:
                doc_freq[w] += 1
    vectors = []
    for words in doc_word_lists:
        word_count = Counter(words)
        total = len(words) if words else 1
        vec = [0.0] * len(word_list)
        for w, idx in word_to_idx.items():
            tf = word_count.get(w, 0) / total
            idf = math.log((n_docs + 1) / (doc_freq.get(w, 0) + 1)) + 1
            vec[idx] = tf * idf
        vectors.append(vec)
    return vectors, word_list


def extract_keyphrases(text: str, top_n: int = 20) -> List[Tuple[str, int]]:
    """Extract keyphrases using simple n-gram frequency analysis."""
    words = tokenize_words(text)
    stopwords = {
        'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
        'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
        'should', 'may', 'might', 'shall', 'can', 'to', 'of', 'in', 'for',
        'on', 'with', 'at', 'by', 'from', 'as', 'into', 'through', 'during',
        'before', 'after', 'above', 'below', 'between', 'out', 'off', 'over',
        'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when',
        'where', 'why', 'how', 'all', 'each', 'every', 'both', 'few', 'more',
        'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own',
        'same', 'so', 'than', 'too', 'very', 'just', 'because', 'but', 'and',
        'or', 'if', 'while', 'that', 'this', 'these', 'those', 'it', 'its',
        'they', 'them', 'their', 'what', 'which', 'who', 'whom', 'he', 'she',
        'his', 'her', 'my', 'your', 'our', 'about', 'up', 'also', 'it\'s',
        'don', 'doesn', 'didn', 'won', 'wouldn', 'couldn', 'shouldn', 'isn',
        'aren', 'wasn', 'weren', 'hasn', 'haven', 'hadn', 'let', 'us',
        'we', 'you', 'i', 'me', 'mine', 'yours', 'him', 'myself', 'yourself',
    }
    filtered = [w for w in words if w not in stopwords and len(w) > 2]
    bigrams = [f"{filtered[i]} {filtered[i+1]}" for i in range(len(filtered)-1)]
    trigrams = [f"{filtered[i]} {filtered[i+1]} {filtered[i+2]}" for i in range(len(filtered)-2)]
    all_ngrams = filtered + bigrams + trigrams
    freq = Counter(all_ngrams)
    return freq.most_common(top_n)


def generate_text_fingerprint(text: str) -> str:
    """Generate a unique fingerprint for text deduplication."""
    normalized = ' '.join(text.lower().split())
    return hashlib.sha256(normalized.encode()).hexdigest()[:32]


def chunk_text_semantic(text: str, max_tokens: int = 400) -> List[Dict[str, Any]]:
    """Split text into semantically coherent chunks for RAG testing."""
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
    chunks = []
    current_chunk = []
    current_tokens = 0

    for para in paragraphs:
        words = tokenize_words(para)
        para_tokens = len(words)
        if current_tokens + para_tokens > max_tokens and current_chunk:
            chunk_text = '\n\n'.join(current_chunk)
            chunks.append({
                "chunk_id": len(chunks),
                "text": chunk_text,
                "token_estimate": current_tokens,
                "word_count": len(tokenize_words(chunk_text)),
                "sentence_count": len(tokenize_sentences(chunk_text)),
                "starts_with_definition": bool(re.match(
                    r'^(?:\w+\s+){0,3}(?:is|are|refers?\s+to|means?)\s',
                    chunk_text, re.IGNORECASE
                )),
                "is_self_contained": current_tokens > 50 and len(tokenize_sentences(chunk_text)) >= 2
            })
            current_chunk = []
            current_tokens = 0
        current_chunk.append(para)
        current_tokens += para_tokens

    if current_chunk:
        chunk_text = '\n\n'.join(current_chunk)
        chunks.append({
            "chunk_id": len(chunks),
            "text": chunk_text,
            "token_estimate": current_tokens,
            "word_count": len(tokenize_words(chunk_text)),
            "sentence_count": len(tokenize_sentences(chunk_text)),
            "starts_with_definition": bool(re.match(
                r'^(?:\w+\s+){0,3}(?:is|are|refers?\s+to|means?)\s',
                chunk_text, re.IGNORECASE
            )),
            "is_self_contained": current_tokens > 50 and len(tokenize_sentences(chunk_text)) >= 2
        })

    for i, chunk in enumerate(chunks):
        preceding = chunks[i-1]["text"][-200:] if i > 0 else ""
        following = chunks[i+1]["text"][:200] if i < len(chunks)-1 else ""
        chunk["has_ambiguous_pronouns"] = bool(re.search(
            r'\b(?:this|that|these|those|it|they|he|she)\b', chunk["text"][:100], re.IGNORECASE
        ))
        chunk["needs_context_from_surrounding"] = chunk["has_ambiguous_pronouns"] and not chunk["starts_with_definition"]

    return chunks


def extract_entities_simple(text: str) -> Dict[str, List[str]]:
    """Simple named entity extraction using pattern matching."""
    entities = {"organizations": [], "people": [], "locations": [], "products": [], "dates": [], "numbers": []}
    org_patterns = [
        r'\b(?:[A-Z][a-z]+\s*){1,4}\s+(?:Inc|Corp|LLC|Ltd|Co|Company|Group|Partners|Associates|Solutions|Technologies|Systems)\b',
        r'\b(?:Google|Microsoft|Amazon|Apple|Meta|OpenAI|Anthropic|Perplexity|ChatGPT|Gemini|Bing)\b',
    ]
    for pattern in org_patterns:
        for m in re.finditer(pattern, text):
            entities["organizations"].append(m.group().strip())
    name_patterns = [
        r'\b(?:Mr|Mrs|Ms|Dr|Prof|CEO|CTO|CFO|COO|CMO)\.?\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2})\b',
        r'\b([A-Z][a-z]+)\s+([A-Z][a-z]+)(?:\s*,\s*(?:CEO|CTO|CFO|COO|CMO|VP|Director|Manager|Engineer|Analyst))',
    ]
    for pattern in name_patterns:
        for m in re.finditer(pattern, text):
            entities["people"].append(m.group().strip())
    location_patterns = [
        r'\b(?:San Francisco|New York|Los Angeles|Chicago|Houston|Seattle|Austin|Boston|Denver|London|Tokyo|Berlin|Paris|Singapore|Sydney|Toronto|Mumbai|Dubai)\b',
        r'\b(?:United States|United Kingdom|European Union|Asia Pacific|North America|Europe|Middle East|Africa)\b',
    ]
    for pattern in location_patterns:
        for m in re.finditer(pattern, text):
            entities["locations"].append(m.group().strip())
    date_patterns = [
        r'\b\d{4}[-/]\d{2}[-/]\d{2}\b',
        r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b',
        r'\b\d{1,2}/\d{1,2}/\d{2,4}\b',
    ]
    for pattern in date_patterns:
        for m in re.finditer(pattern, text):
            entities["dates"].append(m.group().strip())
    number_patterns = [
        r'\b\d+(?:\.\d+)?%\b',
        r'\$\d+(?:,\d{3})*(?:\.\d+)?(?:\s*(?:million|billion|trillion|M|B|K))?',
        r'\b\d+(?:,\d{3})*(?:\.\d+)?\s*(?:million|billion|trillion|M|B|K)\b',
    ]
    for pattern in number_patterns:
        for m in re.finditer(pattern, text):
            entities["numbers"].append(m.group().strip())
    for key in entities:
        entities[key] = list(dict.fromkeys(entities[key]))
    return entities


def schema_json_ld_validate(schema_dict: Dict) -> List[str]:
    """Validate a JSON-LD schema structure."""
    errors = []
    if "@context" not in schema_dict:
        errors.append("Missing @context property")
    if "@type" not in schema_dict:
        errors.append("Missing @type property")
    if schema_dict.get("@context") != "https://schema.org":
        errors.append("@context should be 'https://schema.org'")
    valid_types = [
        "Article", "TechArticle", "NewsArticle", "ScholarlyArticle", "Report",
        "FAQPage", "HowTo", "Product", "Organization", "Person",
        "BreadcrumbList", "ItemList", "WebPage", "WebSite",
        "VideoObject", "AudioObject", "ImageObject",
        "LocalBusiness", "Event", "Course",
    ]
    if schema_dict.get("@type") not in valid_types:
        errors.append(f"Uncommon @type: {schema_dict.get('@type')}")
    if "headline" in schema_dict and len(str(schema_dict["headline"])) > 110:
        errors.append("headline exceeds 110 characters (may be truncated in SERPs)")
    if "description" in schema_dict and len(str(schema_dict["description"])) > 160:
        errors.append("description exceeds 160 characters (may be truncated in SERPs)")
    return errors


def calculate_information_gain(existing_texts: List[str], candidate_text: str) -> Dict[str, Any]:
    """Estimate information gain of candidate text vs existing content."""
    if not existing_texts:
        return {"gain_score": 1.0, "unique_concepts": [], "overlap_ratio": 0.0}
    existing_combined = ' '.join(existing_texts)
    existing_vectors, feature_names = tf_idf_vectorize([existing_combined, candidate_text], max_features=300)
    if len(existing_vectors) < 2:
        return {"gain_score": 0.5, "unique_concepts": [], "overlap_ratio": 0.5}
    existing_vec = existing_vectors[0]
    candidate_vec = existing_vectors[1]
    overlap = cosine_similarity(existing_vec, candidate_vec)
    unique_words_in_candidate = []
    for i, word in enumerate(feature_names):
        if candidate_vec[i] > 0 and existing_vec[i] == 0:
            unique_words_in_candidate.append(word)
    existing_keyphrases = set(kp for kp, _ in extract_keyphrases(existing_combined, top_n=50))
    candidate_keyphrases = set(kp for kp, _ in extract_keyphrases(candidate_text, top_n=50))
    unique_keyphrases = candidate_keyphrases - existing_keyphrases
    gain_score = max(0, min(1.0, 1.0 - overlap + len(unique_keyphrases) * 0.05))
    return {
        "gain_score": round(gain_score, 4),
        "cosine_similarity": round(overlap, 4),
        "unique_words_count": len(unique_words_in_candidate),
        "unique_keyphrases": list(unique_keyphrases)[:20],
        "overlap_ratio": round(overlap, 4),
        "recommendation": (
            "STRONG GAIN - Highly differentiated content" if gain_score > 0.7 else
            "MODERATE GAIN - Some unique value" if gain_score > 0.4 else
            "LOW GAIN - Largely overlaps existing content"
        )
    }


def compute_readability_for_level(text: str, target_level: str) -> Dict[str, Any]:
    """Check if text readability matches target audience level."""
    grade = flesch_kincaid_grade(text)
    ease = flesch_reading_ease(text)
    fog = gunning_fog_index(text)
    LEVEL_RANGES = {
        "beginner": {"grade_range": (4, 7), "ease_range": (70, 100), "fog_range": (5, 8)},
        "intermediate": {"grade_range": (7, 10), "ease_range": (50, 70), "fog_range": (8, 12)},
        "advanced": {"grade_range": (10, 14), "ease_range": (30, 50), "fog_range": (12, 16)},
        "expert": {"grade_range": (14, 20), "ease_range": (0, 30), "fog_range": (16, 22)},
        "c-suite": {"grade_range": (8, 12), "ease_range": (40, 60), "fog_range": (10, 14)},
    }
    target = LEVEL_RANGES.get(target_level, LEVEL_RANGES["intermediate"])
    in_grade = target["grade_range"][0] <= grade <= target["grade_range"][1]
    in_ease = target["ease_range"][0] <= ease <= target["ease_range"][1]
    in_fog = target["fog_range"][0] <= fog <= target["fog_range"][1]
    alignment_score = (int(in_grade) + int(in_ease) + int(in_fog)) / 3
    issues = []
    if grade < target["grade_range"][0]:
        issues.append(f"Text is too simple (grade {grade}) for {target_level} audience (target: {target['grade_range'][0]}+)")
    elif grade > target["grade_range"][1]:
        issues.append(f"Text is too complex (grade {grade}) for {target_level} audience (target: max {target['grade_range'][1]})")
    if ease < target["ease_range"][0]:
        issues.append(f"Reading ease too low ({ease}) - consider simplifying")
    elif ease > target["ease_range"][1]:
        issues.append(f"Reading ease too high ({ease}) - may be too simplistic")
    return {
        "flesch_kincaid_grade": round(grade, 2),
        "flesch_reading_ease": round(ease, 2),
        "gunning_fog_index": round(fog, 2),
        "target_level": target_level,
        "alignment_score": round(alignment_score, 2),
        "in_grade_range": in_grade,
        "in_ease_range": in_ease,
        "in_fog_range": in_fog,
        "issues": issues,
        "verdict": (
            "WELL ALIGNED" if alignment_score >= 0.8 else
            "MOSTLY ALIGNED" if alignment_score >= 0.5 else
            "MISALIGNED - Revision needed"
        )
    }


def generate_internal_link_plan(existing_pages: List[Dict[str, str]], target_topic: str, new_page_url: str) -> Dict[str, Any]:
    """Generate internal linking recommendations."""
    target_words = set(tokenize_words(target_topic))
    scored_pages = []
    for page in existing_pages:
        page_words = set(tokenize_words(page.get("title", "") + " " + page.get("snippet", "")))
        relevance = len(target_words & page_words) / max(1, len(target_words))
        scored_pages.append({
            "url": page.get("url", ""),
            "title": page.get("title", ""),
            "relevance_score": round(relevance, 3),
            "suggested_anchor": page.get("title", target_topic)[:50],
            "direction": "outbound_from_new"
        })
    scored_pages.sort(key=lambda x: x["relevance_score"], reverse=True)
    outbound = [p for p in scored_pages[:10] if p["relevance_score"] > 0.1]
    inbound_candidates = scored_pages[:5]
    for p in inbound_candidates:
        p["direction"] = "inbound_to_new"
        p["action"] = f"Add link from {p['url']} to {new_page_url}"
    return {
        "outbound_links": outbound[:5],
        "inbound_recommendations": inbound_candidates,
        "cannibalization_risk": _check_cannibalization(scored_pages, target_topic),
        "link_equity_score": len(outbound) / max(1, len(scored_pages))
    }


def _check_cannibalization(pages: List[Dict], topic: str) -> Dict[str, Any]:
    """Check for potential keyword cannibalization."""
    high_overlap = [p for p in pages if p["relevance_score"] > 0.5]
    return {
        "risk_level": "HIGH" if len(high_overlap) > 3 else "MODERATE" if len(high_overlap) > 1 else "LOW",
        "competing_pages": [{"url": p["url"], "overlap": p["relevance_score"]} for p in high_overlap[:5]],
        "recommendation": (
            "Merge or differentiate content significantly" if len(high_overlap) > 3 else
            "Ensure clear topic differentiation" if len(high_overlap) > 1 else
            "No significant cannibalization detected"
        )
    }


def estimate_dom_complexity(html_content: str) -> Dict[str, Any]:
    """Estimate DOM complexity from HTML content."""
    open_tags = re.findall(r'<([a-zA-Z][a-zA-Z0-9]*)\b', html_content)
    total_elements = len(open_tags)
    tag_counter = Counter(open_tags)
    nesting_depth = 0
    max_depth = 0
    for char in html_content:
        if char == '<':
            nesting_depth += 1
            max_depth = max(max_depth, nesting_depth)
        elif char == '>':
            nesting_depth = max(0, nesting_depth - 1)
    script_count = len(re.findall(r'<script\b', html_content, re.IGNORECASE))
    style_count = len(re.findall(r'<style\b', html_content, re.IGNORECASE))
    inline_styles = len(re.findall(r'\bstyle\s*=', html_content, re.IGNORECASE))
    return {
        "total_dom_elements": total_elements,
        "unique_tag_types": len(tag_counter),
        "max_nesting_depth": max_depth,
        "top_tags": tag_counter.most_common(10),
        "script_count": script_count,
        "style_count": style_count,
        "inline_style_count": inline_styles,
        "dom_size_risk": (
            "CRITICAL" if total_elements > 3000 else
            "HIGH" if total_elements > 1500 else
            "MODERATE" if total_elements > 800 else
            "LOW"
        ),
        "nesting_risk": (
            "HIGH" if max_depth > 15 else
            "MODERATE" if max_depth > 10 else
            "LOW"
        )
    }


def generate_edge_worker_snippet(schema_json: str, meta_tags: Dict[str, str], headers: Dict[str, str]) -> str:
    """Generate a Cloudflare Worker snippet for edge-injecting schema and headers."""
    meta_html = '\n'.join(
        f'<meta name="{k}" content="{v}" />' if not k.startswith("http") else
        f'<meta property="{k}" content="{v}" />'
        for k, v in meta_tags.items()
    )
    header_directives = '\n'.join(
        f'  response.headers.set("{k}", "{v}");'
        for k, v in headers.items()
    )
    return f'''addEventListener("fetch", event => {{
  event.respondWith(handleRequest(event.request));
}});

async function handleRequest(request) {{
  const response = await fetch(request);
  const contentType = response.headers.get("content-type") || "";

  if (!contentType.includes("text/html")) {{
    return response;
  }}

  let html = await response.text();

  const schemaScript = `<script type="application/ld+json">{schema_json}</script>`;
  const metaTags = `{meta_html}`;

  html = html.replace("</head>", `${{metaTags}}\\n${{schemaScript}}\\n</head>`);

  const newResponse = new Response(html, {{
    status: response.status,
    statusText: response.statusText,
    headers: response.headers
  }});

{header_directives}

  return newResponse;
}}'''
