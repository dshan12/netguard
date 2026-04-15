import time
import statistics
from typing import List, Dict, Optional
from collections import defaultdict, deque
from generator import PacketData

class RulesEngine:
    def __init__(self):
        # Port scan detection: track unique ports per source IP in a time window
        self.port_scan_window = 10.0  # seconds
        self.port_scan_threshold = 20
        self.source_ports = defaultdict(lambda: deque())
        
        # DDoS detection: track packet rate per destination IP
        self.ddos_window = 5.0  # seconds
        self.ddos_threshold = 50  # packets per second
        self.dest_rates = defaultdict(lambda: deque())
        
        # Brute force detection: track connection attempts to specific ports
        self.auth_ports = {22, 3389, 21, 23, 3306, 5432}
        self.brute_force_window = 60.0  # seconds
        self.brute_force_threshold = 30
        self.auth_attempts = defaultdict(lambda: deque())
        
        # Beaconing detection: track intervals between connections for IP pairs
        self.beacon_flows = defaultdict(lambda: deque())
        
        # Exfiltration detection: track outbound flow volumes and large packet bursts
        self.exfil_flows = defaultdict(lambda: deque())
        self.exfil_large_bursts = defaultdict(lambda: deque())

    def process_packet(self, pkt: PacketData) -> List[Dict]:
        alerts = []
        now = pkt.timestamp

        # 1. Port Scan Check
        if pkt.protocol == "TCP" and pkt.dst_port:
            self._cleanup_window(self.source_ports[pkt.src_ip], now, self.port_scan_window)
            # Store (port, timestamp)
            self.source_ports[pkt.src_ip].append((pkt.dst_port, now))
            unique_ports = len(set(p for p, t in self.source_ports[pkt.src_ip]))
            if unique_ports > self.port_scan_threshold:
                alerts.append({
                    "alert_type": "Port Scan Detected",
                    "severity": "High",
                    "src_ip": pkt.src_ip,
                    "dst_ip": pkt.dst_ip,
                    "protocol": pkt.protocol,
                    "description": f"Source IP {pkt.src_ip} probed {unique_ports} unique ports in {self.port_scan_window}s",
                    "rule_triggered": "PORT_SCAN_RULE"
                })

        # 2. DDoS Check
        self._cleanup_window(self.dest_rates[pkt.dst_ip], now, self.ddos_window)
        self.dest_rates[pkt.dst_ip].append(now)
        pps = len(self.dest_rates[pkt.dst_ip]) / self.ddos_window
        if pps > self.ddos_threshold:
            alerts.append({
                "alert_type": "DDoS Attack Detected",
                "severity": "Critical",
                "src_ip": pkt.src_ip, # Note: in real DDoS this might be a spoofed IP or one of many
                "dst_ip": pkt.dst_ip,
                "protocol": pkt.protocol,
                "description": f"Target IP {pkt.dst_ip} receiving {pps:.1f} packets/sec",
                "rule_triggered": "DDOS_RULE"
            })

        # 3. Brute Force Check
        if pkt.dst_port in self.auth_ports:
            self._cleanup_window(self.auth_attempts[(pkt.src_ip, pkt.dst_ip, pkt.dst_port)], now, self.brute_force_window)
            self.auth_attempts[(pkt.src_ip, pkt.dst_ip, pkt.dst_port)].append(now)
            attempts = len(self.auth_attempts[(pkt.src_ip, pkt.dst_ip, pkt.dst_port)])
            if attempts > self.brute_force_threshold:
                alerts.append({
                    "alert_type": "Brute Force Attack Detected",
                    "severity": "High",
                    "src_ip": pkt.src_ip,
                    "dst_ip": pkt.dst_ip,
                    "dst_port": pkt.dst_port,
                    "protocol": pkt.protocol,
                    "description": f"Potential brute force from {pkt.src_ip} to {pkt.dst_ip} on port {pkt.dst_port} ({attempts} attempts)",
                    "rule_triggered": "BRUTE_FORCE_RULE"
                })

        # 4. Beaconing Detection
        flow_key = (pkt.src_ip, pkt.dst_ip)
        self._cleanup_window(self.beacon_flows[flow_key], now, 300.0)
        self.beacon_flows[flow_key].append(now)
        if len(self.beacon_flows[flow_key]) >= 3:
            timestamps = list(self.beacon_flows[flow_key])
            intervals = [timestamps[i+1] - timestamps[i] for i in range(len(timestamps)-1)]
            if len(intervals) >= 2 and statistics.stdev(intervals) < 0.5:
                alerts.append({
                    "alert_type": "Beaconing Detected",
                    "severity": "High",
                    "src_ip": pkt.src_ip,
                    "dst_ip": pkt.dst_ip,
                    "protocol": pkt.protocol,
                    "description": f"Beaconing from {pkt.src_ip} to {pkt.dst_ip} - regular intervals detected (stddev < 0.5s)",
                    "rule_triggered": "BEACONING_RULE"
                })

        # 5. Data Exfiltration Detection
        if pkt.direction == "outbound":
            self._cleanup_window(self.exfil_flows[flow_key], now, 60.0)
            self.exfil_flows[flow_key].append((now, pkt.packet_size))
            sizes = [s for _, s in self.exfil_flows[flow_key]]
            total_bytes = sum(sizes)
            num_packets = len(sizes)
            avg_size = total_bytes / num_packets if num_packets > 0 else 0
            if total_bytes > 10000 and num_packets > 3 and avg_size > 1000:
                alerts.append({
                    "alert_type": "Data Exfiltration Detected",
                    "severity": "Medium",
                    "src_ip": pkt.src_ip,
                    "dst_ip": pkt.dst_ip,
                    "protocol": pkt.protocol,
                    "description": f"Possible data exfiltration from {pkt.src_ip} to {pkt.dst_ip} - {total_bytes} bytes in {num_packets} packets",
                    "rule_triggered": "EXFILTRATION_RULE"
                })

            if pkt.packet_size > 1400:
                self._cleanup_window(self.exfil_large_bursts[flow_key], now, 10.0)
                self.exfil_large_bursts[flow_key].append(now)
                if len(self.exfil_large_bursts[flow_key]) >= 3:
                    alerts.append({
                        "alert_type": "Data Exfiltration Detected",
                        "severity": "High",
                        "src_ip": pkt.src_ip,
                        "dst_ip": pkt.dst_ip,
                        "protocol": pkt.protocol,
                        "description": f"Large packet exfiltration from {pkt.src_ip} to {pkt.dst_ip} - {len(self.exfil_large_bursts[flow_key])} large packets in 10s",
                        "rule_triggered": "EXFILTRATION_RULE"
                    })

        return alerts

    def _cleanup_window(self, d: deque, now: float, window: float):
        while d:
            val = d[0]
            elapsed = now - val if isinstance(val, (int, float)) else now - val[1]
            if elapsed <= window:
                break
            d.popleft()
