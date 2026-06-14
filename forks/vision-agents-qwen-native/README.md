# Vision Agents Qwen Native Controlled Source

This directory is TideSync-controlled source for the Vision Agents runtime packages used by the Qwen realtime agent path.

Runtime packages:

- `agents-core` provides `vision_agents.core`.
- `plugins/qwen` provides `vision_agents.plugins.qwen`.
- `plugins/getstream` provides `vision_agents.plugins.getstream`.

The source baseline is GetStream Vision Agents `v0.6.4`, commit `9c5efe1ef4552efacef83de90a6b4870e2444c7b`. Source provenance and import scope are recorded in `UPSTREAM.adoc`.

This directory establishes a reviewable runtime source boundary. It does not implement the complete Qwen3.5 Omni Realtime WebSocket adapter contract. Adapter behavior work remains governed by `docs/bookshelf/books/09-qwen35-omni-realtime-websocket-adapter-contract/book.adoc`.

Repository discipline for this controlled fork is defined in `GOVERNANCE.md`. PR evidence and change acceptance rules are copied into `团队仓库的 PR 留痕与变更接纳工作流.md`.
