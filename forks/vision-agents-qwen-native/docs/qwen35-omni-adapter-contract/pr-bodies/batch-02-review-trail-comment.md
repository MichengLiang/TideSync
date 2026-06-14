Review trail note.

Formal approval is unavailable in this single-operator coordinator flow; the independent review evidence is recorded in the repository instead of relying on a separate GitHub approving account.

Review conclusion:

- Scope: Batch 02 is limited to current input-turn state, video send-permission state, fake/event tests, batch evidence, and coordinator review records.
- Rationale: The adapter no longer uses historical `_audio_emitted_once` as the video gate. Current-turn audio opens image permission, speech stopped, Manual commit/clear, committed events, track reconnect, and image timing errors close or suspend the current image window.
- Verification: Local evidence records `uv run pytest tests/test_vision_agents_runtime_path.py`, `uv run pytest forks/vision-agents-qwen-native/plugins/qwen/tests`, focused `ruff check`, and focused `ruff format --check`; the independent reviewer returned `APPROVED_WITH_NOTES` for final reviewed HEAD `8b5423c`.
- Evidence paths: `forks/vision-agents-qwen-native/docs/qwen35-omni-adapter-contract/reports/batch-02-input-turn-and-video-send-permission-state.md`, `forks/vision-agents-qwen-native/docs/qwen35-omni-adapter-contract/reports/batch-02-input-turn-and-video-send-permission-state-review.md`, and `forks/vision-agents-qwen-native/docs/qwen35-omni-adapter-contract/coordinator-state.md`.
- Remaining limit: live Qwen smoke remains blocked without API key, cost authorization, and service availability; deterministic tests call provider hooks rather than the real `VideoForwarder` timing loop.
- Merge readiness: ready to merge after platform checks remain green.
