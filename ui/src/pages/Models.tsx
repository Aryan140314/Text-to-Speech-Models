import React from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { apiClient } from '../services/apiClient';
import { Cpu, CheckCircle2, Zap, HardDrive } from 'lucide-react';

export const Models: React.FC = () => {
  const { data, refetch } = useQuery({ queryKey: ['models'], queryFn: apiClient.getModels });
  const models = data?.models || [];
  const activeId = data?.active_model_id || 'f5tts';

  const loadMutation = useMutation({
    mutationFn: (modelId: string) => apiClient.loadModel(modelId),
    onSuccess: () => refetch(),
  });

  return (
    <div className="p-8 max-w-6xl mx-auto space-y-8 select-none">
      <div>
        <h2 className="text-2xl font-bold text-slate-100 flex items-center gap-2">
          <Cpu className="w-6 h-6 text-primary" /> Neural Model Manager
        </h2>
        <p className="text-xs text-slate-400">View and manage loaded zero-shot neural synthesis backends.</p>
      </div>

      <div className="grid grid-cols-2 gap-6">
        {models.map((m) => {
          const isActive = m.id === activeId;
          return (
            <div
              key={m.id}
              className={`bg-card border p-6 rounded-2xl space-y-4 transition-all ${
                isActive ? 'border-primary shadow-xl shadow-primary/10' : 'border-border'
              }`}
            >
              <div className="flex items-start justify-between">
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <h3 className="font-bold text-slate-100 text-lg">{m.name}</h3>
                    {isActive && (
                      <span className="px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 text-[10px] font-bold border border-emerald-500/20">
                        Active Engine
                      </span>
                    )}
                  </div>
                  <p className="text-xs text-slate-400 font-mono">{m.architecture}</p>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3 text-xs">
                <div className="p-3 bg-slate-900 rounded-xl">
                  <span className="text-slate-500 block text-[10px]">Zero-Shot Cloning</span>
                  <strong className="text-slate-200">{m.supports_cloning ? 'Supported' : 'No'}</strong>
                </div>
                <div className="p-3 bg-slate-900 rounded-xl">
                  <span className="text-slate-500 block text-[10px]">Sample Rate</span>
                  <strong className="text-slate-200">{m.default_sample_rate} Hz</strong>
                </div>
              </div>

              <button
                onClick={() => loadMutation.mutate(m.id)}
                disabled={isActive || loadMutation.isPending}
                className={`w-full py-2.5 rounded-xl font-semibold text-xs transition-all ${
                  isActive
                    ? 'bg-slate-800 text-slate-500 cursor-default'
                    : 'bg-primary hover:bg-indigo-600 text-white shadow-md shadow-primary/20'
                }`}
              >
                {isActive ? 'Currently Active' : 'Load Model'}
              </button>
            </div>
          );
        })}
      </div>
    </div>
  );
};
