/**
 * API Credentials Store (Zustand)
 */
import { create } from 'zustand';
import type { ApiCredentials } from '../types/api.types';

interface ApiStore {
  credentials: ApiCredentials | null;
  setCredentials: (credentials: ApiCredentials) => void;
  clearCredentials: () => void;
  hasCredentials: (api: keyof ApiCredentials) => boolean;
}

export const useApiStore = create<ApiStore>((set, get) => ({
  credentials: null,
  setCredentials: (credentials) => set({ credentials }),
  clearCredentials: () => set({ credentials: null }),
  hasCredentials: (api) => {
    const creds = get().credentials;
    if (!creds) return false;
    return !!creds[api];
  },
}));

