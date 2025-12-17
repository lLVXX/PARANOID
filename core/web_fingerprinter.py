import re
import subprocess
from core.hosts_manager import add_to_hosts

WEB_PORTS = {80, 443, 8000, 8080, 8443}


class WebFingerprinter:

    @staticmethod
    def detect_ports(nmap_output: str):
        """Devuelve lista de puertos web detectados."""
        ports = []

        for line in nmap_output.splitlines():
            m = re.search(r"(\d+)/tcp\s+open", line)
            if m:
                port = int(m.group(1))
                if port in WEB_PORTS:
                    ports.append(port)

        return ports

    # ---------------------------------------------------------------------

    @staticmethod
    def detect_web_host(ip: str, port: int):
        """
        Detecta el host real del servicio web:
        - Location redirect
        - Host en HTML
        - Cookies
        - <title>
        """

        url = f"http://{ip}:{port}" if port != 80 else f"http://{ip}"

        try:
            result = subprocess.run(
                ["curl", "-k", "-I", "-L", "--max-time", "4", url],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            headers = result.stdout

            # 1) Location:
            m = re.search(r"Location:\s*https?://([^/\s]+)", headers, re.I)
            if m:
                dom = m.group(1).strip()
                if dom.lower() != "nmap.org":
                    return dom

            # 2) Host por Set-Cookie (a veces aparece)
            m = re.search(r"Domain=([^;]+)", headers, re.I)
            if m:
                return m.group(1).strip()

            # 3) Server header (última opción)
            m = re.search(r"Server:\s*([^/\s]+)", headers, re.I)
            if m and "." in m.group(1):
                return m.group(1).strip()

        except Exception as e:
            print(f"[!] Error detectando dominio: {e}")

        return None

    # ---------------------------------------------------------------------

    @staticmethod
    def process(ip, nmap_output):
        """
        Detecta puertos web, intenta descubrir host real
        y pregunta si se agrega al /etc/hosts.
        """

        ports = WebFingerprinter.detect_ports(nmap_output)

        if not ports:
            return

        print(f"\n[+] Servicios web detectados en puertos: {ports}")
        print("\n=== Gestión /etc/hosts ===")

        for port in ports:
            domain = WebFingerprinter.detect_web_host(ip, port)

            if domain:
                print(f"[+] Dominio detectado en puerto {port}: {domain}")
                choice = input("¿Deseas agregarlo al /etc/hosts? (y/n) > ").lower()

                if choice == "y":
                    add_to_hosts(ip, domain)
                    print(f"[✓] Agregado: {ip} {domain}")

            else:
                print(f"[!] No se pudo detectar dominio en puerto {port}")
