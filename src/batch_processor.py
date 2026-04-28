"""
batch_processor.py — Batch extraction using the Anthropic Message Batches API.

CERTIFICATION CONCEPTS COVERED:
  - Message Batches API: submit many requests in one call, poll for completion,
    retrieve results as JSONL.
  - Each batch request gets a custom_id for result correlation.
  - Batch jobs are async: you submit, wait, then retrieve.

WHEN TO USE BATCHES VS SINGLE CALLS:
  - Batches: large volumes, cost matters (50% cheaper), latency not critical.
  - Single calls: real-time UX, need results immediately.
"""

import json
import time
import anthropic
from typing import List, Optional
from anthropic.types.messages import MessageBatch

from src.schemas import CUSTOMER_EXTRACTION_TOOL

MODEL      = "claude-sonnet-4-6"
MAX_TOKENS = 1024
POLL_INTERVAL_S = 10   # seconds between status checks


# ── Build one batch request per record ───────────────────────────────────────

def _build_batch_request(record_id: str, raw_text: str) -> dict:
    """
    Each batch request follows the same structure as a normal messages.create()
    call, wrapped with a custom_id for later correlation.
    """
    return {
        "custom_id": record_id,
        "params": {
            "model": MODEL,
            "max_tokens": MAX_TOKENS,
            "system": (
                "You are a precise data extraction assistant. "
                "Always use the provided tool. Use null for absent optional fields."
            ),
            "tools": [CUSTOMER_EXTRACTION_TOOL],
            "tool_choice": {"type": "any"},
            "messages": [
                {
                    "role": "user",
                    "content": (
                        f"Extract structured customer data from this CRM record.\n"
                        f"Record ID: {record_id}\n\nRaw text:\n{raw_text}"
                    )
                }
            ]
        }
    }


# ── Submit batch ──────────────────────────────────────────────────────────────

def submit_batch(client: anthropic.Anthropic, records: List[dict]) -> str:
    """
    Submit all records as a single Message Batch.
    Returns the batch_id to poll later.
    """
    requests = [
        _build_batch_request(r["id"], r["raw_text"])
        for r in records
    ]

    print(f"\n📤 Submitting batch of {len(requests)} requests...")
    batch = client.messages.batches.create(requests=requests)

    print(f"   Batch ID  : {batch.id}")
    print(f"   Status    : {batch.processing_status}")
    print(f"   Created   : {batch.created_at}")
    return batch.id


# ── Poll until done ───────────────────────────────────────────────────────────

def wait_for_batch(client: anthropic.Anthropic, batch_id: str) -> MessageBatch:
    """
    Poll the batch status until it reaches 'ended'.
    Prints a progress line on each poll.
    """
    print(f"\n⏳ Polling batch {batch_id} every {POLL_INTERVAL_S}s...")
    while True:
        batch = client.messages.batches.retrieve(batch_id)
        counts = batch.request_counts

        print(
            f"   [{batch.processing_status}] "
            f"processing={counts.processing} | "
            f"succeeded={counts.succeeded} | "
            f"errored={counts.errored} | "
            f"expired={counts.expired}"
        )

        if batch.processing_status == "ended":
            print("   ✓ Batch complete!")
            return batch

        time.sleep(POLL_INTERVAL_S)


# ── Retrieve and parse results ────────────────────────────────────────────────

def retrieve_batch_results(
    client: anthropic.Anthropic,
    batch_id: str
) -> List[dict]:
    """
    Stream the JSONL results and extract tool_use outputs.
    Returns a list of dicts with keys: record_id, success, data / error.
    """
    results = []
    print(f"\n📥 Retrieving results for batch {batch_id}...")

    for result in client.messages.batches.results(batch_id):
        record_id = result.custom_id

        if result.result.type == "succeeded":
            message = result.result.message
            # Find the tool_use block
            extracted = None
            for block in message.content:
                if block.type == "tool_use":
                    extracted = block.input
                    break

            if extracted:
                results.append({
                    "record_id": record_id,
                    "success":   True,
                    "data":      extracted
                })
            else:
                results.append({
                    "record_id": record_id,
                    "success":   False,
                    "error":     "No tool_use block in response"
                })

        elif result.result.type == "errored":
            results.append({
                "record_id": record_id,
                "success":   False,
                "error":     str(result.result.error)
            })
        else:
            results.append({
                "record_id": record_id,
                "success":   False,
                "error":     f"Unexpected result type: {result.result.type}"
            })

    return results


# ── Convenience: run full batch pipeline ─────────────────────────────────────

def run_batch_pipeline(
    client: anthropic.Anthropic,
    records: List[dict],
    output_path: Optional[str] = None
) -> List[dict]:
    """
    End-to-end: submit → poll → retrieve → (optionally save).
    """
    batch_id = submit_batch(client, records)
    wait_for_batch(client, batch_id)
    results = retrieve_batch_results(client, batch_id)

    if output_path:
        with open(output_path, "w") as f:
            json.dump(results, f, indent=2, default=str)
        print(f"\n💾 Results saved to {output_path}")

    return results