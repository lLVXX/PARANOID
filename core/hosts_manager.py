import os
import re

HOSTS_FILE = "/etc/hosts"


def add_to_hosts(ip, domains):
    """
    Agrega una línea IP -> múltiples hostnames a /etc/hosts
    Ejemplo:
    10.10.11.96 fries.htb dc01.fries.htb
    """

    if not ip or not domains:
        print("[!] IP o dominio vacío")
        return False

    # Normalizar a lista
    if isinstance(domains, str):
        domains = [domains]

    # Limpiar duplicados y ordenar
    domains = sorted(set(domains))

    # Validar IP
    if not re.match(r"^\d{1,3}(\.\d{1,3}){3}$", ip):
        print(f"[!] IP inválida: {ip}")
        return False

    entry = f"{ip}\t{' '.join(domains)}"

    print(f"\n[+] Agregando a /etc/hosts:")
    print(f"    {entry}")

    try:
        existing_lines = []

        if os.path.exists(HOSTS_FILE):
            with open(HOSTS_FILE, "r") as f:
                existing_lines = f.readlines()

            # Evitar duplicados exactos
            for line in existing_lines:
                if line.strip() == entry:
                    print("[i] La entrada ya existe")
                    return True

        with open(HOSTS_FILE, "a") as f:
            f.write(entry + "\n")

        print("[✓] Añadido correctamente")
        return True

    except PermissionError:
        print("[!] Permisos insuficientes. Ejecuta con sudo.")
    except Exception as e:
        print(f"[!] Error: {e}")

    return False


def list_hosts_entries():
    """
    Lista las entradas actuales de /etc/hosts
    """
    try:
        if not os.path.exists(HOSTS_FILE):
            print("[!] /etc/hosts no existe")
            return

        print("\n=== Entradas en /etc/hosts ===")
        with open(HOSTS_FILE, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    print(f"  {line}")
        print("=" * 30)

    except Exception as e:
        print(f"[!] Error leyendo /etc/hosts: {e}")
