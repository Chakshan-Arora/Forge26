import React, { useState, useEffect } from 'react';
import { Navbar } from './components/Navbar';
import { Dashboard } from './pages/Dashboard';
import { PolicyExplorer } from './pages/PolicyExplorer';
import { PolicyComparison } from './pages/PolicyComparison';
import { ImpactAnalysis } from './pages/ImpactAnalysis';
import { RegulatoryGraph } from './pages/RegulatoryGraph';
import { AiInvestigation } from './pages/AiInvestigation';
import { api } from './services/api';
import { Scale } from 'lucide-react';

export function App() {
  const [activeTab, setActiveTab] = useState<string>('dashboard');
  const [navContext, setNavContext] = useState<any>(null);
  const [systemStatus, setSystemStatus] = useState({ healthy: false, docCount: 0 });

  useEffect(() => {
    async function checkHealth() {
      try {
        const data = await api.getHealth();
        setSystemStatus({
          healthy: data.status === 'healthy',
          docCount: data.registered_documents,
        });
      } catch (err) {
        console.warn('Backend connection pending or offline:', err);
      }
    }
    checkHealth();
  }, []);

  const handleNavigate = (tab: string, context?: any) => {
    setActiveTab(tab);
    setNavContext(context || null);
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans selection:bg-indigo-600 selection:text-white">
      {/* Global Regulatory Top Header */}
      <Navbar
        activeTab={activeTab}
        setActiveTab={(tab) => {
          setActiveTab(tab);
          setNavContext(null);
        }}
        systemStatus={systemStatus}
      />

      {/* Main View Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {activeTab === 'dashboard' && <Dashboard onNavigate={handleNavigate} />}
        {activeTab === 'explorer' && (
          <PolicyExplorer initialScheme={navContext?.scheme} />
        )}
        {activeTab === 'compare' && <PolicyComparison />}
        {activeTab === 'impact' && <ImpactAnalysis />}
        {activeTab === 'graph' && <RegulatoryGraph />}
        {activeTab === 'investigation' && <AiInvestigation />}
      </main>

      {/* Authoritative Regulatory Footer */}
      <footer className="bg-slate-900 border-t border-slate-800/80 py-6 text-slate-400 text-xs mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-3">
          <div className="flex items-center space-x-2">
            <Scale className="w-4 h-4 text-indigo-400" />
            <span className="font-semibold text-slate-300">Policy Intel Regulatory Platform</span>
            <span>&bull;</span>
            <span>Indian Central Government Policies & Scholarships</span>
          </div>
          <div className="flex items-center space-x-4 text-slate-500 font-mono text-[11px]">
            <span>MoE & MoSJE Notifications</span>
            <span>&bull;</span>
            <span>Deterministic Temporal Reasoning</span>
            <span>&bull;</span>
            <span>Verifiable Provenance</span>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;
