import { format } from 'date-fns';

interface Alert {
  id?: number;
  timestamp?: string;
  alert_type?: string;
  severity?: string;
  src_ip?: string;
  dst_ip?: string;
  description?: string;
}

interface AlertTimelineProps {
  alerts: Alert[];
}

const severityColors: Record<string, string> = {
  Critical: 'bg-accent-red text-accent-red border-accent-red',
  High: 'bg-orange-500/20 text-orange-400 border-orange-500',
  Medium: 'bg-accent-yellow/20 text-accent-yellow border-accent-yellow',
  Low: 'bg-blue-500/20 text-blue-400 border-blue-500',
};

const severityDots: Record<string, string> = {
  Critical: 'bg-accent-red shadow-[0_0_8px_#ef4444]',
  High: 'bg-orange-500 shadow-[0_0_8px_#f97316]',
  Medium: 'bg-accent-yellow shadow-[0_0_8px_#eab308]',
  Low: 'bg-blue-500 shadow-[0_0_8px_#3b82f6]',
};

export default function AlertTimeline({ alerts }: AlertTimelineProps) {
  if (!alerts || alerts.length === 0) {
    return (
      <div className="flex items-center justify-center h-full text-slate-600 text-sm">
        <p>No threats detected yet. System is secure.</p>
      </div>
    );
  }

  return (
    <div className="divide-y divide-border">
      {alerts.slice(0, 50).map((alert, idx) => (
        <div
          key={alert.id || idx}
          className="p-4 hover:bg-slate-800/30 transition-colors"
        >
          <div className="flex items-start gap-3">
            <div className={`mt-1.5 w-2 h-2 rounded-full flex-shrink-0 ${severityDots[alert.severity || 'Low'] || severityDots.Low}`} />
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 mb-1">
                <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded border ${severityColors[alert.severity || 'Low'] || severityColors.Low}`}>
                  {alert.severity || 'LOW'}
                </span>
                <span className="text-xs text-slate-400 font-mono">
                  {alert.alert_type || 'Alert'}
                </span>
                <span className="text-[10px] text-slate-600 ml-auto">
                  {alert.timestamp ? format(new Date(alert.timestamp), 'HH:mm:ss') : ''}
                </span>
              </div>
              <p className="text-xs text-slate-400 line-clamp-2">
                {alert.description || 'No description'}
              </p>
              <div className="flex gap-2 mt-1 text-[10px] text-slate-500 font-mono">
                {alert.src_ip && <span>SRC: {alert.src_ip}</span>}
                {alert.dst_ip && <span>DST: {alert.dst_ip}</span>}
              </div>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
