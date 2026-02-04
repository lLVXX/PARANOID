# core/cli/commands/help.py
from core.cli.commands.base import Command


class HelpCommand(Command):
    def matches(self, cmd: str) -> bool:
        return cmd == "help"

    def execute(self, cmd, session_mgr, scanner) -> bool:
        print("""
set target <IP/Dominio>
set interface <iface>

session new/use/close/delete/list

show target
show interface
show hosts

scan quick | full | service | stealth
scan dir | scan subdomain

exit / quit / q
""")
        return True
