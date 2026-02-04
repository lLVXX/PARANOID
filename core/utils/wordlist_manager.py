#core/utils/wordlist_manager.py

from pathlib import Path


WORDLIST_DIRS = [
    "/usr/share/seclists",
    "/usr/share/wordlists",
    "/usr/share/dirb",
    "/usr/share/dirbuster",
]


class WordlistManager:

    DIR_KEYWORDS = (
        "dir", "directory", "directories",
        "common", "small", "big",
        "content", "raft"
    )

    EXCLUDE_KEYWORDS = (
        "vuln", "stress", "unicode",
        "cgi", "payload", "fuzz",
        "injection", "xss", "sqli"
    )

    @staticmethod
    def discover_dir_wordlists(extensions=(".txt", ".lst")) -> list[str]:
        results = []

        for base in WORDLIST_DIRS:
            path = Path(base)
            if not path.exists():
                continue

            for file in path.rglob("*"):
                if not file.is_file():
                    continue

                if file.suffix not in extensions:
                    continue

                full = str(file).lower()

                if any(bad in full for bad in WordlistManager.EXCLUDE_KEYWORDS):
                    continue

                if any(ok in full for ok in WordlistManager.DIR_KEYWORDS):
                    results.append(str(file))

        return sorted(results)

    @staticmethod
    def pretty_list(wordlists: list[str], limit=30):
        shown = wordlists[:limit]
        for idx, wl in enumerate(shown, 1):
            print(f"  [{idx:02}] {wl}")

        if len(wordlists) > limit:
            print(f"  ... ({len(wordlists) - limit} more)")
