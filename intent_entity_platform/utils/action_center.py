"""Action Center (P1): insight -> assignable tasks. Closes the loop AirOps-style.

Converts any analysis result (module_results + blueprints) into tasks with
priority / effort / owner / engine-impact, exportable to CSV and to
Jira/Linear-shaped JSON. Includes a GA4 revenue-attribution stub (no key
needed; honest NOT_CONFIGURED state). Stdlib only.
"""
import csv
import io
from typing import Any, Dict, List

_PRIORITY_RANK = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
_EFFORT_MAP = {"CRITICAL": "M", "HIGH": "M", "MEDIUM": "S", "LOW": "XS"}


def build_tasks(module_results: Dict[str, Any], max_tasks: int = 40) -> List[Dict[str, Any]]:
    tasks: List[Dict[str, Any]] = []
    for mid, mr in (module_results or {}).items():
        if not isinstance(mr, dict):
            continue
        recs = mr.get("recommendations") or mr.get("specific_recommendations") or []
        if isinstance(recs, dict):
            recs = [recs]
        for r in recs[:6]:
            if isinstance(r, dict):
                title = str(r.get("action") or r.get("title") or r.get("recommendation") or "")[:180]
                pri = str(r.get("priority", "MEDIUM")).upper()
            else:
                title, pri = str(r)[:180], "MEDIUM"
            if not title:
                continue
            if pri not in _PRIORITY_RANK:
                pri = "MEDIUM"
            tasks.append({
                "id": f"{mid}-{len(tasks) + 1:02d}",
                "module": mid,
                "title": title,
                "priority": pri,
                "effort": _EFFORT_MAP[pri],
                "owner": "Content" if mid in ("M02", "M03", "M06", "M11", "M14") else
                         "Engineering" if mid in ("M10", "M16", "M18", "M21") else
                         "SEO",
                "status": "todo",
                "engine_impact": ("GEO" if mid in ("M02", "M09", "M11", "M22") else
                                  "SEO+GEO" if mid in ("M01", "M03", "M13") else "SEO"),
            })
    tasks.sort(key=lambda t: (_PRIORITY_RANK[t["priority"]], t["module"]))
    seen, dedup = set(), []
    for t in tasks:
        k = t["title"].lower()[:80]
        if k in seen:
            continue
        seen.add(k)
        dedup.append(t)
    return dedup[:max_tasks]


def to_csv(tasks: List[Dict[str, Any]]) -> str:
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=["id", "module", "title", "priority",
                                        "effort", "owner", "status", "engine_impact"])
    w.writeheader()
    for t in tasks:
        w.writerow({k: t.get(k, "") for k in w.fieldnames})
    return buf.getvalue()


def to_issue_tracker(tasks: List[Dict[str, Any]], system: str = "jira") -> List[Dict[str, Any]]:
    out = []
    for t in tasks:
        if system == "linear":
            out.append({"title": f"[{t['id']}] {t['title']}",
                        "priority": {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}[t["priority"]],
                        "labels": [t["module"], t["engine_impact"], t["effort"]]})
        else:
            out.append({"fields": {
                "summary": f"[{t['id']}] {t['title']}",
                "priority": {"name": t["priority"].capitalize()},
                "labels": [t["module"], t["engine_impact"], f"effort-{t['effort']}"],
                "assignee": {"name": t["owner"]},
                "description": f"Module {t['module']} | Engine impact: {t['engine_impact']} | Effort: {t['effort']}"}})
    return out


def ga4_attribution_stub() -> Dict[str, Any]:
    import os
    configured = bool(os.environ.get("GA4_PROPERTY_ID"))
    return {"status": "CONFIGURED" if configured else "NOT_CONFIGURED",
            "property": os.environ.get("GA4_PROPERTY_ID", ""),
            "method_note": ("Tie tasks to revenue via GA4 Data API (conversions by landing page) + "
                            "Shopify orders if configured; otherwise attach UTM + expected CTR lift manually.")
            if configured else
            "Set GA4_PROPERTY_ID (+ service JSON) to enable revenue tie-out. Tasks still export without it."}
