import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';

interface AppState {
  isLoading: boolean;
  theme: 'light' | 'dark';
  sidebarOpen: boolean;
  
  setIsLoading: (loading: boolean) => void;
  setTheme: (theme: 'light' | 'dark') => void;
  toggleSidebar: () => void;
  setSidebarOpen: (open: boolean) => void;
}

export const useAppStore = create<AppState>()(
  devtools(
    persist(
      (set) => ({
        isLoading: false,
        theme: 'light',
        sidebarOpen: true,
        
        setIsLoading: (loading) => set({ isLoading: loading }),
        setTheme: (theme) => set({ theme }),
        toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
        setSidebarOpen: (open) => set({ sidebarOpen: open }),
      }),
      {
        name: 'app-storage',
        partialize: (state) => ({
          theme: state.theme,
          sidebarOpen: state.sidebarOpen,
        }),
      }
    )
  )
);
