import React, { useRef, useState, useEffect } from 'react';
import { Play, Pause, Download, Folder, Volume2, VolumeX, RotateCcw } from 'lucide-react';
import { apiClient } from '../../services/apiClient';

interface AudioPlayerProps {
  filePath: string;
  modelName?: string;
  voiceName?: string;
}

export const AudioPlayer: React.FC<AudioPlayerProps> = ({ filePath, modelName = 'F5-TTS', voiceName = 'Reference Voice' }) => {
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [volume, setVolume] = useState(1);
  const [isMuted, setIsMuted] = useState(false);

  const audioUrl = apiClient.getAudioUrl(filePath);

  useEffect(() => {
    setIsPlaying(false);
    setCurrentTime(0);
  }, [filePath]);

  const togglePlay = () => {
    if (!audioRef.current) return;
    if (isPlaying) {
      audioRef.current.pause();
    } else {
      audioRef.current.play();
    }
    setIsPlaying(!isPlaying);
  };

  const handleTimeUpdate = () => {
    if (audioRef.current) {
      setCurrentTime(audioRef.current.currentTime);
    }
  };

  const handleLoadedMetadata = () => {
    if (audioRef.current) {
      setDuration(audioRef.current.duration);
    }
  };

  const handleSeek = (e: React.ChangeEvent<HTMLInputElement>) => {
    const val = parseFloat(e.target.value);
    if (audioRef.current) {
      audioRef.current.currentTime = val;
      setCurrentTime(val);
    }
  };

  const handleOpenFolder = () => {
    if (window.electronAPI && filePath) {
      window.electronAPI.openOutputFolder(filePath);
    }
  };

  const formatTime = (sec: number) => {
    if (isNaN(sec)) return '0:00';
    const m = Math.floor(sec / 60);
    const s = Math.floor(sec % 60);
    return `${m}:${s < 10 ? '0' : ''}${s}`;
  };

  return (
    <div className="bg-card border border-border rounded-2xl p-5 shadow-xl space-y-4">
      <audio
        ref={audioRef}
        src={audioUrl}
        onTimeUpdate={handleTimeUpdate}
        onLoadedMetadata={handleLoadedMetadata}
        onEnded={() => setIsPlaying(false)}
      />

      <div className="flex items-center justify-between">
        <div>
          <h4 className="font-semibold text-slate-100 text-sm">{modelName} Speech Synthesis</h4>
          <p className="text-xs text-slate-400">Voice: <strong className="text-indigo-400">{voiceName}</strong></p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={handleOpenFolder}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-medium text-slate-300 transition-colors"
          >
            <Folder className="w-3.5 h-3.5" /> Open Folder
          </button>
          <a
            href={audioUrl}
            download
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-primary hover:bg-indigo-600 text-xs font-medium text-white shadow-md shadow-primary/20 transition-all"
          >
            <Download className="w-3.5 h-3.5" /> Download WAV
          </a>
        </div>
      </div>

      {/* Progress slider & time display */}
      <div className="space-y-1.5">
        <input
          type="range"
          min={0}
          max={duration || 100}
          value={currentTime}
          onChange={handleSeek}
          className="w-full h-2 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-primary"
        />
        <div className="flex justify-between text-[11px] text-slate-400 font-mono">
          <span>{formatTime(currentTime)}</span>
          <span>{formatTime(duration)}</span>
        </div>
      </div>

      {/* Audio Playback Controls */}
      <div className="flex items-center justify-between pt-2">
        <button
          onClick={togglePlay}
          className="w-12 h-12 rounded-full bg-primary hover:bg-indigo-600 text-white flex items-center justify-center shadow-lg shadow-primary/30 transition-all transform hover:scale-105 active:scale-95"
        >
          {isPlaying ? <Pause className="w-5 h-5 fill-current" /> : <Play className="w-5 h-5 fill-current ml-0.5" />}
        </button>

        <div className="flex items-center gap-3">
          <button
            onClick={() => {
              if (audioRef.current) {
                audioRef.current.currentTime = 0;
                setCurrentTime(0);
              }
            }}
            className="p-2 rounded-lg bg-slate-800 text-slate-400 hover:text-slate-200 text-xs"
          >
            <RotateCcw className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
};
