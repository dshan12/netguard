import NetworkMap from '../components/NetworkMap';

interface PacketData {
  src_ip: string;
  dst_ip: string;
  protocol: string;
  packet_size: number;
  timestamp?: string;
}

interface MapPageProps {
  packets: PacketData[];
}

export default function MapPage({ packets }: MapPageProps) {
  const uniqueIps = new Set<string>();
  packets.forEach(p => {
    uniqueIps.add(p.src_ip);
    uniqueIps.add(p.dst_ip);
  });
  const nodeCount = uniqueIps.size;
  const flowCount = packets.length;
  const tcpCount = packets.filter(p => p.protocol === 'TCP').length;
  const udpCount = packets.filter(p => p.protocol === 'UDP').length;
  const maliciousCount = flowCount - tcpCount - udpCount;

  return (
    <div className="h-full flex flex-col animate-in fade-in duration-500">
      <div className="flex-1 bg-card border border-border rounded-2xl overflow-hidden relative">
        <NetworkMap packets={packets} />

        <div className="absolute top-4 left-4 space-y-2">
          <div className="bg-background/80 backdrop-blur-md border border-border rounded-xl p-4 space-y-2">
            <div className="text-xs text-slate-500 font-bold uppercase tracking-wider">Statistics</div>
            <div className="text-sm text-slate-300 font-mono">Nodes: {nodeCount}</div>
            <div className="text-sm text-slate-300 font-mono">Flows: {flowCount}</div>
            <div className="text-sm text-slate-300 font-mono">Packets/s: {packets.length}</div>
          </div>
        </div>

        <div className="absolute bottom-4 left-4 bg-background/80 backdrop-blur-md border border-border rounded-xl p-4">
          <div className="text-xs text-slate-500 font-bold uppercase tracking-wider mb-2">Legend</div>
          <div className="space-y-1.5">
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-cyan-400" />
              <span className="text-xs text-slate-400">TCP</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-green-400" />
              <span className="text-xs text-slate-400">UDP</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-red-500" />
              <span className="text-xs text-slate-400">Malicious Traffic</span>
            </div>
          </div>
        </div>

        <div className="absolute top-4 right-4 bg-background/80 backdrop-blur-md border border-border rounded-xl p-4">
          <div className="text-xs text-slate-500 font-bold uppercase tracking-wider mb-2">Protocols</div>
          <div className="space-y-1">
            <div className="flex justify-between gap-6 text-xs">
              <span className="text-cyan-400">TCP</span>
              <span className="text-slate-300 font-mono">{tcpCount}</span>
            </div>
            <div className="flex justify-between gap-6 text-xs">
              <span className="text-green-400">UDP</span>
              <span className="text-slate-300 font-mono">{udpCount}</span>
            </div>
            {maliciousCount > 0 && (
              <div className="flex justify-between gap-6 text-xs">
                <span className="text-red-400">Malicious</span>
                <span className="text-slate-300 font-mono">{maliciousCount}</span>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
