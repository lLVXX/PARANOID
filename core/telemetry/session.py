# core/telemetry/session.py

class TelemetrySession:
    """
    TelemetrySession
    ----------------
    Adaptador entre PacketSniffer y el sistema de telemetría.
    Garantiza un contrato estable independientemente del engine.
    """

    def __init__(self, sniffer):
        self.sniffer = sniffer
        self.raw = sniffer.final_stats() or {}

    def snapshot(self) -> dict:
        duration = float(self.raw.get("duration", 0.0))

        packets_total = int(self.raw.get("packets", 0))
        tx_pkts, tx_bytes = self.raw.get("tx", (0, 0))
        rx_pkts, rx_bytes = self.raw.get("rx", (0, 0))

        protocols = self.raw.get("protocols", {})
        flags = self.raw.get("tcp_flags", {})

        pps = packets_total / duration if duration > 0 else 0.0

        return {
            "meta": {
                "duration": duration,
                "engine": self.raw.get("engine"),
                "iface": self.raw.get("iface"),
            },
            "traffic": {
                "packets": {
                    "total": packets_total,
                    "tx": tx_pkts,
                    "rx": rx_pkts,
                },
                "bytes": {
                    "tx": tx_bytes,
                    "rx": rx_bytes,
                },
                "pps": pps,
            },
            "protocols": {
                "tcp": int(protocols.get("tcp", 0)),
                "udp": int(protocols.get("udp", 0)),
                "icmp": int(protocols.get("icmp", 0)),
                "other": int(protocols.get("other", 0)),
            },
            "tcp": {
                "syn": int(flags.get("syn", 0)),
                "synack": int(flags.get("synack", 0)),
                "rst": int(flags.get("rst", 0)),
                "fin": int(flags.get("fin", 0)),
            },
            "timing": {
                "rtt_avg": self.raw.get("rtt_avg"),
                "retransmissions": int(self.raw.get("retransmissions", 0)),
                "silences": int(self.raw.get("silences", 0)),
            },
            "detection": {
                "firewall": self.raw.get("firewall"),
                "noise": self.raw.get("noise"),
            },
            "extras": {
                "top_ports": self.raw.get("top_ports", []),
            },
        }
