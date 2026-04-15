import { useEffect, useRef, useState, useCallback } from 'react';

interface PacketData {
  src_ip: string;
  dst_ip: string;
  protocol: string;
  packet_size: number;
  timestamp?: string;
}

interface Flow {
  src: { x: number; y: number };
  dst: { x: number; y: number };
  progress: number;
  size: number;
  protocol: string;
  id: number;
}

interface NetworkMapProps {
  packets: PacketData[];
}

const ipToColor = (ip: string) => {
  const hash = ip.split('.').reduce((acc, oct) => acc + parseInt(oct), 0);
  const hue = hash % 360;
  return `hsl(${hue}, 70%, 60%)`;
};

export default function NetworkMap({ packets }: NetworkMapProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const flowsRef = useRef<Flow[]>([]);
  const nodePositionsRef = useRef<Map<string, { x: number; y: number }>>(new Map());
  const animFrameRef = useRef<number>(0);
  const flowIdRef = useRef<number>(0);

  const getOrCreateNode = useCallback((ip: string, width: number, height: number) => {
    if (!nodePositionsRef.current.has(ip)) {
      nodePositionsRef.current.set(ip, {
        x: 50 + Math.random() * (width - 100),
        y: 50 + Math.random() * (height - 100),
      });
    }
    return nodePositionsRef.current.get(ip)!;
  }, []);

  useEffect(() => {
    if (packets.length === 0) return;
    const canvas = canvasRef.current;
    if (!canvas) return;
    const w = canvas.width;
    const h = canvas.height;

    const latest = packets[0];
    const src = getOrCreateNode(latest.src_ip, w, h);
    const dst = getOrCreateNode(latest.dst_ip, w, h);

    flowsRef.current.push({
      src,
      dst,
      progress: 0,
      size: Math.min(latest.packet_size / 1500, 1) * 4 + 1,
      protocol: latest.protocol,
      id: flowIdRef.current++,
    });

    if (flowsRef.current.length > 100) {
      flowsRef.current = flowsRef.current.slice(-100);
    }
  }, [packets, getOrCreateNode]);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const animate = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      // Draw background grid
      ctx.strokeStyle = 'rgba(31, 31, 34, 0.5)';
      ctx.lineWidth = 1;
      for (let x = 0; x < canvas.width; x += 30) {
        ctx.beginPath();
        ctx.moveTo(x, 0);
        ctx.lineTo(x, canvas.height);
        ctx.stroke();
      }
      for (let y = 0; y < canvas.height; y += 30) {
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(canvas.width, y);
        ctx.stroke();
      }

      // Draw nodes
      nodePositionsRef.current.forEach((pos, ip) => {
        ctx.beginPath();
        ctx.arc(pos.x, pos.y, 6, 0, Math.PI * 2);
        ctx.fillStyle = ipToColor(ip);
        ctx.fill();
        ctx.strokeStyle = 'rgba(6, 182, 212, 0.3)';
        ctx.lineWidth = 2;
        ctx.stroke();

        ctx.fillStyle = 'rgba(148, 163, 184, 0.6)';
        ctx.font = '9px monospace';
        ctx.fillText(ip, pos.x + 8, pos.y + 3);
      });

      // Draw & update flows
      flowsRef.current = flowsRef.current.filter((flow) => {
        flow.progress += 0.02;
        if (flow.progress >= 1) return false;

        const x = flow.src.x + (flow.dst.x - flow.src.x) * flow.progress;
        const y = flow.src.y + (flow.dst.y - flow.src.y) * flow.progress;

        ctx.beginPath();
        ctx.arc(x, y, flow.size, 0, Math.PI * 2);
        const alpha = flow.progress < 0.5 ? flow.progress * 2 : (1 - flow.progress) * 2;
        ctx.fillStyle = flow.protocol === 'TCP'
          ? `rgba(6, 182, 212, ${alpha * 0.6})`
          : `rgba(34, 197, 94, ${alpha * 0.4})`;
        ctx.fill();

        // Trail
        ctx.beginPath();
        ctx.moveTo(flow.src.x, flow.src.y);
        const trailX = flow.src.x + (flow.dst.x - flow.src.x) * Math.max(0, flow.progress - 0.05);
        const trailY = flow.src.y + (flow.dst.y - flow.src.y) * Math.max(0, flow.progress - 0.05);
        ctx.lineTo(x, y);
        ctx.strokeStyle = `rgba(6, 182, 212, ${alpha * 0.3})`;
        ctx.lineWidth = flow.size;
        ctx.stroke();

        return true;
      });

      animFrameRef.current = requestAnimationFrame(animate);
    };

    animate();
    return () => cancelAnimationFrame(animFrameRef.current);
  }, []);

  return (
    <canvas
      ref={canvasRef}
      width={800}
      height={480}
      className="w-full h-full"
    />
  );
}
