# core/engine/ffuf_engine.py


import subprocess
import tempfile
import json
from pathlib import Path

from core.engine.scan_result import ScanResult


class FFUFEngine:

    @staticmethod
    def name():
        return "ffuf"

    @staticmethod
    def supports(scan_type: str) -> bool:
        return scan_type in ("dir", "subdomain")

    def run(self, context, profile=None) -> ScanResult:
        if not context.wordlist:
            raise RuntimeError("FFUF requiere wordlist")

        protocol = context.protocol or "http"
        hostname = context.hostname or context.target
        port = f":{context.port}" if context.port else ""

        url = f"{protocol}://{hostname}{port}/FUZZ"

        # -----------------------------
        # JSON output
        # -----------------------------
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
        output_path = tmp.name
        tmp.close()

        threads = context.threads or 40
        timeout = context.extra.get("timeout", 10)

        cmd = [
            "ffuf",
            "-u", url,
            "-w", context.wordlist,
            "-t", str(threads),
            "-mc", "200,204,301,302,307,401,403",
            "-of", "json",
            "-o", output_path,
            "-timeout", str(timeout),
            "-fs", "0",
        ]

        print(f"[+] FFUF → {url}")
        print("[+] Resultados aparecerán en vivo (nativo FFUF)\n")

        subprocess.run(cmd, check=False)

        print("\n[+] FFUF finalizado, procesando resultados...\n")

        # --------------------------------------------------
        # Parse JSON
        # --------------------------------------------------
        raw = {}
        results = []

        try:
            with open(output_path, "r") as f:
                raw = json.load(f)
                results = raw.get("results", [])
        finally:
            Path(output_path).unlink(missing_ok=True)

        useful = []
        routes = []

        for r in results:
            path = r.get("input", {}).get("FUZZ")
            if not path:
                continue

            useful.append({
                "path": path,
                "status": r.get("status"),
                "length": r.get("length"),
                "url": r.get("url"),
            })

            # INFO -> WRITER
            routes.append(f"/{path}")

        return ScanResult(
            raw_output=raw,
            useful_output=useful,
            ports=[],
            hostnames=[hostname],
            traffic=None,
            metadata={
                "engine": self.name(),
                "url": url,
                "wordlist": context.wordlist,
                "threads": threads,
                "profile": profile,
                "routes": routes,   
            },
        )
