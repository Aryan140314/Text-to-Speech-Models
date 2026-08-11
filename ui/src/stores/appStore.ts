import { create } from 'zustand';
import { ModelInfo, VoiceInfo, HardwareInfo, GenerationStatus } from '../types/api';

interface AppState {
  selectedModelId: string;
  selectedVoicePath: string;
  hardware: HardwareInfo | null;
  models: ModelInfo[];
  voices: VoiceInfo[];
  currentJob: GenerationStatus | null;
  setSelectedModelId: (id: string) => void;
  setSelectedVoicePath: (path: string) => void;
  setHardware: (hw: HardwareInfo) => void;
  setModels: (models: ModelInfo[]) => void;
  setVoices: (voices: VoiceInfo[]) => void;
  setCurrentJob: (job: GenerationStatus | null) => void;
}

export const useAppStore = create<AppState>((set) => ({
  selectedModelId: 'f5tts',
  selectedVoicePath: '',
  hardware: null,
  models: [],
  voices: [],
  currentJob: null,
  setSelectedModelId: (id) => set({ selectedModelId: id }),
  setSelectedVoicePath: (path) => set({ selectedVoicePath: path }),
  setHardware: (hw) => set({ hardware: hw }),
  setModels: (models) => set({ models }),
  setVoices: (voices) => set({ voices }),
  setCurrentJob: (job) => set({ currentJob: job }),
}));
