# Instructions for AI agents

This repository is the persistent source of truth for Capable 55. Chat and voice are input surfaces, not memory.

## Read first

Read `README.md`, `PROFILE.md`, `SCORECARD.md`, the current file in `plans/`, the latest dated file in `reviews/`, `training/README.md` and the relevant part of `research/evidence.md` before acting.

## Rules

- Preserve history. Append new observations; do not silently rewrite or delete earlier records.
- Distinguish `measured`, `reported` and `derived` data. Derived values must name their inputs and calculation.
- Never invent a measurement, date, protocol, prescription, test result or symptom. Use `TBD` in prose and `null`/blank fields where the data contract requires them.
- Use ISO 8601 dates. Include a UTC offset and IANA timezone for timestamps; default to `Europe/Stockholm` only when appropriate.
- Preserve the raw conversational wording when creating a structured training record.
- Follow `training/README.md` exactly. Add corrections as amendment events; never edit an existing JSONL line.
- Treat `measurements.csv` as append-only. Use a new unique `record_id` for each observation or correction.
- Keep historical results as references, not proof of current readiness or automatic targets.
- Cite `research/evidence.md` and the underlying source for substantive program changes. Record the decision in a dated review.
- State uncertainty and evidence strength. Personal response can change a program decision without changing what a paper found.
- Do not add sensitive medical or mental-health information unless Henrik explicitly requests that specific record.
- Keep all formats and instructions model/provider-independent. Do not require Hermes, ChatGPT, Claude or any vendor-specific feature.
- Before committing, validate CSV shape, parse every JSONL record if the ledger exists, check links/paths, and review the diff for invented facts.

## Commit discipline

Use a clear imperative commit message. Report which observations were appended, which decisions changed and which fields remain unknown.
