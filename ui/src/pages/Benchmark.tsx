import React, { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { apiClient } from '../services/apiClient';
import { BarChart2, Play, Loader2 } from 'lucide-react';
import { BenchmarkItem } from '../types/api';

export const Benchmark: React.FC = () => {
  const [results, setResults] = useState<BenchmarkItem[]>([]);

  const runMutation = useMutation({
    mutationFn: () => apiClient.runBenchmark(),
    onSuccess: (data) => {
      setResults(data.results || []);
    },
  });

  return (
    <div className="p-8 max-w-6xl mx-auto space-y-8 select-none">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-slate-100 flex items-center gap-2">
            <BarChart2 className="w-6 h-6 text-primary" /> Multi-Model Performance Benchmarking
          </h2>
          <p className="text-xs text-slate-400">Benchmark real inference latency, audio duration, and Real-Time Factor (RTF) across models.</p>
        </div>
        <button
          onClick={() => runMutation.mutate()}
          disabled={runMutation.isPending}
          className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-primary hover:bg-indigo-600 text-white text-xs font-semibold shadow-lg shadow-primary/20 transition-all"
        >
          {runMutation.isPending ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" /> Benchmarking Models...
            </>
          ) : (
            <>
              <Play className="w-4 h-4" /> Run Benchmark Suite
            </>
          )}
        </button>
      </div>

      {/* Benchmark Results Table */}
      {results.length > 0 && (
        <div className="bg-card border border-border rounded-2xl overflow-hidden shadow-xl">
          <table className="w-full text-left text-xs text-slate-300">
            <thead className="bg-slate-900 text-slate-400 font-semibold border-b border-border uppercase">
              <tr>
                <th className="p-4">Model Name</th>
                <th className="p-4">Words</th>
                <th className="p-4">Device</th>
                <th className="p-4">Gen Time</th>
                <th className="p-4">Audio Duration</th>
                <th className="p-4">Real-Time Factor (RTF)</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {results.map((r) => (
                <tr key={r.model_id} className="hover:bg-slate-800/50">
                  <td className="p-4 font-bold text-slate-100">{r.model_name}</td>
                  <td className="p-4">{r.word_count}</td>
                  <td className="p-4 uppercase font-semibold text-indigo-400">{r.device}</td>
                  <td className="p-4 font-mono">{r.gen_time_sec}s</td>
                  <td className="p-4 font-mono">{r.audio_duration_sec}s</td>
                  <td className="p-4 font-mono font-bold text-emerald-400">{r.rtf}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};
