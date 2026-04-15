import { useState, useEffect, useRef } from 'react';

export function useWebSocket() {
  const [packets, setPackets] = useState<any[]>([]);
  const [alerts, setAlerts] = useState<any[]>([]);
  const [metrics, setMetrics] = useState<any>({});
  const socketRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    // Connect to WebSocket
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.host;
    const socket = new WebSocket(`${protocol}//${host}/ws/live`);
    socketRef.current = socket;

    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      
      if (data.alert_type) {
        setAlerts(prev => [data, ...prev].slice(0, 50));
      } else if (data.src_ip) {
        setPackets(prev => [data, ...prev].slice(0, 100));
      }
    };

    // Poll for metrics
    const fetchMetrics = async () => {
      try {
        const response = await fetch('/api/metrics/summary');
        const data = await response.json();
        setMetrics(data);
      } catch (error) {
        console.error('Failed to fetch metrics:', error);
      }
    };

    fetchMetrics();
    const interval = setInterval(fetchMetrics, 2000);

    return () => {
      socket.close();
      clearInterval(interval);
    };
  }, []);

  return { packets, alerts, metrics };
}
