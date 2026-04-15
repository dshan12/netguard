import os
import json
import time
import redis
from scapy.all import sniff, IP, TCP, UDP
from config import get_settings
from generator import PacketData, create_mixed_traffic
from rules_engine import RulesEngine

settings = get_settings()

class SecuritySniffer:
    def __init__(self):
        self.redis_client = redis.from_url(settings.redis_url, decode_responses=True)
        self.rules_engine = RulesEngine()
        self.packet_batch = []
        self.last_flush = time.time()

    def packet_callback(self, pkt_data: PacketData):
        # 1. Run Rules Engine
        alerts = self.rules_engine.process_packet(pkt_data)
        
        # 2. Publish alerts immediately
        for alert in alerts:
            self.redis_client.publish("alerts", json.dumps(alert))
            # Also store in a list for the backend to persist
            self.redis_client.lpush("pending_alerts", json.dumps(alert))

        # 3. Queue packet for batching
        packet_dict = {
            "timestamp": pkt_data.timestamp,
            "src_ip": pkt_data.src_ip,
            "dst_ip": pkt_data.dst_ip,
            "src_port": pkt_data.src_port,
            "dst_port": pkt_data.dst_port,
            "protocol": pkt_data.protocol,
            "packet_size": pkt_data.packet_size,
            "tcp_flags": pkt_data.tcp_flags,
            "payload_size": pkt_data.payload_size,
            "direction": pkt_data.direction
        }
        
        # Publish live stream for UI
        self.redis_client.publish("packets", json.dumps(packet_dict))
        
        self.packet_batch.append(packet_dict)
        
        # 4. Flush batch if needed
        if len(self.packet_batch) >= settings.packet_batch_size or \
           (time.time() - self.last_flush) > settings.packet_batch_timeout:
            self.flush_batch()

    def flush_batch(self):
        if not self.packet_batch:
            return
            
        # Push batch to Redis for backend to process
        pipeline = self.redis_client.pipeline()
        for pkt in self.packet_batch:
            pipeline.lpush("pending_packets", json.dumps(pkt))
        pipeline.execute()
        
        self.packet_batch = []
        self.last_flush = time.time()

    def run_simulation(self):
        print("Starting traffic simulation...")
        for pkt_data in create_mixed_traffic():
            self.packet_callback(pkt_data)

    def run_live(self):
        print(f"Starting live capture on interface {settings.interface}...")
        def scapy_callback(pkt):
            if IP in pkt:
                src_ip = pkt[IP].src
                dst_ip = pkt[IP].dst
                proto = "Other"
                sport = None
                dport = None
                flags = None
                
                if TCP in pkt:
                    proto = "TCP"
                    sport = pkt[TCP].sport
                    dport = pkt[TCP].dport
                    flags = str(pkt[TCP].flags)
                elif UDP in pkt:
                    proto = "UDP"
                    sport = pkt[UDP].sport
                    dport = pkt[UDP].dport
                
                pkt_data = PacketData(
                    timestamp=float(pkt.time),
                    src_ip=src_ip,
                    dst_ip=dst_ip,
                    src_port=sport,
                    dst_port=dport,
                    protocol=proto,
                    packet_size=len(pkt),
                    tcp_flags=flags,
                    payload_size=len(pkt.payload),
                    direction="inbound" # Simplified
                )
                self.packet_callback(pkt_data)

        sniff(iface=settings.interface, prn=scapy_callback, store=0)

    def start(self):
        if settings.simulation_mode == "always":
            self.run_simulation()
        elif settings.simulation_mode == "auto":
            try:
                # Test if we can sniff
                sniff(count=1, timeout=1)
                self.run_live()
            except Exception as e:
                print(f"Live capture failed: {e}. Falling back to simulation.")
                self.run_simulation()
        else:
            self.run_live()

if __name__ == "__main__":
    sniffer = SecuritySniffer()
    sniffer.start()
