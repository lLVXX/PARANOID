class CommandHandler:
    def __init__(self, scanner):
        self.scanner = scanner
        self.running = True

    def handle(self, cmd):
        parts = cmd.split()

        if not parts:
            return

        if parts[0] == "exit":
            self.running = False

        elif parts[0] == "help":
            self.help()

        elif parts[0] == "set":
            self.set_option(parts)

        elif parts[0] == "scan":
            self.scan(parts)

        elif parts[0] == "show":
            self.show(parts)

        else:
            print("[!] Comando desconocido")

    def help(self):
        print("""
Comandos disponibles:
  help                   Mostrar ayuda
  set target <IP/Host>    Definir objetivo
  scan quick              Escaneo rápido
  scan full               Escaneo completo
  scan services           Servicios y scripts
  scan stealth            Escaneo sigiloso
  show options            Mostrar configuración
  exit                    Salir
        """)

    def set_option(self, parts):
        if len(parts) == 3 and parts[1] == "target":
            self.scanner.target = parts[2]
            print(f"[+] Target establecido: {parts[2]}")
        else:
            print("[!] Uso: set target <IP>")

    def scan(self, parts):
        if not self.scanner.target:
            print("[!] Define un target primero")
            return

        if parts[1] == "quick":
            self.scanner.quick_scan()
        elif parts[1] == "full":
            self.scanner.full_scan()
        elif parts[1] == "services":
            self.scanner.service_scan()
        elif parts[1] == "stealth":
            self.scanner.stealth_scan()
        else:
            print("[!] Tipo de escaneo inválido")

    def show(self, parts):
        if parts[1] == "options":
            print(f"Target: {self.scanner.target}")
