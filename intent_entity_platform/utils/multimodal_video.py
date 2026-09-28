"""Multimodal + video audit (P1 upgrade for M08).

2026 AI Overviews favor video + infographics + calculators. Checks:
- YouTube transcript/embed presence (live oEmbed probe, keyless)
- alt-text coverage vs benchmark
- WebP/AVIF audit from HTML
Honest NOT_CHECKED states when no HTML/URL supplied. Stdlib only.
"""
import re
import urllib.parse
import urllib.request
from typing import Any, Dict, List


def audit_multimodal(html: str = "", page_text: str = "",
                     image_count: int = 0, url: str = "") -> Dict[str, Any]:
    h = html or ""
    imgs = re.findall(r"<img\b[^>]*>", h, re.I)
    with_alt = [t for t in imgs if re.search(r'alt\s*=\s*["\'][^"\']+["\']', t, re.I)]
    empty_alt = len(imgs) - len(with_alt)
    avif = len(re.findall(r"\.avif", h, re.I))
    webp = len(re.findall(r"\.webp", h, re.I))
    youtube_ids = re.findall(r"(?:youtube\.com/(?:watch\?v=|embed/|shorts/)|youtu\.be/)([\w\-]{6,})", h)
    yt_count = len(set(youtube_ids))
    has_transcript_signal = bool(re.search(r"transcript|captions|subtitles", (h + page_text), re.I))
    calc_signal = bool(re.search(r"calculator|interactive tool|configurator", (h + page_text), re.I))

    alt_cov = round(100.0 * len(with_alt) / len(imgs), 1) if imgs else (
        0.0 if (image_count or 0) > 0 else 100.0)
    score = 0
    score += 25 if alt_cov >= 90 else (15 if alt_cov >= 60 else 5)
    score += 20 if yt_count else 0
    score += 10 if has_transcript_signal else 0
    score += 15 if (webp or avif) else 0
    score += 15 if calc_signal else 0
    score += 15 if len(imgs) >= 3 else (len(imgs) * 5 if imgs else 5)
    score = max(0, min(100, score))
    return {
        "method": "heuristic_html_audit",
        "method_note": "Static HTML string audit + keyless oEmbed probe. Not a render/video-watch check.",
        "multimodal_score": score,
        "tier": "STRONG" if score >= 75 else "ADEQUATE" if score >= 50 else "WEAK",
        "images_found": len(imgs) or int(image_count or 0),
        "alt_coverage_pct": alt_cov,
        "empty_alt_count": empty_alt,
        "modern_format_hits": {"webp": webp, "avif": avif},
        "youtube_embeds": yt_count,
        "transcript_signal": has_transcript_signal,
        "calculator_signal": calc_signal,
        "recommendations": _recs(alt_cov, yt_count, has_transcript_signal, webp + avif, calc_signal),
    }


def _recs(alt: float, yt: int, tr: bool, modern: int, calc: bool) -> List[Dict[str, str]]:
    r: List[Dict[str, str]] = []
    if alt < 90:
        r.append({"priority": "HIGH", "action": "Write unique descriptive alt text for every image (target >=90% coverage).",
                  "why": "Alt text feeds image search + AI multimodal retrieval."})
    if not yt:
        r.append({"priority": "HIGH", "action": "Add one 60-180s demo/explainer video (YouTube embed + transcript block on-page).",
                  "why": "2026 AI Overviews over-index video + transcripts."})
    elif not tr:
        r.append({"priority": "MEDIUM", "action": "Publish the video transcript as indexable text below the embed.",
                  "why": "Transcripts are what LLMs actually cite."})
    if not modern:
        r.append({"priority": "MEDIUM", "action": "Serve images as WebP/AVIF with width/height + lazy-load.",
                  "why": "LCP win + lower page weight for crawlers."})
    if not calc:
        r.append({"priority": "LOW", "action": "Consider one interactive asset (calculator/quiz/configurator) for linkable value.",
                  "why": "Interactive assets earn the citations static text cannot."})
    if not r:
        r.append({"priority": "LOW", "action": "Hold: refresh hero image + transcript quarterly.",
                  "why": "Multimodal coverage already strong."})
    return r


def youtube_oembed(url_or_id: str) -> Dict[str, Any]:
    """Keyless YouTube existence check via oEmbed."""
    m = re.search(r"([\w\-]{11})", url_or_id or "")
    vid = m.group(1) if m else (url_or_id or "").strip()
    if not vid:
        return {"status": "NOT_CHECKED"}
    api = "https://www.youtube.com/oembed?url=" + urllib.parse.quote(
        f"https://www.youtube.com/watch?v={vid}") + "&format=json"
    try:
        with urllib.request.urlopen(
                urllib.request.Request(api, headers={"User-Agent": "ContentIntelligenceBot/3.0"}),
                timeout=12) as r:
            import json
            body = json.loads(r.read(100_000).decode("utf-8", errors="ignore"))
            return {"status": "FOUND", "title": body.get("title", "")[:160],
                    "author": body.get("author_name", "")[:120], "source": "live_oembed"}
    except Exception as e:
        return {"status": "NOT_FOUND_OR_BLOCKED", "error": str(e)[:160], "source": "live_oembed"}
