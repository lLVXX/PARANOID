# core/cli/commands/set.py
from core.cli.commands.base import Command
from core.utils.validation import validate_target


class SetCommand(Command):
    def matches(self, cmd: str) -> bool:
        return cmd.startswith("set ")

    def execute(self, cmd, session_mgr, scanner) -> bool:
        parts = cmd.split()
        session = session_mgr.current

        if parts[1] == "target" and len(parts) == 3:
            target = parts[2]

            if not validate_target(target):
                print("[!] Target inválido")
                return True

            # ✅ MODELO NUEVO CORRECTO
            session.register_target(target)

            # 🎯 set target = agregar + activar
            session.active_target_index = session.targets.index(target)
            session_mgr._write_meta()

            print(f"[+] Target activo: {target}")

            return True

        if parts[1] == "interface" and len(parts) == 3:
            iface = parts[2]
            session.set_interface(iface)
            scanner.set_interface(iface)
            print(f"[+] Interfaz establecida: {iface}")
            return True

        print("[!] Uso inválido de set")
        return True
