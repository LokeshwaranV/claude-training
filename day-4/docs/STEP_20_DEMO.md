# Step 20 — Demo to First User: Agentic RAG Pharma Literature Review

This is a walkthrough guide for demonstrating the Agentic RAG system to a first user. The system is live at **http://localhost:3000** (frontend) backed by **http://127.0.0.1:8000** (backend).

## System Overview (1 minute)

**What this system does:**
- Searches a curated, allowlisted corpus of pharma literature, patents, clinical trials, and internal reports
- Returns answers grounded in real documents with clickable citations to the exact source chunk
- Refuses or escalates when evidence is insufficient — never fabricates
- Offers an optional "Open Research" mode for general-knowledge questions outside the corpus
- All grounded answers are backed by claim-level citations (every sentence traceable to a source)

**Under the hood:**
- Hybrid retrieval: BM25 keyword + TF-IDF semantic search
- Allowlist filter: only approved, reviewed documents are searchable
- Groq LLM (simulated in this demo) synthesizes readable prose from retrieved chunks, citing inline
- Two-mode architecture: grounded (strict, cited) vs. open-research (ungrounded, opt-in)

**Current corpus:** 15 documents across 6 domains:
- GLP-1 / Obesity
- Oncology / PD-1 Checkpoint Inhibitors
- Oncology / PARP Inhibitors
- Cardio-Renal-Metabolic / SGLT2 Inhibitors
- HIV Pre-Exposure Prophylaxis (PrEP)
- Gene Therapy (allowlist demonstration)

---

## Demo Flow (5–7 minutes)

### Part 1: Grounded Query — Correct Answer with Citations (2 min)

**Action:** Open http://localhost:3000 in a browser. The **Query** tab should be active by default (grounded mode).

**Demo query #1:** Copy and paste:
```
How does semaglutide work as a GLP-1 receptor agonist?
```

**Expected outcome:**
- Status badge shows **"Answered"** (green)
- Confidence shows **"High"** or **"Medium"** (green shades)
- Answer is synthesized prose like: *"Semaglutide is a glucagon-like peptide-1 (GLP-1) receptor agonist that mimics the GLP-1 hormone..."* (not raw concatenation)
- **Citations panel** at the bottom lists 1–3 citations like:
  - `doc-lit-001` (Literature) — Semaglutide mechanism of action in GLP-1 receptor agonism
  - Shows the exact chunk that backs the answer

**Why this matters:** This demonstrates the core grounding guarantee — every sentence is traceable to a real, approved document.

**User interaction:** Click a citation to see the full chunk text and document metadata. Point out the `source_type` (literature/patent/clinical_trial/internal_report) and the `approved: true` flag.

---

### Part 2: Grounded Query — Correct Refusal (1.5 min)

**Demo query #2:** In the same Query tab, enter:
```
What are the most effective astrology practices for predicting financial markets?
```

**Expected outcome:**
- Status badge shows **"Refused"** (orange/red)
- Confidence shows **"Low"** (red)
- Answer shows: `null` (no answer text)
- Caveat message: *"No allowlisted source cleared the minimum relevance threshold for this question. Refusing rather than fabricating an answer."*
- **Citations panel is empty**

**Why this matters:** This demonstrates commitment 4 ("fail gracefully") — rather than hallucinate or guess, the system recognizes when it has no relevant evidence and says so clearly.

**Narration point:** "The system doesn't panic when it doesn't know something. It refuses cleanly instead of making things up."

---

### Part 3: Open Research Mode — Ungrounded, Opt-In (1.5 min)

**Action:** Click the **Open Research** tab in the sidebar.

**Visual indicator:** The card should have a **dashed border** (distinct from the solid-border grounded query card), and a persistent **amber/yellow banner** at the top saying:
```
Ungrounded — generated from general model knowledge, no corpus citations, not verified against the allowlist. 
(SIMULATED — no live model configured.)
```

**Demo query #3:** Enter:
```
What is dark matter and how does it affect galaxy formation?
```

**Expected outcome:**
- No citations appear (by design — this is ungrounded)
- No confidence/status badges (this schema has none)
- Answer shows: *"This is a simulated Open Research response — no live Groq/LLM model is configured. A real model would attempt a detailed, general-knowledge answer to: 'What is dark matter...'. Set AGENTIC_RAG_GROQ_API_KEY to enable real answers."*
- **The disclaimer banner persists** (doesn't go away after the first answer)

**Why this matters:** This demonstrates commitment 6 — open research is visibly separate, not confusable with grounded answers, and clearly labeled as ungrounded every time.

**Narration point:** "This is a different mode entirely. It doesn't retrieve from the corpus, it doesn't cite, and it's always labeled as unverified. Users know they're leaving the grounded evidence zone."

---

### Part 4: Browse Mode — Allowlist Transparency (1 min)

**Action:** Click the **Browse** tab in the sidebar.

**Visual elements:**
- **Corpus Stats tiles** in the left sidebar showing:
  - Total documents in the corpus
  - Number of approved documents
  - Per-source-type breakdown (Literature, Patent, Clinical Trial, Internal Report)
- **Filter buttons** in the Browse panel for each source type
- **Document list** showing all approved documents (you can click one to see its title, source type, and approval status)

**Demo action:** Filter by **Clinical Trials** only. Point out:
- Only documents with `source_type: "clinical_trial"` and `approved: true` show up
- Everything else is hidden (including any unapproved docs in the trial category)

**Why this matters:** This demonstrates commitment 5 — users can explore the corpus and understand what's approved and available. The allowlist is transparent, not hidden.

**Narration point:** "The corpus is always visible. You can see what's in it, what's approved, and what source types we're covering. No mystery, no hidden filtering."

---

### Part 5: Recent Queries Widget — Session History (30 sec)

**Location:** Right sidebar, "Recent Queries" section. It should show a session-local list of the 5 most recent queries from both Query and Open Research tabs.

**What it shows:**
- Query text (truncated if long)
- Mode (Query vs. Open Research)
- For grounded queries: status badge (Answered/Refused/Escalated)

**Why this matters:** Users can see their query history at a glance within this session.

---

## Success Criteria (checklist for the demo)

By the end of the demo, the user should observe:

- [ ] **Query tab (grounded mode):**
  - Answered a pharma question correctly with real citations
  - Refused an off-topic question cleanly (no fabrication)
  - Every citation resolves to a real approved document

- [ ] **Open Research tab:**
  - Visually distinct from Query (dashed border, different accent color)
  - Persistent disclaimer banner on every result
  - Clearly marked as simulated/unverified
  - Does not cite or include grounded confidence/status fields

- [ ] **Browse tab:**
  - Shows the full corpus with approve/source-type labels
  - Filtering by source type works correctly
  - No unapproved documents leak through

- [ ] **General:**
  - System is responsive (queries return in <2s typically)
  - No JavaScript errors in the browser console
  - No backend 5xx errors

---

## Sample Queries by Domain (for extended demo)

Use these if the user wants to see more breadth:

### GLP-1 / Obesity
- "What is the mechanism of action of semaglutide?" → expect grounded answer
- "Does GLP-1 receptor agonism cause weight loss by suppressing appetite?" → expect grounded answer with multiple citations

### Oncology / PD-1 Checkpoint Inhibitors
- "How does PD-1 blockade work in melanoma?" → expect grounded answer
- "What is the safety profile of PD-1 checkpoint inhibitors in NSCLC?" → expect grounded answer citing clinical trial data

### Oncology / PARP Inhibitors
- "What is a PARP inhibitor and when is it used?" → expect grounded answer or refusal (depends on corpus)
- "How do PARP inhibitors treat BRCA-mutant tumors?" → expect grounded answer

### Cardio-Renal-Metabolic / SGLT2 Inhibitors
- "What does SGLT2 stand for and what is its role?" → expect grounded answer
- "Can SGLT2 inhibitors treat heart failure?" → expect grounded answer citing trial data

### HIV PrEP
- "What is pre-exposure prophylaxis and how is it administered?" → expect grounded answer
- "What oral regimens exist for HIV PrEP?" → expect grounded answer or refusal (corpus has limited PrEP detail)

### Refusal Examples (off-topic)
- "What's the boiling point of liquid nitrogen?" → expect refusal
- "Who won the 2023 World Cup?" → expect refusal
- "How do I make a sourdough starter?" → expect refusal

---

## Known Limitations & Notes

1. **Simulated Groq:** The system is running in simulation mode (`AGENTIC_RAG_GROQ_SIMULATE=1`) because no live Groq API key is configured. When a real key is available, set `AGENTIC_RAG_GROQ_API_KEY` as an environment variable and restart the backend to see real LLM synthesis.

2. **BM25 Scoring Edge Case:** The retrieval system can occasionally score weak matches high if they share only one or two incidental tokens with the corpus. This is a known tuning opportunity documented in `docs/reviews/STEP_19_REVIEW.md` — it doesn't violate grounding (citations are still real/approved) but can weaken refusal accuracy on truly underserved queries.

3. **Citation Markers in Simulated Mode:** Simulated grounded answers use `[1]`, `[2]` citation markers placed within the text (before trailing punctuation). These markers are synthetic for demo purposes — real Groq synthesis would generate more natural prose with the markers still respecting the grounding check.

4. **No Real-Time Corpus Updates:** The corpus is static (loaded from `ingestion/seed_data.py` at boot). To add new documents, modify that file and restart the backend.

---

## Walkthrough Narrative (Suggested)

> *"This is Agentic RAG — a grounded search system for pharma literature. It searches a curated, allowlisted corpus and returns answers backed by real documents. Every sentence you see is traceable to a specific source.*
>
> *Let me show you three things: first, how it answers a real pharma question and cites its sources. Second, how it refuses when it doesn't know something. And third, how it distinguishes between grounded answers and ungrounded general knowledge if you want to explore outside the corpus.*
>
> *Start with a query about GLP-1..."*

Then walk through Parts 1–3 above.

---

## Technical Details for the Curious

- **Backend:** FastAPI + Python, running on `http://127.0.0.1:8000`
  - Endpoints: `/query` (grounded), `/query/open-research` (ungrounded), `/browse` (list only), `/health`
  - All grounded answers are post-hoc validated against a grounding check — if Groq generates an uncited claim, the answer is escalated and re-offered as extractive fallback
- **Frontend:** Next.js 16, running on `http://localhost:3000`
  - Dashboard with tabs for Query / Browse / Open Research
  - Two-mode UI design ensures grounded and ungrounded answers are never visually confused
- **Corpus:** 15 approved + 3 unapproved documents, 4 source types, ~7k words of content
- **Allowlist:** Strictly enforced — only `approved: true` documents are searchable
- **Grounding:** Every citation is checked against the corpus at response time

---

## What Comes Next

After this demo, the project can:
1. **Expand the corpus** with real pharma sources (papers, patents, trial registries)
2. **Tune the retrieval thresholds** based on real-world query patterns
3. **Integrate a live Groq key** (or another LLM) for real synthesis instead of simulation
4. **Deploy to staging/production** (currently local dev servers only)
5. **Gather user feedback** and iterate on the grounding/refusal policies

---

**Demo ready. Open http://localhost:3000 in a browser and start with the Query tab.**
