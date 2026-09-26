"use client";

import { useState } from "react";
import styles from "../page.module.css";
import { API_BASE, BrowseItem, SOURCE_TYPES } from "../types";

export default function BrowsePanel() {
  const [browseFilter, setBrowseFilter] = useState<string>("");
  const [browseItems, setBrowseItems] = useState<BrowseItem[]>([]);
  const [browseLoading, setBrowseLoading] = useState(false);
  const [browseError, setBrowseError] = useState<string | null>(null);

  async function runBrowse(sourceType: string) {
    setBrowseFilter(sourceType);
    setBrowseLoading(true);
    setBrowseError(null);
    try {
      const qs = sourceType ? `?source_type=${sourceType}` : "";
      const res = await fetch(`${API_BASE}/browse${qs}`);
      if (!res.ok) {
        throw new Error(`Browse failed (${res.status} ${res.statusText})`);
      }
      const data: BrowseItem[] = await res.json();
      setBrowseItems(data);
    } catch (err) {
      setBrowseItems([]);
      setBrowseError(
        err instanceof Error ? err.message : "Unknown error while browsing."
      );
    } finally {
      setBrowseLoading(false);
    }
  }

  return (
    <section className={styles.card}>
      <h2 className={styles.sectionHeading}>Browse across domains</h2>
      <div className={styles.filterRow}>
        <button
          className={`${styles.filterButton} ${
            browseFilter === "" ? styles.filterButtonActive : ""
          }`}
          onClick={() => runBrowse("")}
        >
          All
        </button>
        {SOURCE_TYPES.map((t) => (
          <button
            key={t}
            className={`${styles.filterButton} ${
              browseFilter === t ? styles.filterButtonActive : ""
            }`}
            onClick={() => runBrowse(t)}
          >
            {t}
          </button>
        ))}
      </div>

      <p className={styles.filterLabel}>
        Filter: <strong>{browseFilter || "all"}</strong>
      </p>

      {browseLoading && <p className={styles.loadingText}>Loading…</p>}

      {browseError && (
        <div className={styles.errorBox} role="alert">
          {browseError}
        </div>
      )}

      {!browseLoading && !browseError && (
        <ul className={styles.browseList}>
          {browseItems.map((item) => (
            <li key={item.document_id} className={styles.browseItem}>
              <span className={styles.citationTag}>{item.source_type}</span>{" "}
              {item.title} (v{item.version})
            </li>
          ))}
          {browseItems.length === 0 && (
            <li className={styles.emptyState}>No items to show.</li>
          )}
        </ul>
      )}
    </section>
  );
}
