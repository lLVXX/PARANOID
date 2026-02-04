#core/cli/commands/session_info.py

from core.cli.commands.base import Command


class SessionInfoCommand(Command):
    def matches(self, cmd: str) -> bool:
        return cmd in ("session info", "session show")

    def execute(self, cmd, session_mgr, scanner) -> bool:
        s = session_mgr.current
        if not s:
            print("[!] No hay sesión activa")
            return True

        print(f"\n📂 Sesión: {s.name}")
        print(f"🌐 Interfaz: {s.interface}")
        print(f"🕒 Creada: {s.created_at}\n")

        # -------------------------
        # TARGETS
        # -------------------------
        print(f"🎯 Targets ({len(s.targets)}):")

        if not s.targets:
            print("  (ninguno)")
        else:
            for idx, t in enumerate(s.targets):
                marker = " ★" if idx == s.active_target_index else ""
                print(f"  [{idx}] {t}{marker}")

        # Target activo (SEGURO)
        active = s.get_active_target()
        if active:
            print(f"\n▶ Target activo: {active}")
        else:
            print(f"\n▶ Target activo: (ninguno)")

        # -------------------------
        # SCANS
        # -------------------------
        print("\n🧪 Scans:")
        if not s.scans:
            print("  (sin scans)")
        else:
            for scan in s.scans:
                print(
                    f"  - {scan['scan_type']} @ {scan['timestamp']}"
                )

        print()
        return True
