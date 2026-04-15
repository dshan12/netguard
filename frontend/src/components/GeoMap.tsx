import { useEffect, useRef, useState, useCallback } from 'react';

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

interface GeoMapProps {
  sources: GeoSource[];
}

interface TooltipData {
  x: number;
  y: number;
  ip: string;
  country: string;
  city: string;
  threat_score: number;
}

const CONTINENTS = [
  [[-130, 20], [-130, 50], [-100, 50], [-100, 60], [-80, 60], [-60, 50], [-60, 20], [-80, 10], [-100, 10], [-120, 10]],
  [[-80, -60], [-60, -60], [-40, -20], [-50, 0], [-80, 10], [-80, -10], [-70, -20]],
  [[-10, 35], [-10, 60], [10, 60], [30, 60], [30, 50], [40, 40], [30, 35], [10, 35]],
  [[10, 35], [30, 35], [40, 10], [50, 10], [40, -35], [20, -35], [10, 0]],
  [[30, 60], [60, 60], [120, 60], [140, 50], [140, 20], [120, 10], [100, 10], [80, 20], [60, 20], [40, 40]],
  [[115, -40], [155, -40], [155, -15], [130, -15], [115, -25]],
];

function getThreatColor(score: number): string {
  if (score < 30) return '#22c55e';
  if (score < 60) return '#eab308';
  if (score < 80) return '#f97316';
  return '#ef4444';
}

function project(lat: number, lon: number, width: number, height: number): { x: number; y: number } {
  const x = ((lon + 180) / 360) * width;
  const y = ((90 - lat) / 180) * height;
  return { x, y };
}

export default function GeoMap({ sources }: GeoMapProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const animFrameRef = useRef<number>(0);
  const timeRef = useRef<number>(0);
  const [tooltip, setTooltip] = useState<TooltipData | null>(null);
  const hoveredRef = useRef<number | null>(null);

  const drawMap = useCallback((ctx: CanvasRenderingContext2D, w: number, h: number, time: number) => {
    ctx.clearRect(0, 0, w, h);

    // Draw continents
    ctx.fillStyle = 'rgba(31, 31, 34, 0.6)';
    ctx.strokeStyle = 'rgba(31, 31, 34, 0.8)';
    ctx.lineWidth = 1;
    for (const continent of CONTINENTS) {
      ctx.beginPath();
      const first = continent[0] as [number, number];
      const p = project(first[1], first[0], w, h);
      ctx.moveTo(p.x, p.y);
      for (let i = 1; i < continent.length; i++) {
        const pt = continent[i] as [number, number];
        const np = project(pt[1], pt[0], w, h);
        ctx.lineTo(np.x, np.y);
      }
      ctx.closePath();
      ctx.fill();
      ctx.stroke();
    }

    // Draw threat points
    for (let i = 0; i < sources.length; i++) {
      const src = sources[i];
      const pos = project(src.latitude, src.longitude, w, h);
      const radius = Math.max(2, Math.min(src.threat_score / 100, 1) * 10);
      const color = getThreatColor(src.threat_score);
      const pulse = Math.sin(time * 0.002 + i) * 0.3 + 0.7;

      // Glow
      const gradient = ctx.createRadialGradient(pos.x, pos.y, 0, pos.x, pos.y, radius * 4);
      gradient.addColorStop(0, color.replace(')', `, ${0.3 * pulse})`).replace('rgb', 'rgba').replace(/(\d+)/, (m) => {
        const c = parseInt(m);
        return `${c}`;
      }));
      const alpha = 0.2 * pulse;
      const r = parseInt(color.slice(1, 3), 16);
      const g = parseInt(color.slice(3, 5), 16);
      const b = parseInt(color.slice(5, 7), 16);
      gradient.addColorStop(0, `rgba(${r}, ${g}, ${b}, ${0.4 * pulse})`);
      gradient.addColorStop(1, `rgba(${r}, ${g}, ${b}, 0)`);
      ctx.beginPath();
      ctx.arc(pos.x, pos.y, radius * 4, 0, Math.PI * 2);
      ctx.fillStyle = gradient;
      ctx.fill();

      // Core dot
      ctx.beginPath();
      ctx.arc(pos.x, pos.y, radius, 0, Math.PI * 2);
      ctx.fillStyle = color;
      ctx.fill();
      ctx.strokeStyle = `rgba(${r}, ${g}, ${b}, ${0.5 * pulse})`;
      ctx.lineWidth = 1.5;
      ctx.stroke();
    }
  }, [sources]);

  const handleMouseMove = useCallback((e: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current;
    if (!canvas || sources.length === 0) return;
    const rect = canvas.getBoundingClientRect();
    const mouseX = e.clientX - rect.left;
    const mouseY = e.clientY - rect.top;
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;

    let closest: TooltipData | null = null;
    let closestDist = 15;

    for (const src of sources) {
      const pos = project(src.latitude, src.longitude, canvas.width, canvas.height);
      const dx = mouseX * scaleX - pos.x;
      const dy = mouseY * scaleY - pos.y;
      const dist = Math.sqrt(dx * dx + dy * dy);
      if (dist < closestDist) {
        closestDist = dist;
        closest = {
          x: e.clientX - rect.left,
          y: e.clientY - rect.top,
          ip: src.ip,
          country: src.country,
          city: src.city,
          threat_score: src.threat_score,
        };
      }
    }
    setTooltip(closest);
  }, [sources]);

  const handleMouseLeave = useCallback(() => {
    setTooltip(null);
  }, []);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const resize = () => {
      const parent = canvas.parentElement;
      if (!parent) return;
      canvas.width = parent.clientWidth;
      canvas.height = parent.clientHeight;
    };
    resize();

    const animate = (t: number) => {
      timeRef.current = t;
      drawMap(ctx, canvas.width, canvas.height, t);
      animFrameRef.current = requestAnimationFrame(animate);
    };
    animFrameRef.current = requestAnimationFrame(animate);

    window.addEventListener('resize', resize);
    return () => {
      cancelAnimationFrame(animFrameRef.current);
      window.removeEventListener('resize', resize);
    };
  }, [drawMap]);

  return (
    <div className="relative w-full h-full">
      <canvas
        ref={canvasRef}
        className="w-full h-full cursor-crosshair"
        onMouseMove={handleMouseMove}
        onMouseLeave={handleMouseLeave}
      />
      {tooltip && (
        <div
          className="absolute pointer-events-none bg-background/90 backdrop-blur-md border border-border rounded-xl p-3 shadow-2xl z-50"
          style={{ left: tooltip.x + 12, top: tooltip.y - 10 }}
        >
          <div className="text-xs font-mono text-accent-cyan mb-1">{tooltip.ip}</div>
          <div className="text-xs text-slate-400">{tooltip.city}, {tooltip.country}</div>
          <div className="text-xs text-slate-400">
            Threat: <span className="text-accent-red font-bold">{tooltip.threat_score.toFixed(1)}</span>
          </div>
        </div>
      )}
    </div>
  );
}
