#core/cli/autocomplete.py
import readline

# --------------------------------------------------
# STATIC COMMANDS
# --------------------------------------------------

BASE_COMMANDS = [
    "help", "clear", "exit", "quit", "q",

    "set target", "set interface",

    "show target", "show interface", "show hosts",

    "session new", "session use", "session close",
    "session delete", "session list", "session info", "session show",

    "target list", "target use", "target remove",

    "scan quick", "scan full", "scan service", "scan stealth",
    "scan dir", "scan subdomain"
]


# --------------------------------------------------
# COMPLETER FACTORY (needs session_mgr)
# --------------------------------------------------

def build_completer(session_mgr):
    """
    Devuelve un completer con acceso al estado de sesión
    (targets, índices, etc).
    """

    def completer(text, state):
        buffer = readline.get_line_buffer().strip()
        options = []

        # ---------------- BASE ----------------
        if " " not in buffer:
            options = [c for c in BASE_COMMANDS if c.startswith(text)]

        # ---------------- SESSION ----------------
        elif buffer.startswith("session "):
            options = [
                c for c in BASE_COMMANDS
                if c.startswith(buffer)
            ]

        # ---------------- TARGET ----------------
        elif buffer.startswith("target use") or buffer.startswith("target remove"):
            session = session_mgr.current
            if session and session.targets:
                options = [str(i) for i in range(len(session.targets))]

        elif buffer.startswith("target "):
            options = [c for c in BASE_COMMANDS if c.startswith(buffer)]

        # ---------------- SCAN ----------------
        elif buffer.startswith("scan "):
            options = [c for c in BASE_COMMANDS if c.startswith(buffer)]

        # ---------------- FALLBACK ----------------
        else:
            options = [c for c in BASE_COMMANDS if c.startswith(buffer)]

        try:
            return options[state]
        except IndexError:
            return None

    return completer


# --------------------------------------------------
# READLINE SETUP
# --------------------------------------------------

def setup_readline(session_mgr):
    """
    Inicializa readline con autocompletado dinámico.
    """
    readline.set_completer(build_completer(session_mgr))
    readline.parse_and_bind("tab: complete")
