import { create } from 'zustand';
import type { Domain, WorkflowTemplate, Artifact, RecentItem, Subject, Chapter } from '../workspaceTypes';
import { INITIAL_DOMAINS, INITIAL_WORKFLOWS, INITIAL_ARTIFACTS } from './mockData';
import { api } from '../api/workspaceApi';

// ── Chat types ─────────────────────────────────────────────────────
export type ChatMessage = {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: string;
};

const getLocalStorageItem = (key: string, fallback: any) => {
  try {
    if (typeof window !== 'undefined' && window.localStorage) {
      const raw = window.localStorage.getItem(key);
      return raw ? JSON.parse(raw) : fallback;
    }
  } catch (err) {
    console.warn(`Error reading localStorage key "${key}":`, err);
  }
  return fallback;
};

const setLocalStorageItem = (key: string, value: any) => {
  try {
    if (typeof window !== 'undefined' && window.localStorage) {
      window.localStorage.setItem(key, JSON.stringify(value));
    }
  } catch (err) {
    console.warn(`Error writing localStorage key "${key}":`, err);
  }
};

type SetState = (partial: WorkspaceState | Partial<WorkspaceState> | ((state: WorkspaceState) => WorkspaceState | Partial<WorkspaceState>)) => void

const mutateDomains = (set: SetState, mapper: (domains: Domain[]) => Domain[]) =>
  set((state: WorkspaceState) => {
    const next = mapper(state.domains);
    setLocalStorageItem('domains', next);
    return { domains: next };
  });

interface WorkspaceState {
  domains: Domain[];
  workflows: WorkflowTemplate[];
  artifacts: Artifact[];
  recentItems: RecentItem[];

  // ── Chat state ───────────────────────────────────────────────────
  chatSessionId: string | null;
  chatMessages: ChatMessage[];
  isChatLoading: boolean;
  startChatSession: () => Promise<void>;
  endChatSession: () => Promise<void>;
  sendChatMessage: (text: string, conceptIds?: string[], sourceIds?: string[]) => Promise<void>;

  // ── Practice attempt submission (delegated to backend event store) ─
  submitPracticeAttempt: (attempt: {
    sessionId?: string;
    artifactId?: string;
    conceptId?: string;
    verdict: string;
    hintCount?: number;
    durationMs?: number;
  }) => Promise<void>;

  // Domains
  setDomains: (domains: Domain[]) => void;
  renameDomain: (id: string, name: string) => void;
  deleteDomain: (id: string) => void;
  togglePinDomain: (id: string) => void;
  toggleArchiveDomain: (id: string) => void;
  addDomain: (name: string) => void;

  // Subjects
  addSubject: (domainId: string, name: string, description?: string) => void;
  renameSubject: (domainId: string, subjectId: string, name: string) => void;
  deleteSubject: (domainId: string, subjectId: string) => void;
  updateSubject: (domainId: string, subjectId: string, fields: Partial<Subject>) => void;

  // Chapters
  addChapter: (domainId: string, subjectId: string, name: string, description?: string) => void;
  updateChapter: (domainId: string, subjectId: string, chapterId: string, fields: Partial<Chapter>) => void;

  // Topics
  addTopic: (domainId: string, subjectId: string, chapterId: string, name: string) => void;

  // Resources
  addResource: (domainId: string, subjectId: string, name: string, fileType: string, linesCount: number) => void;
  removeResource: (domainId: string, subjectId: string, resourceId: string) => void;

  // Recents
  addToRecents: (label: string, type: RecentItem['type'], loc: any) => void;

  // Workflows
  saveWorkflow: (wf: WorkflowTemplate) => void;
  deleteWorkflow: (id: string) => void;
  updateWorkflow: (wf: WorkflowTemplate) => void;
  duplicateWorkflow: (id: string) => void;

  // Artifacts
  addArtifact: (art: Omit<Artifact, 'id' | 'time'>) => void;
  deleteArtifact: (id: string) => void;

  // Notebooks (simple string-keyed stubs for notebook route)
  notebooks: Record<string, string[]>;
  createNotebook: (domainId: string, subjectId: string, name: string) => void;
  deleteNotebook: (domainId: string, subjectId: string, id: string) => void;
}

export const useWorkspaceStore = create<WorkspaceState>((set) => ({
  domains: getLocalStorageItem('domains', INITIAL_DOMAINS),
  workflows: getLocalStorageItem('workflows', INITIAL_WORKFLOWS),
  artifacts: getLocalStorageItem('artifacts', INITIAL_ARTIFACTS),
  recentItems: getLocalStorageItem('recentItems', [
    {
      id: 'recent-1',
      label: 'Degrees of Freedom',
      type: 'topic',
      loc: { level: 'topic', domainId: 'robotics', subjectId: 'modern-robotics', chapterId: 'c2', topicId: 'deg-freedom' },
      time: '2 hours ago'
    },
    {
      id: 'recent-2',
      label: 'Modern Robotics',
      type: 'subject',
      loc: { level: 'subject', domainId: 'robotics', subjectId: 'modern-robotics' },
      time: '3 hours ago'
    }
  ]),
  // ── Chat state ───────────────────────────────────────────────────
  chatSessionId: null,
  chatMessages: [],
  isChatLoading: false,

  startChatSession: async () => {
    try {
      const { sessionId } = await api.createChatSession();
      set({ chatSessionId: sessionId, chatMessages: [] });
    } catch (err) {
      console.error('Failed to start chat session:', err);
    }
  },

  endChatSession: async () => {
    const sessionId = useWorkspaceStore.getState().chatSessionId;
    if (!sessionId) return;
    try {
      await api.endChatSession(sessionId);
    } catch (err) {
      console.error('Failed to end chat session:', err);
    }
    set({ chatSessionId: null, chatMessages: [] });
  },

  sendChatMessage: async (text, conceptIds = [], sourceIds = []) => {
    let { chatSessionId } = useWorkspaceStore.getState();

    // Auto-create session if none exists
    if (!chatSessionId) {
      try {
        const { sessionId } = await api.createChatSession();
        chatSessionId = sessionId;
        set({ chatSessionId: sessionId });
      } catch (err) {
        console.error('Failed to auto-create chat session:', err);
        return;
      }
    }

    // Add user message
    const userMsg: ChatMessage = {
      id: `msg-${Date.now()}`,
      role: 'user',
      content: text,
      timestamp: new Date().toISOString(),
    };
    set((state) => ({ chatMessages: [...state.chatMessages, userMsg], isChatLoading: true }));

    try {
      const response = await api.sendChatMessage(chatSessionId, text, conceptIds, sourceIds);
      const assistantMsg: ChatMessage = {
        id: `msg-${Date.now()}-resp`,
        role: 'assistant',
        content: response.response,
        timestamp: new Date().toISOString(),
      };
      set((state) => ({
        chatMessages: [...state.chatMessages, assistantMsg],
        isChatLoading: false,
      }));
    } catch (err) {
      console.error('Chat message failed:', err);
      const errorMsg: ChatMessage = {
        id: `msg-${Date.now()}-err`,
        role: 'system',
        content: 'Failed to reach the tutor. Please check the backend connection.',
        timestamp: new Date().toISOString(),
      };
      set((state) => ({
        chatMessages: [...state.chatMessages, errorMsg],
        isChatLoading: false,
      }));
    }
  },

  submitPracticeAttempt: async (attempt) => {
    try {
      await api.submitAttempt(attempt);
    } catch (err) {
      console.error('Failed to submit practice attempt:', err);
    }
  },

  setDomains: (domains) => mutateDomains(set, () => domains),

  renameDomain: (id, name) => mutateDomains(set,
    ds => ds.map(d => d.id === id ? { ...d, name } : d)),

  deleteDomain: (id) => mutateDomains(set,
    ds => ds.filter(d => d.id !== id)),

  togglePinDomain: (id) => mutateDomains(set,
    ds => ds.map(d => d.id === id ? { ...d, pinned: !d.pinned } : d)),

  toggleArchiveDomain: (id) => mutateDomains(set,
    ds => ds.map(d => d.id === id ? { ...d, archived: !d.archived } : d)),

  addDomain: (name) => mutateDomains(set, ds => [...ds, {
    id: `domain-${Date.now()}`, name, subjects: []
  }]),

  addSubject: (domainId, name, description) => mutateDomains(set,
    ds => ds.map(d => d.id !== domainId ? d : {
      ...d, subjects: [...d.subjects, {
        id: `subject-${Date.now()}`, name, description,
        chapters: [{ id: `c-init-${Date.now()}`, name: 'Chapter 1: Foundations', topics: [] }],
        resources: []
      }]
    })),

  renameSubject: (domainId, subjectId, name) => mutateDomains(set,
    ds => ds.map(d => d.id !== domainId ? d : {
      ...d, subjects: d.subjects.map(s => s.id === subjectId ? { ...s, name } : s)
    })),

  deleteSubject: (domainId, subjectId) => mutateDomains(set,
    ds => ds.map(d => d.id !== domainId ? d : {
      ...d, subjects: d.subjects.filter(s => s.id !== subjectId)
    })),

  updateSubject: (domainId, subjectId, fields) => mutateDomains(set,
    ds => ds.map(d => d.id !== domainId ? d : {
      ...d, subjects: d.subjects.map(s => s.id === subjectId ? { ...s, ...fields } : s)
    })),

  addChapter: (domainId, subjectId, name, description) => mutateDomains(set,
    ds => ds.map(d => d.id !== domainId ? d : {
      ...d, subjects: d.subjects.map(s => s.id !== subjectId ? s : {
        ...s, chapters: [...s.chapters, {
          id: `chapter-${Date.now()}`, name,
          description: description || `Learning modules for ${name}.`, topics: []
        }]
      })
    })),

  updateChapter: (domainId, subjectId, chapterId, fields) => mutateDomains(set,
    ds => ds.map(d => d.id !== domainId ? d : {
      ...d, subjects: d.subjects.map(s => s.id !== subjectId ? s : {
        ...s, chapters: s.chapters.map(c => c.id === chapterId ? { ...c, ...fields } : c)
      })
    })),

  addTopic: (domainId, subjectId, chapterId, name) => mutateDomains(set,
    ds => ds.map(d => d.id !== domainId ? d : {
      ...d, subjects: d.subjects.map(s => s.id !== subjectId ? s : {
        ...s, chapters: s.chapters.map(c => c.id !== chapterId ? c : {
          ...c, topics: [...c.topics, { id: `topic-${Date.now()}`, name, lastMessage: 'Not started' }]
        })
      })
    })),

  addResource: (domainId, subjectId, name, fileType, linesCount) => mutateDomains(set,
    ds => ds.map(d => d.id !== domainId ? d : {
      ...d, subjects: d.subjects.map(s => s.id !== subjectId ? s : {
        ...s, resources: [...s.resources, { id: `res-${Date.now()}`, name, fileType, lines: linesCount }]
      })
    })),

  removeResource: (domainId, subjectId, resourceId) => mutateDomains(set,
    ds => ds.map(d => d.id !== domainId ? d : {
      ...d, subjects: d.subjects.map(s => s.id !== subjectId ? s : {
        ...s, resources: s.resources.filter(r => r.id !== resourceId)
      })
    })),

  addToRecents: (label, type, loc) => set((state) => {
    const filtered = state.recentItems.filter(r => JSON.stringify(r.loc) !== JSON.stringify(loc));
    const newItem: RecentItem = {
      id: `recent-${Date.now()}`,
      label,
      type,
      loc,
      time: 'Just now'
    };
    const next = [newItem, ...filtered].slice(0, 5);
    setLocalStorageItem('recentItems', next);
    return { recentItems: next };
  }),

  saveWorkflow: (wf) => set((state) => {
    const idx = state.workflows.findIndex(w => w.id === wf.id);
    let next;
    if (idx >= 0) {
      next = [...state.workflows];
      next[idx] = wf;
    } else {
      next = [...state.workflows, wf];
    }
    setLocalStorageItem('workflows', next);
    return { workflows: next };
  }),

  deleteWorkflow: (id) => set((state) => {
    const next = state.workflows.filter(w => w.id !== id);
    setLocalStorageItem('workflows', next);
    return { workflows: next };
  }),

  updateWorkflow: (wf) => set((state) => {
    const idx = state.workflows.findIndex(w => w.id === wf.id);
    let next;
    if (idx >= 0) {
      next = [...state.workflows];
      next[idx] = wf;
    } else {
      next = [...state.workflows, wf];
    }
    setLocalStorageItem('workflows', next);
    return { workflows: next };
  }),

  duplicateWorkflow: (id) => set((state) => {
    const wf = state.workflows.find(w => w.id === id);
    if (!wf) return state;
    const next = [...state.workflows, { ...wf, id: `wf-dup-${Date.now()}`, name: `${wf.name} (copy)` }];
    setLocalStorageItem('workflows', next);
    return { workflows: next };
  }),

  addArtifact: (art) => set((state) => {
    const newArt: Artifact = {
      ...art,
      id: `art-${Date.now()}`,
      time: 'Just now'
    };
    const next = [newArt, ...state.artifacts];
    setLocalStorageItem('artifacts', next);
    return { artifacts: next };
  }),

  deleteArtifact: (id) => set((state) => {
    const next = state.artifacts.filter(a => a.id !== id);
    setLocalStorageItem('artifacts', next);
    return { artifacts: next };
  }),

  notebooks: getLocalStorageItem('notebooks', {}),
  createNotebook: (domainId, subjectId, name) => set((state) => {
    const key = `${domainId}::${subjectId}`;
    const next = { ...state.notebooks, [key]: [...(state.notebooks[key] ?? []), name] };
    setLocalStorageItem('notebooks', next);
    return { notebooks: next };
  }),
  deleteNotebook: (domainId, subjectId, id) => set((state) => {
    const key = `${domainId}::${subjectId}`;
    const next = { ...state.notebooks, [key]: (state.notebooks[key] ?? []).filter(n => n !== id) };
    setLocalStorageItem('notebooks', next);
    return { notebooks: next };
  }),
}));
