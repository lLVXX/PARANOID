# core/engine/nmap_engine.py

import re
import time
import subprocess
import sys

from core.engine.base import ScanEngine
from core.engine.scan_result import ScanResult

from core.parsers.nmap_parser import (
    extract_useful_output,
    process_ports,
    extract_hostnames,
    infer_hostnames,
)


class NmapEngine(ScanEngine):
    """
    NmapEngine
    ----------
    Engine PURO:
    - Construye comando
    - Ejecuta nmap
    - Parsea resultados
    - NO maneja telemetría
    """

    def name(self) -> str:
        return "nmap"

    def supports(self, scan_type: str) -> bool:
        return scan_type in {"quick", "full", "service", "stealth"}

    def run(self, context, profile=None):
        """
        Ejecuta Nmap según scan_type / profile.
        """

        args_map = {
            "quick": ["-T4", "--open", "-p", "21,22,80,443"],
            "full": ["-T4", "--open", "-p-"],
            "service": ["-sV", "-sC", "--open"],
            "stealth": ["-sS", "--open", "-T2"],
        }

        args = args_map.get(context.scan_type)
        if not args:
            raise RuntimeError("Scan no soportado")

        cmd = ["nmap"] + args + ["--stats-every", "1s", context.target]

        start = time.time()
        raw = self._run_with_progress(cmd, context.scan_type)
        duration = time.time() - start

        # ----------------------------
        # PARSEO (IGUAL QUE ANTES)
        # ----------------------------
        useful = extract_useful_output(raw)
        ports = process_ports(raw)

        confirmed = extract_hostnames(raw, context.target)
        inferred = infer_hostnames(raw)

        # 🔥 FIX REAL: fallback legacy (SE MANTIENE)
        if not confirmed and inferred:
            confirmed = inferred
            inferred = set()

        return ScanResult(
            raw_output=raw,
            useful_output=useful,
            ports=ports,
            hostnames=confirmed,   # ← EL MENÚ DEPENDE DE ESTO
            traffic=None,          # ← ahora lo maneja ScanExecution
            metadata={
                "engine": "nmap",
                "scan_type": context.scan_type,
                "target": context.target,
                "duration": duration,
            }
        )

    # --------------------------------------------------

    def _run_with_progress(self, cmd, label):
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )

        output = []
        last = -1

        while True:
            line = process.stdout.readline()
            if not line and process.poll() is not None:
                break
            if not line:
                continue

            output.append(line)

            m = re.search(r'(\d+\.\d+)% done', line)
            if m:
                pct = int(float(m.group(1)))
                if pct != last:
                    last = pct
                    bar = "█" * (pct // 3) + "░" * (30 - pct // 3)
                    sys.stdout.write(f"\r[SCAN] {label}: [{bar}] {pct}%")
                    sys.stdout.flush()

        sys.stdout.write("\r" + " " * 80 + "\r")
        return "".join(output)
