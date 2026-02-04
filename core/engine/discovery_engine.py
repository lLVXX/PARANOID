#core/engine/discovery_engine.py

from core.engine.packet_sniffer import PacketSniffer
import subprocess
import ipaddress
import time
import re

class DiscoveryEngine:

    def run(self, context):
        target = context.target
        iface = context.interface

        if "/" not in target:
            raise RuntimeError("Discovery requiere CIDR")

        network = ipaddress.ip_network(target, strict=False)

        print(f"\n[+] Iniciando host discovery en {network}")
        print(f"[+] Interfaz: {iface}")

        sniffer = PacketSniffer(target=str(network), iface=iface)
        sniffer.start()

        cmd = ["arp-scan", "--interface", iface, "--localnet"]
        result = subprocess.run(cmd, capture_output=True, text=True)

        hosts = []
        for line in result.stdout.splitlines():
            m = re.match(r"(\d+\.\d+\.\d+\.\d+)\s+([0-9A-Fa-f:]{17})(?:\s+(.*))?", line)
            if m:
                ip, mac, vendor = m.groups()
                if ipaddress.ip_address(ip) in network:
                    hosts.append((ip, mac, vendor or "Unknown"))

        stats = sniffer.stop()

        for i, h in enumerate(hosts, 1):
            print(f" {i:02d}. {h[0]} | MAC: {h[1]} ({h[2]})")

        print("\n[+] Packet sniffer stats:\n")
        print(PacketSniffer.render(stats))

        return hosts
