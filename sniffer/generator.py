import random
import time
import threading
from dataclasses import dataclass
from typing import Dict, Generator, List, Optional
from scapy.all import IP, TCP, UDP, Raw, Ether
from ipaddress import IPv4Address


@dataclass
class PacketData:
    timestamp: float
    src_ip: str
    dst_ip: str
    src_port: Optional[int]
    dst_port: Optional[int]
    protocol: str
    packet_size: int
    tcp_flags: Optional[str]
    payload_size: Optional[int]
    direction: str


class TrafficGenerator:
    def __init__(self):
        self.running = False
        self.thread: Optional[threading.Thread] = None
        self.attack_mode = "normal"
        self.internal_ips = [f"192.168.1.{i}" for i in range(10, 50)]
        self.external_ips = [f"{random.randint(1,223)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}" for _ in range(100)]
        self.c2_servers = [f"10.0.0.{i}" for i in range(1, 5)]
        self.geo_cache: Dict[str, dict] = {}

    def _generate_geo_data(self, ip: str) -> dict:
        if ip in self.geo_cache:
            return self.geo_cache[ip]
        last_octet = int(ip.split(".")[-1])
        cities = [
            ("US", "New York", 40.7128, -74.0060),
            ("GB", "London", 51.5074, -0.1278),
            ("RU", "Moscow", 55.7558, 37.6173),
            ("CN", "Beijing", 39.9042, 116.4074),
            ("IN", "Mumbai", 19.0760, 72.8777),
            ("BR", "São Paulo", -23.5505, -46.6333),
            ("AU", "Sydney", -33.8688, 151.2093),
            ("AE", "Dubai", 25.2048, 55.2708),
            ("SG", "Singapore", 1.3521, 103.8198),
            ("CA", "Toronto", 43.6532, -79.3832),
            ("DE", "Berlin", 52.5200, 13.4050),
            ("JP", "Tokyo", 35.6762, 139.6503),
        ]
        country, city, lat, lon = cities[last_octet % len(cities)]
        geo = {"country": country, "city": city, "latitude": lat, "longitude": lon}
        self.geo_cache[ip] = geo
        return geo

    @property
    def get_geo_data(self, ip):
        return self._generate_geo_data(ip)

    def start(self, mode: str = "normal"):
        self.attack_mode = mode
        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=2)

    def _run(self):
        while self.running:
            packets = self._generate_batch()
            for pkt in packets:
                yield pkt
            time.sleep(0.01)

    def _generate_batch(self) -> List[PacketData]:
        if self.attack_mode == "port_scan":
            return self._generate_port_scan()
        elif self.attack_mode == "ddos":
            return self._generate_ddos()
        elif self.attack_mode == "brute_force":
            return self._generate_brute_force()
        elif self.attack_mode == "beaconing":
            return self._generate_beaconing()
        elif self.attack_mode == "exfiltration":
            return self._generate_exfiltration()
        else:
            return self._generate_normal()

    def _generate_normal(self) -> List[PacketData]:
        packets = []
        for _ in range(random.randint(1, 5)):
            src = random.choice(self.internal_ips)
            dst = random.choice(self.external_ips)
            proto = random.choice(["TCP", "UDP"])
            sport = random.randint(1024, 65535)
            dport = random.choice([80, 443, 53, 22, 3306, 5432, 8080])
            size = random.randint(64, 1500)
            packets.append(PacketData(
                timestamp=time.time(),
                src_ip=src,
                dst_ip=dst,
                src_port=sport,
                dst_port=dport,
                protocol=proto,
                packet_size=size,
                tcp_flags="PA" if proto == "TCP" else None,
                payload_size=size - 40 if proto == "TCP" else size - 28,
                direction="outbound"
            ))
        return packets

    def _generate_port_scan(self) -> List[PacketData]:
        packets = []
        scanner = random.choice(self.external_ips)
        target = random.choice(self.internal_ips)
        ports = random.sample(range(1, 65535), random.randint(20, 50))
        for port in ports:
            packets.append(PacketData(
                timestamp=time.time(),
                src_ip=scanner,
                dst_ip=target,
                src_port=random.randint(1024, 65535),
                dst_port=port,
                protocol="TCP",
                packet_size=60,
                tcp_flags="S",
                payload_size=0,
                direction="inbound"
            ))
        return packets

    def _generate_ddos(self) -> List[PacketData]:
        packets = []
        target = random.choice(self.internal_ips)
        attackers = random.sample(self.external_ips, random.randint(10, 30))
        for attacker in attackers:
            for _ in range(random.randint(10, 50)):
                proto = random.choice(["TCP", "UDP", "ICMP"])
                packets.append(PacketData(
                    timestamp=time.time(),
                    src_ip=attacker,
                    dst_ip=target,
                    src_port=random.randint(1024, 65535) if proto != "ICMP" else None,
                    dst_port=random.choice([80, 443, 53]) if proto != "ICMP" else None,
                    protocol=proto,
                    packet_size=random.randint(64, 1500),
                    tcp_flags="S" if proto == "TCP" else None,
                    payload_size=random.randint(0, 100),
                    direction="inbound"
                ))
        return packets

    def _generate_brute_force(self) -> List[PacketData]:
        packets = []
        attacker = random.choice(self.external_ips)
        target = random.choice(self.internal_ips)
        port = random.choice([22, 3389, 21, 23])
        for _ in range(random.randint(20, 100)):
            packets.append(PacketData(
                timestamp=time.time(),
                src_ip=attacker,
                dst_ip=target,
                src_port=random.randint(1024, 65535),
                dst_port=port,
                protocol="TCP",
                packet_size=random.randint(60, 200),
                tcp_flags="PA",
                payload_size=random.randint(20, 160),
                direction="inbound"
            ))
        return packets

    def _generate_beaconing(self) -> List[PacketData]:
        packets = []
        infected = random.choice(self.internal_ips)
        c2 = random.choice(self.c2_servers)
        interval = random.uniform(5.0, 30.0)
        for _ in range(random.randint(4, 6)):
            packets.append(PacketData(
                timestamp=time.time(),
                src_ip=infected,
                dst_ip=c2,
                src_port=random.randint(1024, 65535),
                dst_port=random.choice([80, 443, 8080, 53]),
                protocol="TCP",
                packet_size=random.randint(100, 500),
                tcp_flags="PA",
                payload_size=random.randint(60, 460),
                direction="outbound"
            ))
        return packets

    def _generate_exfiltration(self) -> List[PacketData]:
        packets = []
        infected = random.choice(self.internal_ips)
        dst = random.choice(self.external_ips)
        for _ in range(random.randint(5, 20)):
            size = random.randint(1000, 1500)
            packets.append(PacketData(
                timestamp=time.time(),
                src_ip=infected,
                dst_ip=dst,
                src_port=random.randint(1024, 65535),
                dst_port=random.choice([443, 53, 8080]),
                protocol="TCP",
                packet_size=size,
                tcp_flags="PA",
                payload_size=size - 40,
                direction="outbound"
            ))
        return packets


def create_mixed_traffic() -> Generator[PacketData, None, None]:
    generator = TrafficGenerator()
    modes = ["normal"] * 70 + ["port_scan"] * 5 + ["ddos"] * 5 + ["brute_force"] * 5 + ["beaconing"] * 5 + ["exfiltration"] * 10
    mode_idx = 0
    while True:
        mode = modes[mode_idx % len(modes)]
        generator.attack_mode = mode
        packets = generator._generate_batch()
        for pkt in packets:
            yield pkt
        mode_idx += 1
        time.sleep(0.1)