"use client";

import styles from "../page.module.css";
import { RecentQueryEntry } from "../types";

const STATUS_LABEL: Record<string, string> = {
  answered: "Answered",
  refused: "Refused",
  escalated: "Escalated",
};

type Props = {
  entries: RecentQueryEntry[];
};

export default function RecentQueriesWidget({ entries }: Props) {
  return (
    <section className={`${styles.card} ${styles.recentQueries}`}>
      <h2 className={styles.sectionHeading}>Recent questions</h2>
      {entries.length === 0 ? (
        <p className={styles.emptyState}>No questions asked yet this session.</p>
      ) : (
        <ul className={styles.browseList}>
          {entries.map((entry) => (
            <li key={entry.id} className={styles.browseItem}>
              <span className={styles.citationTag}>
                {entry.mode === "grounded" ? "grounded" : "open research"}
              </span>{" "}
              {entry.mode === "grounded" && entry.status && (
                <span
                  className={`${styles.badge} ${
                    entry.status === "answered"
                      ? styles.badgeAnswered
                      : entry.status === "escalated"
                      ? styles.badgeEscalated
                      : styles.badgeRefused
                  }`}
                >
                  {STATUS_LABEL[entry.status]}
                </span>
              )}{" "}
              {entry.question}
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
