#core/cli/commands/session.py

from core.cli.commands.base import Command


class SessionCommand(Command):
    def matches(self, cmd: str) -> bool:
        return cmd.startswith("session ")

    def execute(self, cmd, session_mgr, scanner) -> bool:
        parts = cmd.split()
        session = session_mgr.current

        # ---------------- SESSION NEW ----------------

        if parts[1] == "new" and len(parts) == 3:
            session_mgr.create(parts[2])
            print(f"[+] Sesión creada y activa: {parts[2]}")
            return True

        # ---------------- SESSION USE ----------------

        if parts[1] == "use" and len(parts) == 3:
            session_mgr.activate(parts[2])
            print(f"[+] Sesión activa: {parts[2]}")
            return True

        # ---------------- SESSION CLOSE ----------------

        if parts[1] == "close":
            session_mgr.close_current()
            print(f"[+] Sesión activa: {session_mgr.get_active_name()}")
            return True

        # ---------------- SESSION DELETE ----------------

        if parts[1] == "delete" and len(parts) == 3:
            if session_mgr.delete(parts[2]):
                print(f"[+] Sesión eliminada: {parts[2]}")
            else:
                print("[!] No se puede eliminar esa sesión")
            return True

        # ---------------- SESSION LIST ----------------

        if parts[1] == "list":
            current = session_mgr.get_active_name()
            for s in session_mgr.list_sessions():
                mark = "*" if s == current else " "
                print(f"{mark} {s}")
            return True

        # ---------------- SESSION INFO / SHOW ----------------

        if parts[1] in ("info", "show"):
            if not session:
                print("[!] No hay sesión activa")
                return True

            active = session.get_active_target()

            print(f"\n📂 Sesión: {session.name}")
            print(f"🌐 Interfaz: {session.interface}")
            print(f"🕒 Creada: {session.created_at}")

            print("\n🎯 Targets:")
            if not session.targets:
                print("  (ninguno)")
            else:
                for i, t in enumerate(session.targets):
                    mark = "★" if t == active else " "
                    print(f"  [{i}] {t} {mark}")

            if active:
                print(f"\n▶ Target activo: {active}")

            print()
            return True

        # ---------------- INVALID ----------------

        print("[!] Comando session inválido")
        return True
