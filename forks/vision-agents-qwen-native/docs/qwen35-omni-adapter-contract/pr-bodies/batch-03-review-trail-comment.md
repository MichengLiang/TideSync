Review trail note.

Formal approval is unavailable in this single-operator coordinator flow; the independent review evidence is recorded in the repository instead of relying on a separate GitHub approving account.

Review conclusion:

- Scope: Batch 03 is limited to non-interruption server event mapping for response lifecycle, audio done, assistant/user transcripts, response.done usage/search usage, replay tests, batch evidence, and coordinator review records.
- Rationale: The adapter now emits an audio done boundary, maps assistant transcript done to final transcript text, stops using `response.done` as an empty transcript final substitute, and retains raw usage plus `plugins.search` in a test-visible projection.
- Verification: Local evidence records `uv run pytest tests/test_vision_agents_runtime_path.py`, `uv run pytest forks/vision-agents-qwen-native/plugins/qwen/tests`, focused `ruff check`, and focused `ruff format --check`; the independent reviewer returned `APPROVED_WITH_NOTES` for final reviewed HEAD `223cc13`.
- Evidence paths: `forks/vision-agents-qwen-native/docs/qwen35-omni-adapter-contract/reports/batch-03-server-event-mapping-speech-audio-transcript-usage.md`, `forks/vision-agents-qwen-native/docs/qwen35-omni-adapter-contract/reports/batch-03-server-event-mapping-speech-audio-transcript-usage-review.md`, and `forks/vision-agents-qwen-native/docs/qwen35-omni-adapter-contract/coordinator-state.md`.
- Remaining limit: live Qwen smoke remains blocked without API key, cost authorization, and service availability; usage/search projection remains adapter-private for this batch.
- Merge readiness: ready to merge after platform checks remain green.
