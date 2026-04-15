import pandas as pd
import numpy as np

def extract_features(df_packets):
    """
    Extracts statistical features per source IP.
    """
    if df_packets.empty:
        return pd.DataFrame()

    # Features:
    # 1. Packet count
    # 2. Total bytes
    # 3. Unique destination IPs
    # 4. Unique destination ports
    # 5. Protocol entropy (simplified: ratio of TCP/UDP/Other)
    # 6. Average packet size
    # 7. Standard deviation of packet sizes
    
    features = df_packets.groupby('src_ip').agg(
        packet_count=('id', 'count'),
        total_bytes=('packet_size', 'sum'),
        unique_dst_ips=('dst_ip', 'nunique'),
        unique_dst_ports=('dst_port', 'nunique'),
        avg_packet_size=('packet_size', 'mean'),
        std_packet_size=('packet_size', 'std'),
    ).fillna(0)

    # Add protocol ratios
    proto_counts = df_packets.groupby(['src_ip', 'protocol']).size().unstack(fill_value=0)
    for col in ['TCP', 'UDP', 'Other']:
        if col not in proto_counts.columns:
            proto_counts[col] = 0
            
    total_proto = proto_counts.sum(axis=1)
    for col in ['TCP', 'UDP', 'Other']:
        features[f'{col.lower()}_ratio'] = proto_counts[col] / total_proto

    return features
