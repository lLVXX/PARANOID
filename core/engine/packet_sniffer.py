# core/engine/packet_sniffer.py

import time
import threading
import ipaddress
from collections import defaultdict

from scapy.all import sniff, TCP, UDP, ICMP, ARP, IP


class PacketSniffer:
    """
    Packet sniffer REAL usado por Nmap y FFUF.
    - Nmap: análisis de puertos / ruido / firewall
    - FFUF: análisis de volumen + contexto HTTP
    """

    def __init__(self, target=None, iface=None, mode="generic"):
        self.iface = iface
        self.mode = mode
        self.running = False
        self.thread = None

        self.start_time = None
        self.end_time = None

        self.target = None
        self.network = None

        # FFUF
        self.found_routes = []

        if target:
            try:
                if "/" in target:
                    self.network = ipaddress.ip_network(target, strict=False)
                else:
                    self.target = ipaddress.ip_address(target)
            except ValueError:
                raise ValueError(f"Target inválido: {target}")

        # ------------------------------
        # CONTADORES
        # ------------------------------
        self.stats = {
            "total": 0,
            "tcp": 0,
            "udp": 0,
            "icmp": 0,
            "arp": 0,
            "other": 0,
            "syn": 0,
            "synack": 0,
            "rst": 0,
            "fin": 0,
            "tx_pkts": 0,
            "rx_pkts": 0,
            "tx_bytes": 0,
            "rx_bytes": 0,
        }

        self.dst_ports = defaultdict(int)
        self.seen_seq = set()
        self.retransmissions = 0

        self.syn_timestamps = {}
        self.rtt_samples = []

    # --------------------------------------------------
    # SCOPE
    # --------------------------------------------------

    def _packet_in_scope(self, pkt):
        if not pkt.haslayer(IP):
            return False

        ip = pkt[IP]

        if self.target:
            return (
                ipaddress.ip_address(ip.src) == self.target
                or ipaddress.ip_address(ip.dst) == self.target
            )

        if self.network:
            return (
                ipaddress.ip_address(ip.src) in self.network
                or ipaddress.ip_address(ip.dst) in self.network
            )

        return True

    # --------------------------------------------------
    # PROCESAMIENTO
    # --------------------------------------------------

    def _process_packet(self, pkt):
        if not self.running or not self._packet_in_scope(pkt):
            return

        self.stats["total"] += 1

        if pkt.haslayer(IP):
            ip = pkt[IP]
            size = len(pkt)

            if self.target:
                if ip.dst == str(self.target):
                    self.stats["tx_pkts"] += 1
                    self.stats["tx_bytes"] += size
                elif ip.src == str(self.target):
                    self.stats["rx_pkts"] += 1
                    self.stats["rx_bytes"] += size

        if pkt.haslayer(TCP):
            self.stats["tcp"] += 1
            tcp = pkt[TCP]
            flags = tcp.flags

            self.dst_ports[tcp.dport] += 1

            seq_id = (tcp.sport, tcp.dport, tcp.seq)
            if seq_id in self.seen_seq:
                self.retransmissions += 1
            else:
                self.seen_seq.add(seq_id)

            if flags & 0x02 and not flags & 0x10:
                self.stats["syn"] += 1
                self.syn_timestamps[(tcp.sport, tcp.dport)] = time.time()

            elif flags & 0x12:
                self.stats["synack"] += 1
                key = (tcp.dport, tcp.sport)
                if key in self.syn_timestamps:
                    self.rtt_samples.append(
                        time.time() - self.syn_timestamps[key]
                    )

            elif flags & 0x04:
                self.stats["rst"] += 1

            elif flags & 0x01:
                self.stats["fin"] += 1

        elif pkt.haslayer(UDP):
            self.stats["udp"] += 1
            self.dst_ports[pkt[UDP].dport] += 1

        elif pkt.haslayer(ICMP):
            self.stats["icmp"] += 1

        elif pkt.haslayer(ARP):
            self.stats["arp"] += 1

        else:
            self.stats["other"] += 1

    # --------------------------------------------------
    # SNIFF LOOP
    # --------------------------------------------------

    def _sniff(self):
        sniff(
            iface=self.iface,
            filter=self._build_bpf(),
            prn=self._process_packet,
            store=False,
            stop_filter=lambda _: not self.running
        )

    def _build_bpf(self):
        if self.target:
            return f"host {self.target}"
        if self.network:
            return f"net {self.network}"
        return None

    # --------------------------------------------------
    # CONTROL
    # --------------------------------------------------

    def start(self):
        self.running = True
        self.start_time = time.time()

        self.thread = threading.Thread(target=self._sniff, daemon=True)
        self.thread.start()

        scope = self.target or self.network or "ALL"
        print(f"[+] Packet sniffer iniciado (scope={scope})")

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=2)

        self.end_time = time.time()
        print(f"[+] Packet sniffer detenido ({self.duration:.2f}s)")
        return self._finalize()

    # --------------------------------------------------
    # FINALIZACIÓN
    # --------------------------------------------------

    @property
    def duration(self):
        return max((self.end_time or time.time()) - self.start_time, 0.001)

    def add_routes(self, routes):
        self.found_routes = routes or []

    def final_stats(self) -> dict:
        """
        CONTRATO ÚNICO PARA TELEMETRÍA
        (usado por TelemetrySession / Analyzer / Renderer)
        """
        data = self._finalize()

        return {
            "duration": data["duration"],
            "total_packets": data["total"],
            "packets": data["total"],
            "pps": data["pps"],
            "tx": (data["tx_pkts"], data["tx_bytes"]),
            "rx": (data["rx_pkts"], data["rx_bytes"]),
            "protocols": {
                "tcp": data["tcp"],
                "udp": data["udp"],
                "icmp": data["icmp"],
            },
            "tcp_flags": {
                "syn": data["syn"],
                "synack": data["synack"],
                "rst": data["rst"],
                "fin": data["fin"],
            },
            "top_ports": data.get("top_ports", []),
            "noise": data["noise"],
            "firewall": data["firewall"] == "POSIBLE",
            "rtt_avg": data["avg_rtt"] * 1000,
            "retransmissions": data["retransmissions"],
            "silences": data["silence"],
            "routes": data.get("routes", []),
        }

    def _finalize(self):
        syn = self.stats["syn"]
        synack = self.stats["synack"]

        silence = max(syn - (synack + self.stats["rst"]), 0)
        ratio = (synack / syn * 100) if syn > 0 else 0.0
        pps = self.stats["total"] / self.duration

        noise = (
            "SIGILOSO" if pps < 30 else
            "BAJO" if pps < 80 else
            "MEDIO" if pps < 150 else
            "ALTO"
        )

        avg_rtt = (
            sum(self.rtt_samples) / len(self.rtt_samples)
            if self.rtt_samples else 0.0
        )

        firewall = (
            "POSIBLE" if syn and silence / syn > 0.5 else "NO EVIDENTE"
        )

        data = {
            **self.stats,
            "duration": self.duration,
            "pps": pps,
            "silence": silence,
            "response_ratio": ratio,
            "noise": noise,
            "firewall": firewall,
            "retransmissions": self.retransmissions,
            "avg_rtt": avg_rtt,
        }

        if self.mode != "ffuf":
            data["top_ports"] = sorted(
                self.dst_ports.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]

        if self.found_routes:
            data["routes"] = self.found_routes

        return data
