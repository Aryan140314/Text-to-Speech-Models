import React, { useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '../../services/apiClient';
import { useAppStore } from '../../stores/appStore';
import { Cpu, HardDrive, Zap, CheckCircle, AlertTriangle } from 'lucide-react';

export const HardwareBanner: React.FC = () => {
  const { setHardware } = useAppStore();

  const { data: hw, isLoading } = useQuery({
    queryKey: ['hardware'],
    queryFn: apiClient.getHardware,
    refetchInterval: 5000,
  });

  useEffect(() => {
    if (hw) setHardware(hw);
  }, [hw, setHardware]);

  if (isLoading || !hw) {
    return (
      <div className="h-12 bg-slate-900 border-b border-border flex items-center justify-between px-6 text-xs text-slate-400">
        <span>Inspecting system hardware...</span>
      </div>
    );
  }

  const isGpu = hw.gpu.available;

  return (
    <div className="h-12 bg-slate-900/80 border-b border-border flex items-center justify-between px-6 text-xs text-slate-300 backdrop-blur-md">
      <div className="flex items-center gap-6">
        {/* GPU status badge */}
        <div className="flex items-center gap-2">
          {isGpu ? (
            <span className="flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-emerald-500/10 text-emerald-400 font-semibold border border-emerald-500/20">
              <CheckCircle className="w-3.5 h-3.5" /> CUDA GPU Active
            </span>
          ) : (
            <span className="flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-amber-500/10 text-amber-400 font-semibold border border-amber-500/20">
              <AlertTriangle className="w-3.5 h-3.5" /> CPU Mode
            </span>
          )}
          <span className="font-medium text-slate-200">
            {isGpu ? hw.gpu.name : hw.cpu_name}
          </span>
        </div>

        {/* VRAM / RAM Meter */}
        <div className="flex items-center gap-4 text-slate-400">
          {isGpu && (
            <div className="flex items-center gap-1">
              <Zap className="w-3.5 h-3.5 text-indigo-400" />
              <span>VRAM: <strong className="text-slate-200">{hw.gpu.vram_used_gb} GB</strong> / {hw.gpu.vram_total_gb} GB</span>
            </div>
          )}
          <div className="flex items-center gap-1">
            <HardDrive className="w-3.5 h-3.5 text-purple-400" />
            <span>RAM: <strong className="text-slate-200">{hw.ram_used_gb} GB</strong> / {hw.ram_total_gb} GB</span>
          </div>
        </div>
      </div>

      <div className="text-slate-500 font-mono text-[11px]">
        PyTorch v{hw.cuda.pytorch_version || '2.x'}
      </div>
    </div>
  );
};
