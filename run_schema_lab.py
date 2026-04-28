"""
run_schema_lab.py — Exercise 3: Schema Design & Validation Lab

Run:
  python run_schema_lab.py

PURPOSE:
  Practice designing schemas with optional/nullable fields and understand
  how jsonschema validation works before connecting to the real API.

  This is a ZERO-API-CALL exercise — great for understanding the concepts
  without spending credits.

CONCEPTS DEMONSTRATED:
  - required vs optional fields
  - nullable fields via anyOf: [{type: T}, {type: null}]
  - enum constraints
  - additionalProperties: false (strict mode)
  - What valid and invalid data looks like
"""

import json
import jsonschema
from src.schemas import VALIDATION_SCHEMA

# ─────────────────────────────────────────────────────────────────────────────
# Test cases: a mix of valid and intentionally broken records
# ─────────────────────────────────────────────────────────────────────────────

TEST_CASES = [
    {
        "label": "✅ VALID — full record",
        "data": {
            "record_id": "REC-001",
            "extraction_confidence": "high",
            "record_type": "customer",
            "language_detected": "en",
            "full_name": "Maria Gonzalez",
            "email": "maria.g@outlook.com",
            "phone": "+57 312 4567890",
            "company": None,                  # ← null is fine for optional field
            "age": 34,
            "plan_name": "Pro",
            "monthly_amount_usd": 49.0,
            "renewal_date": "2025-03-15",
            "account_status": "active",
            "flags": ["open_ticket"],
            "extraction_notes": None
        }
    },
    {
        "label": "✅ VALID — minimal (only required fields)",
        "data": {
            "record_id": "REC-008",
            "extraction_confidence": "low",
            "record_type": "support_only",
            "language_detected": "en"
            # All optional fields are simply absent — perfectly valid
        }
    },
    {
        "label": "✅ VALID — corrupted record with nulls",
        "data": {
            "record_id": "REC-005",
            "extraction_confidence": "low",
            "record_type": "corrupted",
            "language_detected": "other",
            "full_name": None,
            "email": None,
            "plan_name": None,
            "monthly_amount_usd": None,
            "flags": ["no_contact_info"],
            "extraction_notes": "Record appears corrupted, no usable data."
        }
    },
    {
        "label": "❌ INVALID — missing required field 'record_id'",
        "data": {
            "extraction_confidence": "high",
            "record_type": "customer",
            "language_detected": "en"
        }
    },
    {
        "label": "❌ INVALID — bad enum value for record_type",
        "data": {
            "record_id": "REC-X",
            "extraction_confidence": "high",
            "record_type": "prospect",      # ← not in enum
            "language_detected": "en"
        }
    },
    {
        "label": "❌ INVALID — age is a string instead of integer",
        "data": {
            "record_id": "REC-X",
            "extraction_confidence": "medium",
            "record_type": "lead",
            "language_detected": "es",
            "age": "34"                      # ← should be integer or null
        }
    },
    {
        "label": "❌ INVALID — extra field not in schema (strict mode)",
        "data": {
            "record_id": "REC-X",
            "extraction_confidence": "medium",
            "record_type": "lead",
            "language_detected": "en",
            "unknown_field": "surprise"      # ← additionalProperties: false
        }
    },
    {
        "label": "❌ INVALID — account_status uses wrong enum value",
        "data": {
            "record_id": "REC-X",
            "extraction_confidence": "high",
            "record_type": "customer",
            "language_detected": "en",
            "account_status": "inactive"    # ← valid values: active/cancelled/pending/unknown
        }
    }
]


# ─────────────────────────────────────────────────────────────────────────────
# Runner
# ─────────────────────────────────────────────────────────────────────────────

def validate_case(label: str, data: dict):
    try:
        jsonschema.validate(instance=data, schema=VALIDATION_SCHEMA)
        result = "PASS ✓"
        detail = ""
    except jsonschema.ValidationError as e:
        result = "FAIL ✗"
        path   = " → ".join(str(p) for p in e.path) or "root"
        detail = f"  Path: {path}\n  Error: {e.message}"

    print(f"\n{label}")
    print(f"  Result: {result}")
    if detail:
        print(detail)


def explain_schema_design():
    print("\n" + "="*60)
    print("  SCHEMA DESIGN NOTES")
    print("="*60)
    notes = """
  1. REQUIRED vs OPTIONAL
     ─────────────────────
     Fields in 'required' must always be present.
     Fields only in 'properties' (not in 'required') can be omitted entirely.

     required: ["record_id", "extraction_confidence", "record_type", "language_detected"]
     Optional: full_name, email, phone, company, age, plan_name, etc.

  2. NULLABLE FIELDS
     ────────────────
     Use anyOf to allow both a real value OR null:

       "email": {
         "anyOf": [
           {"type": "string"},
           {"type": "null"}
         ]
       }

     This is DIFFERENT from the field being absent (optional).
     Nullable means the field IS present but explicitly set to null.

  3. STRICT MODE
     ────────────
     "additionalProperties": false
     Rejects any field not declared in 'properties'.
     Forces Claude to stay within the schema — no surprise keys.

  4. ENUM CONSTRAINTS
     ─────────────────
     Enum values must match EXACTLY (case-sensitive).
     Wrong: "Inactive", "ACTIVE", "prospect"
     Right: "active", "cancelled", "pending", "unknown"

  5. RETRY LOOP TRIGGER
     ────────────────────
     When jsonschema.validate() raises ValidationError,
     inject the error message back into the conversation
     and ask Claude to call the tool again with corrections.
     Limit retries to 2-3 to avoid infinite loops.
"""
    print(notes)


def main():
    print("\n" + "="*60)
    print("  EXERCISE 3: Schema Design & Validation Lab")
    print("  (no API calls — pure schema practice)")
    print("="*60)

    for case in TEST_CASES:
        validate_case(case["label"], case["data"])

    explain_schema_design()

    print("\n" + "="*60)
    print("  CHALLENGE: modify a test case above to introduce a new")
    print("  validation error, then fix the schema to allow it.")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()