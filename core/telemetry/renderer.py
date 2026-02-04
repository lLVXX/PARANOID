# core/telemetry/renderer.py

class TelemetryRenderer:
    @staticmethod
    def render(stats: dict, minimal: bool = False):
        meta = stats["meta"]
        traffic = stats["traffic"]
        protocols = stats["protocols"]
        tcp = stats["tcp"]
        timing = stats["timing"]
        detection = stats["detection"]
        extras = stats["extras"]

        print("┌────────────────────────────────────────────┐")
        print("│           PACKET INTELLIGENCE              │")
        print("├────────────────────────────────────────────┤")

        duration = meta["duration"]
        packets = traffic["packets"]["total"]
        pps = traffic["pps"]

        print(f"│ Duración:        {duration:.2f} s")
        print(f"│ Paquetes:          {packets}")
        print(f"│ PPS:               {pps:.2f}")

        if minimal:
            print("└────────────────────────────────────────────┘")
            return

        print("├────────────────────────────────────────────┤")

        print(
            f"│ TX:  {traffic['packets']['tx']} pkts | "
            f"{traffic['bytes']['tx']} bytes"
        )
        print(
            f"│ RX:  {traffic['packets']['rx']} pkts | "
            f"{traffic['bytes']['rx']} bytes"
        )

        print("├────────────────────────────────────────────┤")

        print(
            f"│ TCP:  {protocols['tcp']} | "
            f"UDP:  {protocols['udp']} | "
            f"ICMP:   {protocols['icmp']}"
        )

        print("├────────────────────────────────────────────┤")

        print(
            f"│ SYN:  {tcp['syn']} | "
            f"SYN/ACK:  {tcp['synack']}"
        )
        print(
            f"│ RST:    {tcp['rst']} | "
            f"FIN:         {tcp['fin']}"
        )

        print("├────────────────────────────────────────────┤")

        print(f"│ RTT promedio:    {timing['rtt_avg']}")
        print(f"│ Retransmisiones:   {timing['retransmissions']}")
        print(f"│ Silencios:           {timing['silences']}")

        firewall = detection["firewall"]
        print(f"│ Firewall:      {'POSIBLE' if firewall else 'NO EVIDENTE'}")

        print("├────────────────────────────────────────────┤")
        print(f"│ Nivel de ruido:     {detection['noise']}    ")
        print("└────────────────────────────────────────────┘")

        if extras["top_ports"]:
            print("\nTop puertos destino:")
            for port, count in extras["top_ports"]:
                print(f"  - {port}/tcp → {count} pkts")
