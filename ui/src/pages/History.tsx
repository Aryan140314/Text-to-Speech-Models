import React from 'react';
import { History as HistoryIcon, Music, Play } from 'lucide-react';

export const History: React.FC = () => {
  return (
    <div className="p-8 max-w-6xl mx-auto space-y-8 select-none">
      <div>
        <h2 className="text-2xl font-bold text-slate-100 flex items-center gap-2">
          <HistoryIcon className="w-6 h-6 text-primary" /> Audio Output History
        </h2>
        <p className="text-xs text-slate-400">View and play previously synthesized voice WAV files.</p>
      </div>

      <div className="bg-card border border-border rounded-2xl p-8 text-center text-slate-400 space-y-3">
        <Music className="w-12 h-12 text-slate-600 mx-auto" />
        <h4 className="font-bold text-slate-200 text-base">Generated Audio Gallery</h4>
        <p className="text-xs text-slate-400 max-w-md mx-auto">
          All audio files generated in your synthesis sessions are saved automatically to your outputs folder.
        </p>
      </div>
    </div>
  );
};
