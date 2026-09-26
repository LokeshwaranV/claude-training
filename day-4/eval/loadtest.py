"""Locust load-test script for the Agentic RAG query API (Step 16).

k6-vs-locust: AIDLC_PLAN.md's Step 16 calls for "k6 or JMeter" — k6 was not
installed and would require adding an external APT repo (a system-level
change), so locust (pure-Python, pip-installable into the project venv) was
substituted instead, per the same "load testing scripts against the query
API" spirit.

## How to re-run

    pip install -r requirements.txt   # includes locust
    # with the backend already running at http://127.0.0.1:8000:
    locust -f eval/loadtest.py --headless -u 10 -r 2 -t 30s \
        --host http://127.0.0.1:8000 --csv=/tmp/loadtest

Or run with the interactive web UI (omit --headless) and open
http://localhost:8089.

## Last observed numbers (2026-09-19, u=10, r=2, t=30s, against a local
uvicorn instance with AGENTIC_RAG_OTEL_EXPORTER=console)

    /query (aggregated across all 5 question variants): p50 ~4-5 ms,
        p95 ~6-10 ms, ~11.9 req/s combined, 0% failures
    All endpoints aggregated: 478 requests, 0 failures (0.00%), p50 4 ms,
        p95 8 ms, ~16.3 req/s

See eval/LOADTEST.md for the full run transcript and OTel sanity-check
notes (query_requests_total and grounding_failures_total counters
confirmed moving during the run).
"""

from __future__ import annotations

import random

from locust import HttpUser, between, task

# A couple of valid SourceType values from retrieval/schema.py.
SOURCE_TYPES = ["literature", "clinical_trial"]

# Realistic questions that should retrieve grounded answers from the
# 7-doc seed corpus (ingestion/seed_data.py) — all seeded around GLP-1
# agonist literature/patent/trial/internal-report content.
GROUNDED_QUESTIONS = [
    "What is the mechanism of action of semaglutide?",
    "What were the cardiovascular outcomes of the GLP-1 agonist Phase III trial?",
    "How does the sustained-release GLP-1 agonist formulation work?",
    "How does dual GIP/GLP-1 receptor agonism compare to single-target agonists?",
]

# A question designed to have no grounded match in the seed corpus, to
# exercise the refusal path (and grounding_failures_total counter).
REFUSAL_QUESTION = "What is the recommended dosage of a CAR-T therapy for pediatric leukemia?"


class QueryApiUser(HttpUser):
    """Simulates a user hitting /health, /browse, and (mostly) /query."""

    wait_time = between(0.1, 1.0)

    @task(1)
    def health(self):
        self.client.get("/health")

    @task(2)
    def browse_unfiltered(self):
        self.client.get("/browse")

    @task(2)
    def browse_filtered(self):
        source_type = random.choice(SOURCE_TYPES)
        self.client.get("/browse", params={"source_type": source_type})

    @task(10)
    def query_grounded(self):
        question = random.choice(GROUNDED_QUESTIONS)
        self.client.post("/query", params={"question": question})

    @task(3)
    def query_refusal(self):
        self.client.post("/query", params={"question": REFUSAL_QUESTION})
