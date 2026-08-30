# Training log specification

The training log is an append-only event stream. A person or AI agent may translate a conversational report into structured data, but the raw report remains beside that translation.

## Canonical ledger

Store real training events in `training/sessions.jsonl`, one compact JSON object per line. Create the file with the first real session. Do not place examples, comments, Markdown or blank lines in it.

JSONL was chosen because each event can contain several exercises, symptoms and device metrics without flattening them into ambiguous CSV columns. Appending one line does not rewrite earlier sessions. Standard JSON keeps the ledger independent of any model or vendor.

## Invariants

1. Read this specification and the full ledger before assigning an ID.
2. Append exactly one new line for each session or amendment. Never edit, reorder or delete an earlier line.
3. Preserve the user's source words verbatim in `source.raw_text`.
4. Do not infer an exercise variant, start time, result, unit, symptom timing or intensity.
5. Use JSON `null` for one unknown scalar and `[]` for no reported items. Never use zero to mean unknown.
6. Use ISO 8601 dates and timestamps. Timestamps must include an offset. Default timezone: `Europe/Stockholm`.
7. Resolve relative dates such as “today” against the user's local date at the time of the report. Mark that field `derived` and state the basis.
8. Store numbers as JSON numbers. Use canonical unit fields; keep the original wording in `raw_text`.
9. Label every material field or object as `measured`, `reported` or `derived` through `field_sources`.
10. Record corrections as amendment events. The ledger history is never silently cleaned up.
11. Do not add sensitive medical or mental-health detail unless Henrik explicitly asks for that specific detail to be recorded.
12. End every write by parsing every JSONL line and reporting the appended `record_id`.

## Session record

Every session line uses these top-level fields. Optional scalar fields still appear with `null`; arrays still appear as arrays.

| Field | Type | Rule |
|---|---|---|
| `schema_version` | string | Required; currently `1.0` |
| `record_type` | string | Required; `session` |
| `record_id` | string | Required; `session-YYYY-MM-DD-NN` |
| `session_date` | string or null | Local ISO date on which training occurred |
| `recorded_at` | string | ISO timestamp with UTC offset |
| `timezone` | string | IANA name, normally `Europe/Stockholm` |
| `source` | object | Required provenance and verbatim report |
| `title` | string or null | Short reported/neutral label |
| `modalities` | array of strings | Lowercase `snake_case`; do not infer unreported modalities |
| `started_at` | string or null | ISO timestamp with offset; null unless known |
| `duration_min` | number or null | Total reported duration |
| `session_rpe` | number or null | 0–10 only when reported |
| `activities` | array | Structured work performed |
| `symptoms` | array | Non-diagnostic sensations reported for this session |
| `metrics` | array | Device or test observations |
| `notes` | string or null | Relevant detail that has no better field |
| `field_sources` | object | JSON Pointer keys mapped to provenance records |

### Source object

```json
{
  "interface": "voice",
  "agent": "Hermes",
  "reporter": "Henrik",
  "raw_text": "The exact words received from Henrik"
}
```

Allowed `interface` values are `chat`, `voice`, `manual_import` and `other`. Agent names are labels, not dependencies.

### Activity object

```json
{
  "activity_id": "a01",
  "category": "strength",
  "name": "squat",
  "variant": null,
  "efforts": [
    {
      "sets": 5,
      "reps": 5,
      "load_value": 100,
      "load_unit": "kg",
      "distance_m": null,
      "duration_sec": null,
      "result": null,
      "rpe": null
    }
  ],
  "notes": null
}
```

Allowed `category` values are `strength`, `conditioning`, `skill`, `power`, `mobility`, `balance`, `recovery`, `adventure` and `other`. `name` should use a plain stable term. Keep `variant` null when the report says “squats” but does not say back, front or another variant.

Use additional effort objects when sets, loads or results differ. Do not compress changing loads into a false single value.

### Symptom object

```json
{
  "area": "shoulder",
  "side": null,
  "rating": 2,
  "scale_max": 10,
  "timing": null,
  "quality": null,
  "effect_on_session": null,
  "notes": null
}
```

This records the user's observation without diagnosing it. `timing`, `side` and `effect_on_session` remain null unless stated.

### Metric object

```json
{
  "name": "average_heart_rate",
  "value": 142,
  "unit": "bpm",
  "provenance": "measured",
  "device": "TBD",
  "notes": null
}
```

Allowed provenance values are `measured`, `reported` and `derived`. A derived value needs its formula or conversion basis in `notes` or `field_sources`.

### Field-source object

Keys are JSON Pointers to the field or object they describe.

Cover every non-null observation that is not self-evident administrative metadata. Schema normalisation is `derived`: for example, converting “squats” to the stable name `squat` or classifying it as `strength`. The raw wording remains the audit trail.

```json
{
  "/session_date": {
    "kind": "derived",
    "basis": "Resolved 'today' using Europe/Stockholm at recorded_at"
  },
  "/duration_min": {
    "kind": "reported",
    "basis": "source.raw_text"
  },
  "/activities/0/name": {
    "kind": "derived",
    "basis": "Normalised the reported plural 'squats' to the stable name 'squat'"
  },
  "/activities/0/efforts/0": {
    "kind": "reported",
    "basis": "source.raw_text"
  }
}
```

## Deterministic ID rule

For a known session date, scan existing session records for that date and use the next two-digit ordinal: `session-2026-08-30-01`, then `session-2026-08-30-02`. Amendments use `amendment-YYYY-MM-DD-NN`, with the ordinal based on the amendment's local recorded date.

If the session date is unknown, use `session-unknown-YYYYMMDD-NN`, based on the recorded date, and keep `session_date` null. Never guess a date to make the ID prettier.

## Example conversion, not a real session

Input:

> CrossFit today, 60 minutes, squats 5x5 at 100 kg, shoulder felt 2/10

Assuming the report arrived on 2026-08-30 in Stockholm, an agent would append one physical JSON line equivalent to the formatted example below:

```json
{
  "schema_version": "1.0",
  "record_type": "session",
  "record_id": "session-2026-08-30-01",
  "session_date": "2026-08-30",
  "recorded_at": "2026-08-30T18:15:00+02:00",
  "timezone": "Europe/Stockholm",
  "source": {
    "interface": "voice",
    "agent": "Hermes",
    "reporter": "Henrik",
    "raw_text": "CrossFit today, 60 minutes, squats 5x5 at 100 kg, shoulder felt 2/10"
  },
  "title": "CrossFit",
  "modalities": ["crossfit"],
  "started_at": null,
  "duration_min": 60,
  "session_rpe": null,
  "activities": [
    {
      "activity_id": "a01",
      "category": "strength",
      "name": "squat",
      "variant": null,
      "efforts": [
        {
          "sets": 5,
          "reps": 5,
          "load_value": 100,
          "load_unit": "kg",
          "distance_m": null,
          "duration_sec": null,
          "result": null,
          "rpe": null
        }
      ],
      "notes": null
    }
  ],
  "symptoms": [
    {
      "area": "shoulder",
      "side": null,
      "rating": 2,
      "scale_max": 10,
      "timing": null,
      "quality": null,
      "effect_on_session": null,
      "notes": null
    }
  ],
  "metrics": [],
  "notes": null,
  "field_sources": {
    "/session_date": {
      "kind": "derived",
      "basis": "Resolved 'today' using Europe/Stockholm at recorded_at"
    },
    "/duration_min": {
      "kind": "reported",
      "basis": "source.raw_text"
    },
    "/title": {
      "kind": "reported",
      "basis": "source.raw_text"
    },
    "/modalities/0": {
      "kind": "reported",
      "basis": "Normalised the reported label 'CrossFit' to lowercase"
    },
    "/activities/0/category": {
      "kind": "derived",
      "basis": "Schema classification of the reported squat work"
    },
    "/activities/0/name": {
      "kind": "derived",
      "basis": "Normalised the reported plural 'squats' to the stable name 'squat'"
    },
    "/activities/0/efforts/0": {
      "kind": "reported",
      "basis": "source.raw_text"
    },
    "/symptoms/0": {
      "kind": "reported",
      "basis": "source.raw_text"
    }
  }
}
```

The timestamp is illustrative. A real record must use the actual append time. The example does not assume the squat variant, shoulder side or symptom timing.

## Amendments and corrections

Never change the original session. Append an RFC 6902-style amendment event:

```json
{
  "schema_version": "1.0",
  "record_type": "amendment",
  "record_id": "amendment-2026-08-31-01",
  "recorded_at": "2026-08-31T09:00:00+02:00",
  "timezone": "Europe/Stockholm",
  "target_record_id": "session-2026-08-30-01",
  "reason": "Henrik corrected the duration",
  "operations": [
    {
      "op": "replace",
      "path": "/duration_min",
      "value": 65,
      "provenance": "reported"
    }
  ],
  "source": {
    "interface": "chat",
    "agent": "ChatGPT",
    "reporter": "Henrik",
    "raw_text": "Correction: it was 65 minutes"
  }
}
```

Consumers build the current view by applying valid amendments in ledger order. An amendment may correct or void a record, but the original line stays intact.

## Agent write checklist

- Confirm the report describes a real session, not an example or plan.
- Identify only explicit facts; leave every other scalar null.
- Resolve the date and record any derivation.
- Assign the next deterministic ID after scanning the ledger.
- Preserve the exact source words.
- Append one compact JSON line.
- Parse the complete ledger and check record IDs are unique.
- Report the appended ID and any fields left unknown.
