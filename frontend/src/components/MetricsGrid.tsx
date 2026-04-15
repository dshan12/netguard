import { Shield, AlertTriangle, Activity, Wifi, TrendingUp } from 'lucide-react';

interface Metrics {
  total_packets?: number;
  total_alerts?: number;
  active_threats?: number;
  critical_alerts?: number;
  high_alerts?: number;
  medium_alerts?: number;
  low_alerts?: number;
  packets_per_second?: number;
  bytes_per_second?: number;
  total_bytes?: number;
}

interface MetricsGridProps {
  metrics: Metrics | null;
}

function MetricCard({
  title,
  value,
  subtitle,
  icon,
  color,
  trend,
}: {
  title: string;
  value: string | number;
  subtitle: string;
  icon: React.ReactNode;
  color: string;
  trend?: 'up' | 'down' | 'neutral';
}) {
  return (
    <div className={`bg-card border border-border rounded-2xl p-6 shadow-2xl ${color} transition-all hover:scale-[1.02] duration-300`}>
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-background/50 rounded-xl">{icon}</div>
          <div>
            <p className="text-xs font-bold text-slate-500 uppercase tracking-widest">{title}</p>
            <p className="text-3xl font-bold mt-1 font-mono">{value}</p>
          </div>
        </div>
        {trend && (
          <div className={`p-1.5 rounded-lg ${trend === 'up' ? 'bg-accent-red/10' : 'bg-accent-green/10'}`}>
            <TrendingUp className={`w-4 h-4 ${trend === 'up' ? 'text-accent-red' : 'text-accent-green'} ${trend === 'down' ? 'rotate-180' : ''}`} />
          </div>
        )}
      </div>
      <p className="text-xs text-slate-600 font-mono">{subtitle}</p>
    </div>
  );
}

export default function MetricsGrid({ metrics }: MetricsGridProps) {
  if (!metrics) {
    return (
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-6">
        {Array.from({ length: 4 }).map((_, i) => (
          <div key={i} className="bg-card border border-border rounded-2xl p-6 animate-pulse">
            <div className="h-4 bg-slate-800 rounded w-20 mb-4" />
            <div className="h-8 bg-slate-800 rounded w-16 mb-2" />
            <div className="h-3 bg-slate-800 rounded w-32" />
          </div>
        ))}
      </div>
    );
  }

  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-6">
      <MetricCard
        title="Total Packets"
        value={(metrics.total_packets ?? 0).toLocaleString()}
        subtitle={`${(metrics.packets_per_second ?? 0).toFixed(1)} pkts/s`}
        icon={<Wifi className="w-5 h-5 text-accent-cyan" />}
        color="hover:shadow-[0_0_30px_rgba(6,182,212,0.1)]"
        trend="up"
      />
      <MetricCard
        title="Active Alerts"
        value={metrics.total_alerts ?? 0}
        subtitle={`${metrics.critical_alerts ?? 0} critical, ${metrics.high_alerts ?? 0} high`}
        icon={<AlertTriangle className="w-5 h-5 text-accent-red" />}
        color="hover:shadow-[0_0_30px_rgba(239,68,68,0.1)]"
        trend={metrics.critical_alerts && metrics.critical_alerts > 0 ? 'up' : 'down'}
      />
      <MetricCard
        title="Active Threats"
        value={metrics.active_threats ?? 0}
        subtitle="Sources with score > 50"
        icon={<Shield className="w-5 h-5 text-accent-yellow" />}
        color="hover:shadow-[0_0_30px_rgba(234,179,8,0.1)]"
        trend={(metrics.active_threats ?? 0) > 0 ? 'up' : 'neutral'}
      />
      <MetricCard
        title="Throughput"
        value={`${((metrics.bytes_per_second ?? 0) / 1024).toFixed(1)} KB/s`}
        subtitle={`${((metrics.total_bytes ?? 0) / 1024 / 1024).toFixed(2)} MB total`}
        icon={<Activity className="w-5 h-5 text-accent-green" />}
        color="hover:shadow-[0_0_30px_rgba(34,197,94,0.1)]"
        trend="neutral"
      />
    </div>
  );
}
