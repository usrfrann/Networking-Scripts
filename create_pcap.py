import logging
import os
import time
from datetime import datetime
from scapy.all import sniff, wrpcap

CAPTURE_INTERVAL = 5 * 60
PACKETS_PER_INTERVAL = 0
BASE_DIR = "./pcap_captures"

def create_timestamped_folder():
    timestamp = datetime.now().strftime("%Y-%m-%d_%:%M:%S")
    folder_path = os.path.join(BASE_DIR, timestamp)
    os.makedirs(folder_path, exist_ok=True)
    return folder_path

def capture_packets():
    logging.info(f"Starting 5 min packet captures. Saving to: {BASE_DIR}")
    while True:
        folder_path = create_timestamped_folder()
        filename = os.path.join(folder_path, "capture.pcap")
        logging.info(f"Saving to: {filename}")
        packets = sniff(timeout=CAPTURE_INTERVAL, count=PACKETS_PER_INTERVAL)
        wrpcap(filename, packets)

        print(f"Saved {len(packets)} packets to {filename}")

if __name__ == "__main__":
    os.makedirs(BASE_DIR, exist_ok=True)
    try:
        capture_packets()
    except KeyboardInterrupt:
        logging.error(f"Stopped by keyboard interrupt.")