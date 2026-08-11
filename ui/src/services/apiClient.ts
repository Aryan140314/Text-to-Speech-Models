import axios from 'axios';
import { HardwareInfo, ModelInfo, VoiceInfo, GenerationRequest, GenerationStatus, BenchmarkResponse } from '../types/api';

declare global {
  interface Window {
    electronAPI?: {
      getBackendPort: () => Promise<number>;
      openOutputFolder: (path: string) => Promise<boolean>;
      getAppVersion: () => Promise<string>;
    };
  }
}

let backendPort = 8000;

export async function getBaseUrl(): Promise<string> {
  if (window.electronAPI) {
    try {
      backendPort = await window.electronAPI.getBackendPort();
    } catch {
      backendPort = 8000;
    }
  }
  return `http://127.0.0.1:${backendPort}`;
}

const api = axios.create();

api.interceptors.request.use(async (config) => {
  const baseUrl = await getBaseUrl();
  config.baseURL = baseUrl;
  return config;
});

export const apiClient = {
  getHealth: async () => (await api.get('/api/health')).data,
  getHardware: async (): Promise<HardwareInfo> => (await api.get('/api/system/hardware')).data,
  getModels: async (): Promise<{ models: ModelInfo[]; active_model_id: string }> => (await api.get('/api/models')).data,
  loadModel: async (modelId: string) => (await api.post(`/api/models/${modelId}/load`)).data,
  getVoices: async (): Promise<{ voices: VoiceInfo[]; default_voice_id: string }> => (await api.get('/api/voices')).data,
  cleanVoice: async (voiceId: string, strength: number = 0.75) => (await api.post('/api/voices/clean', { voice_id: voiceId, strength })).data,
  createGenerationJob: async (req: GenerationRequest): Promise<GenerationStatus> => (await api.post('/api/generation', req)).data,
  getGenerationStatus: async (taskId: string): Promise<GenerationStatus> => (await api.get(`/api/generation/${taskId}/status`)).data,
  getAudioUrl: (filePath: string) => `http://127.0.0.1:${backendPort}/api/generation/audio/file?path=${encodeURIComponent(filePath)}`,
  runBenchmark: async (req?: any): Promise<BenchmarkResponse> => (await api.post('/api/benchmark/run', req || {})).data,
  getSettings: async () => (await api.get('/api/settings')).data,
};
