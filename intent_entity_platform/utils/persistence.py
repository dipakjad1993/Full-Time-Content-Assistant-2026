"""Enterprise persistence: SQLite-backed OTP / progress / share / history / audit stores.

Replaces in-memory _OTP_STORE / _PROGRESS_STORE / _REPORT_STORE so the app
works correctly under multi-worker gunicorn/waitress. Stdlib only (sqlite3).
Thread-safe via short-lived connections + WAL mode. All tables carry TTL and
are garbage-collected on read/write.

DB path: intent_entity_platform/data/platform.sqlite3 (env PLATFORM_DB override).
"""
import json
import os
import sqlite3
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

_DB_PATH = Path(os.environ.get(
    "PLATFORM_DB",
    str(Path(__file__).parent.parent / "data" / "platform.sqlite3"),
))

_SCHEMA = """
CREATE TABLE IF NOT EXISTS otp(
  email TEXT PRIMARY KEY, otp TEXT NOT NULL, exp REAL NOT NULL,
  tries INTEGER NOT NULL DEFAULT 0, req_count INTEGER NOT NULL DEFAULT 1,
  window_start REAL NOT NULL, created REAL NOT NULL);
CREATE TABLE IF NOT EXISTS progress(
  id TEXT PRIMARY KEY, payload TEXT NOT NULL, started REAL NOT NULL, updated REAL NOT NULL);
CREATE TABLE IF NOT EXISTS shares(
  sid TEXT PRIMARY KEY, payload TEXT NOT NULL, created REAL NOT NULL, label TEXT NOT NULL DEFAULT '');
CREATE TABLE IF NOT EXISTS history(
  id INTEGER PRIMARY KEY AUTOINCREMENT, kind TEXT NOT NULL, key TEXT NOT NULL,
  payload TEXT NOT NULL, created REAL NOT NULL);
CREATE INDEX IF NOT EXISTS idx_history_kind_key ON history(kind, key, created);
CREATE TABLE IF NOT EXISTS audit(
  id INTEGER PRIMARY KEY AUTOINCREMENT, actor TEXT NOT NULL, action TEXT NOT NULL,
  detail TEXT NOT NULL DEFAULT '', created REAL NOT NULL);
CREATE TABLE IF NOT EXISTS workspaces(
  ws TEXT PRIMARY KEY, api_key_hash TEXT NOT NULL, created REAL NOT NULL, label TEXT NOT NULL DEFAULT '');
"""


def _con() -> sqlite3.Connection:
    _DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(str(_DB_PATH), timeout=10, check_same_thread=False)
    try:
        con.execute("PRAGMA journal_mode=WAL")
        con.execute("PRAGMA synchronous=NORMAL")
    except Exception:
        pass
    con.executescript(_SCHEMA)
    return con


# ---- OTP ----
def otp_get(email: str) -> Optional[Dict[str, Any]]:
    con = _con()
    try:
        row = con.execute(
            "SELECT otp, exp, tries, req_count, window_start FROM otp WHERE email=?",
            (email,)).fetchone()
        if not row:
            return None
        otp, exp, tries, req_count, window_start = row
        if time.time() > float(exp):
            con.execute("DELETE FROM otp WHERE email=?", (email,))
            con.commit()
            return None
        return {"otp": otp, "exp": float(exp), "tries": int(tries),
                "req_count": int(req_count), "window_start": float(window_start)}
    finally:
        con.close()


def otp_request(email: str, otp: str, ttl: int = 600,
                max_requests: int = 3, window: int = 600) -> Dict[str, Any]:
    """Create/refresh an OTP record. Returns {ok, error?} honoring rate window."""
    now = time.time()
    con = _con()
    try:
        row = con.execute(
            "SELECT req_count, window_start, exp FROM otp WHERE email=?",
            (email,)).fetchone()
        if row:
            req_count, window_start, exp = int(row[0]), float(row[1]), float(row[2])
            if now - window_start > window:
                req_count, window_start = 0, now
            # still-valid OTP counts toward the window
            if now < float(exp) and req_count >= max_requests:
                return {"ok": False, "error": "Too many OTP requests. Please wait 10 minutes."}
            req_count += 1
            con.execute(
                "REPLACE INTO otp(email,otp,exp,tries,req_count,window_start,created)"
                " VALUES(?,?,?,?,?,?,?)",
                (email, otp, now + ttl, 0, req_count, window_start, now))
        else:
            con.execute(
                "INSERT INTO otp(email,otp,exp,tries,req_count,window_start,created)"
                " VALUES(?,?,?,?,?,?,?)",
                (email, otp, now + ttl, 0, 1, now, now))
        con.commit()
        return {"ok": True}
    finally:
        con.close()


def otp_consume_try(email: str) -> None:
    con = _con()
    try:
        con.execute("UPDATE otp SET tries=tries+1 WHERE email=?", (email,))
        con.commit()
    finally:
        con.close()


def otp_clear(email: str) -> None:
    con = _con()
    try:
        con.execute("DELETE FROM otp WHERE email=?", (email,))
        con.commit()
    finally:
        con.close()


# ---- progress ----
def progress_put(pid: str, payload: Dict[str, Any]) -> None:
    now = time.time()
    con = _con()
    try:
        row = con.execute("SELECT payload, started FROM progress WHERE id=?",
                          (pid,)).fetchone()
        started = json.loads(row[0]).get("started_at", now) if row else now
        payload = dict(payload)
        payload.setdefault("started_at", started)
        con.execute("REPLACE INTO progress(id,payload,started,updated) VALUES(?,?,?,?)",
                    (pid, json.dumps(payload, default=str), started, now))
        # GC stale (>15min)
        con.execute("DELETE FROM progress WHERE updated < ?", (now - 900,))
        con.commit()
    finally:
        con.close()


def progress_get(pid: str) -> Optional[Dict[str, Any]]:
    con = _con()
    try:
        row = con.execute("SELECT payload, updated FROM progress WHERE id=?",
                          (pid,)).fetchone()
        if not row:
            return None
        if time.time() - float(row[1]) > 900:
            con.execute("DELETE FROM progress WHERE id=?", (pid,))
            con.commit()
            return None
        return json.loads(row[0])
    finally:
        con.close()


# ---- shares (versioned links, replaces in-memory _REPORT_STORE) ----
def share_put(sid: str, report: Dict[str, Any], label: str = "") -> None:
    con = _con()
    try:
        con.execute("REPLACE INTO shares(sid,payload,created,label) VALUES(?,?,?,?)",
                    (sid, json.dumps(report, default=str)[:5_000_000],
                     time.time(), label[:120]))
        cnt = con.execute("SELECT COUNT(*) FROM shares").fetchone()[0]
        if cnt > 500:
            con.execute("DELETE FROM shares WHERE sid IN "
                        "(SELECT sid FROM shares ORDER BY created ASC LIMIT ?)",
                        (cnt - 500,))
        con.commit()
    finally:
        con.close()


def share_get(sid: str) -> Optional[Dict[str, Any]]:
    con = _con()
    try:
        row = con.execute("SELECT payload, label, created FROM shares WHERE sid=?",
                          (sid,)).fetchone()
        if not row:
            return None
        return {"report": json.loads(row[0]), "label": row[1], "created": row[2]}
    finally:
        con.close()


# ---- longitudinal history (M09 tracker, M22 citation runs) ----
def history_add(kind: str, key: str, payload: Dict[str, Any]) -> int:
    con = _con()
    try:
        cur = con.execute(
            "INSERT INTO history(kind,key,payload,created) VALUES(?,?,?,?)",
            (kind, key[:240], json.dumps(payload, default=str)[:500_000],
             time.time()))
        con.commit()
        return int(cur.lastrowid)
    finally:
        con.close()


def history_list(kind: str, key: str, limit: int = 90) -> List[Dict[str, Any]]:
    con = _con()
    try:
        rows = con.execute(
            "SELECT payload, created FROM history WHERE kind=? AND key=? "
            "ORDER BY created DESC LIMIT ?",
            (kind, key[:240], max(1, min(int(limit), 500)))).fetchall()
        out = []
        for payload, created in rows:
            try:
                d = json.loads(payload)
            except Exception:
                d = {"_raw": payload}
            d["_captured_at"] = created
            out.append(d)
        return list(reversed(out))  # chronological
    finally:
        con.close()


def audit_add(actor: str, action: str, detail: str = "") -> None:
    con = _con()
    try:
        con.execute("INSERT INTO audit(actor,action,detail,created) VALUES(?,?,?,?)",
                    (actor[:160], action[:160], detail[:2000], time.time()))
        con.commit()
    finally:
        con.close()


def db_path() -> str:
    return str(_DB_PATH)
