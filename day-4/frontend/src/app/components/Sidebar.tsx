"use client";

import { useEffect, useState } from "react";
import styles from "../page.module.css";
import { API_BASE, BrowseItem, SOURCE_TYPES } from "../types";

export type Tab = "query" | "browse" | "open_research";

type Props = {
  activeTab: Tab;
  onTabChange: (tab: Tab) => void;
};

const TAB_LABEL: Record<Tab, string> = {
  query: "Query",
  browse: "Browse",
  open_research: "Open Research",
};

export default function Sidebar({ activeTab, onTabChange }: Props) {
  const [items, setItems] = useState<BrowseItem[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    async function loadStats() {
      try {
        const res = await fetch(`${API_BASE}/browse`);
        if (!res.ok) {
          throw new Error(`Stats fetch failed (${res.status})`);
        }
        const data: BrowseItem[] = await res.json();
        if (!cancelled) setItems(data);
      } catch (err) {
        if (!cancelled) {
          setError(
            err instanceof Error ? err.message : "Failed to load corpus stats."
          );
        }
      }
    }
    loadStats();
    return () => {
      cancelled = true;
    };
  }, []);

  const total = items?.length ?? 0;
  const approved = items?.filter((i) => i.approved).length ?? 0;
  const bySourceType = SOURCE_TYPES.map((t) => ({
    type: t,
    count: items?.filter((i) => i.source_type === t).length ?? 0,
  }));

  return (
    <nav className={styles.sidebar}>
      <div className={styles.modeTabs}>
        {(["query", "browse", "open_research"] as Tab[]).map((tab) => (
          <button
            key={tab}
            className={`${styles.navItem} ${
              activeTab === tab ? styles.navItemActive : ""
            }`}
            onClick={() => onTabChange(tab)}
          >
            {TAB_LABEL[tab]}
          </button>
        ))}
      </div>

      <div className={styles.statTiles}>
        <h3 className={styles.sidebarHeading}>Corpus stats</h3>
        {error && (
          <div className={styles.errorBox} role="alert">
            {error}
          </div>
        )}
        {!error && (
          <>
            <div className={styles.statTile}>
              <span className={styles.statTileValue}>{total}</span>
              <span className={styles.statTileLabel}>Total documents</span>
            </div>
            <div className={styles.statTile}>
              <span className={styles.statTileValue}>{approved}</span>
              <span className={styles.statTileLabel}>Approved</span>
            </div>
            {bySourceType.map(({ type, count }) => (
              <div className={styles.statTile} key={type}>
                <span className={styles.statTileValue}>{count}</span>
                <span className={styles.statTileLabel}>{type}</span>
              </div>
            ))}
          </>
        )}
      </div>
    </nav>
  );
}
