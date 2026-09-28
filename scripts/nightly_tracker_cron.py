"""Nightly longitudinal tracker (M09 snapshots + M22 SOV). Cron-safe, keyless-tolerant.

Usage:
  python scripts/nightly_tracker_cron.py --entity "Acme CRM" --vertical b2b_saas
  python scripts/nightly_tracker_cron.py --config intent_entity_platform/data/tracked.json

tracked.json: [{"entity": "...", "seed": "...", "brand": "...", "vertical": "b2b_saas"}]
Writes to SQLite history (kinds: tracker_snapshot, m22). No API keys -> honest
mock rows still recorded with mode flag so charts show coverage gaps, not fake wins.
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from intent_entity_platform.modules.module_22_llm_citation import LLMCitationTester
from intent_entity_platform.utils.persistence import history_add, history_list


def run_entity(entity: str, seed: str = "", brand: str = "", vertical: str = "") -> dict:
    tester = LLMCitationTester()
    out = tester.analyze({"primary_entity": entity, "seed_phrase": seed,
                          "brand": brand or entity, "m22_prompts": 10})
    snap = {"entity": entity, "seed": seed, "brand": brand, "vertical": vertical,
            "mode": out.get("mode"), "sov": out.get("share_of_voice_pct"),
            "providers_live": out.get("providers_live")}
    history_add("tracker_snapshot", entity.lower(), snap)
    return snap


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--entity", default="")
    ap.add_argument("--seed", default="")
    ap.add_argument("--brand", default="")
    ap.add_argument("--vertical", default="b2b_saas")
    ap.add_argument("--config", default="")
    args = ap.parse_args()
    targets = []
    if args.config:
        try:
            targets = json.loads(Path(args.config).read_text(encoding="utf-8"))
        except Exception as e:
            print(f"config error: {e}", file=sys.stderr)
            return 2
    elif args.entity:
        targets = [{"entity": args.entity, "seed": args.seed,
                    "brand": args.brand, "vertical": args.vertical}]
    else:
        print("pass --entity or --config", file=sys.stderr)
        return 2
    for t in targets:
        snap = run_entity(str(t.get("entity", "")), str(t.get("seed", "")),
                          str(t.get("brand", "")), str(t.get("vertical", "")))
        print(json.dumps(snap))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
