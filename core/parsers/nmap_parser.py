# core/parsers/nmap_parser.py
import re
from typing import Set


# ==========================================================
# EXTRAER SALIDA ÚTIL
# ==========================================================

def extract_useful_output(output: str) -> str:
    for i, line in enumerate(output.splitlines()):
        if line.strip().startswith("PORT"):
            return "\n".join(output.splitlines()[i:])
    return ""


# ==========================================================
# PUERTOS
# ==========================================================

def process_ports(output: str) -> str:
    ports = re.findall(r'(\d+)/tcp\s+open\s+([\w\-?/]+)', output)
    if not ports:
        return ""

    lines = [f"[+] PUERTOS ABIERTOS ({len(ports)}):"]
    for port, service in ports:
        icon = "🌐" if port in ("80", "443", "8080", "8443") else "🔧"
        lines.append(f"    {icon} {port}/tcp - {service}")
    return "\n".join(lines)


# ==========================================================
# HOSTNAMES CONFIRMADOS
# ==========================================================

_HOSTNAME_REGEXES = [
    r'DNS:([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
    r'commonName\s*=\s*([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
    r'Did not follow redirect to http[s]?://([a-zA-Z0-9.-]+)',
    r'http[s]?://([a-zA-Z0-9.-]+)',
    r'Domain:\s*([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
]

_BLACKLIST = {"localhost", "nmap.org"}


def _is_valid(h: str) -> bool:
    return (
        len(h) >= 4
        and "." in h
        and h.lower() not in _BLACKLIST
        and not re.fullmatch(r"\d+\.\d+\.\d+\.\d+", h)
    )


def extract_hostnames(output: str, target: str | None = None) -> Set[str]:
    found = set()

    for rx in _HOSTNAME_REGEXES:
        for h in re.findall(rx, output, re.IGNORECASE):
            h = h.strip().lower()
            if _is_valid(h):
                found.add(h)

    if target and not re.match(r"\d+\.\d+\.\d+\.\d+", target):
        found.discard(target.lower())

    return found


# ==========================================================
# HOSTNAMES INFERIDOS (LEGACY)
# ==========================================================

def infer_hostnames(output: str) -> Set[str]:
    inferred = set()

    # http-title → branding
    m = re.search(r'http-title:\s*([^\n\r]+)', output, re.IGNORECASE)
    if m:
        title = m.group(1).lower()
        words = re.findall(r'[a-z]{4,}', title)

        for w in words:
            if w not in {"network", "social", "hackers", "welcome"}:
                inferred.add(f"{w}.htb")

    return inferred
