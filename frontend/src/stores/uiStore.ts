import { create } from 'zustand';
import type { Theme } from '../types';
import type { RightDockPanel as RightDockPanelType, BottomDockTab } from '../workspaceTypes';
import { getBrowserStorage, readTextStorage, writeTextStorage } from '../appState';

type CreationModalType = 'domain' | 'subject' | 'chapter' | 'topic';

interface CreationModalState {
  open: boolean;
  type: CreationModalType;
  domainId?: string;
  subjectId?: string;
  chapterId?: string;
}

interface UIState {
  // Theme
  theme: Theme;
  setTheme: (theme: Theme) => void;
  toggleTheme: () => void;

  // Search Palette
  searchModalOpen: boolean;
  setSearchModalOpen: (open: boolean) => void;
  searchQuery: string;
  setSearchQuery: (query: string) => void;
  selectedIndex: number;
  setSelectedIndex: (index: number | ((prev: number) => number)) => void;

  // Creation Modal
  creationModal: CreationModalState | null;
  setCreationModal: (modal: CreationModalState | null) => void;
  modalName: string;
  setModalName: (name: string) => void;
  modalDesc: string;
  setModalDesc: (desc: string) => void;

  // Workspace Shell Layout
  leftCollapsed: boolean;
  setLeftCollapsed: (collapsed: boolean | ((prev: boolean) => boolean)) => void;
  practiceNavCollapsed: boolean;
  setPracticeNavCollapsed: (collapsed: boolean | ((prev: boolean) => boolean)) => void;
  rightPanel: RightDockPanelType;
  setRightPanel: (panel: RightDockPanelType) => void;
  bottomOpen: boolean;
  setBottomOpen: (open: boolean) => void;
  bottomTab: BottomDockTab;
  setBottomTab: (tab: BottomDockTab) => void;
}

export const useUIStore = create<UIState>((set) => ({
  theme: readTextStorage(getBrowserStorage(), 'theme', 'dark') === 'light' ? 'light' : 'dark',
  setTheme: (theme) => {
    writeTextStorage(getBrowserStorage(), 'theme', theme);
    document.documentElement.dataset.theme = theme;
    document.documentElement.style.setProperty('color-scheme', theme);
    set({ theme });
  },
  toggleTheme: () => {
    set((state) => {
      const newTheme = state.theme === 'dark' ? 'light' : 'dark';
      writeTextStorage(getBrowserStorage(), 'theme', newTheme);
      document.documentElement.dataset.theme = newTheme;
      document.documentElement.style.setProperty('color-scheme', newTheme);
      return { theme: newTheme };
    });
  },

  searchModalOpen: false,
  setSearchModalOpen: (open) => set({ searchModalOpen: open }),
  searchQuery: '',
  setSearchQuery: (query) => set({ searchQuery: query }),
  selectedIndex: 0,
  setSelectedIndex: (index) => set((state) => ({ 
    selectedIndex: typeof index === 'function' ? index(state.selectedIndex) : index 
  })),

  creationModal: null,
  setCreationModal: (modal) => set({ creationModal: modal }),
  modalName: '',
  setModalName: (name) => set({ modalName: name }),
  modalDesc: '',
  setModalDesc: (desc) => set({ modalDesc: desc }),

  leftCollapsed: false,
  setLeftCollapsed: (collapsed) => set((state) => ({ 
    leftCollapsed: typeof collapsed === 'function' ? collapsed(state.leftCollapsed) : collapsed 
  })),
  practiceNavCollapsed: false,
  setPracticeNavCollapsed: (collapsed) => set((state) => ({
    practiceNavCollapsed: typeof collapsed === 'function' ? collapsed(state.practiceNavCollapsed) : collapsed
  })),
  rightPanel: null,
  setRightPanel: (panel) => set({ rightPanel: panel }),
  bottomOpen: false,
  setBottomOpen: (open) => set({ bottomOpen: open }),
  bottomTab: 'output',
  setBottomTab: (tab) => set({ bottomTab: tab }),
}));
