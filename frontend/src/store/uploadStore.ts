import { create } from 'zustand';
import type { UploadProgress } from '@/types';

interface UploadState {
  uploads: Record<string, UploadProgress>;
  addUpload: (id: string, upload: UploadProgress) => void;
  updateUpload: (id: string, updates: Partial<UploadProgress>) => void;
  removeUpload: (id: string) => void;
  clearCompleted: () => void;
}

export const useUploadStore = create<UploadState>((set) => ({
  uploads: {},
  addUpload: (id, upload) =>
    set((state) => ({
      uploads: { ...state.uploads, [id]: upload },
    })),
  updateUpload: (id, updates) =>
    set((state) => ({
      uploads: {
        ...state.uploads,
        [id]: { ...state.uploads[id], ...updates },
      },
    })),
  removeUpload: (id) =>
    set((state) => {
      const { [id]: _, ...rest } = state.uploads;
      return { uploads: rest };
    }),
  clearCompleted: () =>
    set((state) => ({
      uploads: Object.fromEntries(
        Object.entries(state.uploads).filter(([_, upload]) => upload.status !== 'completed')
      ),
    })),
}));
