# Capable 55

Capable 55 is a long-term system for building a body that seldom limits a chosen life.

> **North Star:** Be ready to say yes to strength, endurance, power, gymnastics, mobility, balance, coordination and real-world adventure without the body becoming the reason to decline.

## The model

```text
chat or voice -> raw observation -> append-only record -> GitHub history -> review -> evidence-backed decision
```

**Chat and voice interfaces are the cockpit. GitHub is the persistent memory. Raw observations are the truth.** Models and interfaces may change. The history, evidence and decision trail must survive them.

## Architecture

| Path | Role |
|---|---|
| [`PROFILE.md`](PROFILE.md) | Stable background, goals, constraints and principles |
| [`SCORECARD.md`](SCORECARD.md) | Current baseline, historical references, directions and test protocols |
| [`measurements.csv`](measurements.csv) | Append-only structured measurement ledger |
| [`training/README.md`](training/README.md) | Training-log data contract for people and AI agents |
| `training/sessions.jsonl` | Canonical append-only workout ledger, created with the first real session |
| [`plans/2026-Q3-rebuild.md`](plans/2026-Q3-rebuild.md) | Current assessment and rebuild phase |
| [`reviews/2026-08-baseline.md`](reviews/2026-08-baseline.md) | Baseline interpretation and decision record |
| [`research/evidence.md`](research/evidence.md) | Research rationale, confidence, gaps and change protocol |
| [`AGENTS.md`](AGENTS.md) | Rules for any agent that reads or changes this repository |

## Data hierarchy

When records disagree, preserve each record and label its origin. Do not silently choose the convenient value.

1. **Measured:** captured directly by a defined test or device.
2. **Reported:** stated by Henrik or imported from a named source.
3. **Derived:** calculated from measured or reported inputs; the formula and inputs must remain visible.
4. **Interpretation:** a review-time judgement, never a replacement for the observation.
5. **Decision:** a dated choice based on observations, interpretation and evidence.

`TBD` means the information is missing. It is not zero, false or permission to infer.

## Operating rules

- Read this file, `PROFILE.md`, `SCORECARD.md`, the current plan and the latest review before advising or logging.
- Preserve raw wording when a conversational report becomes structured data.
- Append measurements and training events. Correct mistakes with a new amendment record.
- Use ISO 8601 dates. Use an explicit timezone for timestamps; the working default is `Europe/Stockholm`.
- Store canonical units alongside the reported wording. Record any conversion as derived.
- Cite the evidence base before making a substantive program change.
- Keep historical performances as references, not automatic near-term targets.
- Mark missing prescriptions, protocols and results `TBD`; never fill gaps from plausibility.
- Exclude sensitive medical or mental-health information unless Henrik explicitly asks to record a specific item.
- Keep the repository useful without any particular model, app or provider.

## Operating cycle

1. Capture what happened in the cockpit.
2. Append the raw report and its structured representation.
3. Review trends on an 8–12 week horizon, or sooner when the data justify it.
4. Compare interpretation with the evidence base.
5. Record the decision and its reason in a dated review.
6. Change the plan only after the decision is recorded.

## Measurement ledger contract

Each `measurements.csv` row is either an `observation` or an `amendment`. An observation leaves `target_record_id` blank. A correction appends a new `amendment` row, points `target_record_id` at the earlier row, supplies the corrected fields and states the reason in `notes`. The original row stays unchanged. Blank cells mean unknown or not applicable; they never mean zero.

## Current state

The repository began on 2026-08-30 with a reported baseline and historical references. Exact measurement dates, several test protocols, the first training ledger entry and the detailed rebuild prescription remain `TBD`.
