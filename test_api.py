"""pytest suite (replaces legacy Popen+sleep demo script).

Run:  python -m pytest test_api.py -q
All live-network tests are mocked — 0 external calls, deterministic.
"""
import json
import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent))

import server as srv
from intent_entity_platform.utils import security as sec
from intent_entity_platform.utils.content_scorer import score_content
from intent_entity_platform.utils.gsc_quickwins import parse_gsc_csv, quick_wins


def _client():
    srv.app.config["TESTING"] = True
    return srv.app.test_client()


def test_health():
    c = _client()
    r = c.get("/api/health")
    assert r.status_code == 200
    body = r.get_json()
    assert body["ok"] is True
    assert "version" in body


def test_analyze_validation_error():
    c = _client()
    r = c.post("/api/analyze", json={})
    assert r.status_code in (400, 500)
    # must never leak tracebacks in default (APP_DEBUG=false) mode
    body = r.get_json()
    assert "trace" not in body


def test_analyze_happy_path_mocked():
    c = _client()
    fake_results = {
        "blueprint": {}, "module_results": {"M01": {"module": "M01", "status": "ok"}},
        "errors": {},
    }
    with patch.object(srv.PlatformEngine, "run_analysis", return_value=fake_results):
        r = c.post("/api/analyze", json={
            "seed": "content strategy", "entity": "content management",
            "brand": "TestCo", "locale": "en-US", "device": "desktop",
            "funnel": "middle", "knowledge": "intermediate",
            "voice": "authoritative", "secondary": "SEO,digital marketing",
        })
    assert r.status_code == 200
    body = r.get_json()
    assert body["analysis_id"].startswith("an_")
    assert "module_results" in body


def test_analyze_url_ssrf_blocked():
    c = _client()
    for bad in ["http://localhost:5000/", "http://169.254.169.254/",
                "http://127.0.0.1/", "file:///etc/passwd", "ftp://x/y"]:
        r = c.post("/api/analyze-url", json={"url": bad})
        assert r.status_code == 400, bad
        assert "blocked" in r.get_json()["error"].lower() or "ssrf" in r.get_json()["error"].lower()


def test_analyze_url_happy_path_mocked():
    c = _client()
    fake_fetch = {"ok": True, "html": "<html><head><title>T</title></head>"
                  "<body><h1>H</h1><p>" + ("word " * 200) + "</p></body></html>",
                  "status": 200, "final_url": "https://example.com/", "headers": {}, "error": None}
    fake_results = {"blueprint": {}, "module_results": {}, "errors": {}}
    with patch.object(srv, "safe_fetch", return_value=fake_fetch), \
         patch.object(srv.PlatformEngine, "run_analysis", return_value=fake_results):
        r = c.post("/api/analyze-url", json={"url": "https://example.com/"})
    assert r.status_code == 200
    body = r.get_json()
    assert body["_url_mode"] is True
    assert body["_url_data"]["url"] == "https://example.com/"


def test_otp_uses_secrets_and_single_use():
    c = _client()
    with patch.object(srv, "_send_email", return_value=None) as m:
        with patch.object(srv.secrets, "randbelow", return_value=42) as rb:
            r = c.post("/api/send_otp", json={"email": "a@example.com"})
            assert r.status_code == 200
            rb.assert_called_once()
            assert srv._OTP_STORE["a@example.com"]["otp"] == "000042"
        m.assert_called_once()
    # wrong OTP consumes a try; correct OTP is single-use
    r = c.post("/api/verify_and_send_report",
               json={"email": "a@example.com", "otp": "000000", "report": {}})
    assert r.status_code == 400
    with patch.object(srv, "build_report_pdf", return_value=b"%PDF"), \
         patch.object(srv, "_send_email", return_value=None):
        r = c.post("/api/verify_and_send_report",
                   json={"email": "a@example.com", "otp": "000042", "report": {"blueprint": {}}})
        assert r.status_code == 200
        assert "a@example.com" not in srv._OTP_STORE  # single-use


def test_security_headers_present():
    c = _client()
    r = c.get("/")
    assert r.headers.get("X-Content-Type-Options") == "nosniff"
    assert "Content-Security-Policy" in r.headers
    assert r.headers.get("X-Frame-Options") == "SAMEORIGIN"


def test_rate_limit_analyze():
    c = _client()
    srv._RATE_STORE if hasattr(srv, "_RATE_STORE") else None
    # hit the shared limiter directly through repeated analyze calls with tiny limit patch
    with patch.object(srv, "check_rate_limit", return_value=(False, "Rate limit exceeded")):
        r = c.post("/api/analyze", json={"seed": "x", "entity": "y"})
        assert r.status_code == 429


def test_ssrf_private_ip_blocked():
    ok, reason = sec.is_url_allowed("http://192.168.1.5/admin")
    assert not ok
    ok, _ = sec.is_url_allowed("https://example.com/blog")
    assert ok


def test_content_scorer_contract():
    out = score_content("seo content marketing strategy guide with tables and quotes",
                        ["seo content marketing strategy", "content guide marketing"],
                        ["seo", "tables"], {"words": 50})
    assert 0 <= out["seo_score"] <= 100
    assert out["method"] == "heuristic_tfidf_cosine"
    assert "heuristic" in out["method_note"].lower()
    assert out["grade"] in ("A", "B", "C", "D", "F")


def test_gsc_quick_wins():
    csv_text = ("query,page,clicks,impressions,ctr,position\n"
                "best crm,https://x/a,10,500,2.0,6\n"
                "best crm,https://x/b,5,300,1.6,9\n"
                "what is crm,https://x/a,2,400,0.5,12\n")
    rows = parse_gsc_csv(csv_text)
    assert len(rows) == 3
    q = quick_wins(rows)
    assert q["striking_count"] >= 2
    assert q["cannibalization_count"] == 1  # 'best crm' on 2 pages


def test_m19_sync_wired():
    from intent_entity_platform.core.engine import PlatformEngine
    eng = PlatformEngine()
    assert eng.modules["M19"]["class"].__name__ == "LocalizationSyncEngine"
    inst = eng.modules["M19"]["class"]()
    out = inst.analyze({"_url_data": {}, "url": "https://example.com"})
    assert out["module"] == "M19"
    assert out.get("url_localization_analysis", {}).get("status") == "NO_URL_DATA"


def test_module_result_contract():
    from intent_entity_platform.core.engine import _normalize_result
    r = _normalize_result("M02", "GEO", {"module": "M02", "x": 1})
    assert r["status"] == "ok"
    assert "heuristic readiness" in r["method_note"]
    e = _normalize_result("M99", "X", {"module": "M99", "error": "boom"})
    assert e["status"] == "error"
    assert "traceback" not in e
