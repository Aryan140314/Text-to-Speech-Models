import React, { useState } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { apiClient } from '../services/apiClient';
import { useAppStore } from '../stores/appStore';
import { AudioPlayer } from '../components/audio/AudioPlayer';
import { Zap, Mic, AlertCircle, Loader2, Sparkles } from 'lucide-react';
import { motion } from 'framer-motion';

export const Generate: React.FC = () => {
  const { selectedModelId, setSelectedModelId, selectedVoicePath, setSelectedVoicePath } = useAppStore();
  const [text, setText] = useState<string>(
    "Welcome to the local Text-to-Speech research laboratory. You can select any model and generate high fidelity voice audio instantly."
  );
  const [activeJob, setActiveJob] = useState<any | null>(null);
  const [isSynthesizing, setIsSynthesizing] = useState(false);

  // Queries
  const { data: modelsData } = useQuery({ queryKey: ['models'], queryFn: apiClient.getModels });
  const { data: voicesData } = useQuery({ queryKey: ['voices'], queryFn: apiClient.getVoices });

  const models = modelsData?.models || [];
  const voices = voicesData?.voices || [];

  // Word & Character count validation (MAX_WORDS = 2000)
  const MAX_WORDS = 2000;
  const wordCount = text.trim() ? text.trim().split(/\s+/).length : 0;
  const charCount = text.length;
  const isLimitExceeded = wordCount > MAX_WORDS;

  // Synthesis Mutation & Polling
  const handleGenerate = async () => {
    if (!text.trim() || isLimitExceeded) return;
    setIsSynthesizing(true);
    try {
      const job = await apiClient.createGenerationJob({
        text,
        model_id: selectedModelId,
        voice_path: selectedVoicePath || undefined,
      });
      setActiveJob(job);

      // Poll job status until completed
      const interval = setInterval(async () => {
        try {
          const status = await apiClient.getGenerationStatus(job.task_id);
          setActiveJob(status);
          if (status.status === 'completed' || status.status === 'failed') {
            clearInterval(interval);
            setIsSynthesizing(false);
          }
        } catch {
          clearInterval(interval);
          setIsSynthesizing(false);
        }
      }, 1000);
    } catch (err) {
      console.error(err);
      setIsSynthesizing(false);
    }
  };

  return (
    <div className="p-8 max-w-6xl mx-auto space-y-8 select-none">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-slate-100 flex items-center gap-2">
            <Zap className="w-6 h-6 text-primary" /> Speech Generation Studio
          </h2>
          <p className="text-xs text-slate-400">Synthesize human-like speech locally with zero-shot voice cloning.</p>
        </div>
      </div>

      <div className="grid grid-cols-12 gap-8">
        {/* Left Column: Form Controls */}
        <div className="col-span-7 space-y-6">
          {/* Model & Voice Selectors */}
          <div className="bg-card border border-border p-5 rounded-2xl space-y-4">
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5">Select TTS Model Engine</label>
              <select
                value={selectedModelId}
                onChange={(e) => setSelectedModelId(e.target.value)}
                className="w-full bg-slate-900 border border-border rounded-xl px-3.5 py-2.5 text-sm text-slate-200 focus:outline-none focus:border-primary"
              >
                {models.map((m) => (
                  <option key={m.id} value={m.id}>
                    {m.name} — ({m.architecture})
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5 flex items-center gap-1">
                <Mic className="w-3.5 h-3.5 text-indigo-400" /> Reference Voice Profile (Zero-Shot Clone)
              </label>
              <select
                value={selectedVoicePath}
                onChange={(e) => setSelectedVoicePath(e.target.value)}
                className="w-full bg-slate-900 border border-border rounded-xl px-3.5 py-2.5 text-sm text-slate-200 focus:outline-none focus:border-primary"
              >
                <option value="">Default Neural Voice Profile</option>
                {voices.map((v) => (
                  <option key={v.id} value={v.file_path}>
                    [{v.genre}] {v.name}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Text Input Area with 2,000-Word Validation */}
          <div className="bg-card border border-border p-5 rounded-2xl space-y-3">
            <div className="flex justify-between items-center text-xs">
              <label className="font-semibold text-slate-300">Enter English Text Prompt</label>
              <span className={`font-mono font-medium ${isLimitExceeded ? 'text-rose-400' : 'text-slate-400'}`}>
                Words: <strong>{wordCount.toLocaleString()}</strong> / {MAX_WORDS.toLocaleString()} | Chars: {charCount.toLocaleString()}
              </span>
            </div>

            <textarea
              value={text}
              onChange={(e) => setText(e.target.value)}
              rows={6}
              placeholder="Type or paste your text here..."
              className="w-full bg-slate-900 border border-border rounded-xl p-4 text-sm text-slate-200 focus:outline-none focus:border-primary leading-relaxed"
            />

            {isLimitExceeded && (
              <div className="p-3 bg-rose-500/10 border border-rose-500/20 rounded-xl flex items-start gap-2.5 text-rose-300 text-xs">
                <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
                <div>
                  <strong>Maximum limit: 2,000 words</strong>
                  <p>Current input: {wordCount.toLocaleString()} words. Please reduce text before generating audio.</p>
                </div>
              </div>
            )}

            <button
              onClick={handleGenerate}
              disabled={isSynthesizing || isLimitExceeded || !text.trim()}
              className={`w-full py-3.5 rounded-xl font-bold text-sm shadow-xl flex items-center justify-center gap-2 transition-all ${
                isSynthesizing || isLimitExceeded || !text.trim()
                  ? 'bg-slate-800 text-slate-500 cursor-not-allowed'
                  : 'bg-gradient-to-r from-primary via-purple-600 to-accent text-white shadow-primary/30 hover:opacity-95 transform hover:scale-[1.01]'
              }`}
            >
              {isSynthesizing ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" /> Synthesizing Speech...
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4" /> Generate Speech Audio
                </>
              )}
            </button>
          </div>
        </div>

        {/* Right Column: Audio Player & Live Progress */}
        <div className="col-span-5 space-y-6">
          {activeJob && (
            <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} className="space-y-4">
              {/* Progress Card */}
              {isSynthesizing && (
                <div className="bg-card border border-border p-5 rounded-2xl space-y-3">
                  <div className="flex justify-between items-center text-xs">
                    <span className="font-semibold text-slate-300">{activeJob.message}</span>
                    <span className="font-mono text-indigo-400">{activeJob.progress_percent}%</span>
                  </div>
                  <div className="w-full bg-slate-900 h-2 rounded-full overflow-hidden">
                    <div className="bg-primary h-full transition-all duration-300" style={{ width: `${activeJob.progress_percent}%` }} />
                  </div>
                </div>
              )}

              {/* Completed Audio Player */}
              {activeJob.status === 'completed' && activeJob.output_wav_path && (
                <div className="space-y-4">
                  <AudioPlayer
                    filePath={activeJob.output_wav_path}
                    modelName={models.find((m) => m.id === activeJob.model_id)?.name || activeJob.model_id}
                  />

                  {/* Metric Badges */}
                  <div className="grid grid-cols-3 gap-3 text-center">
                    <div className="bg-slate-900 border border-border p-3 rounded-xl">
                      <span className="text-[10px] text-slate-500 uppercase font-semibold">Gen Time</span>
                      <p className="text-sm font-bold text-slate-200">{activeJob.gen_time_sec}s</p>
                    </div>
                    <div className="bg-slate-900 border border-border p-3 rounded-xl">
                      <span className="text-[10px] text-slate-500 uppercase font-semibold">Duration</span>
                      <p className="text-sm font-bold text-slate-200">{activeJob.duration_sec}s</p>
                    </div>
                    <div className="bg-slate-900 border border-border p-3 rounded-xl">
                      <span className="text-[10px] text-slate-500 uppercase font-semibold">RTF</span>
                      <p className="text-sm font-bold text-emerald-400">{activeJob.rtf}</p>
                    </div>
                  </div>
                </div>
              )}
            </motion.div>
          )}
        </div>
      </div>
    </div>
  );
};
