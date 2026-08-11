import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Sidebar } from '../components/layout/Sidebar';
import { HardwareBanner } from '../components/layout/HardwareBanner';
import { Home } from '../pages/Home';
import { Generate } from '../pages/Generate';
import { Voices } from '../pages/Voices';
import { Models } from '../pages/Models';
import { History } from '../pages/History';
import { Benchmark } from '../pages/Benchmark';
import { Settings } from '../pages/Settings';

const queryClient = new QueryClient();

export const App: React.FC = () => {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <div className="flex h-screen w-screen overflow-hidden bg-background">
          <Sidebar />
          <div className="flex-1 flex flex-col min-w-0">
            <HardwareBanner />
            <main className="flex-1 overflow-y-auto">
              <Routes>
                <Route path="/" element={<Home />} />
                <Route path="/generate" element={<Generate />} />
                <Route path="/voices" element={<Voices />} />
                <Route path="/models" element={<Models />} />
                <Route path="/history" element={<History />} />
                <Route path="/benchmark" element={<Benchmark />} />
                <Route path="/settings" element={<Settings />} />
              </Routes>
            </main>
          </div>
        </div>
      </Router>
    </QueryClientProvider>
  );
};
