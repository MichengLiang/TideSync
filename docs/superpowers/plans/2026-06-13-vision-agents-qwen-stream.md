# Vision Agents Qwen Stream Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a TideSync Python Vision-Agents entrypoint that runs Qwen3.5-Omni-Flash-Realtime through Stream Video and opens Stream's hosted demo UI.

**Architecture:** TideSync exposes a focused `tidesync.agent` module containing configuration helpers, `create_agent`, `join_call`, `runner`, and a CLI `main`. The package `__init__` only re-exports those stable entrypoints, while `.env` carries local secrets and `.env.example` documents required variables.

**Tech Stack:** Python 3.13, uv, Vision-Agents 0.6.4, `vision-agents-plugins-qwen`, `vision-agents-plugins-getstream`, python-dotenv, pytest, ruff, pnpm/biome for existing TypeScript checks.

---

### Task 1: Configuration Tests

**Files:**
- Modify: `tests/test_hello.py`
- Later modify: `src/tidesync/agent.py`

- [x] **Step 1: Write failing tests**

Replace placeholder hello/greet tests with tests for `RealtimeSettings`, default China Mainland DashScope endpoint, and runner export.

- [x] **Step 2: Run tests to verify failure**

Run: `uv run pytest tests/test_hello.py -q`
Expected: FAIL because `tidesync.agent` does not exist.

### Task 2: Agent Module

**Files:**
- Create: `src/tidesync/agent.py`
- Modify: `src/tidesync/__init__.py`

- [x] **Step 1: Implement minimal agent configuration**

Create a typed settings dataclass, env parsing helpers, `create_agent`, `join_call`, `runner`, and `main`.

- [x] **Step 2: Export agent entrypoints**

Update `src/tidesync/__init__.py` to export `RealtimeSettings`, `create_agent`, `join_call`, `main`, and `runner`.

- [x] **Step 3: Run unit tests**

Run: `uv run pytest tests/test_hello.py -q`
Expected: PASS without connecting to Qwen or Stream.

### Task 3: Project Configuration And Secrets

**Files:**
- Modify: `pyproject.toml`
- Modify: `.gitignore`
- Create: `.env.example`
- Create local ignored file: `.env`

- [x] **Step 1: Add dependencies and scripts**

Add `python-dotenv`, `vision-agents[qwen,getstream]`, `tidesync-agent` script, and `[tool.vision-agents.agent]`.

- [x] **Step 2: Harden ignored files**

Ignore `.env`, Python cache, coverage, `.venv`, and uv cache.

- [x] **Step 3: Add `.env.example`**

Document required environment variables with placeholders only.

- [x] **Step 4: Add local `.env`**

Use the provided DashScope and Stream credentials locally. Do not track this file.

### Task 4: Verification And Smoke

**Files:**
- No new files expected.

- [x] **Step 1: Run Python tests**

Run: `uv run pytest`

- [x] **Step 2: Run Python lint**

Run: `uv run ruff check .`

- [x] **Step 3: Run TypeScript checks**

Run: `pnpm lint`, `pnpm typecheck`, and `pnpm test`.

- [x] **Step 4: Run import smoke**

Run an import/config smoke that avoids network calls.

- [x] **Step 5: Attempt real hosted demo smoke**

Run `uv run tidesync-agent run --call-id tidesync-qwen-smoke --log-level INFO` and inspect whether the Stream hosted demo URL opens or is logged. Stop the process after confirming startup behavior.
