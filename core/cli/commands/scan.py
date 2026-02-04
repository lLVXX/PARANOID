# core/cli/commands/scan.py
from core.cli.commands.base import Command
from core.cli.prompts import confirm_active_recon, select_wordlist, select_hostname
from core.cli.render import render_result
from core.utils.wordlist_manager import WordlistManager
import os


from core.cli.commands.base import Command
from core.cli.prompts import confirm_active_recon, select_wordlist, select_hostname
from core.cli.render import render_result
from core.utils.wordlist_manager import WordlistManager


class ScanCommand(Command):
    def matches(self, cmd: str) -> bool:
        return cmd.startswith("scan ")

    def execute(self, cmd, session_mgr, scanner) -> bool:
        session = session_mgr.current
        target = session.get_active_target()

        if not target:
            print("[!] Define un target primero")
            return True

        scan_type = cmd.split()[1]

        # ---------------- ACTIVE RECON ----------------

        if scan_type in ("dir", "subdomain"):
            if not confirm_active_recon():
                print("[i] Reconocimiento activo cancelado")
                return True

            hostname = select_hostname(session, target)
            wordlists = WordlistManager.discover_dir_wordlists()

            WordlistManager.pretty_list(wordlists)
            wordlist = select_wordlist(wordlists)

            result = scanner.run_scan(
                target=target,
                scan_type=scan_type,
                wordlist=wordlist,
                hostname=hostname
            )

            render_result(result, target)
            return True

        # ---------------- PASIVE / STANDARD SCAN ----------------

        result = scanner.run_scan(target, scan_type)

        if scan_type == "service" and result and result.hostnames:
            session.add_http_hostnames(
                target=target,
                hostnames=result.hostnames,
                confirmed=True
            )

        render_result(result, target)
        return True
