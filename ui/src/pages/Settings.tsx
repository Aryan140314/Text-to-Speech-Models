import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '../services/apiClient';
import { Settings as SettingsIcon, HardDrive, Cpu, ShieldCheck } from 'lucide-react';

export const Settings: React.FC = () => {
  const { data: settings } = useQuery({ queryKey: ['settings'], queryFn: apiClient.getSettings });
  const { data: hw } = useQuery({ queryKey: ['hardware'], queryFn: apiClient.getHardware });

  return (
    <div className="p-8 max-w-6xl mx-auto space-y-8 select-none">
      <div>
        <h2 className="text-2xl font-bold text-slate-100 flex items-center gap-2">
          <SettingsIcon className="w-6 h-6 text-primary" /> App Settings & System Diagnostics
        </h2>
        <p className="text-xs text-slate-400">View configuration limits and system paths.</p>
      </div>

      <div className="grid grid-cols-2 gap-6">
        {/* System Settings */}
        <div className="bg-card border border-border p-6 rounded-2xl space-y-4">
          <h3 className="font-bold text-slate-100 text-base flex items-center gap-2">
            <ShieldCheck className="w-5 h-5 text-indigo-400" /> General Configuration
          </h3>
          <div className="space-y-3 text-xs text-slate-300">
            <div className="p-3 bg-slate-900 rounded-xl flex justify-between">
              <span>Application Limit</span>
              <strong className="text-slate-100">2,000 Words / Request</strong>
            </div>
            <div className="p-3 bg-slate-900 rounded-xl flex justify-between">
              <span>Execution Mode</span>
              <strong className="text-emerald-400">100% Offline CUDA GPU</strong>
            </div>
          </div>
        </div>

        {/* Directory Paths */}
        <div className="bg-card border border-border p-6 rounded-2xl space-y-4">
          <h3 className="font-bold text-slate-100 text-base flex items-center gap-2">
            <HardDrive className="w-5 h-5 text-purple-400" /> User Data Paths
          </h3>
          <div className="space-y-2 text-xs font-mono text-slate-400 overflow-x-auto">
            <p>Voices: <span className="text-slate-200">{settings?.voices_dir || 'N/A'}</span></p>
            <p>Outputs: <span className="text-slate-200">{settings?.outputs_dir || 'N/A'}</span></p>
            <p>Cache: <span className="text-slate-200">{settings?.cache_dir || 'N/A'}</span></p>
            <p>Logs: <span className="text-slate-200">{settings?.logs_dir || 'N/A'}</span></p>
          </div>
        </div>
      </div>
    </div>
  );
};
