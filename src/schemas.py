"""
schemas.py — JSON Schemas for structured data extraction.

CERTIFICATION CONCEPT: Designing schemas with optional/nullable fields.
  - 'required' lists only the truly mandatory fields.
  - Optional fields still appear in 'properties' but are absent from 'required'.
  - Nullable fields use anyOf: [{type: <T>}, {type: "null"}] pattern.
"""

# ─────────────────────────────────────────────
# Schema v1 — Tool Use Input Schema
# Used when calling Claude with tool_use to extract CRM data.
# ─────────────────────────────────────────────
CUSTOMER_EXTRACTION_TOOL = {
    "name": "extract_customer_data",
    "description": (
        "Extract structured customer/lead information from raw CRM text. "
        "Use null for fields that are genuinely absent or ambiguous in the source text."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            # ── REQUIRED fields ─────────────────────
            "record_id": {
                "type": "string",
                "description": "Original record identifier passed in context."
            },
            "extraction_confidence": {
                "type": "string",
                "enum": ["high", "medium", "low"],
                "description": "How confident you are in this extraction overall."
            },
            "record_type": {
                "type": "string",
                "enum": ["customer", "lead", "support_only", "corrupted"],
                "description": "Classification of the record."
            },

            # ── OPTIONAL / NULLABLE contact fields ──
            "full_name": {
                "anyOf": [{"type": "string"}, {"type": "null"}],
                "description": "Full name of the person. Null if not found."
            },
            "email": {
                "anyOf": [{"type": "string", "format": "email"}, {"type": "null"}],
                "description": "Primary email address. Null if not found."
            },
            "phone": {
                "anyOf": [{"type": "string"}, {"type": "null"}],
                "description": "Phone or WhatsApp number as-is in the text. Null if absent."
            },
            "company": {
                "anyOf": [{"type": "string"}, {"type": "null"}],
                "description": "Company or organization name. Null if not mentioned."
            },
            "age": {
                "anyOf": [{"type": "integer", "minimum": 0, "maximum": 120}, {"type": "null"}],
                "description": "Age in years. Null if not mentioned."
            },

            # ── OPTIONAL plan / commercial fields ───
            "plan_name": {
                "anyOf": [{"type": "string"}, {"type": "null"}],
                "description": "Subscription plan name (e.g. Pro, Basic, Enterprise). Null if unknown."
            },
            "monthly_amount_usd": {
                "anyOf": [{"type": "number", "minimum": 0}, {"type": "null"}],
                "description": "Monthly billing amount in USD. Null if not specified."
            },
            "renewal_date": {
                "anyOf": [{"type": "string"}, {"type": "null"}],
                "description": "Renewal or expiry date as found in text. Null if absent."
            },
            "account_status": {
                "anyOf": [
                    {"type": "string", "enum": ["active", "cancelled", "pending", "unknown"]},
                    {"type": "null"}
                ],
                "description": "Current account status derived from context."
            },

            # ── OPTIONAL metadata ───────────────────
            "language_detected": {
                "type": "string",
                "enum": ["en", "es", "zh", "other"],
                "description": "Primary language of the source text."
            },
            "flags": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of notable flags: e.g. 'upsell_opportunity', 'open_ticket', 'no_contact_info'.",
                "default": []
            },
            "extraction_notes": {
                "anyOf": [{"type": "string"}, {"type": "null"}],
                "description": "Brief notes on ambiguities or assumptions made during extraction."
            }
        },
        "required": [
            "record_id",
            "extraction_confidence",
            "record_type",
            "language_detected"
        ]
    }
}


# ─────────────────────────────────────────────
# Schema v2 — Validation Schema (jsonschema library)
# Used AFTER extraction to validate the tool output.
# This is the retry-loop trigger.
# ─────────────────────────────────────────────
VALIDATION_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "required": ["record_id", "extraction_confidence", "record_type", "language_detected"],
    "properties": {
        "record_id":             {"type": "string", "minLength": 1},
        "extraction_confidence": {"type": "string", "enum": ["high", "medium", "low"]},
        "record_type":           {"type": "string", "enum": ["customer", "lead", "support_only", "corrupted"]},
        "language_detected":     {"type": "string", "enum": ["en", "es", "zh", "other"]},
        "full_name":             {"anyOf": [{"type": "string"}, {"type": "null"}]},
        "email":                 {"anyOf": [{"type": "string"}, {"type": "null"}]},
        "phone":                 {"anyOf": [{"type": "string"}, {"type": "null"}]},
        "company":               {"anyOf": [{"type": "string"}, {"type": "null"}]},
        "age":                   {"anyOf": [{"type": "integer", "minimum": 0}, {"type": "null"}]},
        "plan_name":             {"anyOf": [{"type": "string"}, {"type": "null"}]},
        "monthly_amount_usd":    {"anyOf": [{"type": "number", "minimum": 0}, {"type": "null"}]},
        "renewal_date":          {"anyOf": [{"type": "string"}, {"type": "null"}]},
        "account_status":        {
            "anyOf": [
                {"type": "string", "enum": ["active", "cancelled", "pending", "unknown"]},
                {"type": "null"}
            ]
        },
        "flags": {
            "type": "array",
            "items": {"type": "string"}
        },
        "extraction_notes":      {"anyOf": [{"type": "string"}, {"type": "null"}]}
    },
    "additionalProperties": False
}