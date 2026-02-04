# core/cli/menu.py



from core.banner import show_banner
from core.controller.scanner_controller import ScannerController
from core.session.manager import SessionManager

from core.cli.autocomplete import setup_readline
from core.cli.commands import dispatch_command
from core.cli.prompts import build_prompt


def main_menu():
    session_mgr = SessionManager()
    scanner = ScannerController(session_mgr)

    setup_readline(session_mgr)
    show_banner(session_mgr.get_active_name())

    print("\n" + "=" * 60)
    print("PARANOID - BLUE | Recon Framework")
    print("Escribe 'help' para ver comandos | TAB para autocompletar")
    print("=" * 60 + "\n")

    while True:
        try:
            prompt = build_prompt(session_mgr.current)
            cmd = input(prompt).strip()

            if not cmd:
                continue

            if not dispatch_command(cmd, session_mgr, scanner):
                break

        except KeyboardInterrupt:
            print("\n[i] Usa 'exit' para salir")
