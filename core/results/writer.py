#core/results/writer.py

import os
import json
from datetime import datetime


class ResultWriter:
    """
    ResultWriter
    ------------
    Responsabilidad única:
    - Persistir ScanResult en disco
    - Sin lógica de scans
    - Sin conocimiento de sesiones
    """

    # --------------------------------------------------
    # PUBLIC
    # --------------------------------------------------

    def write(self, scan_result, output_dir: str):
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(os.path.join(output_dir, "raw"), exist_ok=True)

        self._write_meta(scan_result, output_dir)
        self._write_summary(scan_result, output_dir)
        self._write_engine_outputs(scan_result, output_dir)
        self._write_raw(scan_result, output_dir)

    # --------------------------------------------------
    # META
    # --------------------------------------------------

    def _write_meta(self, scan_result, output_dir: str):
        meta = {
            "target": scan_result.metadata.get("target"),
            "engine": scan_result.metadata.get("engine"),
            "scan_type": scan_result.metadata.get("scan_type"),
            "profile": scan_result.metadata.get("profile"),
            "timestamp": datetime.now().isoformat(),
            "hostnames": list(scan_result.hostnames or []),
            "ports_count": self._count_ports(scan_result),
        }

        with open(os.path.join(output_dir, "meta.json"), "w") as f:
            json.dump(meta, f, indent=4)

    # --------------------------------------------------
    # SUMMARY
    # --------------------------------------------------

    def _write_summary(self, scan_result, output_dir: str):
        path = os.path.join(output_dir, "summary.txt")

        with open(path, "w") as f:
            f.write(f"Engine: {scan_result.metadata.get('engine')}\n")
            f.write(f"Scan type: {scan_result.metadata.get('scan_type')}\n")

            if scan_result.hostnames:
                f.write("\nHostnames:\n")
                for h in scan_result.hostnames:
                    f.write(f" - {h}\n")

            if scan_result.ports:
                f.write("\nPorts detected\n")

            if scan_result.useful_output:
                f.write("\nUseful results present\n")

    # --------------------------------------------------
    # ENGINE OUTPUTS
    # --------------------------------------------------

    def _write_engine_outputs(self, scan_result, output_dir: str):
        engine = scan_result.metadata.get("engine")

        if engine == "ffuf":
            self._write_ffuf(scan_result, output_dir)

        if engine == "nmap":
            self._write_nmap(scan_result, output_dir)

        if scan_result.traffic:
            self._write_text(
                output_dir,
                "traffic.txt",
                scan_result.traffic
            )

    # --------------------------------------------------
    # FFUF
    # --------------------------------------------------

    def _write_ffuf(self, scan_result, output_dir: str):
        if not scan_result.useful_output:
            return

        path = os.path.join(output_dir, "routes.txt")

        with open(path, "w") as f:
            for r in scan_result.useful_output:
                f.write(
                    f"[{r.get('status')}] "
                    f"/{r.get('path')} "
                    f"({r.get('length')} bytes)\n"
                )
                f.write(f" -> {r.get('url')}\n\n")

    # --------------------------------------------------
    # NMAP
    # --------------------------------------------------

    def _write_nmap(self, scan_result, output_dir: str):
        if scan_result.ports:
            self._write_text(
                output_dir,
                "ports.txt",
                scan_result.ports
            )

        if scan_result.hostnames:
            path = os.path.join(output_dir, "hostnames.txt")
            with open(path, "w") as f:
                for h in scan_result.hostnames:
                    f.write(h + "\n")

    # --------------------------------------------------
    # RAW
    # --------------------------------------------------

    def _write_raw(self, scan_result, output_dir: str):
        if not scan_result.raw_output:
            return

        engine = scan_result.metadata.get("engine")
        ext = "json" if isinstance(scan_result.raw_output, dict) else "txt"

        path = os.path.join(output_dir, "raw", f"{engine}.{ext}")

        with open(path, "w") as f:
            if isinstance(scan_result.raw_output, dict):
                json.dump(scan_result.raw_output, f, indent=2)
            else:
                f.write(str(scan_result.raw_output))

    # --------------------------------------------------
    # HELPERS
    # --------------------------------------------------

    def _write_text(self, output_dir, filename, content):
        path = os.path.join(output_dir, filename)

        with open(path, "w") as f:
            if isinstance(content, dict):
                for k, v in content.items():
                    if isinstance(v, list):
                        f.write(f"{k}:\n")
                        for item in v:
                            f.write(f"  - {item}\n")
                    elif isinstance(v, dict):
                        f.write(f"{k}:\n")
                        for sub_k, sub_v in v.items():
                            f.write(f"  {sub_k}: {sub_v}\n")
                    else:
                        f.write(f"{k}: {v}\n")
            else:
                f.write(str(content))

    def _count_ports(self, scan_result) -> int:
        if not scan_result.ports or not isinstance(scan_result.ports, str):
            return 0
        return len(
            [l for l in scan_result.ports.splitlines() if "/" in l]
        )


