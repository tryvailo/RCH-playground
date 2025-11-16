/**
 * Test Results Store (Zustand)
 */
import { create } from 'zustand';
import type { TestResult, ApiTestResult } from '../types/api.types';

interface TestStore {
  currentTest: TestResult | null;
  testHistory: TestResult[];
  setCurrentTest: (test: TestResult | null) => void;
  addTestToHistory: (test: TestResult) => void;
  updateTestProgress: (jobId: string, progress: number, currentApi?: string) => void;
  updateTestResults: (jobId: string, results: Record<string, ApiTestResult>) => void;
}

export const useTestStore = create<TestStore>((set) => ({
  currentTest: null,
  testHistory: [],
  setCurrentTest: (test) => set({ currentTest: test }),
  addTestToHistory: (test) =>
    set((state) => ({
      testHistory: [test, ...state.testHistory].slice(0, 50), // Keep last 50
    })),
  updateTestProgress: (jobId, progress, currentApi) =>
    set((state) => {
      if (state.currentTest?.jobId === jobId) {
        return {
          currentTest: {
            ...state.currentTest,
            progress,
            ...(currentApi && { currentApi }),
          },
        };
      }
      return state;
    }),
  updateTestResults: (jobId, results) =>
    set((state) => {
      if (state.currentTest?.jobId === jobId) {
        return {
          currentTest: {
            ...state.currentTest,
            results,
            status: 'completed',
            completedAt: new Date().toISOString(),
          },
        };
      }
      return state;
    }),
}));

