import { useState, useEffect } from 'react';
import { Search, ChevronDown, ChevronUp, CheckCircle, AlertTriangle, Loader2, Globe } from 'lucide-react';
import { format } from 'date-fns';
import GeoMap from '../components/GeoMap';

interface Alert {
  id: number;
  timestamp: string;
  alert_type: string;
  severity: string;
  src_ip: string;
  dst_ip: string;
  description: string;
  resolved: boolean;
}

const severityColors: Record<string, string> = {
  Critical: 'bg-accent-red/20 text-accent-red border-accent-red',
  High: 'bg-orange-500/20 text-orange-400 border-orange-500',
  Medium: 'bg-accent-yellow/20 text-accent-yellow border-accent-yellow',
  Low: 'bg-blue-500/20 text-blue-400 border-blue-500',
};

const severityDots: Record<string, string> = {
  Critical: 'bg-accent-red',
  High: 'bg-orange-500',
  Medium: 'bg-accent-yellow',
  Low: 'bg-blue-500',
};

interface GeoSource {
  ip: string;
  latitude: number;
  longitude: number;
  threat_score: number;
  country: string;
  city: string;
  total_alerts: number;
  categories: string;
}

export default function AlertsPage() {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [severityFilter, setSeverityFilter] = useState('All');
  const [searchIp, setSearchIp] = useState('');
  const [expandedId, setExpandedId] = useState<number | null>(null);
  const [resolvingId, setResolvingId] = useState<number | null>(null);
  const [geoSources, setGeoSources] = useState<GeoSource[]>([]);

  const fetchAlerts = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch('/api/alerts/');
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      setAlerts(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch alerts');
    } finally {
      setLoading(false);
    }
  };

  const fetchGeoSources = async () => {
    try {
      const res = await fetch('/api/geo/sources');
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      setGeoSources(data);
    } catch (err) {
      console.error('Failed to fetch geo sources:', err);
    }
  };

  useEffect(() => {
    fetchAlerts();
    fetchGeoSources();
  }, []);

  const handleResolve = async (id: number) => {
    setResolvingId(id);
    try {
      const res = await fetch(`/api/alerts/${id}/resolve`, { method: 'POST' });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      setAlerts(prev => prev.map(a => a.id === id ? { ...a, resolved: true } : a));
    } catch (err) {
      console.error('Failed to resolve alert:', err);
    } finally {
      setResolvingId(null);
    }
  };

  const filteredAlerts = alerts.filter(alert => {
    if (severityFilter !== 'All' && alert.severity !== severityFilter) return false;
    if (searchIp && !alert.src_ip?.includes(searchIp) && !alert.dst_ip?.includes(searchIp)) return false;
    return true;
  });

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-8 h-8 text-accent-cyan animate-spin" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center h-64 gap-4">
        <AlertTriangle className="w-12 h-12 text-accent-red" />
        <p className="text-accent-red font-medium">{error}</p>
        <button onClick={fetchAlerts} className="px-4 py-2 bg-accent-cyan/10 border border-accent-cyan/30 rounded-lg text-accent-cyan text-sm hover:bg-accent-cyan/20 transition-all">
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-in fade-in duration-500">
      <div className="flex flex-wrap gap-4 items-center">
        <select
          value={severityFilter}
          onChange={e => setSeverityFilter(e.target.value)}
          className="bg-card border border-border rounded-lg px-3 py-2 text-sm text-slate-300 focus:outline-none focus:border-accent-cyan"
        >
          <option>All</option>
          <option>Critical</option>
          <option>High</option>
          <option>Medium</option>
          <option>Low</option>
        </select>
        <div className="relative flex-1 max-w-xs">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
          <input
            type="text"
            placeholder="Search by IP..."
            value={searchIp}
            onChange={e => setSearchIp(e.target.value)}
            className="w-full bg-card border border-border rounded-lg pl-10 pr-3 py-2 text-sm text-slate-300 focus:outline-none focus:border-accent-cyan"
          />
        </div>
        <span className="text-xs text-slate-500">{filteredAlerts.length} alerts</span>
      </div>

      {filteredAlerts.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-20 text-slate-500">
          <CheckCircle className="w-12 h-12 mb-3 text-accent-green" />
          <p className="font-medium">No alerts match your filters</p>
        </div>
      ) : (
        <div className="space-y-2">
          {filteredAlerts.map(alert => (
            <div key={alert.id} className="bg-card border border-border rounded-xl overflow-hidden">
              <button
                onClick={() => setExpandedId(expandedId === alert.id ? null : alert.id)}
                className="w-full flex items-center gap-4 p-4 hover:bg-slate-800/30 transition-colors text-left"
              >
                <div className={`w-2 h-2 rounded-full flex-shrink-0 ${severityDots[alert.severity] || severityDots.Low}`} />
                <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded border ${severityColors[alert.severity] || severityColors.Low}`}>
                  {alert.severity}
                </span>
                <span className="text-sm text-slate-200 flex-1">{alert.alert_type}</span>
                <span className="text-xs text-slate-500 font-mono">{alert.timestamp ? format(new Date(alert.timestamp), 'MMM dd, HH:mm:ss') : ''}</span>
                {alert.resolved && (
                  <span className="text-[10px] text-accent-green font-bold px-2 py-0.5 bg-accent-green/10 rounded">RESOLVED</span>
                )}
                {expandedId === alert.id ? <ChevronUp className="w-4 h-4 text-slate-500" /> : <ChevronDown className="w-4 h-4 text-slate-500" />}
              </button>
              {expandedId === alert.id && (
                <div className="px-4 pb-4 border-t border-border">
                  <div className="mt-3 space-y-2 text-sm text-slate-400">
                    <p>{alert.description || 'No description'}</p>
                    <div className="flex gap-4 text-xs font-mono">
                      {alert.src_ip && <span>SRC: {alert.src_ip}</span>}
                      {alert.dst_ip && <span>DST: {alert.dst_ip}</span>}
                    </div>
                    {!alert.resolved && (
                      <button
                        onClick={e => { e.stopPropagation(); handleResolve(alert.id); }}
                        disabled={resolvingId === alert.id}
                        className="mt-2 flex items-center gap-2 px-3 py-1.5 bg-accent-green/10 border border-accent-green/30 rounded-lg text-accent-green text-xs hover:bg-accent-green/20 transition-all disabled:opacity-50"
                      >
                        {resolvingId === alert.id ? <Loader2 className="w-3 h-3 animate-spin" /> : <CheckCircle className="w-3 h-3" />}
                        Resolve
                      </button>
                    )}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Geographic Sources Section */}
      <div className="bg-card border border-border rounded-2xl overflow-hidden shadow-2xl">
        <div className="p-4 border-b border-border bg-background/50 flex justify-between items-center">
          <h3 className="text-sm font-bold flex items-center gap-2">
            <Globe className="w-4 h-4 text-accent-cyan" />
            THREAT SOURCE GEOGRAPHY
          </h3>
          <span className="text-[10px] font-mono text-slate-500">{geoSources.length} SOURCES</span>
        </div>
        <div className="h-[400px] bg-black/40 relative">
          <GeoMap sources={geoSources} />
        </div>
        {geoSources.length > 0 && (
          <div className="border-t border-border overflow-x-auto">
            <table className="w-full text-xs">
              <thead>
                <tr className="border-b border-border text-slate-500">
                  <th className="text-left p-3 font-mono font-medium">IP</th>
                  <th className="text-left p-3 font-mono font-medium">Country</th>
                  <th className="text-left p-3 font-mono font-medium">City</th>
                  <th className="text-right p-3 font-mono font-medium">Threat Score</th>
                </tr>
              </thead>
              <tbody>
                {geoSources.slice(0, 20).map((src, i) => (
                  <tr key={i} className="border-b border-border/50 hover:bg-slate-800/20 transition-colors">
                    <td className="p-3 font-mono text-accent-cyan">{src.ip}</td>
                    <td className="p-3 text-slate-300">{src.country}</td>
                    <td className="p-3 text-slate-300">{src.city}</td>
                    <td className="p-3 text-right font-mono">
                      <span className={src.threat_score >= 60 ? 'text-accent-red' : src.threat_score >= 30 ? 'text-accent-yellow' : 'text-accent-green'}>
                        {src.threat_score.toFixed(1)}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
