# core/cli/commands/__init__.py
import os
from core.cli.commands.help import HelpCommand
from core.cli.commands.set import SetCommand
from core.cli.commands.show import ShowCommand
from core.cli.commands.session import SessionCommand
from core.cli.commands.scan import ScanCommand


COMMANDS = [
    HelpCommand(),
    SetCommand(),
    ShowCommand(),
    SessionCommand(),
    ScanCommand(),
]


def dispatch_command(cmd: str, session_mgr, scanner) -> bool:
    cmd = cmd.lower()

    if cmd in ("exit", "quit", "q"):
        print("\n[+] Saliendo...")
        return False

    if cmd == "clear":
        os.system("clear" if os.name == "posix" else "cls")
        return True

    for command in COMMANDS:
        if command.matches(cmd):
            return command.execute(cmd, session_mgr, scanner)

    print("[!] Comando no reconocido")
    return True
