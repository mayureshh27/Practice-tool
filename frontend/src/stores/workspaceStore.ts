import { create } from 'zustand';
import type { Domain, WorkflowTemplate, Artifact, RecentItem, Subject, Chapter } from '../workspaceTypes';
import { INITIAL_DOMAINS, INITIAL_WORKFLOWS, INITIAL_ARTIFACTS } from './mockData';

interface WorkspaceState {
  domains: Domain[];
  workflows: WorkflowTemplate[];
  artifacts: Artifact[];
  recentItems: RecentItem[];

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
  deleteArtifact: (id: string) => void;

  // Notebooks (simple string-keyed stubs for notebook route)
  notebooks: Record<string, string[]>;
  createNotebook: (domainId: string, subjectId: string, name: string) => void;
  deleteNotebook: (domainId: string, subjectId: string, id: string) => void;
}

export const useWorkspaceStore = create<WorkspaceState>((set) => ({
  domains: INITIAL_DOMAINS,
  workflows: INITIAL_WORKFLOWS,
  artifacts: INITIAL_ARTIFACTS,
  recentItems: [
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
  ],

  setDomains: (domains) => set({ domains }),

  renameDomain: (id, name) => set((state) => ({
    domains: state.domains.map(d => d.id === id ? { ...d, name } : d)
  })),

  deleteDomain: (id) => set((state) => ({
    domains: state.domains.filter(d => d.id !== id)
  })),

  togglePinDomain: (id) => set((state) => ({
    domains: state.domains.map(d => d.id === id ? { ...d, pinned: !d.pinned } : d)
  })),

  toggleArchiveDomain: (id) => set((state) => ({
    domains: state.domains.map(d => d.id === id ? { ...d, archived: !d.archived } : d)
  })),

  addDomain: (name) => set((state) => {
    const newDomain: Domain = {
      id: `domain-${Date.now()}`,
      name,
      subjects: []
    };
    return { domains: [...state.domains, newDomain] };
  }),

  addSubject: (domainId, name, description) => set((state) => ({
    domains: state.domains.map(d => {
      if (d.id !== domainId) return d;
      const newSubject: Subject = {
        id: `subject-${Date.now()}`,
        name,
        description,
        chapters: [
          {
            id: `c-init-${Date.now()}`,
            name: 'Chapter 1: Foundations',
            topics: []
          }
        ],
        resources: []
      };
      return { ...d, subjects: [...d.subjects, newSubject] };
    })
  })),

  renameSubject: (domainId, subjectId, name) => set((state) => ({
    domains: state.domains.map(d => {
      if (d.id !== domainId) return d;
      return {
        ...d,
        subjects: d.subjects.map(s => s.id === subjectId ? { ...s, name } : s)
      };
    })
  })),

  deleteSubject: (domainId, subjectId) => set((state) => ({
    domains: state.domains.map(d => {
      if (d.id !== domainId) return d;
      return {
        ...d,
        subjects: d.subjects.filter(s => s.id !== subjectId)
      };
    })
  })),

  updateSubject: (domainId, subjectId, fields) => set((state) => ({
    domains: state.domains.map(d => {
      if (d.id !== domainId) return d;
      return {
        ...d,
        subjects: d.subjects.map(s => s.id === subjectId ? { ...s, ...fields } : s)
      };
    })
  })),

  addChapter: (domainId, subjectId, name, description) => set((state) => ({
    domains: state.domains.map(d => {
      if (d.id !== domainId) return d;
      return {
        ...d,
        subjects: d.subjects.map(s => {
          if (s.id !== subjectId) return s;
          const newChapter: Chapter = {
            id: `chapter-${Date.now()}`,
            name,
            description: description || `Learning modules for ${name}.`,
            topics: []
          };
          return { ...s, chapters: [...s.chapters, newChapter] };
        })
      };
    })
  })),

  updateChapter: (domainId, subjectId, chapterId, fields) => set((state) => ({
    domains: state.domains.map(d => {
      if (d.id !== domainId) return d;
      return {
        ...d,
        subjects: d.subjects.map(s => {
          if (s.id !== subjectId) return s;
          return {
            ...s,
            chapters: s.chapters.map(c => c.id === chapterId ? { ...c, ...fields } : c)
          };
        })
      };
    })
  })),

  addTopic: (domainId, subjectId, chapterId, name) => set((state) => ({
    domains: state.domains.map(d => {
      if (d.id !== domainId) return d;
      return {
        ...d,
        subjects: d.subjects.map(s => {
          if (s.id !== subjectId) return s;
          return {
            ...s,
            chapters: s.chapters.map(c => {
              if (c.id !== chapterId) return c;
              return {
                ...c,
                topics: [...c.topics, { id: `topic-${Date.now()}`, name, lastMessage: 'Not started' }]
              };
            })
          };
        })
      };
    })
  })),

  addResource: (domainId, subjectId, name, fileType, linesCount) => set((state) => ({
    domains: state.domains.map(d => {
      if (d.id !== domainId) return d;
      return {
        ...d,
        subjects: d.subjects.map(s => {
          if (s.id !== subjectId) return s;
          return {
            ...s,
            resources: [...s.resources, { id: `res-${Date.now()}`, name, fileType, lines: linesCount }]
          };
        })
      };
    })
  })),

  removeResource: (domainId, subjectId, resourceId) => set((state) => ({
    domains: state.domains.map(d => {
      if (d.id !== domainId) return d;
      return {
        ...d,
        subjects: d.subjects.map(s => {
          if (s.id !== subjectId) return s;
          return {
            ...s,
            resources: s.resources.filter(r => r.id !== resourceId)
          };
        })
      };
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
    return { recentItems: [newItem, ...filtered].slice(0, 5) };
  }),

  saveWorkflow: (wf) => set((state) => {
    const idx = state.workflows.findIndex(w => w.id === wf.id);
    if (idx >= 0) {
      const next = [...state.workflows];
      next[idx] = wf;
      return { workflows: next };
    } else {
      return { workflows: [...state.workflows, wf] };
    }
  }),

  deleteWorkflow: (id) => set((state) => ({
    workflows: state.workflows.filter(w => w.id !== id)
  })),

  updateWorkflow: (wf) => set((state) => {
    const idx = state.workflows.findIndex(w => w.id === wf.id);
    if (idx >= 0) {
      const next = [...state.workflows];
      next[idx] = wf;
      return { workflows: next };
    }
    return { workflows: [...state.workflows, wf] };
  }),

  duplicateWorkflow: (id) => set((state) => {
    const wf = state.workflows.find(w => w.id === id);
    if (!wf) return state;
    return { workflows: [...state.workflows, { ...wf, id: `wf-dup-${Date.now()}`, name: `${wf.name} (copy)` }] };
  }),

  deleteArtifact: (id) => set((state) => ({
    artifacts: state.artifacts.filter(a => a.id !== id)
  })),

  notebooks: {},
  createNotebook: (domainId, subjectId, name) => set((state) => {
    const key = `${domainId}::${subjectId}`;
    return { notebooks: { ...state.notebooks, [key]: [...(state.notebooks[key] ?? []), name] } };
  }),
  deleteNotebook: (domainId, subjectId, id) => set((state) => {
    const key = `${domainId}::${subjectId}`;
    return { notebooks: { ...state.notebooks, [key]: (state.notebooks[key] ?? []).filter(n => n !== id) } };
  }),
}));
