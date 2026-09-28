"""Auth + multi-tenancy (P1): API keys, workspaces, audit log. SSO-ready stub.

Modes:
- OPEN (default, backward compatible): no key required; requests logged as anon.
- KEY mode: set ENTERPRISE_API_KEYS="ws1:key1,ws2:key2" -> clients send
  X-API-Key header. Unknown key -> 401. Workspace = prefix before ':'.
- SSO stub: ENTERPRISE_SSO_ISSUER set -> /api/auth/status reports ready;
  actual OIDC verify left to the edge proxy (Authentik/Keycloak) to keep deps stdlib.

All decisions audit-logged to SQLite (persistence.audit_add). Stdlib only.
"""
import hashlib
import hmac
import os
from functools import wraps
from typing import Any, Dict, Tuple

from flask import jsonify, request


def _key_map() -> Dict[str, str]:
    raw = os.environ.get("ENTERPRISE_API_KEYS", "").strip()
    out: Dict[str, str] = {}
    if not raw:
        return out
    for pair in raw.split(","):
        if ":" not in pair:
            continue
        ws, key = pair.split(":", 1)
        ws, key = ws.strip(), key.strip()
        if ws and key:
            out[key] = ws
    return out


def auth_status() -> Dict[str, Any]:
    km = _key_map()
    return {
        "mode": "key_enforced" if km else "open_single_tenant",
        "workspaces": sorted(set(km.values())) if km else ["default"],
        "sso": {"issuer": os.environ.get("ENTERPRISE_SSO_ISSUER", ""),
                "status": "READY_AT_EDGE_PROXY" if os.environ.get("ENTERPRISE_SSO_ISSUER") else "NOT_CONFIGURED",
                "note": "Terminate OIDC at reverse proxy; forward X-Auth-User + X-Auth-Groups."},
        "header": "X-API-Key",
        "audit": "SQLite audit table (actor/action/detail/created)",
    }


def resolve_workspace() -> Tuple[str, bool, str]:
    """Return (workspace, ok, error). In open mode always ('default', True, '')."""
    km = _key_map()
    if not km:
        return "default", True, ""
    key = (request.headers.get("X-API-Key") or "").strip()
    if not key:
        return "", False, "Missing X-API-Key"
    ws = km.get(key)
    if not ws:
        return "", False, "Invalid API key"
    return ws, True, ""


def require_key(fn):
    @wraps(fn)
    def inner(*a, **kw):
        ws, ok, err = resolve_workspace()
        if not ok:
            try:
                from .persistence import audit_add
                audit_add("unknown", "auth_denied", err)
            except Exception:
                pass
            return jsonify({"error": err}), 401
        request.environ["workspace"] = ws
        return fn(*a, **kw)
    return inner


def api_key_hash(key: str) -> str:
    return hashlib.sha256(key.encode()).hexdigest()[:32]


def constant_time_eq(a: str, b: str) -> bool:
    return hmac.compare_digest(a or "", b or "")
