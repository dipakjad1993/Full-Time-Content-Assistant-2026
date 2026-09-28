<div align="center">

# 🧠 Full Time Content Assistant 2026

### Rank on Google. Get cited by ChatGPT. Be the answer everywhere.

[![Python](https://img.shields.io/badge/Python-3.13-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Version](https://img.shields.io/badge/Version-v3.0.0--enterprise-6d4ff0?style=for-the-badge)](https://github.com/dipakjad1993/Full-Time-Content-Assistant-2026)
[![Tests](https://img.shields.io/badge/Tests-44%2F44%20pytest%20passing-059669?style=for-the-badge)](https://docs.pytest.org/)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-0078D6?style=for-the-badge)](https://www.python.org/)

**Self-hosted, real-time SEO + GEO/AEO analyzer.** Paste a URL (or a keyword + entity) → the engine runs **22 analysis modules in parallel against live web data** and hands you 5 ready-to-execute blueprints. No stale templates, no fabricated numbers.

</div>

---

## ⚡ What it does for you, in real time

| You want… | You get in a single run |
|---|---|
| See your **live SERP landscape** | Real rankings, People-Also-Ask, and winnable features for your query (M01) |
| Know if **AI engines can cite you** | Extractability score + **live citation tests** on ChatGPT, Gemini, Perplexity & Claude with share-of-voice history (M02/M22) |
| Catch **technical blockers now** | Live robots.txt, `llms.txt`, sitemap, headers, CDN, and schema-validity checks (M13/M16/M18) |
| Know if content is **decaying** | Real Wayback Machine history + a section-by-section refresh brief (M15) |
| Stop guessing **what to write** | SERP-driven brief: outline, word targets, questions, schema & E-E-A-T targets (`/api/brief`) |
| Turn findings into **shipped work** | Every recommendation as an assignable task → CSV / Jira / Linear (Action Center) |
| **Prove** the change worked | Statistically valid A/B designs with real sample-size math (M17) + nightly tracking cron |

Every number is labeled **live_measurement** (computed this run), **heuristic estimate** (honest guess, disclosed), or **cited_research** (2026 third-party study, sourced). Where data can't be measured, the tool says so instead of inventing it.

---

## 🚀 Quickstart (2 minutes)

```bash
git clone https://github.com/dipakjad1993/Full-Time-Content-Assistant-2026.git
cd Full-Time-Content-Assistant-2026
pip install -r requirements.txt
python server.py          # → http://localhost:5000 (PORT env var overrides)
```

Or one-command prod:

```bash
docker compose up         # → http://localhost:5000, SQLite volume persisted
```

**Two modes:** paste a published URL *or* enter a seed keyword + primary entity — everything else is optional with working defaults. Optional power-ups via env keys: `SERPER_API_KEY` (Google SERP), `OPENAI/ANTHROPIC/GEMINI/PERPLEXITY_API_KEY` (live LLM tests), `PSI_API_KEY` (Core Web Vitals), GSC OAuth (Search Console pull). Without keys, honest fallbacks apply — never fake data.

---

## 🖥️ The UI — top nav, no sidebar

| Page | What's on it |
|---|---|
| **Analyzer** | Inputs only: URL mode + manual form + live progress dots |
| **About** | What the tool is and why it exists |
| **Required Inputs** | Every field explained: required vs optional, what to enter, how it's used |
| **Features & Functions** | The 3 output layers, platform functions, all 22 modules |
| **Outputs** | The 5 blueprints + everything a run produces |
| **Business Impact** | How this converts to rankings, citations, and shipped work |

Results open in their own view (Executive Summary + 5 blueprints + 22 module tabs + Raw JSON) with a **← New Analysis** button back. Dark/light themes included.

---

## 🧩 The 22 modules — one line each

Full reference: [`docs/MODULES.md`](docs/MODULES.md). Screenshots: [`docs/SCREENSHOTS.md`](docs/SCREENSHOTS.md).

| # | Module | Live check | You get |
|---|---|---|---|
| M01 | SERP & Knowledge Graph | DDG SERP + PAA, Wikidata Q-ID | Winnable features, entity gaps |
| M02 | GEO & AEO Simulator | Page-signal scan | Per-engine readiness + fixes |
| M03 | Semantic Structure | Headings/schema/answer bands | Hierarchy + extractability fixes |
| M04 | E-E-A-T Gap Profiler | Trust signals, consensus phrases | Weakest pillar + gap ranking |
| M05 | Internal Links & Cannibalization | Live link-health checks | Link blueprint, cannibal flags |
| M06 | Fluff & Cliché Decoder | Real text statistics | Rewrite priority list |
| M07 | Citation Verifier | Live URL verification | Hallucination-risk score |
| M08 | Multimodal Blueprint | Image/alt audit | Asset plan + video/transcript audit |
| M09 | GEO Tracker | Live SERP snapshot + history DB | Monitoring + alert config |
| M10 | CSR Simulator | Content-availability checks | Bot-visibility risk + prerender fixes |
| M11 | RAG Tester | Real chunking of your text | Retrievability score + chunk plan |
| M12 | Brand Compliance | Voice/claim scan | Violations + required disclaimers |
| M13 | Schema Generator | Page-signal suitability | Copy-ready JSON-LD (10+ types) |
| M14 | Intent & Bounce | Depth/read-time signals | Bounce risk + above-fold fixes |
| M15 | Decay Engine | Wayback CDX snapshots | Freshness score + refresh brief |
| M16 | CDN Edge Previewer | Live headers + CDN detect | Edge worker + deploy guide |
| M17 | A/B Testing Engine | Real power math | Sample sizes, durations, guardrails |
| M18 | Indexing Sentinel | Live robots/sitemap + `llms.txt`, 9-bot audit | Crawl-block fixes |
| M19 | Localization Sync | Locale/currency signals | hreflang set + rollout priority |
| M20 | Digital PR Engine | Outlet discovery + Wikidata | Pitch angles + off-site gap plan |
| M21 | DOM Inspector | Resource/lazy-load audit | CLS + weight optimization list |
| M22 | Live LLM Citation Tester | Real provider transcripts (or honest mock) | Share-of-voice + sentiment trend |

Each module returns stat boxes, priority-tagged recommendations, ordered implementation steps, placement guidance, and a collapsible deep-dive. Problem values (`MISSING`, `NOT_CONFIGURED`, …) highlight red everywhere.

---

## 🗂 Blueprints + export — what leaves the tool

- **5 blueprints**: Editorial & Writing · GEO/AEO Optimization · Technical Payload · CDN & Edge Deployment · Post-Publish Sentinel Brief
- **PDF**: full report *or* slim narrative-only (no raw-JSON appendix) — timestamped, page-numbered
- **JSON artifact** (`/api/download_json`), **versioned share links** (`/api/share`), **OTP-verified email** (6-digit, single-use, 10-min TTL)
- **Action Center**: tasks with priority/effort/owner → CSV / Jira / Linear

---

## 🔌 API cheat sheet

Spec: [`openapi.yaml`](openapi.yaml) · Live index: `/api/docs` · Agent endpoint: `/api/mcp` (`tools/list`, `tools/call`)

| Call | Purpose |
|---|---|
| `POST /api/analyze`, `POST /api/analyze-url` | Full 22-module run (20/hr/IP, SSRF-guarded) |
| `POST /api/score`, `/api/brief`, `/api/gsc_quick_wins` | Draft score · SERP brief · GSC striking-distance/decay/cannibalization |
| `POST /api/llm_test`, `GET /api/llm_history` | Live LLM citation run + SOV trend |
| `POST /api/pagespeed`, `/api/ai_crawl_audit`, `/api/extractability`, `/api/offsite_authority`, `/api/multimodal_audit` | Vitals · AI-bot audit · answer-block score · off-site graph · video audit |
| `POST /api/action_center` | Tasks (+ `format=csv/jira/linear`) |
| `POST /api/download_pdf?narrative_only=1`, `/api/download_json`, `/api/share` | Exports & sharing |
| `GET /api/health`, `/api/serp_status`, `/api/gsc_oauth_status`, `/api/auth/status` | Health · provider/cost guard · GSC mode · auth mode |

Full examples: [`docs/API.md`](docs/API.md).

```bash
curl -X POST http://localhost:5000/api/analyze -H "Content-Type: application/json" \
  -d '{"seed":"best enterprise accounting software","entity":"multi-currency accounting software"}'
```

---

## 🌐 Live data, honestly labeled

DuckDuckGo SERP + PAA · Wikidata entities · Wayback CDX · live robots/sitemap/headers/CDN/link checks · optional Serper/DataForSEO (30-day SQLite cache), PSI/CrUX, GSC OAuth, LLM providers. Timeouts, UA rotation, retries, graceful fallbacks throughout; M04–M22 run in an 8-worker pool. M02/M10/M14/M17 carry explicit `method_note: heuristic estimate`.

---

## 🚀 Deploy

Localhost by default (`HOST`/`PORT` override). Prod: `wsgi.py` + gunicorn (Linux) / waitress (Windows) behind nginx with TLS; keep `APP_DEBUG` off; rate-limit analyze/pdf endpoints at the edge. SMTP via `mail_config.json` (git-ignored) or `SMTP_*` env vars — without it, everything works except email OTP.

## 🧫 Testing

```bash
python -m pytest test_api.py test_enterprise.py -q   # 44 tests, mocked network
```

Covers contract, SSRF bypass matrix (incl. IPv4-mapped IPv6 + DNS rebinding), OTP lockout/windows, PDF overflow + slim mode, all-22-module error paths, SERP cache, and every enterprise endpoint.

## 🔒 Security snapshot

CSPRNG OTPs (single-use, 5-try lockout, 3-per-10-min window) · SSRF allowlist + DNS re-check + redirect/size caps · per-IP rate limits · CSP/HSTS/nosniff/SAMEORIGIN · no traceback leaks · escaped rendering · SQLite-persisted stores (multi-worker safe) · localhost-by-default bind.

## 📁 Structure

```
server.py  requirements.txt/.lock  wsgi.py  Dockerfile  docker-compose.yml
openapi.yaml  .env.example  test_api.py  test_enterprise.py  scripts/nightly_tracker_cron.py
intent_entity_platform/{core/engine.py, modules/module_01…module_22.py, utils/*.py, data/prompts.yml}
docs/{MODULES.md, API.md, SCREENSHOTS.md}  screenshots/
```

## ❓ FAQ

**Do I need API keys or to pay?** No — free public endpoints cover everything; keys only upgrade precision (Google SERP, live LLM tests, CrUX lab data).
**Cloud-hosted?** No — runs on your machine; data leaves only for the live public queries and emails you trigger.
**Offline?** Partially — live-data modules need internet; the rest analyze local content.
**Which SERP source?** `SERP_PROVIDER=serper|dataforseo|ddg_fallback` (free DDG/Wikipedia default, 30-day cache).
**Where do SMTP secrets live?** `mail_config.json` — git-ignored, never committed.
**How do I deploy?** gunicorn/waitress + nginx + TLS; see Deploy above.

## 📄 License

MIT — see [LICENSE](LICENSE). Built for the search + generative-AI era: *rank on Google, get cited by ChatGPT, be the answer.*
