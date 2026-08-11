import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Zap, Mic, Cpu, ShieldCheck, Sparkles, ArrowRight } from 'lucide-react';
import { motion } from 'framer-motion';

export const Home: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div className="p-8 max-w-6xl mx-auto space-y-8 select-none">
      {/* Hero Header */}
      <motion.div
        initial={{ opacity: 0, y: 15 }}
        animate={{ opacity: 1, y: 0 }}
        className="relative overflow-hidden rounded-3xl bg-gradient-to-r from-indigo-900/60 via-purple-900/40 to-slate-900 border border-indigo-500/20 p-10 shadow-2xl"
      >
        <div className="relative z-10 max-w-2xl space-y-4">
          <span className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/20 border border-indigo-500/30 text-indigo-300 text-xs font-semibold">
            <Sparkles className="w-3.5 h-3.5" /> Production ElevenLabs Alternative
          </span>
          <h1 className="text-4xl font-extrabold tracking-tight text-white leading-tight">
            Local AI Voice Studio & Zero-Shot Synthesis Laboratory
          </h1>
          <p className="text-slate-300 text-sm leading-relaxed">
            Generate ultra-realistic voice audio on local hardware. Benchmark 7 state-of-the-art neural engines, clone any voice from 5 seconds of sample audio, and clean audio datasets with DeepFilterNet3.
          </p>
          <div className="pt-2 flex items-center gap-4">
            <button
              onClick={() => navigate('/generate')}
              className="flex items-center gap-2 px-6 py-3 rounded-xl bg-primary hover:bg-indigo-600 text-white font-semibold text-sm shadow-xl shadow-primary/30 transition-all transform hover:scale-105"
            >
              <Zap className="w-4 h-4" /> Open Generation Studio <ArrowRight className="w-4 h-4" />
            </button>
            <button
              onClick={() => navigate('/voices')}
              className="flex items-center gap-2 px-6 py-3 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 font-semibold text-sm transition-all"
            >
              <Mic className="w-4 h-4" /> Voice Library
            </button>
          </div>
        </div>
      </motion.div>

      {/* Feature Cards Grid */}
      <div className="grid grid-cols-3 gap-6">
        <div className="bg-card border border-border p-6 rounded-2xl space-y-3">
          <div className="w-12 h-12 rounded-xl bg-indigo-500/10 text-indigo-400 flex items-center justify-center">
            <Zap className="w-6 h-6" />
          </div>
          <h3 className="font-bold text-slate-100 text-lg">7 Zero-Shot Engines</h3>
          <p className="text-xs text-slate-400 leading-relaxed">
            F5-TTS, Chatterbox Turbo, Fish Speech S2, OmniVoice, CosyVoice 3, XTTS-v2, and IndexTTS2.
          </p>
        </div>

        <div className="bg-card border border-border p-6 rounded-2xl space-y-3">
          <div className="w-12 h-12 rounded-xl bg-purple-500/10 text-purple-400 flex items-center justify-center">
            <ShieldCheck className="w-6 h-6" />
          </div>
          <h3 className="font-bold text-slate-100 text-lg">100% Offline & Local</h3>
          <p className="text-xs text-slate-400 leading-relaxed">
            All synthesis runs locally on your NVIDIA CUDA GPU or CPU. Zero cloud dependencies or subscription API fees.
          </p>
        </div>

        <div className="bg-card border border-border p-6 rounded-2xl space-y-3">
          <div className="w-12 h-12 rounded-xl bg-pink-500/10 text-pink-400 flex items-center justify-center">
            <Cpu className="w-6 h-6" />
          </div>
          <h3 className="font-bold text-slate-100 text-lg">2,000-Word Pipeline</h3>
          <p className="text-xs text-slate-400 leading-relaxed">
            Intelligent sentence-aware chunking prevents context overflow while delivering studio-quality long form speech.
          </p>
        </div>
      </div>
    </div>
  );
};
