import React from 'react';
import {
  ShieldCheck,
  Scale,
  FileText,
  GitCompare,
  TrendingUp,
  Share2,
  Sparkles,
  ExternalLink,
} from 'lucide-react';

interface NavbarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  systemStatus: { healthy: boolean; docCount: number };
}

export const Navbar: React.FC<NavbarProps> = ({
  activeTab,
  setActiveTab,
  systemStatus,
}) => {
  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: ShieldCheck },
    { id: 'explorer', label: 'Policy Explorer', icon: FileText },
    { id: 'compare', label: 'Comparison', icon: GitCompare },
    { id: 'impact', label: 'Impact Analysis', icon: TrendingUp },
    { id: 'graph', label: 'Regulatory Graph', icon: Share2 },
    { id: 'investigation', label: 'AI Investigation', icon: Sparkles },
  ];

  return (
    <header className="sticky top-0 z-50 bg-slate-900/90 backdrop-blur-md border-b border-slate-800 text-slate-100">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo & National Emblem Branding */}
          <div className="flex items-center space-x-3 cursor-pointer" onClick={() => setActiveTab('dashboard')}>
            <div className="p-2 bg-gradient-to-br from-indigo-500 to-emerald-600 rounded-lg shadow-lg">
              <Scale className="w-6 h-6 text-white" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="font-bold text-lg tracking-tight bg-gradient-to-r from-white via-slate-200 to-indigo-300 bg-clip-text text-transparent">
                  Policy Intel
                </span>
                <span className="px-2 py-0.5 text-[10px] font-semibold tracking-wide bg-indigo-500/20 text-indigo-400 border border-indigo-500/30 rounded-full">
                  CENTRAL GOVT
                </span>
              </div>
              <p className="text-[11px] text-slate-400 font-mono">
                Regulatory Change Intelligence Platform
              </p>
            </div>
          </div>

          {/* Navigation Links */}
          <nav className="hidden md:flex space-x-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = activeTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => setActiveTab(item.id)}
                  className={`flex items-center space-x-1.5 px-3 py-2 rounded-md text-xs font-medium transition-all ${
                    isActive
                      ? 'bg-indigo-600/20 text-indigo-300 border border-indigo-500/40 shadow-sm'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
                  }`}
                >
                  <Icon className={`w-4 h-4 ${isActive ? 'text-indigo-400' : 'text-slate-400'}`} />
                  <span>{item.label}</span>
                </button>
              );
            })}
          </nav>

          {/* Live System Readiness Badge */}
          <div className="flex items-center space-x-3">
            <div className="flex items-center space-x-2 px-2.5 py-1 rounded-full bg-slate-800/80 border border-slate-700/80 text-xs">
              <span
                className={`w-2 h-2 rounded-full ${
                  systemStatus.healthy ? 'bg-emerald-400 animate-pulse' : 'bg-amber-400'
                }`}
              />
              <span className="text-[11px] font-mono text-slate-300">
                {systemStatus.healthy ? `${systemStatus.docCount} Policies Active` : 'Initializing'}
              </span>
            </div>
            <a
              href="/api/docs"
              target="_blank"
              rel="noreferrer"
              className="text-slate-400 hover:text-slate-200 text-xs flex items-center space-x-1 px-2 py-1 rounded hover:bg-slate-800"
              title="Open OpenAPI Specifications"
            >
              <span>API</span>
              <ExternalLink className="w-3 h-3" />
            </a>
          </div>
        </div>
      </div>

      {/* Mobile Nav Bar */}
      <div className="md:hidden flex overflow-x-auto px-4 py-2 space-x-2 border-t border-slate-800/80 bg-slate-900">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              className={`flex items-center space-x-1 px-2.5 py-1.5 rounded text-xs whitespace-nowrap ${
                isActive
                  ? 'bg-indigo-600 text-white'
                  : 'text-slate-400 bg-slate-800'
              }`}
            >
              <Icon className="w-3.5 h-3.5" />
              <span>{item.label}</span>
            </button>
          );
        })}
      </div>
    </header>
  );
};
