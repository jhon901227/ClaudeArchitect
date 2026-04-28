# Claude Certification Practice — Structured Data Extraction Pipeline

A hands-on project covering every concept in the **"Build a structured data
extraction pipeline"** certification scenario.

---

## What You Will Practice

| Concept | File | Exercise |
|---|---|---|
| `tool_use` with JSON schemas | `src/schemas.py`, `src/extractor.py` | Exercise 1 |
| Validation-retry loops (multi-turn) | `src/extractor.py` | Exercise 1 |
| Optional / nullable field design | `src/schemas.py`, `run_schema_lab.py` | Exercise 3 |
| Message Batches API | `src/batch_processor.py` | Exercise 2 |

---

## Project Structure

```
claude-extraction-pipeline/
├── data/
│   └── raw_records.json        # 8 realistic CRM records (mixed quality)
├── src/
│   ├── schemas.py              # Tool schema + validation schema
│   ├── extractor.py            # Single-record extraction + retry loop
│   └── batch_processor.py     # Batches API submit / poll / retrieve
├── results/                    # Output JSON files (created at runtime)
├── run_single.py               # Exercise 1 — tool_use + retry
├── run_batch.py                # Exercise 2 — Message Batches API
├── run_schema_lab.py           # Exercise 3 — schema design (no API)
├── requirements.txt
└── README.md
```

---

## Setup (Linux VM)

### 1. Clone / create the project

```bash
# If pushing to GitHub first:
git init
git add .
git commit -m "Initial: Claude extraction pipeline"
git remote add origin https://github.com/YOUR_USER/claude-extraction-pipeline.git
git push -u origin main
```

### 2. Create Python virtualenv

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set your API key

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
# To persist across sessions:
echo 'export ANTHROPIC_API_KEY="sk-ant-..."' >> ~/.bashrc
```

---

## Exercises

### Exercise 3 — Schema Lab (START HERE, no API needed)

```bash
python run_schema_lab.py
```

**What happens:** 8 test cases are validated against the schema locally.
You will see which pass and which fail, and WHY. No API calls, no cost.

**What to study:**
- Open `src/schemas.py` and read the comments explaining `required` vs optional.
- Understand the `anyOf: [{type: T}, {type: null}]` pattern for nullable fields.
- Modify a test case in `run_schema_lab.py` to see a new error, then fix it.

**Certification question types you'll be ready for:**
- "Which field definition allows null but not an empty string?"
- "What happens if a required field is missing?"
- "How do you enforce no extra fields in the response?"

---

### Exercise 1 — Single Extraction + Validation-Retry Loop

```bash
python run_single.py
```

**What happens:**
1. Each record is sent to Claude with `tool_choice: {type: any}` → forces a tool call.
2. Claude calls `extract_customer_data` with extracted values.
3. The output is validated with `jsonschema.validate()`.
4. If validation fails → the error is injected back as a `tool_result` with
   `is_error: true` → Claude is asked to retry.
5. Up to 3 attempts per record.

**Watch for these in the output:**
```
[REC-001]
  ↳ Attempt 1/3 for REC-001... ✓ (confidence=high)
      name     : Maria Gonzalez
      email    : maria.g@outlook.com
      plan     : Pro @ $49.0/mo
      flags    : ['open_ticket']
```

**Retry loop anatomy (src/extractor.py):**

```python
# 1. Send message with tools
response = client.messages.create(tools=[TOOL], tool_choice={"type": "any"}, ...)

# 2. Parse tool_use block
tool_use_id, extracted = _parse_tool_use(response)

# 3. Validate
error = _validate(extracted)

# 4. If invalid → append error to conversation and retry
if error:
    messages.append({"role": "assistant", "content": response.content})
    messages.append({
        "role": "user",
        "content": [{"type": "tool_result", "tool_use_id": tool_use_id,
                     "is_error": True, "content": json.dumps(extracted)}]
    })
    messages.append({"role": "user", "content": f"Fix this error: {error}"})
```

**Certification question types you'll be ready for:**
- "What `tool_choice` value forces Claude to always call a tool?"
- "How do you inject a validation error back into a multi-turn conversation?"
- "What is the role of `is_error: true` in a tool_result block?"

---

### Exercise 2 — Message Batches API

```bash
python run_batch.py
```

**What happens:**
1. All 8 records are submitted in ONE `client.messages.batches.create()` call.
2. The script polls `client.messages.batches.retrieve(batch_id)` every 10s.
3. Once `processing_status == "ended"`, results are streamed with
   `client.messages.batches.results(batch_id)`.
4. Each result has a `custom_id` (your record ID) for correlation.

**Expected output:**
```
📤 Submitting batch of 8 requests...
   Batch ID  : msgbatch_01Xy...
   Status    : in_progress

⏳ Polling batch msgbatch_01Xy... every 10s...
   [in_progress] processing=8 | succeeded=0 | errored=0 | expired=0
   [in_progress] processing=3 | succeeded=5 | errored=0 | expired=0
   [ended] processing=0 | succeeded=8 | errored=0 | expired=0
   ✓ Batch complete!

📥 Retrieving results for batch msgbatch_01Xy...
```

**Batch API lifecycle:**
```
submit → in_progress → ended
          ↓
     (poll every N seconds)
          ↓
     retrieve JSONL results
```

**Key Batches API facts for the certification:**
- Endpoint: `POST /v1/messages/batches`
- Each request needs a unique `custom_id` (your correlation key)
- Results are `JSONL` — one JSON object per line
- Processing time: minutes to 24 hours
- Cost: **50% cheaper** than individual calls
- Results expire after **29 days**
- `result.result.type` can be: `"succeeded"`, `"errored"`, `"canceled"`, `"expired"`

---

## Key API Patterns — Quick Reference

### tool_use request
```python
client.messages.create(
    model="claude-sonnet-4-6",
    tools=[{
        "name": "my_tool",
        "description": "...",
        "input_schema": {
            "type": "object",
            "properties": {
                "name":  {"type": "string"},
                "email": {"anyOf": [{"type": "string"}, {"type": "null"}]}  # nullable
            },
            "required": ["name"]   # email is optional
        }
    }],
    tool_choice={"type": "any"},   # forces tool use
    messages=[{"role": "user", "content": "..."}]
)
```

### Parse tool_use from response
```python
for block in response.content:
    if block.type == "tool_use":
        tool_id    = block.id
        tool_input = block.input   # dict matching input_schema
```

### Multi-turn retry after validation failure
```python
# Step 1: append assistant's tool_use turn
messages.append({"role": "assistant", "content": response.content})

# Step 2: return the (invalid) result with is_error=True
messages.append({"role": "user", "content": [{
    "type": "tool_result",
    "tool_use_id": tool_id,
    "content": json.dumps(bad_data),
    "is_error": True
}]})

# Step 3: ask Claude to fix and retry
messages.append({"role": "user", "content": f"Fix: {error_msg}"})
```

### Message Batches API
```python
# Submit
batch = client.messages.batches.create(requests=[
    {"custom_id": "rec-1", "params": { ...messages.create() params... }},
    {"custom_id": "rec-2", "params": { ... }},
])
batch_id = batch.id

# Poll
batch = client.messages.batches.retrieve(batch_id)
batch.processing_status   # "in_progress" | "ended"
batch.request_counts      # .processing .succeeded .errored .expired

# Retrieve results (JSONL streaming)
for result in client.messages.batches.results(batch_id):
    result.custom_id              # your correlation key
    result.result.type            # "succeeded" | "errored" | ...
    result.result.message.content # list of blocks (if succeeded)
```

---

## Schema Design Cheatsheet

```
Required field:
  "required": ["field_name"]

Optional field (can be absent):
  In properties but NOT in required list

Nullable field (present but can be null):
  "field": {"anyOf": [{"type": "string"}, {"type": "null"}]}

Strict mode (no extra fields):
  "additionalProperties": false

Enum constraint:
  "status": {"type": "string", "enum": ["active", "cancelled"]}

Nullable enum:
  "status": {"anyOf": [
    {"type": "string", "enum": ["active", "cancelled"]},
    {"type": "null"}
  ]}
```

---

## Pushing to GitHub

```bash
# Initial push
git init && git add . && git commit -m "feat: extraction pipeline"
git remote add origin https://github.com/YOU/claude-extraction-pipeline.git
git push -u origin main

# After each exercise, commit your changes
git add results/ && git commit -m "results: exercise 1 single extraction"
```

---

## Certification Checklist

- [ ] Can explain what `tool_choice: {type: "any"}` does vs `{type: "auto"}`
- [ ] Can describe the 3-step multi-turn retry pattern
- [ ] Can write a JSON schema with required, optional, and nullable fields
- [ ] Can distinguish `additionalProperties: false` from omitting a field
- [ ] Can explain the Message Batches API lifecycle (submit → poll → retrieve)
- [ ] Can explain when to use Batches vs individual calls
- [ ] Know that batch results expire after 29 days
- [ ] Know that batch requests get 50% cost reduction
- [ ] Can parse `result.result.type` to handle succeeded/errored results