import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export interface Agent {
  id: string;
  name: string;
  status: 'idle' | 'running' | 'completed' | 'error';
  icon?: string;
  progress?: number;
  result?: string;
  duration?: number;
}

export interface Summary {
  id: string;
  videoId: string;
  videoTitle: string;
  videoUrl: string;
  thumbnail?: string;
  mode: 'quick' | 'standard' | 'research' | 'educational';
  content: string;
  timestamps?: Array<{ time: string; text: string }>;
  citations?: string[];
  createdAt: number;
  duration?: number;
}

export interface ApiKeys {
  openrouter?: string;
  googleAi?: string;
}

export interface AppSettings {
  backend: 'python' | 'nodejs' | 'go' | 'rust' | 'ruby';
  defaultMode: 'quick' | 'standard' | 'research' | 'educational';
  features: {
    factChecking: boolean;
    webResearch: boolean;
    citations: boolean;
    translation: boolean;
  };
}

interface AppState {
  // Processing State
  isProcessing: boolean;
  currentVideoUrl: string | null;
  currentSummary: Summary | null;
  agents: Agent[];

  // Summaries
  summaries: Summary[];

  // API Keys
  apiKeys: ApiKeys;

  // Settings
  settings: AppSettings;

  // Stats
  stats: {
    totalSummaries: number;
    totalQuestions: number;
    totalExports: number;
  };

  // Actions
  setProcessing: (isProcessing: boolean) => void;
  setCurrentVideoUrl: (url: string | null) => void;
  setCurrentSummary: (summary: Summary | null) => void;
  updateAgent: (agentId: string, updates: Partial<Agent>) => void;
  resetAgents: () => void;
  addSummary: (summary: Summary) => void;
  deleteSummary: (id: string) => void;
  setApiKeys: (keys: ApiKeys) => void;
  updateSettings: (settings: Partial<AppSettings>) => void;
  incrementStat: (stat: 'totalSummaries' | 'totalQuestions' | 'totalExports') => void;
}

const defaultAgents: Agent[] = [
  { id: 'supervisor', name: 'Supervisor Agent', status: 'idle' },
  { id: 'extractor', name: 'Extractor Agent', status: 'idle' },
  { id: 'summarizer', name: 'Summarizer Agent', status: 'idle' },
  { id: 'research', name: 'Research Agent', status: 'idle' },
  { id: 'fact_checker', name: 'Fact-Checker Agent', status: 'idle' },
  { id: 'citation', name: 'Citation Agent', status: 'idle' },
  { id: 'qa', name: 'Q&A Agent', status: 'idle' },
  { id: 'export', name: 'Export Agent', status: 'idle' },
];

export const useAppStore = create<AppState>()(
  persist(
    (set) => ({
      // Initial State
      isProcessing: false,
      currentVideoUrl: null,
      currentSummary: null,
      agents: defaultAgents,
      summaries: [],
      apiKeys: {},
      settings: {
        backend: 'python',
        defaultMode: 'standard',
        features: {
          factChecking: true,
          webResearch: true,
          citations: true,
          translation: false,
        },
      },
      stats: {
        totalSummaries: 0,
        totalQuestions: 0,
        totalExports: 0,
      },

      // Actions
      setProcessing: (isProcessing) => set({ isProcessing }),

      setCurrentVideoUrl: (currentVideoUrl) => set({ currentVideoUrl }),

      setCurrentSummary: (currentSummary) => set({ currentSummary }),

      updateAgent: (agentId, updates) =>
        set((state) => ({
          agents: state.agents.map((agent) =>
            agent.id === agentId ? { ...agent, ...updates } : agent
          ),
        })),

      resetAgents: () =>
        set({
          agents: defaultAgents.map((agent) => ({ ...agent, status: 'idle' })),
        }),

      addSummary: (summary) =>
        set((state) => ({
          summaries: [summary, ...state.summaries],
        })),

      deleteSummary: (id) =>
        set((state) => ({
          summaries: state.summaries.filter((s) => s.id !== id),
        })),

      setApiKeys: (apiKeys) =>
        set((state) => ({
          apiKeys: { ...state.apiKeys, ...apiKeys },
        })),

      updateSettings: (newSettings) =>
        set((state) => ({
          settings: { ...state.settings, ...newSettings },
        })),

      incrementStat: (stat) =>
        set((state) => ({
          stats: {
            ...state.stats,
            [stat]: state.stats[stat] + 1,
          },
        })),
    }),
    {
      name: 'app-storage',
      partialize: (state) => ({
        summaries: state.summaries,
        apiKeys: state.apiKeys,
        settings: state.settings,
        stats: state.stats,
      }),
    }
  )
);
