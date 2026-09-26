# Load Test Results

**Date:** 2026-09-26
**Target:** `http://localhost:8000` (local deployment, backend `main.py` v2.1.0)
**Tool:** Custom Python script (`concurrent.futures` + `requests`), since `hey`/`ab`/`wrk` were not available in the environment.

## Method

Two endpoints were tested separately, since they have very different cost profiles:

1. **`GET /health`** — lightweight, no LLM call. Used to measure raw API/server overhead.
2. **`POST /api/chat/message`** — real request, triggers an actual Groq `openai/gpt-oss-120b` completion. Kept at low concurrency/volume to avoid unnecessary load on the third-party API.

## Results

### `/health` (20 concurrent, 200 requests)

| Metric | Value |
|---|---|
| Success rate | 200/200 (100%) |
| Wall clock | 0.51s |
| Throughput | 392.4 req/s |
| Latency avg | 37ms |
| Latency p50 / p95 / p99 | 35ms / 71ms / 82ms |

### `/api/chat/message` (5 concurrent, 15 requests, real LLM calls)

| Metric | Value |
|---|---|
| Success rate | 15/15 (100%) |
| Wall clock | 8.28s |
| Throughput | 1.81 req/s |
| Latency avg | 2.41s |
| Latency min / max | 0.62s / 2.93s |
| Latency p50 / p95 / p99 | 2.69s / 2.92s / 2.92s |

## Findings

- No errors, timeouts, or dropped requests at either concurrency level.
- The API/server layer itself is fast (sub-100ms) and not a bottleneck — `/health` throughput of ~390 req/s shows FastAPI + Uvicorn handle concurrent load fine at this scale.
- Chat latency (2-3s) is dominated by the upstream Groq LLM call, not application code. This is expected for an LLM-backed endpoint and is not a defect.
- `ChatService` is already instantiated once as a module-level singleton (`routes/chat.py`), so no per-request client re-creation overhead exists.

## Action taken

No code changes were made as a result of this test — there was nothing broken or inefficient in the request path to fix. This document exists to record what was actually measured, for future comparison if load or model choice changes.

## Suggested follow-ups (not yet implemented)

- If future usage requires higher chat throughput, consider Groq's streaming API (`stream_response`, already present in `groq_client.py` but unused by `chat_service.py`) so the frontend can render partial output instead of waiting for the full 2-3s response.
- Re-run this test against a higher concurrency (e.g., 20+) on `/api/chat/message` before any production deployment, to check behavior under real multi-user load rather than this small local sample.
