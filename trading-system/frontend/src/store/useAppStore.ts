import { create } from "zustand";

type IngestResult = {
  success: boolean;
  tickers?: string[];
  row_count?: number;
  start_date?: string;
  end_date?: string;
  error?: string;
};

type AppStore = {
  ticker: string;
  setTicker: (ticker: string) => void;

  start: string;
  setStart: (start: string) => void;

  end: string;
  setEnd: (end: string) => void;

  ingestResult: IngestResult | null;
  setIngestResult: (result: IngestResult | null) => void;

  loading: boolean;
  setLoading: (b: boolean) => void;
};

function getCurrentYearStart() {
  const year = new Date().getFullYear();
  return `${year}-01-01`;
}
function getCurrentYearEnd() {
  const year = new Date().getFullYear();
  return `${year}-12-31`;
}

export const useAppStore = create<AppStore>((set) => ({
  ticker: "",
  setTicker: (ticker) => set({ ticker }),

  start: getCurrentYearStart(),
  setStart: (start) => set({ start }),

  end: getCurrentYearEnd(),
  setEnd: (end) => set({ end }),

  ingestResult: null,
  setIngestResult: (ingestResult) => set({ ingestResult }),

  loading: false,
  setLoading: (loading) => set({ loading }),
}));
