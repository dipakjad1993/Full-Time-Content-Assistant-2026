"""2026 AI-crawler completeness audit (M18 upgrade).

Checks the #1 enterprise ask for 2026:
- robots.txt allow/disallow per AI bot (retrieval vs training split)
- llms.txt + ai.txt presence and sanity
- meta noai / noimageai / noml tags in HTML

Bots covered (2026 canonical set):
  Retrieval (answer/citation path): GPTBot, ChatGPT-User, OAI-SearchBot,
    PerplexityBot, Claude-SearchBot, Applebot-Extended
  Training (opt-out path): CCBot, Google-Extended, Bytespider

Live measurement where a URL is given; otherwise returns NOT_CHECKED with
honest method notes. Stdlib only.
"""
import re
import urllib.parse
import urllib.request
from typing import Any, Dict, List, Optional

RETRIEVAL_BOTS = ["GPTBot", "ChatGPT-User", "OAI-SearchBot",
                  "PerplexityBot", "Claude-SearchBot", "Applebot-Extended"]
TRAINING_BOTS = ["CCBot", "Google-Extended", "Bytespider"]
ALL_BOTS = RETRIEVAL_BOTS + TRAINING_BOTS

_UA = ("Mozilla/5.0 (compatible; ContentIntelligenceBot/3.0; +https://example.com/bot)")


def _fetch_text(url: str, timeout: int = 12, max_bytes: int = 300_000) -> Dict[str, Any]:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": _UA})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            raw = r.read(max_bytes + 1)
            truncated = len(raw) > max_bytes
            text = raw[:max_bytes].decode("utf-8", errors="ignore")
            return {"ok": True, "status": getattr(r, "status", 200),
                    "text": text, "truncated": truncated, "error": None}
    except Exception as e:
        return {"ok": False, "status": 0, "text": "",
                "truncated": False, "error": str(e)[:240]}


def _parse_robots_for_bot(robots_text: str, bot: str) -> str:
    """Return ALLOW / DISALLOW / UNSPECIFIED for one bot (first matching group wins)."""
    groups: List[Dict[str, Any]] = []
    cur: Optional[Dict[str, Any]] = None
    for raw in robots_text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            continue
        k, v = [p.strip() for p in line.split(":", 1)]
        kl = k.lower()
        if kl == "user-agent":
            if cur is None or cur.get("has_rule"):
                cur = {"agents": [], "has_rule": False, "verdict": "UNSPECIFIED"}
                groups.append(cur)
            cur["agents"].append(v.lower())
        elif kl in ("allow", "disallow") and cur is not None:
            cur["has_rule"] = True
            path = v
            applies = any(a == "*" or a.lower() == bot.lower() for a in cur["agents"])
            if applies:
                if kl == "disallow" and path in ("", "/"):
                    cur["verdict"] = "DISALLOW_ALL" if path == "/" else cur["verdict"]
                elif kl == "disallow" and path:
                    if cur["verdict"] == "UNSPECIFIED":
                        cur["verdict"] = "PARTIAL_DISALLOW"
                elif kl == "allow" and path in ("/", ""):
                    if cur["verdict"] == "UNSPECIFIED":
                        cur["verdict"] = "ALLOW"
    verdict = "UNSPECIFIED"
    for g in groups:
        if any(a == "*" or a.lower() == bot.lower() for a in g["agents"]):
            if g["verdict"] != "UNSPECIFIED":
                verdict = g["verdict"]
                if verdict in ("DISALLOW_ALL", "ALLOW"):
                    break
    star = next((g for g in groups if "*" in g["agents"]), None)
    if verdict == "UNSPECIFIED" and star and star["verdict"] != "UNSPECIFIED":
        verdict = star["verdict"]
    return verdict


def audit_ai_crawlers(base_url: str = "", robots_text: str = "",
                      html: str = "") -> Dict[str, Any]:
    """Full AI-crawler audit. base_url enables live llms.txt/ai.txt/robots fetches."""
    out: Dict[str, Any] = {
        "method": "live_robots_and_file_fetch",
        "method_note": "Live fetch of robots.txt/llms.txt/ai.txt + static bot-list parse. "
                       "Not a crawl-log proof of bot visits.",
        "retrieval_bots": RETRIEVAL_BOTS,
        "training_bots": TRAINING_BOTS,
        "per_bot": {},
        "files": {},
        "meta_tags": {},
    }
    origin = ""
    if base_url:
        try:
            p = urllib.parse.urlparse(base_url if "://" in base_url else "https://" + base_url)
            origin = f"{p.scheme or 'https'}://{p.hostname}" if p.hostname else ""
        except Exception:
            origin = ""
    if origin and not robots_text:
        r = _fetch_text(origin + "/robots.txt")
        out["files"]["robots_txt"] = {
            "status": "FOUND" if (r["ok"] and r["text"].strip()) else "MISSING",
            "http_status": r["status"], "error": r["error"],
            "source": "live_measurement", "measured_at": "now",
        }
        robots_text = r["text"] if r["ok"] else ""
    elif robots_text:
        out["files"]["robots_txt"] = {"status": "PROVIDED",
                                      "source": "caller_supplied_robots_text"}
    else:
        out["files"]["robots_txt"] = {"status": "NOT_CHECKED",
                                      "source": "no_url_no_robots_text",
                                      "note": "Pass url or robots_text for a live verdict."}
    if origin:
        for fname in ("llms.txt", "ai.txt"):
            r = _fetch_text(origin + "/" + fname)
            ok = bool(r["ok"] and r["text"].strip() and r["status"] < 400)
            entry: Dict[str, Any] = {
                "status": "FOUND" if ok else "MISSING",
                "http_status": r["status"], "error": r["error"],
                "source": "live_measurement",
                "bytes": len(r["text"]) if r["ok"] else 0,
            }
            if ok:
                entry["line_count"] = r["text"].count("\n") + 1
                entry["has_markdown_links"] = bool(re.search(r"\[.*?\]\(.*?\)", r["text"]))
            out["files"][fname] = entry
    else:
        for fname in ("llms.txt", "ai.txt"):
            out["files"].setdefault(fname, {"status": "NOT_CHECKED"})
    if robots_text:
        for bot in ALL_BOTS:
            verdict = _parse_robots_for_bot(robots_text, bot)
            role = "retrieval" if bot in RETRIEVAL_BOTS else "training"
            if role == "retrieval":
                health = ("BLOCKED" if verdict == "DISALLOW_ALL"
                          else "PARTIAL" if verdict == "PARTIAL_DISALLOW"
                          else "ALLOWED" if verdict == "ALLOW" else "UNSPECIFIED")
            else:
                health = verdict
            out["per_bot"][bot] = {"role": role, "robots_verdict": verdict,
                                   "citation_path": health,
                                   "source": "live_measurement" if origin else "static_parse"}
    else:
        for bot in ALL_BOTS:
            out["per_bot"][bot] = {"role": "retrieval" if bot in RETRIEVAL_BOTS else "training",
                                   "robots_verdict": "NOT_CHECKED",
                                   "citation_path": "NOT_CHECKED"}
    h = html or ""
    out["meta_tags"] = {
        "noai": bool(re.search(r'<meta[^>]+name=["\']?noai', h, re.I)),
        "noimageai": bool(re.search(r'<meta[^>]+name=["\']?noimageai', h, re.I)),
        "noml": bool(re.search(r'<meta[^>]+name=["\']?noml', h, re.I)),
        "robots_noai_in_content": bool(re.search(
            r'<meta[^>]+name=["\']?robots["\'][^>]+noai', h, re.I)),
        "source": "live_html_parse" if h else "no_html_supplied",
    }
    blocked_retrieval = [b for b, v in out["per_bot"].items()
                         if v.get("role") == "retrieval"
                         and v.get("citation_path") == "BLOCKED"]
    out["summary"] = {
        "retrieval_blocked_count": len(blocked_retrieval),
        "retrieval_blocked": blocked_retrieval,
        "llms_txt": out["files"].get("llms.txt", {}).get("status", "NOT_CHECKED"),
        "ai_txt": out["files"].get("ai.txt", {}).get("status", "NOT_CHECKED"),
        "verdict": ("CRITICAL_AI_CRAWL_BLOCK" if blocked_retrieval
                    else "NEEDS_LLMS_TXT" if out["files"].get("llms.txt", {}).get("status") == "MISSING"
                    else "OK" if origin else "NOT_CHECKED"),
    }
    out["recommendations"] = []
    if blocked_retrieval:
        out["recommendations"].append(
            {"priority": "CRITICAL",
             "action": f"Unblock retrieval bots in robots.txt: {', '.join(blocked_retrieval)}",
             "why": "Blocked retrieval bots cannot cite the page in AI answers."})
    if out["files"].get("llms.txt", {}).get("status") == "MISSING" and origin:
        out["recommendations"].append(
            {"priority": "HIGH",
             "action": "Add /llms.txt (Markdown index of key URLs + summaries) for LLM ingestion.",
             "why": "#1 2026 enterprise ask; feeds Perplexity/ChatGPT retrieval."})
    if out["meta_tags"].get("noai"):
        out["recommendations"].append(
            {"priority": "MEDIUM",
             "action": "Remove <meta name='noai'> unless AI opt-out is intentional.",
             "why": "noai signals training opt-out and may reduce AI features."})
    return out
