"use client";

import { useState } from "react";
import styles from "./page.module.css";
import { RecentQueryEntry } from "./types";
import Sidebar, { Tab } from "./components/Sidebar";
import GroundedQueryPanel from "./components/GroundedQueryPanel";
import OpenResearchPanel from "./components/OpenResearchPanel";
import BrowsePanel from "./components/BrowsePanel";
import RecentQueriesWidget from "./components/RecentQueriesWidget";

const MAX_RECENT = 5;

export default function Home() {
  const [activeTab, setActiveTab] = useState<Tab>("query");
  const [recentQueries, setRecentQueries] = useState<RecentQueryEntry[]>([]);

  function handleQueryComplete(entry: RecentQueryEntry) {
    setRecentQueries((prev) => [entry, ...prev].slice(0, MAX_RECENT));
  }

  return (
    <div className={styles.page}>
      <main className={styles.main}>
        <h1 className={styles.title}>Agentic RAG — Pharma Literature Review</h1>

        <div className={styles.dashboardLayout}>
          <Sidebar activeTab={activeTab} onTabChange={setActiveTab} />

          <div className={styles.dashboardContent}>
            {activeTab === "query" && (
              <GroundedQueryPanel onQueryComplete={handleQueryComplete} />
            )}
            {activeTab === "browse" && <BrowsePanel />}
            {activeTab === "open_research" && (
              <OpenResearchPanel onQueryComplete={handleQueryComplete} />
            )}

            <RecentQueriesWidget entries={recentQueries} />
          </div>
        </div>
      </main>
    </div>
  );
}
