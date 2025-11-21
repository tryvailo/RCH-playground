/**
 * MSIF Data Store (Zustand)
 * Кэширует данные MSIF для быстрого доступа
 */
import { create } from 'zustand';
import type { MSIFStoreState, MSIFData } from '../types';

export const useMSIFStore = create<MSIFStoreState>((set) => ({
  msifData: null,
  isLoading: false,
  error: null,
  lastFetched: null,
  
  setMSIFData: (data: MSIFData) => 
    set({ 
      msifData: data, 
      isLoading: false, 
      error: null,
      lastFetched: Date.now()
    }),
  
  setLoading: (loading: boolean) => 
    set({ isLoading: loading }),
  
  setError: (error: string | null) => 
    set({ error, isLoading: false }),
  
  clearCache: () => 
    set({ 
      msifData: null, 
      lastFetched: null, 
      error: null 
    }),
}));

