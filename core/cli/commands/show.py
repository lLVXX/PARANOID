# core/cli/commands/show.py
from core.cli.commands.base import Command
from core.utils.hosts import list_hosts_entries


class ShowCommand(Command):
    def matches(self, cmd: str) -> bool:
        return cmd.startswith("show ")

    def execute(self, cmd, session_mgr, scanner) -> bool:
        if cmd == "show target":
            session = session_mgr.current
            tgt = session.get_active_target()
            print(f"[+] Target actual: {tgt}" if tgt else "[!] Target no definido")
            return True

        if cmd == "show interface":
            print(f"[+] Interfaz actual: {session_mgr.current.interface}")
            return True

        if cmd == "show hosts":
            list_hosts_entries()
            return True

        print("[!] Comando show inválido")
        return True
