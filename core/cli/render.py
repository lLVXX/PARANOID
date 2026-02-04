# core/cli/render.py

from core.utils.hosts import add_to_hosts
from core.telemetry.renderer import TelemetryRenderer


def render_result(result, target: str):
    if not result:
        print("[!] El escaneo no devolvió resultados")
        return

    engine = result.metadata.get("engine")

    # ==================================================
    # FFUF OUTPUT (RUTAS, NO HOSTS, NO PUERTOS)
    # ==================================================
    if engine == "ffuf":
        if result.useful_output:
            print("\n[+] Rutas encontradas:\n")
            for r in result.useful_output:
                print(f"[{r.get('status')}] /{r.get('path')} ({r.get('length')} bytes)")
                print(f"    → {r.get('url')}")

        if result.traffic:
            print("\n[+] Packet sniffer stats:\n")
            TelemetryRenderer.render(result.traffic, minimal=True)

        return  # ⛔ FFUF termina aquí

    # ==================================================
    # NMAP OUTPUT (NO TOCAR, YA ESTÁ PERFECTO)
    # ==================================================
    if result.useful_output:
        print("\n" + str(result.useful_output))

    if result.ports:
        print("\n" + result.ports)

    if result.traffic:
        print("\n[+] Packet sniffer stats:\n")
        TelemetryRenderer.render(result.traffic)

    if result.hostnames:
        print("\n[+] Hostnames descubiertos:")
        for i, h in enumerate(sorted(result.hostnames), 1):
            print(f"    {i}. {h}")

        choice = input("\n[?] ¿Agregar hostnames a /etc/hosts? (y/n) > ").lower()
        if choice == "y":
            add_to_hosts(target, result.hostnames)
