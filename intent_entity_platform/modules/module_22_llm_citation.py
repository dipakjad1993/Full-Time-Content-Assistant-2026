"""Module 22: Live LLM Citation Tester (P1) — the GEO moat.

Actually calls LLM provider APIs with a fixed prompt set per entity, captures
transcripts + cited sources + sentiment + share-of-voice, persists runs to
SQLite history. Without keys it runs in HONEST_MOCK mode (labeled, never sold
as measured) so OSS users still get the workflow.

Providers (env-gated, stdlib urllib):
- OpenAI (OPENAI_API_KEY, default model gpt-4o-mini)
- Anthropic (ANTHROPIC_API_KEY, default claude-3-5-haiku-latest)
- Gemini (GEMINI_API_KEY -> generativelanguage v1beta)
- Perplexity (PERPLEXITY_API_KEY -> chat/completions, online model returns citations)

Prompt set: 10 default questions per entity (info/comparison/how-to/price/intent),
branchable by funnel_stage + knowledge_floor inputs. Sentiment = transparent
lexicon heuristic (labeled). SOV = brand-mention share across transcripts.
"""
import json
import os
import re
import urllib.request
from datetime import datetime, timezone
from typing import Any, Dict, List

DEFAULT_PROMPTS = [
    "What is {entity} and who is it best for?",
    "What are the top features of {entity}?",
    "{entity} vs competitors: which should I choose?",
    "How much does {entity} cost / what is the pricing?",
    "How do I get started with {entity}? Give steps.",
    "What are the pros and cons of {entity}?",
    "Is {entity} trustworthy? Cite sources.",
    "What do users say about {entity} on Reddit/YouTube?",
    "What are alternatives to {entity}?",
    "Latest news or updates about {entity} in 2026?",
]

_POS = {"best", "excellent", "great", "love", "leader", "top", "recommended",
        "impressive", "strong", "trusted", "innovative"}
_NEG = {"worst", "bad", "poor", "avoid", "weak", "lawsuit", "breach", "scam",
        "overpriced", "buggy", "unreliable"}


def prompt_set_for(entity: str, funnel: str = "", knowledge: str = "",
                   n: int = 10) -> List[str]:
    prompts = [p.format(entity=entity or "this topic") for p in DEFAULT_PROMPTS[:n]]
    if (funnel or "").lower().startswith("top"):
        prompts.insert(0, f"What is {entity}? Explain simply for a beginner.")
    elif (funnel or "").lower().startswith("bottom"):
        prompts.append(f"Where should I buy {entity} / get a demo? Include pricing caveats.")
    if (knowledge or "").lower().startswith("adv"):
        prompts.append(f"Advanced technical deep-dive: architecture/limits of {entity}.")
    return prompts[: max(4, min(n + 2, 14))]


def _post(url: str, payload: Dict[str, Any], headers: Dict[str, str],
          timeout: int = 40) -> Dict[str, Any]:
    try:
        req = urllib.request.Request(url, data=json.dumps(payload).encode(),
                                     headers=headers)
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return {"ok": True, "body": json.loads(r.read(1_000_000).decode("utf-8", errors="ignore"))}
    except Exception as e:
        return {"ok": False, "error": str(e)[:300]}


def _call_openai(prompt: str, model: str) -> Dict[str, Any]:
    key = os.environ.get("OPENAI_API_KEY", "")
    if not key:
        return {"ok": False, "error": "no_key"}
    return _post("https://api.openai.com/v1/chat/completions",
                 {"model": model, "messages": [{"role": "user", "content": prompt}],
                  "temperature": 0}, {"Authorization": f"Bearer {key}",
                                      "Content-Type": "application/json"})


def _call_anthropic(prompt: str, model: str) -> Dict[str, Any]:
    key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not key:
        return {"ok": False, "error": "no_key"}
    return _post("https://api.anthropic.com/v1/messages",
                 {"model": model, "max_tokens": 600,
                  "messages": [{"role": "user", "content": prompt}]},
                 {"x-api-key": key, "anthropic-version": "2023-06-01",
                  "Content-Type": "application/json"})


def _call_gemini(prompt: str, model: str) -> Dict[str, Any]:
    key = os.environ.get("GEMINI_API_KEY", "")
    if not key:
        return {"ok": False, "error": "no_key"}
    return _post(f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}",
                 {"contents": [{"parts": [{"text": prompt}]}]},
                 {"Content-Type": "application/json"})


def _call_perplexity(prompt: str, model: str) -> Dict[str, Any]:
    key = os.environ.get("PERPLEXITY_API_KEY", "")
    if not key:
        return {"ok": False, "error": "no_key"}
    return _post("https://api.perplexity.ai/chat/completions",
                 {"model": model, "messages": [{"role": "user", "content": prompt}]},
                 {"Authorization": f"Bearer {key}", "Content-Type": "application/json"})


def _extract_text(provider: str, body: Dict[str, Any]) -> str:
    try:
        if provider in ("openai", "perplexity"):
            return (((body.get("choices") or [{}])[0].get("message") or {}).get("content") or "")
        if provider == "anthropic":
            blocks = (body.get("content") or [])
            return " ".join(b.get("text", "") for b in blocks if isinstance(b, dict))
        if provider == "gemini":
            cands = body.get("candidates") or []
            parts = ((cands[0].get("content") or {}).get("parts") or []) if cands else []
            return " ".join(p.get("text", "") for p in parts if isinstance(p, dict))
    except Exception:
        pass
    return ""


def _sentiment(text: str) -> Dict[str, Any]:
    toks = set(re.findall(r"[a-z]+", text.lower()))
    pos = len(toks & _POS)
    neg = len(toks & _NEG)
    label = "positive" if pos - neg >= 2 else "negative" if neg - pos >= 2 else "neutral"
    return {"label": label, "pos_hits": pos, "neg_hits": neg,
            "method": "lexicon_heuristic_v1"}


class LLMCitationTester:
    """M22 engine. analyze(inputs) -> ModuleResult (never raises)."""

    def __init__(self):
        self.module_id = "M22"
        self.module_name = "Live LLM Citation Tester"

    def analyze(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        entity = str(inputs.get("primary_entity") or inputs.get("entity") or "").strip()
        seed = str(inputs.get("seed_phrase") or inputs.get("seed") or "").strip()
        brand = str(inputs.get("brand") or "").strip()
        funnel = str(inputs.get("funnel_stage") or inputs.get("funnel") or "")
        knowledge = str(inputs.get("knowledge_floor") or inputs.get("knowledge") or "")
        n = int(inputs.get("m22_prompts", 0) or 10)
        n = max(4, min(n, 14))
        subject = entity or seed or brand or "this topic"
        prompts = prompt_set_for(subject, funnel, knowledge, n)

        providers = [
            ("openai", os.environ.get("OPENAI_MODEL", "gpt-4o-mini"), _call_openai),
            ("anthropic", os.environ.get("ANTHROPIC_MODEL", "claude-3-5-haiku-latest"), _call_anthropic),
            ("gemini", os.environ.get("GEMINI_MODEL", "gemini-2.0-flash"), _call_gemini),
            ("perplexity", os.environ.get("PERPLEXITY_MODEL", "sonar"), _call_perplexity),
        ]
        live, mocked = [], []
        transcripts: List[Dict[str, Any]] = []
        for prov, model, fn in providers:
            if not os.environ.get(f"{prov.upper()}_API_KEY"):
                mocked.append(prov)
                continue
            # 2 prompts per provider cap (cost guard); full set on /api/llm_test with explicit flag
            for pr in prompts[:2]:
                r = fn(pr, model)
                if not r.get("ok"):
                    transcripts.append({"provider": prov, "model": model, "prompt": pr,
                                        "status": "ERROR", "error": r.get("error"),
                                        "source": "live_api"})
                    continue
                text = _extract_text(prov, r["body"])[:4000]
                urls = re.findall(r"https?://[^\s)>\]]+", text)[:10]
                cited = brand.lower() in text.lower() if brand else subject.lower() in text.lower()
                transcripts.append({"provider": prov, "model": model, "prompt": pr,
                                    "status": "OK", "text": text, "urls_cited": urls,
                                    "subject_mentioned": cited,
                                    "sentiment": _sentiment(text), "source": "live_api"})
            live.append(prov)

        mode = "live" if live else "honest_mock"
        mentions = sum(1 for t in transcripts if t.get("subject_mentioned"))
        denom = len(transcripts) or 1
        sov = round(100.0 * mentions / denom, 1) if transcripts else 0.0
        run = {"entity": subject, "brand": brand, "mode": mode,
               "providers_live": live, "providers_mocked": mocked,
               "prompt_count": len(prompts),
               "share_of_voice_pct": sov,
               "transcripts": transcripts,
               "captured_at": datetime.now(timezone.utc).isoformat(),
               "method_note": ("Live provider transcripts (2 prompts/provider cost guard)."
                               if live else
                               "HONEST MOCK — no provider API keys set. Wire OPENAI/ANTHROPIC/GEMINI/PERPLEXITY_API_KEY for measured citations.")}
        # persist
        try:
            from ..utils.persistence import history_add
            history_add("m22", subject.lower()[:120], run)
        except Exception:
            pass
        recs = []
        if mode == "honest_mock":
            recs.append({"priority": "HIGH",
                         "action": "Set at least one provider API key to convert M22 from mock to measured SOV.",
                         "why": "Without live transcripts you are GEO-ready, not GEO-tracked."})
        if transcripts and sov < 50:
            recs.append({"priority": "HIGH",
                         "action": "Raise SOV: add 40-60 word answer blocks + FAQ schema + off-site mentions (M20).",
                         "why": f"Subject mentioned in only {sov}% of live transcripts."})
        if not recs:
            recs.append({"priority": "LOW", "action": "Schedule nightly M22 runs; alert on SOV drops >10pts.",
                         "why": "Citation share drifts weekly."})
        return {"module": self.module_id, "module_name": self.module_name, "status": "ok",
                "mode": mode, "prompt_set": prompts,
                "share_of_voice_pct": sov, "providers_live": live,
                "providers_mocked": mocked, "run": run,
                "recommendations": recs,
                "implementation_steps": [
                    "1. Set provider keys (server env) for live mode.",
                    "2. POST /api/llm_test with entity + prompts for full-set runs.",
                    "3. GET /api/llm_history?key=<entity> for SOV trend.",
                    "4. Cron scripts/nightly_tracker_cron.py for nightly capture."],
                "where_to_add": ["Nightly tracker DB + GEO dashboard; not on-page copy."],
                "detailed_analysis": {"method_note": run["method_note"], "transcript_count": len(transcripts)}}
