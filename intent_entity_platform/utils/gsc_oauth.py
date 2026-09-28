"""GSC OAuth status + CSV fallback (P0).

2026 winners pull the Search Console API with an AI-Answer-Impressions filter
(zero-click split). Full OAuth flow needs google-api-python-client + a GCP
project; this module exposes:
- oauth_status(): honest capability probe (configured / missing_*).
- oauth_url_hint(): step-by-step operator instructions (no secrets fabricated).
- CSV path stays first-class fallback (existing gsc_quickwins.py untouched).

Env: GSC_CLIENT_ID, GSC_CLIENT_SECRET, GSC_REFRESH_TOKEN (or GSC_SERVICE_JSON).
"""
import os
from typing import Any, Dict, List


def oauth_status() -> Dict[str, Any]:
    cid = bool(os.environ.get("GSC_CLIENT_ID"))
    sec = bool(os.environ.get("GSC_CLIENT_SECRET"))
    rtok = bool(os.environ.get("GSC_REFRESH_TOKEN"))
    svc = bool(os.environ.get("GSC_SERVICE_JSON"))
    configured = (cid and sec and rtok) or svc
    return {
        "mode": "oauth_live" if configured else "csv_fallback",
        "configured": configured,
        "checks": {
            "GSC_CLIENT_ID": "SET" if cid else "MISSING",
            "GSC_CLIENT_SECRET": "SET" if sec else "MISSING",
            "GSC_REFRESH_TOKEN": "SET" if rtok else "MISSING",
            "GSC_SERVICE_JSON": "SET" if svc else "MISSING",
        },
        "method_note": ("Live Search Console API ready (use refresh token -> access token -> "
                        "searchanalytics.query with AI-Answer-Impression dimension filter)."
                        if configured else
                        "OAuth not configured: /api/gsc_quick_wins CSV upload is the supported path. "
                        "No data fabricated."),
        "setup_steps": [
            "1. GCP Console -> APIs & Services -> enable 'Google Search Console API'.",
            "2. OAuth consent (internal) -> Desktop client -> download client_id/secret.",
            "3. First grant: oauth2 flow with scope https://www.googleapis.com/auth/webmasters.readonly; store refresh_token.",
            "4. Set env GSC_CLIENT_ID / GSC_CLIENT_SECRET / GSC_REFRESH_TOKEN on the server.",
            "5. Query siteUrl + date range; segment AI-Overview impressions where the API exposes them; CSV stays as audit fallback.",
        ],
        "zero_click_note": "Filter AI Answer impressions (AI Overviews) separately from classic clicks; "
                           "report zero-click share = AI_impressions / total_impressions.",
    }


def oauth_url_hint(site_url: str = "") -> Dict[str, Any]:
    st = oauth_status()
    st["site_url"] = site_url
    st["token_endpoint"] = "https://oauth2.googleapis.com/token (POST grant_type=refresh_token)"
    st["query_endpoint_template"] = ("https://searchconsole.googleapis.com/v1/urlTestingTools/mobileFriendlyTest:run "
                                     "— use searchanalytics.query: POST /webmasters/v3/sites/{siteUrl}/searchAnalytics/query")
    return st
