"""
run_batch.py — Exercise 2: Batch processing with the Message Batches API.

Run:
  python run_batch.py

What you will observe:
  - All 8 records are submitted in ONE API call
  - The batch is polled until processing_status == "ended"
  - Results are streamed back as JSONL and parsed
  - Summary table is printed

KEY DIFFERENCE from Exercise 1:
  - No per-record validation-retry loop (batches are fire-and-forget)
  - 50% cost reduction vs. individual calls (Anthropic pricing perk)
  - Async: you submit now, results come later (good for pipelines / cron jobs)

For production, you'd save the batch_id to a database, then retrieve results
in a separate job after the batch completes (up to 24 hours window).
"""

import json
import os
from typing import List

import anthropic

from src.batch_processor import run_batch_pipeline

DATA_PATH   = "data/raw_records.json"
OUTPUT_PATH = "results/batch_results.json"

os.makedirs("results", exist_ok=True)


def print_summary(results: List[dict]):
    print(f"\n{'='*60}")
    print("  BATCH RESULTS SUMMARY")
    print(f"{'='*60}")

    succeeded = [r for r in results if r["success"]]
    failed    = [r for r in results if not r["success"]]

    print(f"  Succeeded : {len(succeeded)}/{len(results)}")
    print(f"  Failed    : {len(failed)}/{len(results)}")
    print()

    print(f"  {'ID':<10} {'TYPE':<14} {'NAME':<22} {'EMAIL':<28} {'PLAN'}")
    print(f"  {'-'*9} {'-'*13} {'-'*21} {'-'*27} {'-'*12}")

    for r in results:
        rid = r["record_id"]
        if r["success"]:
            d     = r["data"]
            rtype = d.get("record_type", "?")
            name  = (d.get("full_name") or "—")[:21]
            email = (d.get("email")     or "—")[:27]
            plan  = d.get("plan_name") or "—"
            print(f"  {rid:<10} {rtype:<14} {name:<22} {email:<28} {plan}")
        else:
            print(f"  {rid:<10} {'ERROR':<14} {r['error'][:60]}")

    print(f"{'='*60}\n")


def main():
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise EnvironmentError("ANTHROPIC_API_KEY environment variable not set.")

    client = anthropic.Anthropic(api_key=api_key)

    with open(DATA_PATH) as f:
        records = json.load(f)

    print(f"\n{'='*60}")
    print("  EXERCISE 2: Message Batches API")
    print(f"{'='*60}")

    results = run_batch_pipeline(client, records, output_path=OUTPUT_PATH)
    print_summary(results)


if __name__ == "__main__":
    main()