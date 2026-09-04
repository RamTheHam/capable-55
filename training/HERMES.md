# Hermes → GitHub logging procedure

This is the operational contract for logging Capable 55 training by voice through Hermes.

## Goal

Henrik should be able to speak naturally after a session. Hermes converts that report into a structured event, appends it to the canonical ledger, commits it, pushes it to GitHub, verifies the remote result, and only then says that the session is saved.

GitHub is the persistent source of truth. Voice is only an input surface.

## Required flow

1. Capture Henrik's exact words as `source.raw_text`.
2. Resolve relative dates using `Europe/Stockholm` and the actual report time. Never guess a date if the wording is ambiguous.
3. Extract only explicit facts. Unknown values remain `null` or `[]`.
4. Read `training/README.md` and the complete `training/sessions.jsonl` ledger if it exists.
5. Build one proposed event that conforms to `training/session.schema.json` and the rules in `training/README.md`.
6. Preserve provenance (`reported`, `measured`, `derived`) in `field_sources`.
7. Generate or preserve a stable `source.source_event_id` when the voice platform provides one. If none exists, the append tool creates an idempotency key from stable event content.
8. Use `training/tools/append_session.py` to append the event. Never hand-edit an earlier JSONL line.
9. Run the ledger validation built into the append tool.
10. Commit the append with a message such as `Log session 2026-09-05`.
11. Push to the configured GitHub remote.
12. Verify the remote branch contains the new commit or appended record.
13. Only after remote verification tell Henrik: `Saved to Capable 55 as <record_id>.`

## Failure semantics

Hermes must distinguish four states clearly:

- **Parsed, not written** — the voice report was understood but no local append occurred.
- **Written locally, not committed** — the ledger changed but Git did not commit it.
- **Committed locally, not pushed** — the record is safe on the local machine but not yet in GitHub.
- **Verified in GitHub** — the append is remotely persistent and may be called `saved`.

Never say `saved`, `logged`, `done`, or equivalent if the remote verification did not succeed.

If push fails, do not create a second session record on retry. Retry the existing commit/push first. Idempotency checks should prevent accidental duplicate appends.

## Voice interaction rule

Do not make Henrik fill in a form. Accept conversational reports such as:

> CrossFit today, about an hour. Back squats were 5x5 at 100. Session felt like a 7. Right shoulder was fine, maybe 1 out of 10.

Ask a follow-up only when an ambiguity materially changes the record or training interpretation. Missing non-critical fields stay unknown.

## Corrections

If Henrik later says a prior value was wrong, append an amendment event. Never rewrite the original event.

Example:

> Correction: yesterday's class was 50 minutes, not 60.

Hermes should identify the target record, create an amendment, append it, commit, push, verify, and report the amendment ID.

## Minimum confirmation to Henrik

After a successful remote write, keep confirmation short:

`Saved to Capable 55 as session-YYYY-MM-DD-NN. RPE/duration/etc. left unknown where you didn't report them.`

If something failed, state exactly which persistence stage failed and what remains safe.
