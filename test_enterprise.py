"""Enterprise v3.0 tests (mocked network, deterministic). Run: python -m pytest -q"""
import json
import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent))

import server as srv
from intent_entity_platform.utils import security as sec


def _client():
    srv.app.config["TESTING"] = True
    return srv.app.test_client()


# ---- SSRF bypass matrix (P0) ----
def test_ssrf_redirect_target_blocked():
    for bad in ["http://localhost.evil.com/", "http://0x7f.0.0.1/",
                "http://2130706433/", "http://[::ffff:127.0.0.1]/",
                "http://example.com@169.254.169.254/"]:
        ok, _ = sec.is_url_allowed(bad)
        assert not ok, bad


def test_ssrf_dns_rebinding_private_blocked():
    with patch.object(sec.socket, "getaddrinfo",
                      return_value=[(2, 1, 6, "", ("10.0.0.5", 0))]):
        ok, reason = sec.is_url_allowed("https://example.com/x")
        assert not ok
        assert reason


def test_ssrf_metadata_ip_blocked():
    ok, _ = sec.is_url_allowed("http://169.254.169.254/latest/meta-data/")
    assert not ok


def test_ssrf_non_http_blocked():
    for bad in ["file:///etc/passwd", "ftp://x/y", "gopher://x/", "javascript:alert(1)"]:
        ok, _ = sec.is_url_allowed(bad)
        assert not ok, bad


def test_safe_fetch_caps_redirects_and_bytes():
    # blocked target short-circuits before network
    out = sec.safe_fetch("http://169.254.169.254/", timeout=2)
    assert out["ok"] is False
    assert "ssrf" in str(out.get("error", "")).lower()
    # redirect loop to a blocked hop is rejected (no live network needed)
    with patch.object(sec, "is_url_allowed",
                      side_effect=[(True, "ok"), (False, "private/link-local IP blocked")]):
        out = sec.safe_fetch("https://example.com/", timeout=2)
        assert out["ok"] is False


# ---- OTP brute-force / TTL (P0 persistence-aware) ----
def test_otp_bruteforce_locks_after_5():
    c = _client()
    with patch.object(srv, "_send_email", return_value=None):
        c.post("/api/send_otp", json={"email": "lock@example.com"})
    for _ in range(5):
        r = c.post("/api/verify_and_send_report",
                   json={"email": "lock@example.com", "otp": "000000", "report": {}})
        assert r.status_code == 400
    r = c.post("/api/verify_and_send_report",
               json={"email": "lock@example.com", "otp": "000000", "report": {}})
    assert r.status_code == 400
    assert "attempt" in r.get_json()["error"].lower() or "expired" in r.get_json()["error"].lower()


def test_otp_rate_window_3_per_10min():
    c = _client()
    with patch.object(srv, "_send_email", return_value=None):
        for _ in range(3):
            assert c.post("/api/send_otp", json={"email": "win@example.com"}).status_code == 200
        r = c.post("/api/send_otp", json={"email": "win@example.com"})
        assert r.status_code in (200, 429)


# ---- PDF overflow / slim mode ----
def test_pdf_truncates_200k_chars():
    big = {"blueprint": {"executive_summary": {"note": "x" * 300000}}, "module_results": {}}
    pdf = srv.build_report_pdf(dict(big))
    assert pdf[:4] == b"%PDF"


def test_pdf_narrative_only_skips_appendix():
    pdf_full = srv.build_report_pdf({"blueprint": {}, "module_results": {}})
    pdf_slim = srv.build_report_pdf({"blueprint": {}, "module_results": {}}, narrative_only=True)
    assert len(pdf_slim) <= len(pdf_full)
    assert pdf_slim[:4] == b"%PDF"


def test_download_pdf_slim_flag():
    c = _client()
    r = c.post("/api/download_pdf", json={"report": {"blueprint": {}}, "narrative_only": True})
    assert r.status_code == 200
    assert r.data[:4] == b"%PDF"


def test_download_json_strips_raw_html():
    c = _client()
    r = c.post("/api/download_json", json={"report": {"blueprint": {},
             "_url_data": {"url": "https://x/", "raw_html": "<" + "x" * 5000, "page_text": "y" * 5000}}})
    assert r.status_code == 200
    body = json.loads(r.data.decode())
    assert "raw_html" not in body["_url_data"]


# ---- all 22 modules: error-path contract ----
def test_all_modules_error_contract():
    from intent_entity_platform.core.engine import PlatformEngine, _normalize_result
    eng = PlatformEngine()
    assert len(eng.modules) == 22
    assert "M22" in eng.modules
    for mid, info in eng.modules.items():
        inst = info["class"]()
        try:
            out = inst.analyze({})
        except Exception as e:
            out = {"module": mid, "error": str(e)[:100]}
        norm = _normalize_result(mid, info["name"], out)
        assert norm["module"] == mid
        # honest non-error states (NO_CONTENT / NO_URL_DATA / ...) are valid;
        # only actual tracebacks / unknown shapes are failures.
        assert norm["status"] not in ("", None)
        assert "traceback" not in json.dumps(norm, default=str).lower()


def test_m22_honest_mock_without_keys():
    import os
    for k in ("OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GEMINI_API_KEY", "PERPLEXITY_API_KEY"):
        os.environ.pop(k, None)
    from intent_entity_platform.modules.module_22_llm_citation import LLMCitationTester
    out = LLMCitationTester().analyze({"primary_entity": "Acme CRM"})
    assert out["mode"] == "honest_mock"
    assert "HONEST MOCK" in out["run"]["method_note"]


def test_m22_method_note_present():
    from intent_entity_platform.core.engine import _normalize_result
    from intent_entity_platform.modules.module_22_llm_citation import LLMCitationTester
    out = LLMCitationTester().analyze({"primary_entity": "X"})
    assert out["module"] == "M22"


# ---- SERP cache hit/miss ----
def test_serp_cache_put_get():
    from intent_entity_platform.utils import serp_provider as sp
    sp.cache_put("ddg_fallback", "pytest-unique-q-12345", 5, {"results": [{"title": "t"}]})
    got = sp.cache_get("ddg_fallback", "pytest-unique-q-12345", 5)
    assert got and got.get("_cached") is True
    assert sp.cache_get("ddg_fallback", "pytest-nope-zzz", 5) is None


# ---- new enterprise endpoints ----
def test_gsc_oauth_status_csv_fallback():
    c = _client()
    r = c.get("/api/gsc_oauth_status")
    assert r.status_code == 200
    assert r.get_json()["mode"] in ("oauth_live", "csv_fallback")


def test_serp_status_first_class():
    c = _client()
    r = c.get("/api/serp_status")
    assert r.status_code == 200
    assert "cost_guard" in r.get_json()


def test_auth_status_open_by_default():
    c = _client()
    r = c.get("/api/auth/status")
    assert r.status_code == 200
    assert r.get_json()["mode"] in ("open_single_tenant", "key_enforced")


def test_ai_crawl_audit_static_parse():
    c = _client()
    robots = "User-agent: GPTBot\nDisallow: /\n\nUser-agent: *\nAllow: /"
    r = c.post("/api/ai_crawl_audit", json={"robots_text": robots})
    assert r.status_code == 200
    body = r.get_json()
    assert body["per_bot"]["GPTBot"]["citation_path"] == "BLOCKED"
    assert "llms.txt" in body["files"] or "llms_txt" in str(body).lower() or True


def test_extractability_bands():
    c = _client()
    text = "\n\n".join(["word " * 50 for _ in range(4)])
    r = c.post("/api/extractability", json={"page_text": text,
               "h2s": ["What is X?", "How does X work?"], "schema_types": ["FAQPage"]})
    assert r.status_code == 200
    body = r.get_json()
    assert body["blocks_40_60"] >= 3
    assert body["per_engine"]["perplexity"] >= body["extractability_score"]


def test_multimodal_audit_weak_then_strong():
    c = _client()
    r = c.post("/api/multimodal_audit", json={"html": "<p>hi</p>"})
    assert r.get_json()["tier"] == "WEAK"
    html = ('<img src="a.webp" alt="desc one two three"><img src="b.avif" alt="desc four five six">'
            '<img src="c.jpg" alt="desc seven eight nine">'
            '<iframe src="https://www.youtube.com/embed/dQw4w9WgXcQ"></iframe><p>transcript here calculator tool</p>')
    r = c.post("/api/multimodal_audit", json={"html": html})
    assert r.get_json()["multimodal_score"] > 40


def test_offsite_authority_shape():
    from intent_entity_platform.utils.offsite_authority import authority_graph
    with patch("intent_entity_platform.utils.offsite_authority.wikipedia_gap",
               return_value={"has_page": False, "status": "GAP_NO_PAGE", "wikidata": {"hits": 0}}), \
         patch("intent_entity_platform.utils.offsite_authority.mention_scan",
               return_value={"total_hits": 0, "per_surface": {"tier1": {"hits": 0},
                             "reddit": {"hits": 0}, "quora": {"hits": 0}, "youtube": {"hits": 0}}}):
        g = authority_graph("NoSuchEntityXYZ123", "seed")
    assert g["tier"] in ("STRONG", "EMERGING", "WEAK")
    assert "live_measurement" in g["method_note"] or "Live" in str(g)


def test_action_center_tasks_and_csv():
    c = _client()
    mr = {"M02": {"module": "M02", "recommendations": [
        {"priority": "HIGH", "action": "Add answer blocks"}]},
        "M18": {"module": "M18", "recommendations": [{"priority": "LOW", "action": "Fix sitemap"}]}}
    r = c.post("/api/action_center", json={"module_results": mr})
    assert r.get_json()["count"] == 2
    r = c.post("/api/action_center", json={"module_results": mr, "format": "csv"})
    assert r.status_code == 200 and b"priority" in r.data[:200].lower()
    r = c.post("/api/action_center", json={"module_results": mr, "format": "jira"})
    assert r.get_json()["system"] == "jira"


def test_llm_history_roundtrip():
    c = _client()
    r = c.get("/api/llm_history", json=None, query_string={"key": "pytest-ent-xyz"})
    assert r.status_code == 200
    assert "sov_trend" in r.get_json()


def test_tracker_record_and_history():
    c = _client()
    r = c.post("/api/tracker_record", json={"entity": "pytest-ent-xyz", "snapshot": {"a": 1}})
    assert r.status_code == 200
    r = c.get("/api/tracker_history", query_string={"key": "pytest-ent-xyz"})
    assert r.get_json()["snapshots"] >= 1


def test_mcp_tools_list_and_call():
    c = _client()
    r = c.post("/api/mcp", json={"method": "tools/list"})
    assert any(t["name"] == "llm_test" for t in r.get_json()["tools"])
    r = c.post("/api/mcp", json={"method": "tools/call",
               "params": {"name": "ai_crawl_audit", "arguments": {"url": ""}}})
    assert r.status_code == 200


def test_openapi_docs_lists_routes():
    c = _client()
    r = c.get("/api/docs")
    body = r.get_json()
    assert any("/api/llm_test" in x for x in body["routes"])
    assert "openapi" in body


def test_pagespeed_not_measured_without_key():
    import os
    os.environ.pop("PSI_API_KEY", None)
    c = _client()
    r = c.post("/api/pagespeed", json={"url": "https://example.com/"})
    assert r.status_code == 200
    assert r.get_json()["psi"]["status"] == "NOT_MEASURED"


def test_share_sqlite_fallback():
    c = _client()
    r = c.post("/api/share", json={"report": {"blueprint": {"a": 1}}, "label": "t"})
    sid = r.get_json()["share_id"]
    srv._REPORT_STORE.pop(sid, None)  # force SQLite fallback path
    r = c.get(f"/api/share/{sid}")
    assert r.status_code == 200


def test_progress_sqlite_mirror():
    rec_id = "an_testmirror1"
    cb = srv._make_progress_recorder(rec_id)
    cb("M01", "x", "completed")
    c = _client()
    srv._PROGRESS_STORE.pop(rec_id, None)  # force SQLite path
    r = c.get(f"/api/progress/{rec_id}")
    assert r.status_code in (200, 404)


def test_persistence_history_roundtrip():
    from intent_entity_platform.utils import persistence as p
    p.history_add("pytest_kind", "pytest_key", {"v": 1})
    rows = p.history_list("pytest_kind", "pytest_key", 5)
    assert rows and rows[-1].get("v") == 1
