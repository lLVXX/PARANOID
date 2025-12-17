import subprocess
import os
import re
import time
import sys

from core.packet_sniffer import PacketSniffer
from core.hosts_manager import add_to_hosts


class NmapScanner:
    def __init__(self):
        self.target = None
        self.interface = "tun0"
        self.results_dir = "results"

    # ==================================================
    # ENTRY POINT
    # ==================================================

    def run(self, args, scan_name):
        if not self.target:
            print("[!] No hay target definido")
            return

        if "/" in self.target or "-" in self.target:
            self._run_network_target(args, scan_name)
        else:
            self._run_single_target(args, scan_name)

    # ==================================================
    # SINGLE HOST
    # ==================================================

    def _run_single_target(self, args, scan_name):
        target_ip = self.target
        print(f"\n[+] Ejecutando escaneo en host: {target_ip}")

        cmd = ["nmap"] + args + ["--stats-every", "1s", target_ip]

        sniffer = PacketSniffer(target_ip, iface=self.interface)
        sniffer.start()

        start = time.time()
        nmap_raw = self._run_with_progress(cmd, scan_name)
        duration = time.time() - start

        print(f"\n[✓] Escaneo completado ({duration:.2f}s)\n")

        useful = self._extract_useful_nmap_output(nmap_raw)
        if useful:
            print(useful)

        stats = sniffer.stop()
        traffic_summary = PacketSniffer.render(stats)
        ports_summary = self._process_ports(nmap_raw)

        if traffic_summary:
            print("\n[+] Packet sniffer stats:\n")
            print(traffic_summary)

        hostnames_summary = self._detect_hostnames(nmap_raw, target_ip)

        self._save_result(
            target_ip,
            useful,
            nmap_raw,
            scan_name,
            traffic_summary,
            ports_summary,
            hostnames_summary
        )

    # ==================================================
    # NETWORK TARGET
    # ==================================================

    def _run_network_target(self, args, scan_name):
        print(f"\n[+] Ejecutando escaneo de red: {self.target}")

        cmd = ["nmap"] + args + ["--stats-every", "1s", self.target]

        sniffer = PacketSniffer(self.target, iface=self.interface)
        sniffer.start()

        start = time.time()
        nmap_raw = self._run_with_progress(cmd, scan_name)
        duration = time.time() - start

        print(f"\n[✓] Escaneo de red completado ({duration:.2f}s)\n")

        useful = self._extract_useful_nmap_output(nmap_raw)
        if useful:
            print(useful)

        stats = sniffer.stop()
        traffic_summary = PacketSniffer.render(stats)
        ports_summary = self._process_ports(nmap_raw)

        if traffic_summary:
            print("\n[+] Packet sniffer stats:\n")
            print(traffic_summary)

        hostnames_summary = self._detect_hostnames(nmap_raw, self.target)

        self._save_result(
            self.target,
            useful,
            nmap_raw,
            scan_name,
            traffic_summary,
            ports_summary,
            hostnames_summary
        )

    # ==================================================
    # ACTIVE DIRECTORY DOMAIN DETECTION
    # ==================================================

    def _extract_ad_domain(self, output):
        ad_indicators = (
            "kerberos-sec",
            "Active Directory LDAP",
            "NetBIOS_Domain_Name",
            "DNS_Domain_Name",
            "DNS_Tree_Name"
        )

        if not any(ind in output for ind in ad_indicators):
            return None

        patterns = [
            r'DNS_Domain_Name:\s*([a-zA-Z0-9.-]+)',
            r'DNS_Tree_Name:\s*([a-zA-Z0-9.-]+)',
            r'Domain:\s*([a-zA-Z0-9.-]+)'
        ]

        for pat in patterns:
            m = re.search(pat, output)
            if m:
                return m.group(1).strip().lower()

        return None

    # ==================================================
    # HOSTNAME SANITIZER
    # ==================================================

    def _sanitize_hostname(self, hostname):
        hostname = hostname.strip().lower()

        # descartar si termina en punto
        if hostname.endswith("."):
            return None

        # descartar si termina en numero (htb0, corp1, etc)
        if re.search(r'\d$', hostname):
            return None

        # formato hostname basico
        if not re.match(r'^[a-z0-9.-]+\.[a-z]{2,}$', hostname):
            return None

        return hostname

    # ==================================================
    # HOSTNAME DETECTION
    # ==================================================

    def _detect_hostnames(self, output, target):
        confirmed_raw = set()
        inferred_raw = set()

        noise = {"nmap.org", "www.nmap.org", "scanme.nmap.org"}

        confirmed_raw |= set(re.findall(r'commonName=([a-zA-Z0-9.-]+)', output))
        confirmed_raw |= set(re.findall(r'DNS:([a-zA-Z0-9.-]+)', output))

        ad_domain = self._extract_ad_domain(output)
        if ad_domain:
            confirmed_raw.add(ad_domain)

        inferred_raw |= set(re.findall(
            r'http[s]?://([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
            output
        ))

        confirmed = set()
        inferred = set()

        for h in confirmed_raw:
            h = self._sanitize_hostname(h)
            if h and h not in noise:
                confirmed.add(h)

        for h in inferred_raw:
            h = self._sanitize_hostname(h)
            if h and h not in noise:
                inferred.add(h)

        inferred -= confirmed

        lines = []

        if confirmed:
            print("\n[+] Hostnames confirmados:")
            lines.append("[+] Hostnames confirmados:")
            for i, h in enumerate(sorted(confirmed), 1):
                print(f"    {i}. {h}")
                lines.append(f"    {i}. {h}")

            if input("\n[?] ¿Agregar hostnames CONFIRMADOS a /etc/hosts? (y/n) > ").lower() == "y":
                add_to_hosts(target.split("/")[0], confirmed)

        if inferred:
            print("\n[~] Hostnames inferidos (HTTP / redirect):")
            lines.append("\n[~] Hostnames inferidos (HTTP / redirect):")
            for i, h in enumerate(sorted(inferred), 1):
                print(f"    {i}. {h}")
                lines.append(f"    {i}. {h}")

            if input("\n[?] ¿Agregar hostnames INFERIDOS a /etc/hosts? (y/n) > ").lower() == "y":
                add_to_hosts(target.split("/")[0], inferred)

        return "\n".join(lines)

    # ==================================================
    # SAVE RESULTS
    # ==================================================

    def _save_result(self, target, useful, raw, scan, traffic="", ports="", hostnames=""):
        os.makedirs(self.results_dir, exist_ok=True)
        safe = target.replace("/", "_")
        base = f"{self.results_dir}/{safe}"
        os.makedirs(base, exist_ok=True)

        ts = time.strftime("%Y%m%d_%H%M%S")

        with open(f"{base}/{scan.replace(' ', '_')}_{ts}.txt", "w") as f:
            f.write(useful + "\n\n")
            f.write(ports + "\n\n")
            f.write(hostnames + "\n\n")
            f.write(traffic + "\n")

        with open(f"{base}/NMAP_RAW_{ts}.txt", "w") as f:
            f.write(raw)

        print(f"\n[✓] Resultados guardados en {base}/")

    # ==================================================
    # HELPERS
    # ==================================================

    def _run_with_progress(self, cmd, label):
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )

        output = []
        last = -1

        while True:
            line = process.stdout.readline()
            if not line and process.poll() is not None:
                break
            if not line:
                continue

            output.append(line)
            m = re.search(r'(\d+\.\d+)% done', line)
            if m:
                pct = int(float(m.group(1)))
                if pct != last:
                    last = pct
                    bar = "█" * (pct // 3) + "░" * (30 - pct // 3)
                    sys.stdout.write(f"\r[SCAN] {label}: [{bar}] {pct}%")
                    sys.stdout.flush()

        sys.stdout.write("\r" + " " * 80 + "\r")
        return "".join(output)

    def _extract_useful_nmap_output(self, output):
        lines = output.splitlines()
        for i, l in enumerate(lines):
            if l.strip().startswith("PORT"):
                return "\n".join(lines[i:])
        return ""

    def _process_ports(self, output):
        ports = re.findall(r'(\d+)/tcp\s+open\s+(\S+)', output)
        if not ports:
            return ""

        print(f"\n[+] PUERTOS ABIERTOS ({len(ports)}):")
        lines = [f"[+] PUERTOS ABIERTOS ({len(ports)}):"]

        for p, s in ports:
            icon = "🌐" if p in ("80", "443") else "🔧"
            print(f"    {icon} {p}/tcp - {s}")
            lines.append(f"    {icon} {p}/tcp - {s}")

        return "\n".join(lines)

    # ==================================================
    # SCAN MODES
    # ==================================================

    def quick_scan(self):
        self.run(["-T4", "--open", "-p", "21,22,80,443"], "Quick scan")

    def full_scan(self):
        self.run(["-T4", "--open", "-p-"], "Full scan")

    def service_scan(self):
        self.run(["-sV", "-sC", "--open"], "Service scan")

    def stealth_scan(self):
        self.run(["-sS", "--open", "-T2"], "Stealth scan")
