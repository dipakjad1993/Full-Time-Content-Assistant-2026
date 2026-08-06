"""
CLI Interface for the Intent, Entity & Semantic Intelligence Platform.
"""
import sys
import os
import json
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from intent_entity_platform.core.engine import PlatformEngine
from intent_entity_platform.core.input_framework import (
    InputFramework, SeedKeywordInput, FirstPartyData, SMEAsset,
    BrandConstraints, AudienceProfile, TechnicalCredentials
)


def build_framework_from_args(args) -> InputFramework:
    """Build InputFramework from CLI arguments."""
    framework = InputFramework()
    framework.seed = SeedKeywordInput(
        seed_phrase=args.seed,
        primary_entity=args.entity,
        target_locale=args.locale,
        target_device=args.device,
        secondary_keywords=args.secondary_keywords.split(",") if args.secondary_keywords else [],
    )
    framework.brand = BrandConstraints(
        brand_name=args.brand,
        voice_profile=args.voice,
        regulated_words=args.regulated_words.split(",") if args.regulated_words else [],
        do_not_say_terms=args.do_not_say.split(",") if args.do_not_say else [],
    )
    framework.audience = AudienceProfile(
        funnel_stage=args.funnel,
        knowledge_floor=args.knowledge_level,
        technical_depth=args.depth,
    )
    framework.technical = TechnicalCredentials(
        render_mode=args.render_mode,
        js_framework=args.framework,
        cdn_provider=args.cdn,
    )
    if args.sme_notes:
        for note in args.sme_notes.split("|"):
            asset = SMEAsset(content=note.strip(), expert_name="SME", expert_title="Expert")
            framework.first_party.sme_assets.append(asset)
    return framework


def progress_callback(module_id, module_name, status):
    """Print progress updates."""
    status_icon = "ok" if status == "completed" else ("err" if "error" in status else "...")
    print(f"  [{module_id}] {module_name}: {status_icon}")


def main():
    parser = argparse.ArgumentParser(
        description="Intent, Entity & Semantic Intelligence Platform - 21-Module Content Analysis Engine",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m intent_entity_platform --seed "best enterprise B2B SaaS accounting software" --entity "multi-currency accounting" --brand "Acme Corp"
  python -m intent_entity_platform --seed "AI-powered analytics platform" --entity "predictive analytics" --funnel middle --locale en-GB
        """
    )
    parser.add_argument("--seed", required=True, help="Primary seed keyword/phrase")
    parser.add_argument("--entity", required=True, help="Primary entity definition")
    parser.add_argument("--brand", default="Default Brand", help="Brand name")
    parser.add_argument("--locale", default="en-US", help="Target locale (e.g., en-US, en-GB, de-DE)")
    parser.add_argument("--device", default="desktop", choices=["desktop", "mobile", "tablet"])
    parser.add_argument("--funnel", default="middle", choices=["top", "middle", "bottom"])
    parser.add_argument("--knowledge-level", default="intermediate", choices=["beginner", "intermediate", "advanced", "expert", "c-suite"])
    parser.add_argument("--depth", default="moderate", choices=["shallow", "moderate", "deep", "expert"])
    parser.add_argument("--voice", default="authoritative", choices=["authoritative", "conversational", "academic", "casual", "technical", "journalistic"])
    parser.add_argument("--secondary-keywords", help="Comma-separated secondary keywords")
    parser.add_argument("--regulated-words", help="Comma-separated regulated words")
    parser.add_argument("--do-not-say", help="Comma-separated banned terms")
    parser.add_argument("--sme-notes", help="SME notes separated by |")
    parser.add_argument("--render-mode", default="ssr", choices=["ssr", "csr", "isr", "ssg"])
    parser.add_argument("--framework", default="", choices=["", "react", "nextjs", "angular", "vue", "nuxt"])
    parser.add_argument("--cdn", default="", choices=["", "cloudflare", "fastly", "akamai", "cloudfront"])
    parser.add_argument("--output", "-o", default="blueprint", help="Output directory name")
    parser.add_argument("--json-only", action="store_true", help="Output JSON only (no summary)")
    parser.add_argument("--quiet", "-q", action="store_true", help="Suppress progress output")

    args = parser.parse_args()

    print("\n" + "=" * 70)
    print("  INTENT, ENTITY & SEMANTIC INTELLIGENCE PLATFORM")
    print("  21-Module Content Analysis Engine v1.0")
    print("=" * 70)
    print(f"\nSeed Keyword: {args.seed}")
    print(f"Primary Entity: {args.entity}")
    print(f"Brand: {args.brand}")
    print(f"Locale: {args.locale}")
    print(f"Funnel Stage: {args.funnel}")
    print(f"Knowledge Level: {args.knowledge_level}")
    print()

    framework = build_framework_from_args(args)
    errors = framework.validate_all()
    if errors:
        print("VALIDATION ERRORS:")
        for field, errs in errors.items():
            for err in errs:
                print(f"  - {field}: {err}")
        sys.exit(1)

    engine = PlatformEngine()
    print("Executing 21-module analysis pipeline...")
    print()

    cb = None if args.quiet else progress_callback
    results = engine.run_analysis(framework, progress_callback=cb)

    print()
    print(f"Modules completed: {results['modules_completed']}/{results['total_modules']}")
    if results['errors']:
        print(f"Modules with errors: {results['modules_failed']}")
        for mid, err in results['errors'].items():
            print(f"  [{mid}] {err[:80]}")
    print()

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    json_path = output_dir / "blueprint.json"
    engine.output_pipeline.export_json(results["blueprint"], str(json_path))
    print(f"JSON blueprint saved: {json_path}")

    results_path = output_dir / "full_results.json"
    with open(results_path, 'w', encoding='utf-8') as f:
        json.dump(results["module_results"], f, indent=2, ensure_ascii=False, default=str)
    print(f"Full results saved: {results_path}")

    if not args.json_only:
        summary_path = output_dir / "blueprint_summary.txt"
        summary = engine.output_pipeline.export_summary(results["blueprint"])
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write(summary)
        print(f"Summary saved: {summary_path}")
        print()
        print(summary)

    print()
    print("Analysis complete.")


if __name__ == "__main__":
    main()
