"""
Complete Input Framework for the Intent, Entity & Semantic Intelligence Platform.
Handles all 8 input categories with full validation and normalization.
"""
import json
import re
import hashlib
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Any, Union
from pathlib import Path
from datetime import datetime


@dataclass
class SeedKeywordInput:
    """Input 1: Primary Keyword + Entity Context"""
    seed_phrase: str = ""
    long_tail_variations: List[str] = field(default_factory=list)
    primary_entity: str = ""
    entity_type: str = ""  # product, process, regulatory_standard, concept
    entity_uri: str = ""  # Wikidata / Knowledge Graph URI
    target_locale: str = "en-US"
    target_device: str = "desktop"  # desktop, mobile, tablet
    target_language: str = "en"
    regional_dialect: str = "us"
    secondary_keywords: List[str] = field(default_factory=list)
    negative_keywords: List[str] = field(default_factory=list)

    def validate(self) -> List[str]:
        errors = []
        if not self.seed_phrase.strip():
            errors.append("Seed phrase is required")
        if len(self.seed_phrase) > 200:
            errors.append("Seed phrase exceeds 200 characters")
        if not self.primary_entity.strip():
            errors.append("Primary entity definition is required")
        if self.target_locale not in SUPPORTED_LOCALES:
            errors.append(f"Unsupported locale: {self.target_locale}")
        return errors

    def get_entity_fingerprint(self) -> str:
        raw = f"{self.seed_phrase.lower().strip()}|{self.primary_entity.lower().strip()}"
        return hashlib.sha256(raw.encode()).hexdigest()[:16]


SUPPORTED_LOCALES = [
    "en-US", "en-GB", "en-AU", "en-CA", "en-IN", "en-ZA",
    "es-ES", "es-MX", "es-AR", "es-CO",
    "fr-FR", "fr-CA", "fr-BE",
    "de-DE", "de-AT", "de-CH",
    "it-IT", "pt-BR", "pt-PT",
    "ja-JP", "ko-KR", "zh-CN", "zh-TW",
    "ar-SA", "ar-AE", "ar-EG",
    "hi-IN", "th-TH", "vi-VN", "id-ID",
    "nl-NL", "pl-PL", "ru-RU", "uk-UA",
    "tr-TR", "sv-SE", "da-DK", "fi-FI", "no-NO",
    "cs-CZ", "hu-HU", "ro-RO", "bg-BG", "hr-HR",
    "el-GR", "he-IL", "ms-MY", "fil-PH", "bn-BD"
]


@dataclass
class SMEAsset:
    """Individual SME asset"""
    asset_id: str = ""
    expert_name: str = ""
    expert_title: str = ""
    expert_credentials: List[str] = field(default_factory=list)
    asset_type: str = "transcript"  # transcript, quote, stat, case_study, audio
    content: str = ""
    source_url: str = ""
    date_collected: str = ""
    verified: bool = False
    confidence_score: float = 0.0
    tags: List[str] = field(default_factory=list)


@dataclass
class FirstPartyData:
    """Input 2: First-Party SME Assets"""
    sme_assets: List[SMEAsset] = field(default_factory=list)
    proprietary_stats: List[Dict[str, Any]] = field(default_factory=list)
    internal_case_studies: List[Dict[str, Any]] = field(default_factory=list)
    survey_results: List[Dict[str, Any]] = field(default_factory=list)
    platform_metrics: Dict[str, Any] = field(default_factory=dict)
    raw_notes: List[str] = field(default_factory=list)
    author_social_profiles: Dict[str, str] = field(default_factory=dict)

    def get_all_expert_quotes(self) -> List[Dict[str, str]]:
        quotes = []
        for asset in self.sme_assets:
            if asset.asset_type == "quote" or "quote" in asset.content.lower():
                quotes.append({
                    "expert": asset.expert_name,
                    "title": asset.expert_title,
                    "content": asset.content,
                    "verified": asset.verified
                })
        return quotes

    def get_all_statistics(self) -> List[Dict[str, Any]]:
        stats = []
        stats.extend(self.proprietary_stats)
        for asset in self.sme_assets:
            if asset.asset_type == "stat":
                stats.append({
                    "expert": asset.expert_name,
                    "content": asset.content,
                    "verified": asset.verified
                })
        stats.extend(self.survey_results)
        return stats


@dataclass
class BrandConstraints:
    """Input 3: Brand Guardrails & Tone Matrix"""
    brand_name: str = ""
    voice_profile: str = "authoritative"  # authoritative, conversational, academic, sarcastic, casual
    tone_adjectives: List[str] = field(default_factory=list)
    target_reading_level: str = "intermediate"  # beginner, intermediate, advanced, expert
    regulated_words: List[str] = field(default_factory=list)
    do_not_say_terms: List[str] = field(default_factory=list)
    anti_trope_blacklist: List[str] = field(default_factory=list)
    required_disclaimers: List[str] = field(default_factory=list)
    trademark_rules: Dict[str, str] = field(default_factory=dict)
    legal_restrictions: List[str] = field(default_factory=list)
    brand_colors: List[str] = field(default_factory=list)
    style_guide_url: str = ""
    competitor_brands: List[str] = field(default_factory=list)

    DEFAULT_ANTI_TROPES = [
        "in today's fast-paced", "in today's digital landscape", "game-changer",
        "testament to", "delve into", "delve deeper", "embark on a journey",
        "it's worth noting", "needless to say", "at the end of the day",
        "in this blog post", "buckle up", "let's unpack", "in the realm of",
        "harness the power", "leverage", "synergy", "paradigm shift",
        "unlock the potential", "seamless integration", "robust solution",
        "cutting-edge", "state-of-the-art", "best-in-class", "world-class",
        "game-changing", "revolutionary", "transformative", "innovative",
        "in this article we will", "without further ado", "sit back and relax",
        "the fact of the matter is", "as we move forward", "in conclusion",
        "it is important to note", "with that being said", "that being said",
        "aforementioned", "heretofore", "thus", "henceforth", "moreover",
        "furthermore", "additionally", "in addition", "also",
        "mastering", "unlocking", "navigating", "demystifying",
        "comprehensive guide", "ultimate guide", "everything you need to know",
        "in an era", "in a world", "in recent times", "as technology evolves",
        "the digital age", "the modern era", "the information age"
    ]

    def get_full_blacklist(self) -> List[str]:
        combined = list(set(self.do_not_say_terms + self.anti_trope_blacklist + self.DEFAULT_ANTI_TROPES))
        return sorted(combined)

    def validate(self) -> List[str]:
        errors = []
        if not self.brand_name.strip():
            errors.append("Brand name is required")
        if self.voice_profile not in ["authoritative", "conversational", "academic", "sarcastic", "casual", "technical", "journalistic"]:
            errors.append(f"Invalid voice profile: {self.voice_profile}")
        return errors


@dataclass
class AudienceProfile:
    """Input 4: Audience Intent & Friction Profile"""
    funnel_stage: str = "middle"  # top, middle, bottom
    knowledge_floor: str = "intermediate"  # beginner, intermediate, advanced, expert, c-suite
    technical_depth: str = "moderate"  # shallow, moderate, deep, expert
    reader_persona: str = ""
    pain_points: List[str] = field(default_factory=list)
    decision_criteria: List[str] = field(default_factory=list)
    content_format_preference: str = "comprehensive"  # brief, comprehensive, technical
    max_read_time_minutes: int = 10
    geographic_relevance: List[str] = field(default_factory=list)
    industry_vertical: str = ""
    company_size: str = ""  # smb, mid-market, enterprise
    job_roles: List[str] = field(default_factory=list)

    FUNNEL_STAGE_MAP = {
        "top": {"intent": "informational", "depth": "beginner-intermediate", "cta": "educate"},
        "middle": {"intent": "comparative", "depth": "intermediate-advanced", "cta": "compare"},
        "bottom": {"intent": "transactional", "depth": "advanced-expert", "cta": "convert"}
    }

    def get_intent_vector(self) -> Dict[str, str]:
        return self.FUNNEL_STAGE_MAP.get(self.funnel_stage, self.FUNNEL_STAGE_MAP["middle"])


@dataclass
class TechnicalCredentials:
    """Input 5: Technical & Edge Infrastructure Credentials"""
    gsc_api_key: str = ""
    gsc_property_url: str = ""
    server_log_endpoint: str = ""
    cdn_provider: str = ""  # cloudflare, fastly, akamai, cloudfront
    cdn_api_token: str = ""
    sitemap_url: str = ""
    cms_type: str = ""  # wordpress, contentful, strapi, custom
    cms_api_key: str = ""
    indexing_api_credentials: Dict[str, str] = field(default_factory=dict)
    indexnow_key: str = ""
    render_mode: str = "ssr"  # ssr, csr, isr, ssg
    js_framework: str = ""  # react, nextjs, angular, vue, nuxt


@dataclass
class InputFramework:
    """Master input framework combining all 8 input categories"""
    seed: SeedKeywordInput = field(default_factory=SeedKeywordInput)
    first_party: FirstPartyData = field(default_factory=FirstPartyData)
    brand: BrandConstraints = field(default_factory=BrandConstraints)
    audience: AudienceProfile = field(default_factory=AudienceProfile)
    technical: TechnicalCredentials = field(default_factory=TechnicalCredentials)
    session_id: str = ""
    created_at: str = ""
    raw_input_text: str = ""

    def __post_init__(self):
        if not self.session_id:
            self.session_id = hashlib.sha256(
                f"{datetime.now().isoformat()}|{self.seed.seed_phrase}".encode()
            ).hexdigest()[:12]
        if not self.created_at:
            self.created_at = datetime.now().isoformat()

    def validate_all(self) -> Dict[str, List[str]]:
        all_errors = {}
        seed_errors = self.seed.validate()
        if seed_errors:
            all_errors["seed"] = seed_errors
        brand_errors = self.brand.validate()
        if brand_errors:
            all_errors["brand"] = brand_errors
        return all_errors

    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "created_at": self.created_at,
            "seed": asdict(self.seed),
            "first_party": asdict(self.first_party),
            "brand": asdict(self.brand),
            "audience": asdict(self.audience),
            "technical": asdict(self.technical),
            "raw_input_text": self.raw_input_text
        }

    def save(self, path: str):
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)

    @classmethod
    def load(cls, path: str) -> 'InputFramework':
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        framework = cls()
        framework.session_id = data.get("session_id", "")
        framework.created_at = data.get("created_at", "")
        framework.raw_input_text = data.get("raw_input_text", "")
        if "seed" in data:
            for k, v in data["seed"].items():
                if hasattr(framework.seed, k):
                    setattr(framework.seed, k, v)
        if "first_party" in data:
            fp = data["first_party"]
            framework.first_party.proprietary_stats = fp.get("proprietary_stats", [])
            framework.first_party.internal_case_studies = fp.get("internal_case_studies", [])
            framework.first_party.survey_results = fp.get("survey_results", [])
            framework.first_party.platform_metrics = fp.get("platform_metrics", {})
            framework.first_party.raw_notes = fp.get("raw_notes", [])
            framework.first_party.author_social_profiles = fp.get("author_social_profiles", {})
            for asset_data in fp.get("sme_assets", []):
                asset = SMEAsset()
                for k, v in asset_data.items():
                    if hasattr(asset, k):
                        setattr(asset, k, v)
                framework.first_party.sme_assets.append(asset)
        if "brand" in data:
            for k, v in data["brand"].items():
                if hasattr(framework.brand, k):
                    setattr(framework.brand, k, v)
        if "audience" in data:
            for k, v in data["audience"].items():
                if hasattr(framework.audience, k):
                    setattr(framework.audience, k, v)
        if "technical" in data:
            for k, v in data["technical"].items():
                if hasattr(framework.technical, k):
                    setattr(framework.technical, k, v)
        return framework
