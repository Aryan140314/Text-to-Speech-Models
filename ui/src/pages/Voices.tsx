import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '../services/apiClient';
import { Mic, Sparkles, Filter, CheckCircle2 } from 'lucide-react';

export const Voices: React.FC = () => {
  const { data: voicesData, refetch } = useQuery({ queryKey: ['voices'], queryFn: apiClient.getVoices });
  const voices = voicesData?.voices || [];

  const [selectedGenre, setSelectedGenre] = useState<string>('All');
  const [cleaningId, setCleaningId] = useState<string | null>(null);

  const genres = ['All', ...Array.from(new Set(voices.map((v) => v.genre)))];
  const filteredVoices = selectedGenre === 'All' ? voices : voices.filter((v) => v.genre === selectedGenre);

  const handleCleanVoice = async (voicePath: string) => {
    setCleaningId(voicePath);
    try {
      await apiClient.cleanVoice(voicePath, 0.75);
      await refetch();
    } catch (e) {
      console.error(e);
    } finally {
      setCleaningId(null);
    }
  };

  return (
    <div className="p-8 max-w-6xl mx-auto space-y-8 select-none">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-slate-100 flex items-center gap-2">
            <Mic className="w-6 h-6 text-primary" /> Reference Voice Library
          </h2>
          <p className="text-xs text-slate-400">Manage speaker voice samples and clean audio datasets with DeepFilterNet3.</p>
        </div>
      </div>

      {/* Genre Filter Pills */}
      <div className="flex items-center gap-2 overflow-x-auto pb-2">
        <Filter className="w-4 h-4 text-slate-400 shrink-0" />
        {genres.map((g) => (
          <button
            key={g}
            onClick={() => setSelectedGenre(g)}
            className={`px-3.5 py-1.5 rounded-full text-xs font-semibold transition-all ${
              selectedGenre === g
                ? 'bg-primary text-white shadow-md shadow-primary/20'
                : 'bg-slate-800 text-slate-400 hover:text-slate-200'
            }`}
          >
            {g}
          </button>
        ))}
      </div>

      {/* Voice Cards Grid */}
      <div className="grid grid-cols-3 gap-6">
        {filteredVoices.map((v) => (
          <div key={v.id} className="bg-card border border-border p-5 rounded-2xl space-y-4 shadow-lg">
            <div className="flex items-start justify-between">
              <div>
                <span className="inline-block px-2.5 py-0.5 rounded-md bg-indigo-500/10 text-indigo-400 text-[10px] font-bold uppercase mb-1">
                  {v.genre}
                </span>
                <h4 className="font-bold text-slate-100 text-base">{v.name}</h4>
              </div>
            </div>

            <div className="text-xs text-slate-400 space-y-1">
              <p>Duration: <strong className="text-slate-200">{v.duration_sec}s</strong></p>
              <p>Sample Rate: <strong className="text-slate-200">{v.sample_rate} Hz</strong></p>
              <p>Size: <strong className="text-slate-200">{v.file_size_kb} KB</strong></p>
            </div>

            <div className="pt-2">
              <button
                onClick={() => handleCleanVoice(v.file_path)}
                disabled={cleaningId === v.file_path}
                className="w-full py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold flex items-center justify-center gap-1.5 transition-colors"
              >
                {cleaningId === v.file_path ? (
                  <>Cleaning Audio...</>
                ) : (
                  <>
                    <Sparkles className="w-3.5 h-3.5 text-purple-400" /> Clean DSP Audio
                  </>
                )}
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
