"use client";

import { useState } from "react";
import styles from "../page.module.css";
import {
  API_BASE,
  QueryResponse,
  RecentQueryEntry,
} from "../types";

const STATUS_LABEL: Record<QueryResponse["status"], string> = {
  answered: "Answered",
  refused: "Refused — insufficient grounded evidence",
  escalated: "Escalated for review",
};

type Props = {
  onQueryComplete: (entry: RecentQueryEntry) => void;
};

export default function GroundedQueryPanel({ onQueryComplete }: Props) {
  const [question, setQuestion] = useState("");
  const [result, setResult] = useState<QueryResponse | null>(null);
  const [queryLoading, setQueryLoading] = useState(false);
  const [queryError, setQueryError] = useState<string | null>(null);

  async function runQuery() {
    if (!question.trim() || queryLoading) return;
    setQueryLoading(true);
    setQueryError(null);
    try {
      const res = await fetch(
        `${API_BASE}/query?question=${encodeURIComponent(question)}`,
        { method: "POST" }
      );
      if (!res.ok) {
        throw new Error(`Query failed (${res.status} ${res.statusText})`);
      }
      const data: QueryResponse = await res.json();
      setResult(data);
      onQueryComplete({
        id: `${Date.now()}-${Math.random()}`,
        question,
        mode: "grounded",
        status: data.status,
        timestamp: Date.now(),
      });
    } catch (err) {
      setResult(null);
      setQueryError(
        err instanceof Error ? err.message : "Unknown error while querying."
      );
    } finally {
      setQueryLoading(false);
    }
  }

  function handleQuestionKeyDown(e: React.KeyboardEvent<HTMLInputElement>) {
    if (e.key === "Enter") {
      e.preventDefault();
      runQuery();
    }
  }

  const statusClass =
    result?.status === "answered"
      ? styles.badgeAnswered
      : result?.status === "escalated"
      ? styles.badgeEscalated
      : styles.badgeRefused;

  const confidenceClass =
    result?.confidence === "high"
      ? styles.badgeHigh
      : result?.confidence === "medium"
      ? styles.badgeMedium
      : styles.badgeLow;

  return (
    <section className={styles.card}>
      <h2 className={styles.sectionHeading}>Ask a question</h2>
      <div className={styles.inputRow}>
        <input
          className={styles.textInput}
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyDown={handleQuestionKeyDown}
          placeholder="e.g. What is known about X's mechanism of action?"
          disabled={queryLoading}
        />
        <button
          className={styles.primaryButton}
          onClick={runQuery}
          disabled={queryLoading || !question.trim()}
        >
          {queryLoading ? "Loading…" : "Ask"}
        </button>
      </div>

      {queryLoading && <p className={styles.loadingText}>Loading answer…</p>}

      {queryError && (
        <div className={styles.errorBox} role="alert">
          {queryError}
        </div>
      )}

      {result && !queryLoading && (
        <div className={styles.resultBox}>
          <div className={styles.badgeRow}>
            <span className={`${styles.badge} ${statusClass}`}>
              {STATUS_LABEL[result.status]}
            </span>
            <span className={`${styles.badge} ${confidenceClass}`}>
              Confidence: {result.confidence}
            </span>
          </div>

          {result.status === "answered" && result.answer ? (
            <p className={styles.answerText}>{result.answer}</p>
          ) : (
            <p className={styles.refusedText}>
              No answer — insufficient grounded evidence.
            </p>
          )}

          {result.caveats.length > 0 && (
            <div className={styles.caveats}>
              <strong>Caveats:</strong>
              <ul>
                {result.caveats.map((c, i) => (
                  <li key={i}>{c}</li>
                ))}
              </ul>
            </div>
          )}

          {result.citations.length > 0 && (
            <div className={styles.citations}>
              <strong>Citations:</strong>
              <ul>
                {result.citations.map((c) => (
                  <li key={c.chunk_id}>
                    <span className={styles.citationTag}>{c.source_type}</span>{" "}
                    {c.document_id} / {c.chunk_id}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </section>
  );
}
