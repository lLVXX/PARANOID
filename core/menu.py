import os
import readline

from core.utils import validate_target
from core.scanner import ScannerController
from core.hosts_manager import list_hosts_entries


# Historial de comandos (AUTOCOMPLETADO)
COMMANDS = [
    "help", "clear", "exit", "quit", "q",
    "set target", "set interface",
    "show target", "show interface", "show hosts",
    "scan", "scan discover", "scan quick", "scan full", "scan service", "scan stealth"
]

# ==================================================
# READLINE AUTOCOMPLETE
# ==================================================

def setup_readline():
    readline.set_completer(complete)
    readline.parse_and_bind("tab: complete")

def complete(text, state):
    options = [c for c in COMMANDS if c.startswith(text)]
    return options[state] if state < len(options) else None

def prompt(msg):
    return input(msg).strip()

# ==================================================
# MAIN MENU
# ==================================================

def main_menu():
    scanner = ScannerController()
    target = None
    interface = "tun0"

    setup_readline()

    print("\n" + "=" * 60)
    print("PARANOID - Herramienta de reconocimiento")
    print("Escribe 'help' para ver comandos | TAB para autocompletar")
    print("=" * 60 + "\n")

    while True:
        try:
            cmd = prompt("PARANOID > ")
            if not cmd:
                continue

            cmd_lower = cmd.lower()

            # --------------------------------------------------
            # HELP
            # --------------------------------------------------
            if cmd_lower == "help":
                print("""
COMANDOS DISPONIBLES:

  set target <IP/Rango>      - Definir objetivo
  set interface <nombre>     - Definir interfaz de red

  show target                - Mostrar objetivo actual
  show interface             - Mostrar interfaz actual
  show hosts                 - Mostrar /etc/hosts

  scan                       - Mostrar opciones de escaneo
  scan discover              - Descubrimiento real de hosts vivos (LAN / ARP)
  scan quick                 - Escaneo rápido
  scan full                  - Escaneo completo
  scan service               - Detección de servicios
  scan stealth               - Escaneo sigiloso

  clear                      - Limpiar pantalla
  exit, quit, q              - Salir
""")
                continue

            # --------------------------------------------------
            # CLEAR
            # --------------------------------------------------
            if cmd_lower == "clear":
                os.system("clear" if os.name == "posix" else "cls")
                continue

            # --------------------------------------------------
            # SET TARGET
            # --------------------------------------------------
            if cmd_lower.startswith("set target"):
                parts = cmd.split()
                if len(parts) < 3:
                    print("[!] Uso: set target <IP/Rango/CIDR>")
                    continue

                target_input = parts[2]
                if validate_target(target_input):
                    target = target_input
                    scanner.set_target(target)
                    print(f"[+] Target establecido: {target}")
                else:
                    print("[!] Target inválido")
                continue

            # --------------------------------------------------
            # SET INTERFACE
            # --------------------------------------------------
            if cmd_lower.startswith("set interface"):
                parts = cmd.split()
                if len(parts) < 3:
                    print("[!] Uso: set interface <nombre>")
                    continue

                interface = parts[2]
                scanner.set_interface(interface)
                print(f"[+] Interfaz establecida: {interface}")
                continue

            # --------------------------------------------------
            # SHOW TARGET
            # --------------------------------------------------
            if cmd_lower == "show target":
                print(f"[+] Target actual: {target}" if target else "[!] No hay target definido")
                continue

            # --------------------------------------------------
            # SHOW INTERFACE
            # --------------------------------------------------
            if cmd_lower == "show interface":
                print(f"[+] Interfaz actual: {interface}")
                continue

            # --------------------------------------------------
            # SHOW HOSTS
            # --------------------------------------------------
            if cmd_lower == "show hosts":
                list_hosts_entries()
                continue

            # --------------------------------------------------
            # EXIT
            # --------------------------------------------------
            if cmd_lower in ("exit", "quit", "q"):
                print("\n[+] Saliendo...")
                break

            # --------------------------------------------------
            # SCAN MENU
            # --------------------------------------------------
            if cmd_lower == "scan":
                print("""
OPCIONES DE ESCANEO:
  discover - Descubrimiento real de hosts vivos (LAN / ARP)
  quick    - Escaneo rápido
  full     - Escaneo completo
  service  - Detección de servicios
  stealth  - Escaneo sigiloso
""")
                continue

            # --------------------------------------------------
            # SCAN MODES
            # --------------------------------------------------
            if cmd_lower.startswith("scan "):
                if not target:
                    print("[!] Primero define un target con: set target")
                    continue

                mode = cmd_lower.split()[1]

                print(f"\n[+] Iniciando escaneo {mode}...")
                print(f"[+] Interfaz: {interface}")

                try:
                    if mode == "discover":
                        scanner.discover()

                    elif mode == "quick":
                        scanner.scan_quick()

                    elif mode == "full":
                        scanner.scan_full()

                    elif mode == "service":
                        scanner.scan_service()

                    elif mode == "stealth":
                        scanner.scan_stealth()

                    else:
                        print("[!] Modo inválido")

                except KeyboardInterrupt:
                    print("\n[!] Escaneo cancelado")

                continue

            # --------------------------------------------------
            # UNKNOWN COMMAND
            # --------------------------------------------------
            print(f"[!] Comando no reconocido: '{cmd}'")
            print("[i] Escribe 'help' para ver comandos")

        except KeyboardInterrupt:
            print("\n[i] Usa 'exit' para salir")
        except Exception as e:
            print(f"[!] Error: {e}")
