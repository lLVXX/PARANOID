# core/scanner_discovery.py

import subprocess
import ipaddress
import time
import re

from core.packet_sniffer import PacketSniffer


class DiscoveryScanner:
    def __init__(self, target, interface):
        self.target = target
        self.interface = interface

        if "/" not in target:
            raise ValueError("Discovery requiere red CIDR (ej: 192.168.1.0/24)")

        self.network = ipaddress.ip_network(target, strict=False)
        self.hosts = []

    # -------------------------------------------------

    def _run_arp_scan(self):
        """
        Ejecuta arp-scan como herramienta externa
        """
        cmd = [
            "arp-scan",
            "--interface", self.interface,
            "--localnet"
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
        except FileNotFoundError:
            print("[!] arp-scan no está instalado")
            return []

        hosts = []

        for line in result.stdout.splitlines():
            # Formato típico:
            # 192.168.1.1   aa:bb:cc:dd:ee:ff   Huawei Technologies
            m = re.match(r"(\d+\.\d+\.\d+\.\d+)\s+([0-9A-Fa-f:]{17})(?:\s+(.*))?", line)
            if not m:
                continue

            ip, mac, vendor = m.groups()
            if ipaddress.ip_address(ip) in self.network:
                hosts.append({
                    "ip": ip,
                    "mac": mac,
                    "vendor": vendor or "Unknown"
                })

        return hosts

    # -------------------------------------------------

    def run(self):
        print(f"\n[+] Iniciando host discovery en {self.network}")
        print(f"[+] Interfaz: {self.interface}")

        sniffer = PacketSniffer(target=str(self.network), iface=self.interface)
        sniffer.start()

        start = time.time()
        self.hosts = self._run_arp_scan()
        elapsed = time.time() - start

        stats = sniffer.stop()

        print(f"\n[✓] Host discovery completado ({elapsed:.2f}s)")
        print(f"\n[✓] Hosts vivos detectados ({len(self.hosts)}):\n")

        for idx, h in enumerate(self.hosts, 1):
            print(
                f" {idx:02d}. {h['ip']} | MAC: {h['mac']} ({h['vendor']})"
            )

        print("\n[+] Packet sniffer stats:\n")
        print(PacketSniffer.render(stats))

        return self.hosts
