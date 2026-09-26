"use client";

import { useState } from "react";
import styles from "../page.module.css";
import {
  API_BASE,
  OpenResearchResponse,
  RecentQueryEntry,
} from "../types";

type Props = {
  onQueryComplete: (entry: RecentQueryEntry) => void;
};

export default function OpenResearchPanel({ onQueryComplete }: Props) {
  const [question, setQuestion] = useState("");
  const [result, setResult] = useState<OpenResearchResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function runQuery() {
    if (!question.trim() || loading) return;
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(
        `${API_BASE}/query/open-research?question=${encodeURIComponent(
          question
        )}`,
        { method: "POST" }
      );
      if (res.status === 503) {
        let detail = "Open Research mode is not available — no Groq API key is configured on the server.";
        try {
          const body = await res.json();
          if (body?.detail) detail = body.detail;
        } catch {
          // ignore parse failure, use default message
        }
        throw new Error(detail);
      }
      if (!res.ok) {
        throw new Error(
          `Open research query failed (${res.status} ${res.statusText})`
        );
      }
      const data: OpenResearchResponse = await res.json();
      setResult(data);
      onQueryComplete({
        id: `${Date.now()}-${Math.random()}`,
        question,
        mode: "open_research",
        timestamp: Date.now(),
      });
    } catch (err) {
      setResult(null);
      setError(
        err instanceof Error
          ? err.message
          : "Unknown error while querying open research mode."
      );
    } finally {
      setLoading(false);
    }
  }

  function handleQuestionKeyDown(e: React.KeyboardEvent<HTMLInputElement>) {
    if (e.key === "Enter") {
      e.preventDefault();
      runQuery();
    }
  }

  return (
    <section className={styles.card}>
      <h2 className={styles.sectionHeading}>Open Research (ungrounded)</h2>
      <div className={styles.inputRow}>
        <input
          className={styles.textInput}
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyDown={handleQuestionKeyDown}
          placeholder="Ask a general question beyond the corpus…"
          disabled={loading}
        />
        <button
          className={styles.primaryButton}
          onClick={runQuery}
          disabled={loading || !question.trim()}
        >
          {loading ? "Loading…" : "Ask"}
        </button>
      </div>

      {loading && <p className={styles.loadingText}>Loading answer…</p>}

      {error && (
        <div className={styles.errorBox} role="alert">
          {error}
        </div>
      )}

      {result && !loading && (
        <div className={styles.openResearchCard}>
          <div className={styles.openResearchBanner} role="alert">
            ⚠ {result.disclaimer ||
              "Ungrounded — general model knowledge, no corpus citations, not verified."}
          </div>
          <p className={styles.answerText}>{result.answer}</p>
          <p className={styles.openResearchModel}>
            Answered by {result.model}
          </p>
        </div>
      )}
    </section>
  );
}
