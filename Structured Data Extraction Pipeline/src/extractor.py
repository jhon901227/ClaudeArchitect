"""
extractor.py — Single-record extraction with tool_use + validation-retry loop.

CERTIFICATION CONCEPTS COVERED:
  1. tool_use: Send a tool definition, parse the tool_use block from the response.
  2. Validation-retry loop: validate extracted JSON; if it fails, re-call Claude
     with the validation error injected into the conversation (multi-turn).
  3. Optional/nullable fields: handled naturally via the schema in schemas.py.
"""

import json
import time
import anthropic
import jsonschema
from typing import Dict, List, Optional

from src.schemas import CUSTOMER_EXTRACTION_TOOL, VALIDATION_SCHEMA

# ── Constants ─────────────────────────────────────────────────────────────────
MODEL          = "claude-sonnet-4-6"
MAX_TOKENS     = 1024
MAX_RETRIES    = 3          # how many times to retry on validation failure
RETRY_DELAY_S  = 1.0       # polite pause between retries


# ── Helpers ───────────────────────────────────────────────────────────────────

def _build_user_message(record_id: str, raw_text: str) -> dict:
    """Build the initial user message for extraction."""
    return {
        "role": "user",
        "content": (
            f"Extract structured customer data from the following CRM record.\n"
            f"Record ID: {record_id}\n\n"
            f"Raw text:\n{raw_text}\n\n"
            f"Use the extract_customer_data tool. Set null for any field that "
            f"cannot be reliably determined from the text."
        )
    }


def _build_retry_message(tool_use_id: str, tool_result: dict, error_message: str) -> List[Dict]:
    """
    Build the multi-turn messages needed to retry after a validation failure.

    The Anthropic API expects:
      assistant → tool_use block
      user      → tool_result block (with the error)
      user      → new instruction to fix and retry
    """
    return [
        # Return the (invalid) tool result so the conversation stays valid
        {
            "role": "user",
            "content": [
                {
                    "type": "tool_result",
                    "tool_use_id": tool_use_id,
                    "content": json.dumps(tool_result),
                    "is_error": True
                }
            ]
        },
        # Ask Claude to fix and re-call the tool
        {
            "role": "user",
            "content": (
                f"The extracted data failed validation with this error:\n{error_message}\n\n"
                f"Please call extract_customer_data again with corrected values. "
                f"Ensure all required fields are present and all enum values are exact matches."
            )
        }
    ]


def _parse_tool_use(response: anthropic.types.Message) -> Optional[tuple]:
    """
    Pull the tool_use block out of the response.
    Returns (tool_use_id, extracted_dict) or None if no tool call was made.
    """
    for block in response.content:
        if block.type == "tool_use":
            return block.id, block.input
    return None


def _validate(data: dict) -> Optional[str]:
    """
    Validate extracted data against VALIDATION_SCHEMA.
    Returns an error message string if invalid, None if valid.
    """
    try:
        jsonschema.validate(instance=data, schema=VALIDATION_SCHEMA)
        return None
    except jsonschema.ValidationError as e:
        return f"Field '{e.path[-1] if e.path else 'root'}': {e.message}"
    except jsonschema.SchemaError as e:
        return f"Schema definition error: {e.message}"


# ── Main extraction function ──────────────────────────────────────────────────

def extract_record(
    client: anthropic.Anthropic,
    record_id: str,
    raw_text: str,
    verbose: bool = True
) -> dict:
    """
    Extract structured data from a single raw text record.

    Implements:
      - tool_use call
      - jsonschema validation
      - multi-turn retry loop (up to MAX_RETRIES)

    Returns a result dict with keys:
      success, attempts, data (if success), error (if failed)
    """
    messages = [_build_user_message(record_id, raw_text)]
    attempt  = 0
    last_error = None

    while attempt < MAX_RETRIES:
        attempt += 1

        if verbose:
            print(f"  ↳ Attempt {attempt}/{MAX_RETRIES} for {record_id}...", end=" ")

        # ── API call with tool_use ────────────────────────────────────────────
        response = client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            tools=[CUSTOMER_EXTRACTION_TOOL],
            tool_choice={"type": "any"},          # force tool use
            messages=messages,
            system=(
                "You are a precise data extraction assistant. "
                "Always use the provided tool. Never skip required fields. "
                "Use null (not empty string) for absent optional fields."
            )
        )

        # ── Parse tool response ───────────────────────────────────────────────
        result = _parse_tool_use(response)
        if result is None:
            last_error = "Claude did not call the tool."
            if verbose:
                print(f"✗ (no tool call)")
            # Append assistant response and ask again
            messages.append({"role": "assistant", "content": response.content})
            messages.append({
                "role": "user",
                "content": "You must call the extract_customer_data tool. Please try again."
            })
            time.sleep(RETRY_DELAY_S)
            continue

        tool_use_id, extracted = result

        # ── Validate ──────────────────────────────────────────────────────────
        validation_error = _validate(extracted)

        if validation_error is None:
            if verbose:
                print(f"✓ (confidence={extracted.get('extraction_confidence', '?')})")
            return {
                "success":  True,
                "attempts": attempt,
                "data":     extracted
            }

        # ── Validation failed → set up retry ──────────────────────────────────
        last_error = validation_error
        if verbose:
            print(f"✗ Validation failed: {validation_error}")

        # Append the assistant tool_use turn to conversation history
        messages.append({"role": "assistant", "content": response.content})
        # Append error feedback turns
        messages.extend(_build_retry_message(tool_use_id, extracted, validation_error))
        time.sleep(RETRY_DELAY_S)

    # ── All retries exhausted ─────────────────────────────────────────────────
    if verbose:
        print(f"  ✗ All {MAX_RETRIES} attempts failed for {record_id}.")
    return {
        "success":  False,
        "attempts": attempt,
        "error":    last_error
    }