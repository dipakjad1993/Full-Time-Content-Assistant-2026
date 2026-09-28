# API Examples

Base: `http://localhost:5000` (`PORT` overrides). Full spec: [`openapi.yaml`](../openapi.yaml), live index: `GET /api/docs`, agent endpoint: `POST /api/mcp` (`tools/list`, `tools/call`).

## Run an analysis
```bash
curl -X POST http://localhost:5000/api/analyze -H "Content-Type: application/json" \
  -d '{"seed":"best enterprise accounting software","entity":"multi-currency accounting software"}'
```

## Analyze a URL (SSRF-guarded)
```bash
curl -X POST http://localhost:5000/api/analyze-url -H "Content-Type: application/json" \
  -d '{"url":"https://example.com/blog/post","brand":"ExampleCo"}'
```

## Score a draft (dual SEO+GEO)
```bash
curl -X POST http://localhost:5000/api/score -H "Content-Type: application/json" \
  -d '{"draft":"...","competitor_texts":["..."],"must_include_terms":["pricing","vs"],"targets":{"words":1800}}'
```

## SERP-driven brief
```bash
curl -X POST http://localhost:5000/api/brief -H "Content-Type: application/json" \
  -d '{"seed":"...","entity":"...","word_target":1800}'
```

## GSC Quick Wins (CSV upload or inline)
```bash
curl -X POST http://localhost:5000/api/gsc_quick_wins -F "file=@gsc-performance.csv"
# CSV header: query,page,clicks,impressions,ctr,position
```
OAuth mode probe: `GET /api/gsc_oauth_status` (CSV stays supported when OAuth isn't configured).

## Live LLM citation test + history
```bash
curl -X POST http://localhost:5000/api/llm_test -H "Content-Type: application/json" \
  -d '{"entity":"Acme CRM","prompts":10}'
curl "http://localhost:5000/api/llm_history?key=acme%20crm"
```

## Audits
```bash
curl -X POST http://localhost:5000/api/pagespeed -H "Content-Type: application/json" \
  -d '{"url":"https://example.com/"}'                       # CrUX + PSI (NOT_MEASURED without PSI_API_KEY)
curl -X POST http://localhost:5000/api/ai_crawl_audit -H "Content-Type: application/json" \
  -d '{"url":"https://example.com/"}'                       # llms.txt + 9-bot robots split
curl -X POST http://localhost:5000/api/extractability -H "Content-Type: application/json" \
  -d '{"page_text":"...","h2s":["What is X?"],"schema_types":["FAQPage"]}'
curl -X POST http://localhost:5000/api/offsite_authority -H "Content-Type: application/json" \
  -d '{"entity":"Acme CRM"}'
curl -X POST http://localhost:5000/api/multimodal_audit -H "Content-Type: application/json" \
  -d '{"html":"..."}'
```

## Action Center (tasks → tracker export)
```bash
curl -X POST http://localhost:5000/api/action_center -H "Content-Type: application/json" \
  -d '{"module_results":{...},"format":"jira"}'             # json (default) | csv | jira | linear
```

## Exports & sharing
```bash
curl -X POST http://localhost:5000/api/download_pdf -H "Content-Type: application/json" \
  -d '{"report":{...},"narrative_only":true}' --output report.pdf
curl -X POST http://localhost:5000/api/download_json -H "Content-Type: application/json" \
  -d '{"report":{...}}' --output report.json
curl -X POST http://localhost:5000/api/share -H "Content-Type: application/json" \
  -d '{"report":{...},"label":"Q3 audit"}'                  # → {share_id, share_url}
```

## OTP email flow
```bash
curl -X POST http://localhost:5000/api/send_otp -H "Content-Type: application/json" \
  -d '{"email":"you@example.com"}'
curl -X POST http://localhost:5000/api/verify_and_send_report -H "Content-Type: application/json" \
  -d '{"email":"you@example.com","otp":"123456","report":{...}}'
```

## Ops
```bash
curl http://localhost:5000/api/health
curl http://localhost:5000/api/serp_status        # provider + cost guard
curl http://localhost:5000/api/auth/status        # auth mode + workspaces
curl "http://localhost:5000/api/progress/<analysis_id>"
```

Rate limits (per IP): analyze 20/hr · PDF 10/hr · OTP 5/hr · LLM test 10/hr. Auth: send `X-API-Key` when `ENTERPRISE_API_KEYS` is set.
