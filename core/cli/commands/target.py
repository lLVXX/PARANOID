#core/cli/commands/target.py




from core.cli.commands.base import Command
from core.utils.validation import validate_target


class TargetCommand(Command):
    def matches(self, cmd: str) -> bool:
        return cmd.startswith("target ")

    def execute(self, cmd, session_mgr, scanner) -> bool:
        parts = cmd.split()
        session = session_mgr.current

        if not session:
            print("[!] No hay sesión activa")
            return True

        # ---------------- target add <value> ----------------
        # Agrega target SIN cambiar el activo
        if parts[1] == "add" and len(parts) == 3:
            target = parts[2]

            if not validate_target(target):
                print("[!] Target inválido")
                return True

            if target in session.targets:
                print("[i] El target ya existe")
                return True

            session.register_target(target)
            session_mgr._write_meta()

            print(f"[+] Target agregado: {target}")
            return True

        # ---------------- target list ----------------
        if parts[1] == "list":
            if not session.targets:
                print("[i] No hay targets")
                return True

            for idx, t in enumerate(session.targets):
                marker = " ← activo" if idx == session.active_target_index else ""
                print(f"[{idx}] {t}{marker}")
            return True

        # ---------------- target use <index> ----------------
        if parts[1] == "use" and len(parts) == 3:
            try:
                idx = int(parts[2])
            except ValueError:
                print("[!] Índice inválido")
                return True

            if not session.set_active_target(idx):
                print("[!] Target no existe")
                return True

            session_mgr._write_meta()
            print(f"[+] Target activo: {session.get_active_target()}")
            return True

        # ---------------- target remove <index> ----------------
        if parts[1] == "remove" and len(parts) == 3:
            try:
                idx = int(parts[2])
            except ValueError:
                print("[!] Índice inválido")
                return True

            if idx < 0 or idx >= len(session.targets):
                print("[!] Target no existe")
                return True

            target = session.targets[idx]
            session_mgr.delete_target(target)
            session_mgr._write_meta()

            print(f"[+] Target eliminado: {target}")
            return True

        # ---------------- uso inválido ----------------
        print("[!] Uso: target add <value> | list | use <id> | remove <id>")
        return True
