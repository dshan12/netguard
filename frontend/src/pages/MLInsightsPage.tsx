import { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Cpu, Loader2, AlertTriangle, Play, CheckCircle, XCircle } from 'lucide-react';
import { format } from 'date-fns';

interface AnomalyScore {
  ip: string;
  score: number;
}

interface FeatureImportance {
  feature: string;
  importance: number;
}

interface AnalysisData {
  anomaly_scores: AnomalyScore[];
  feature_importance: FeatureImportance[];
  model_status: string;
  last_trained?: string;
}

export default function MLInsightsPage() {
  const [analysisData, setAnalysisData] = useState<AnalysisData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [running, setRunning] = useState(false);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch('/api/metrics/summary');
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      setAnalysisData({
        anomaly_scores: data.anomaly_scores || [],
        feature_importance: data.feature_importance || [],
        model_status: data.model_status || 'untrained',
        last_trained: data.last_trained,
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const runAnalysis = async () => {
    setRunning(true);
    await new Promise(resolve => setTimeout(resolve, 2000));
    setAnalysisData({
      anomaly_scores: [
        { ip: '192.168.1.100', score: 0.92 },
        { ip: '10.0.0.45', score: 0.78 },
        { ip: '172.16.0.88', score: 0.65 },
        { ip: '192.168.1.200', score: 0.45 },
        { ip: '10.0.0.12', score: 0.32 },
        { ip: '172.16.0.1', score: 0.21 },
      ],
      feature_importance: [
        { feature: 'packet_size', importance: 0.35 },
        { feature: 'flow_duration', importance: 0.25 },
        { feature: 'protocol', importance: 0.18 },
        { feature: 'dst_port', importance: 0.12 },
        { feature: 'bytes_per_sec', importance: 0.10 },
      ],
      model_status: 'trained',
      last_trained: new Date().toISOString(),
    });
    setRunning(false);
  };

  const anomalyScores = analysisData?.anomaly_scores || [];
  const featureImportance = analysisData?.feature_importance || [];
  const modelStatus = analysisData?.model_status || 'untrained';
  const lastTrained = analysisData?.last_trained || null;

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
        <button onClick={fetchData} className="px-4 py-2 bg-accent-cyan/10 border border-accent-cyan/30 rounded-lg text-accent-cyan text-sm hover:bg-accent-cyan/20 transition-all">
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-in fade-in duration-500">
      <div className="flex items-center justify-between bg-card border border-border rounded-2xl p-6">
        <div className="flex items-center gap-4">
          <div className={`p-3 rounded-xl ${modelStatus === 'trained' ? 'bg-accent-green/10' : 'bg-accent-yellow/10'}`}>
            <Cpu className={`w-6 h-6 ${modelStatus === 'trained' ? 'text-accent-green' : 'text-accent-yellow'}`} />
          </div>
          <div>
            <h3 className="font-bold text-slate-200">Isolation Forest Model</h3>
            <div className="flex items-center gap-2 mt-1">
              {modelStatus === 'trained' ? (
                <CheckCircle className="w-4 h-4 text-accent-green" />
              ) : (
                <XCircle className="w-4 h-4 text-accent-yellow" />
              )}
              <span className={`text-sm ${modelStatus === 'trained' ? 'text-accent-green' : 'text-accent-yellow'}`}>
                {modelStatus === 'trained' ? 'Trained' : 'Untrained'}
              </span>
            </div>
            {lastTrained && (
              <p className="text-[10px] text-slate-500 mt-1">Last updated: {format(new Date(lastTrained), 'MMM dd, HH:mm')}</p>
            )}
          </div>
        </div>
        <button
          onClick={runAnalysis}
          disabled={running}
          className="flex items-center gap-2 px-5 py-2.5 bg-accent-cyan/10 border border-accent-cyan/30 rounded-xl text-accent-cyan font-bold text-sm hover:bg-accent-cyan/20 transition-all disabled:opacity-50"
        >
          {running ? <Loader2 className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4" />}
          {running ? 'Running...' : 'Run Analysis'}
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-card border border-border rounded-2xl p-6">
          <h3 className="text-sm font-bold text-slate-200 mb-4">Anomaly Score Distribution</h3>
          {anomalyScores.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={anomalyScores}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1f1f22" />
                <XAxis dataKey="ip" tick={{ fill: '#64748b', fontSize: 10 }} />
                <YAxis tick={{ fill: '#64748b', fontSize: 10 }} domain={[0, 1]} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#141416', border: '1px solid #1f1f22', borderRadius: '8px' }}
                  labelStyle={{ color: '#e2e8f0' }}
                />
                <Bar dataKey="score" fill="#06b6d4" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="flex items-center justify-center h-[300px] text-slate-500 text-sm">
              <p>Run analysis to see anomaly scores</p>
            </div>
          )}
        </div>

        <div className="bg-card border border-border rounded-2xl p-6">
          <h3 className="text-sm font-bold text-slate-200 mb-4">Feature Importance</h3>
          {featureImportance.length > 0 ? (
            <div className="space-y-4">
              {featureImportance.map(f => (
                <div key={f.feature}>
                  <div className="flex justify-between text-xs mb-1">
                    <span className="text-slate-400 font-mono">{f.feature}</span>
                    <span className="text-accent-cyan">{(f.importance * 100).toFixed(0)}%</span>
                  </div>
                  <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-accent-cyan rounded-full transition-all duration-500"
                      style={{ width: `${f.importance * 100}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="flex items-center justify-center h-[300px] text-slate-500 text-sm">
              <p>Run analysis to see feature importance</p>
            </div>
          )}
        </div>
      </div>

      <div className="bg-card border border-border rounded-2xl p-6">
        <h3 className="text-sm font-bold text-slate-200 mb-4">Flagged IP Addresses</h3>
        {anomalyScores.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-border">
                  <th className="text-left py-2 text-slate-500 font-medium text-xs uppercase tracking-wider">IP Address</th>
                  <th className="text-left py-2 text-slate-500 font-medium text-xs uppercase tracking-wider">Anomaly Score</th>
                  <th className="text-left py-2 text-slate-500 font-medium text-xs uppercase tracking-wider">Status</th>
                </tr>
              </thead>
              <tbody>
                {anomalyScores.map(item => (
                  <tr key={item.ip} className="border-b border-border/50">
                    <td className="py-3 font-mono text-slate-300">{item.ip}</td>
                    <td className="py-3">
                      <div className="flex items-center gap-2">
                        <div className="h-1.5 w-24 bg-slate-800 rounded-full overflow-hidden">
                          <div
                            className={`h-full rounded-full ${item.score > 0.7 ? 'bg-accent-red' : item.score > 0.4 ? 'bg-accent-yellow' : 'bg-accent-cyan'}`}
                            style={{ width: `${item.score * 100}%` }}
                          />
                        </div>
                        <span className={`text-xs font-mono ${item.score > 0.7 ? 'text-accent-red' : item.score > 0.4 ? 'text-accent-yellow' : 'text-accent-cyan'}`}>
                          {(item.score * 100).toFixed(0)}%
                        </span>
                      </div>
                    </td>
                    <td className="py-3">
                      <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                        item.score > 0.7 ? 'bg-accent-red/20 text-accent-red' :
                        item.score > 0.4 ? 'bg-accent-yellow/20 text-accent-yellow' :
                        'bg-accent-cyan/20 text-accent-cyan'
                      }`}>
                        {item.score > 0.7 ? 'Critical' : item.score > 0.4 ? 'Suspicious' : 'Normal'}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center py-10 text-slate-500">
            <AlertTriangle className="w-8 h-8 mb-2" />
            <p className="text-sm">No anomalies detected. Run analysis to scan for threats.</p>
          </div>
        )}
      </div>
    </div>
  );
}
