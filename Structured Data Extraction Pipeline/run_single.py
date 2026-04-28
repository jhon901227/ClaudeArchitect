"""
run_single.py — Exercise 1: Single-record extraction with tool_use + retry loop.

Run:
  python run_single.py

What you will observe:
  - Claude is forced to call the extract_customer_data tool (tool_choice: any)
  - The response is validated against VALIDATION_SCHEMA
  - If validation fails, the error is injected back into the conversation
    and Claude is asked to retry (multi-turn retry loop)
  - Results are printed and saved to results/single_results.json
"""

import json
import os
import anthropic

from src.extractor import extract_record

DATA_PATH   = "data/raw_records.json"
OUTPUT_PATH = "results/single_results.json"

os.makedirs("results", exist_ok=True)


def main():
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise EnvironmentError("ANTHROPIC_API_KEY environment variable not set.")

    client = anthropic.Anthropic(api_key=api_key)

    with open(DATA_PATH) as f:
        records = json.load(f)

    print(f"\n{'='*60}")
    print("  EXERCISE 1: Single Extraction + Validation-Retry Loop")
    print(f"{'='*60}\n")
    print(f"Processing {len(records)} records one by one...\n")

    all_results = []
    success_count = 0

    for record in records:
        record_id = record["id"]
        raw_text  = record["raw_text"]

        print(f"[{record_id}]")
        result = extract_record(client, record_id, raw_text, verbose=True)
        all_results.append(result)

        if result["success"]:
            success_count += 1
            d = result["data"]
            print(f"      name     : {d.get('full_name')}")
            print(f"      email    : {d.get('email')}")
            print(f"      plan     : {d.get('plan_name')} @ ${d.get('monthly_amount_usd')}/mo")
            print(f"      type     : {d.get('record_type')} | lang: {d.get('language_detected')}")
            print(f"      flags    : {d.get('flags', [])}")
        else:
            print(f"      FAILED   : {result['error']}")
        print()

    # ── Summary ───────────────────────────────────────────────────────────────
    print(f"{'='*60}")
    print(f"  Results: {success_count}/{len(records)} succeeded")

    total_attempts = sum(r.get("attempts", 0) for r in all_results)
    print(f"  Total API calls (incl. retries): {total_attempts}")
    print(f"{'='*60}\n")

    # ── Save ──────────────────────────────────────────────────────────────────
    with open(OUTPUT_PATH, "w") as f:
        json.dump(all_results, f, indent=2, default=str)
    print(f"💾 Full results saved to {OUTPUT_PATH}\n")


if __name__ == "__main__":
    main()