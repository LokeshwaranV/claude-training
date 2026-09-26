export type Citation = {
  document_id: string;
  chunk_id: string;
  source_type: "literature" | "patent" | "clinical_trial" | "internal_report";
};

export type QueryResponse = {
  answer: string | null;
  confidence: "high" | "medium" | "low";
  citations: Citation[];
  caveats: string[];
  status: "answered" | "refused" | "escalated";
};

export type OpenResearchResponse = {
  answer: string;
  mode: "open_research";
  model: string;
  disclaimer: string;
};

export type BrowseItem = {
  document_id: string;
  title: string;
  source_type: Citation["source_type"];
  approved: boolean;
  version: string;
};

export const SOURCE_TYPES = [
  "literature",
  "patent",
  "clinical_trial",
  "internal_report",
] as const;

export const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE ?? "http://127.0.0.1:8123";

export type RecentQueryEntry = {
  id: string;
  question: string;
  mode: "grounded" | "open_research";
  status?: QueryResponse["status"];
  timestamp: number;
};
