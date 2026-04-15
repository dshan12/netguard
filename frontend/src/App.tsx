import React, { useState } from 'react';
import { Shield, Activity, AlertTriangle, Globe, Cpu, LayoutDashboard } from 'lucide-react';
import NetworkMap from './components/NetworkMap';
import AlertTimeline from './components/AlertTimeline';
import MetricsGrid from './components/MetricsGrid';
import { useWebSocket } from './hooks/useWebSocket';
import AlertsPage from './pages/AlertsPage';
import MapPage from './pages/MapPage';
import MLInsightsPage from './pages/MLInsightsPage';

export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const { packets, alerts, metrics } = useWebSocket();

  return (
    <div className="flex h-screen bg-background text-slate-200 overflow-hidden">
      {/* Sidebar */}
      <nav className="w-16 md:w-64 border-r border-border flex flex-col items-center py-6 bg-card/50 backdrop-blur-sm">
        <div className="flex items-center gap-3 mb-10 px-4">
          <div className="p-2 bg-accent-cyan/10 rounded-lg">
            <Shield className="w-6 h-6 text-accent-cyan" />
          </div>
          <span className="hidden md:block font-bold text-lg tracking-tight">SECURE<span className="text-accent-cyan">ANALYSIS</span></span>
        </div>
        
        <div className="flex-1 w-full space-y-2 px-3">
          <NavItem icon={<LayoutDashboard />} label="Dashboard" active={activeTab === 'dashboard'} onClick={() => setActiveTab('dashboard')} />
          <NavItem icon={<AlertTriangle />} label="Alerts" active={activeTab === 'alerts'} onClick={() => setActiveTab('alerts')} />
          <NavItem icon={<Globe />} label="Network Map" active={activeTab === 'map'} onClick={() => setActiveTab('map')} />
          <NavItem icon={<Cpu />} label="ML Insights" active={activeTab === 'ml'} onClick={() => setActiveTab('ml')} />
        </div>
        
        <div className="px-3 w-full mt-auto">
          <div className="p-4 bg-accent-green/5 border border-accent-green/20 rounded-xl hidden md:block">
            <div className="flex items-center gap-2 mb-2">
              <div className="w-2 h-2 rounded-full bg-accent-green animate-pulse" />
              <span className="text-xs font-medium text-accent-green">SYSTEM LIVE</span>
            </div>
            <p className="text-[10px] text-slate-400">Monitoring 1,242 flows/sec</p>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="flex-1 flex flex-col min-w-0 overflow-hidden relative">
        <header className="h-16 border-b border-border flex items-center justify-between px-8 bg-background/80 backdrop-blur-md z-10">
          <h1 className="text-xl font-semibold capitalize">{activeTab}</h1>
          <div className="flex items-center gap-6">
            <div className="text-right">
              <p className="text-[10px] text-slate-500 uppercase tracking-widest font-bold">Current Load</p>
              <p className="text-sm font-mono text-accent-cyan">{(metrics?.packets_per_second || 0).toFixed(1)} PKTS/S</p>
            </div>
            <div className="h-8 w-px bg-border" />
            <button className="flex items-center gap-2 px-3 py-1.5 bg-accent-red/10 border border-accent-red/20 rounded-lg text-accent-red text-xs font-bold hover:bg-accent-red/20 transition-all">
              <AlertTriangle className="w-4 h-4" />
              EMERGENCY STOP
            </button>
          </div>
        </header>

        <div className="flex-1 overflow-auto p-8 cyber-grid">
          {activeTab === 'dashboard' && (
            <div className="space-y-8 animate-in fade-in duration-500">
              <MetricsGrid metrics={metrics} />
              
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                <div className="lg:col-span-2 bg-card border border-border rounded-2xl overflow-hidden h-[500px] flex flex-col shadow-2xl">
                   <div className="p-4 border-b border-border bg-background/50 flex justify-between items-center">
                     <h3 className="text-sm font-bold flex items-center gap-2">
                       <Globe className="w-4 h-4 text-accent-cyan" />
                       LIVE TRAFFIC VISUALIZER
                     </h3>
                     <span className="text-[10px] font-mono text-slate-500">REALTIME STREAM</span>
                   </div>
                   <div className="flex-1 bg-black/40 relative">
                     <NetworkMap packets={packets} />
                   </div>
                </div>
                
                <div className="bg-card border border-border rounded-2xl overflow-hidden h-[500px] flex flex-col shadow-2xl">
                   <div className="p-4 border-b border-border bg-background/50 flex justify-between items-center">
                     <h3 className="text-sm font-bold flex items-center gap-2">
                       <Activity className="w-4 h-4 text-accent-red" />
                       THREAT TIMELINE
                     </h3>
                     <span className="text-xs text-accent-red font-bold">{(alerts?.length || 0)} NEW</span>
                   </div>
                   <div className="flex-1 overflow-y-auto">
                     <AlertTimeline alerts={alerts} />
                   </div>
                </div>
              </div>
            </div>
          )}
          {activeTab === 'alerts' && <AlertsPage />}
          {activeTab === 'map' && <MapPage packets={packets} />}
          {activeTab === 'ml' && <MLInsightsPage />}
        </div>
      </main>
    </div>
  );
}

function NavItem({ icon, label, active, onClick }: { icon: React.ReactNode, label: string, active?: boolean, onClick: () => void }) {
  return (
    <button 
      onClick={onClick}
      className={`w-full flex items-center gap-4 px-3 py-3 rounded-xl transition-all ${
        active 
          ? 'bg-accent-cyan/10 text-accent-cyan' 
          : 'text-slate-500 hover:bg-slate-800/50 hover:text-slate-300'
      }`}
    >
      <div className={`${active ? 'scale-110' : 'scale-100'} transition-transform`}>
        {React.cloneElement(icon as React.ReactElement, { className: 'w-5 h-5' })}
      </div>
      <span className="hidden md:block font-medium text-sm">{label}</span>
      {active && <div className="hidden md:block ml-auto w-1.5 h-1.5 rounded-full bg-accent-cyan shadow-[0_0_8px_#06b6d4]" />}
    </button>
  );
}
