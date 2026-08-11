export interface HardwareInfo {
  cpu_name: string;
  ram_total_gb: number;
  ram_used_gb: number;
  gpu: {
    available: boolean;
    vendor: string;
    name: string;
    vram_total_gb: number;
    vram_used_gb: number;
    vram_reserved_gb: number;
  };
  cuda: {
    available: boolean;
    version?: string;
    pytorch_version: string;
  };
  recommended_device: string;
}

export interface ModelInfo {
  id: string;
  name: string;
  architecture: string;
  supports_cloning: boolean;
  default_sample_rate: number;
  vram_required_gb: number;
  installed: boolean;
  loaded: boolean;
  device: string;
}

export interface VoiceInfo {
  id: string;
  name: string;
  genre: string;
  file_path: string;
  duration_sec: number;
  sample_rate: number;
  file_size_kb: number;
}

export interface GenerationRequest {
  text: string;
  model_id: string;
  voice_path?: string;
  speed?: number;
  pitch?: number;
}

export interface GenerationStatus {
  task_id: string;
  status: 'queued' | 'processing' | 'completed' | 'failed';
  progress_percent: number;
  message: string;
  model_id: string;
  gen_time_sec: number;
  duration_sec: number;
  rtf: number;
  file_size_kb: number;
  output_wav_path?: string;
  device: string;
}

export interface BenchmarkItem {
  model_id: string;
  model_name: string;
  word_count: number;
  char_count: number;
  chunks: number;
  device: string;
  gen_time_sec: number;
  audio_duration_sec: number;
  rtf: number;
  vram_used_mb: number;
}

export interface BenchmarkResponse {
  timestamp: string;
  results: BenchmarkItem[];
}
