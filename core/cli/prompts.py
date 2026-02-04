# core/cli/prompts.py
import os
from core.cli.style import C




def confirm_active_recon() -> bool:
    print("\n[!] Active reconnaissance detected")
    print("[!] This will generate high-volume HTTP traffic")
    return input("[?] Do you have authorization? (yes/no) > ").lower() == "yes"


def select_wordlist(wordlists: list[str]) -> str:
    while True:
        choice = input("\n[?] Selecciona wordlist (número o path manual) > ").strip()

        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(wordlists):
                return wordlists[idx]

        if os.path.isfile(choice):
            return choice

        print("[!] Selección inválida")


def select_hostname(session, target: str) -> str | None:
    if not session or not session.has_http_hostnames(target):
        return None

    hostnames = session.get_http_hostnames(target)
    if not hostnames:
        return None

    print("\n[+] Hostnames HTTP disponibles:\n")
    for i, h in enumerate(hostnames, 1):
        print(f"  [{i:02}] {h}")
    print(f"  [00] Usar IP directamente ({target})")

    choice = input("\n[?] Selecciona hostname > ").strip()

    if choice.isdigit():
        idx = int(choice)
        if idx == 0:
            return None
        if 1 <= idx <= len(hostnames):
            return hostnames[idx - 1]

    return choice or None


def build_prompt(session) -> str:
    """
    Construye el prompt contextual de forma SEGURA.
    NUNCA debe lanzar excepción.
    """

    if not session:
        return "PARANOID > "

    # Target activo seguro
    target = None
    if hasattr(session, "get_active_target"):
        target = session.get_active_target()

    if target:
        return f"PARANOID[{session.name}:{target}] > "

    return f"PARANOID[{session.name}] > "
