# core/packet_sniffer.py

import time
import threading
import ipaddress
from collections import defaultdict

from scapy.all import sniff, TCP, UDP, ICMP, ARP, IP


class PacketSniffer:
    def __init__(self, target=None, iface=None):
        self.iface = iface
        self.running = False
        self.thread = None

        self.start_time = None
        self.end_time = None

        self.target = None
        self.network = None

        if target:
            try:
                if "/" in target:
                    self.network = ipaddress.ip_network(target, strict=False)
                else:
                    self.target = ipaddress.ip_address(target)
            except ValueError:
                raise ValueError(f"Target inválido: {target}")

        # ------------------------------
        # CONTADORES CRUDOS
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

        # Métricas avanzadas
        self.dst_ports = defaultdict(int)
        self.seen_seq = set()
        self.retransmissions = 0

        self.syn_timestamps = {}
        self.rtt_samples = []

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
                    rtt = time.time() - self.syn_timestamps[key]
                    self.rtt_samples.append(rtt)

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

    @property
    def duration(self):
        return max((self.end_time or time.time()) - self.start_time, 0.001)

    def _finalize(self):
        syn = self.stats["syn"]
        synack = self.stats["synack"]

        silence = max(syn - (synack + self.stats["rst"]), 0)
        ratio = (synack / syn * 100) if syn > 0 else 0.0
        pps = self.stats["total"] / self.duration

        if pps < 30:
            noise = "SIGILOSO"
        elif pps < 80:
            noise = "BAJO"
        elif pps < 150:
            noise = "MEDIO"
        else:
            noise = "ALTO"

        avg_rtt = (
            sum(self.rtt_samples) / len(self.rtt_samples)
            if self.rtt_samples else 0.0
        )

        firewall = "NO APLICABLE"
        if syn > 0:
            firewall = "POSIBLE" if silence / syn > 0.5 else "NO EVIDENTE"

        return {
            **self.stats,
            "duration": self.duration,
            "pps": pps,
            "silence": silence,
            "response_ratio": ratio,
            "noise": noise,
            "firewall": firewall,
            "retransmissions": self.retransmissions,
            "avg_rtt": avg_rtt,
            "top_ports": sorted(
                self.dst_ports.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]
        }

    # --------------------------------------------------

    @staticmethod
    def render(s):
        if not s or s.get("total", 0) == 0:
            return "[!] No se capturó tráfico durante el escaneo"

        return f"""
┌────────────────────────────────────────────┐
│           PACKET INTELLIGENCE              │
├────────────────────────────────────────────┤
│ Duración:        {s['duration']:>6.2f} s
│ Paquetes:        {s['total']:>6}
│ PPS:             {s['pps']:>6.1f}
├────────────────────────────────────────────┤
│ TX: {s['tx_pkts']:>5} pkts | {s['tx_bytes']:>7} bytes
│ RX: {s['rx_pkts']:>5} pkts | {s['rx_bytes']:>7} bytes
├────────────────────────────────────────────┤
│ TCP: {s['tcp']:>5} | UDP: {s['udp']:>3} | ICMP: {s['icmp']:>3}
├────────────────────────────────────────────┤
│ SYN: {s['syn']:>5} | SYN/ACK: {s['synack']:>5}
│ RST: {s['rst']:>5} | FIN:     {s['fin']:>5}
│ Ratio respuesta: {s['response_ratio']:>5.1f}%
├────────────────────────────────────────────┤
│ RTT promedio:    {s['avg_rtt']*1000:>5.1f} ms
│ Retransmisiones: {s['retransmissions']:>5}
│ Silencios:       {s['silence']:>5}
│ Firewall:      {s['firewall']:^12}
├────────────────────────────────────────────┤
│ Nivel de ruido: {s['noise']:^12}
└────────────────────────────────────────────┘
""" + (
            "\nTop puertos destino:\n" +
            "\n".join(f"  - {p}/tcp → {c} pkts" for p, c in s["top_ports"])
            if s.get("top_ports") else ""
        )
