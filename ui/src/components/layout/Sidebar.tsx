import React from 'react';
import { NavLink } from 'react-router-dom';
import { Mic, Zap, Cpu, History, BarChart2, Settings, Volume2, Sparkles } from 'lucide-react';

const navItems = [
  { path: '/', label: 'Home', icon: Sparkles },
  { path: '/generate', label: 'Generate', icon: Zap },
  { path: '/voices', label: 'Voices', icon: Mic },
  { path: '/models', label: 'Models', icon: Cpu },
  { path: '/history', label: 'History', icon: History },
  { path: '/benchmark', label: 'Benchmark', icon: BarChart2 },
  { path: '/settings', label: 'Settings', icon: Settings },
];

export const Sidebar: React.FC = () => {
  return (
    <aside className="w-64 bg-surface border-r border-border flex flex-col h-screen select-none">
      {/* App Branding */}
      <div className="p-6 border-b border-border flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-primary to-accent flex items-center justify-center shadow-lg shadow-primary/20">
          <Volume2 className="w-6 h-6 text-white" />
        </div>
        <div>
          <h1 className="font-bold text-lg tracking-tight bg-gradient-to-r from-indigo-400 via-purple-300 to-pink-400 bg-clip-text text-transparent">
            TTS Studio
          </h1>
          <p className="text-xs text-slate-400">Local ElevenLabs AI</p>
        </div>
      </div>

      {/* Navigation Links */}
      <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
        {navItems.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                `flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all duration-150 ${
                  isActive
                    ? 'bg-primary text-white shadow-md shadow-primary/25 font-semibold'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                }`
              }
            >
              <Icon className="w-5 h-5" />
              <span>{item.label}</span>
            </NavLink>
          );
        })}
      </nav>

      {/* Footer Info */}
      <div className="p-4 border-t border-border text-xs text-slate-500 text-center">
        <p>TTS Studio v1.0.0</p>
        <p className="text-[10px] text-slate-600 mt-1">100% Offline CUDA Engine</p>
      </div>
    </aside>
  );
};
