# core/parsers/ffuf_parser.py
import json
import hashlib


def _hash(body: str) -> str:
    return hashlib.md5(body.encode(errors="ignore")).hexdigest()


def parse_ffuf_json(path: str):
    with open(path, "r") as f:
        data = json.load(f)

    results = data.get("results", [])
    if not results:
        return [], None

    # ---- Detect wildcard baseline ----
    baseline = results[0]
    baseline_size = baseline["length"]
    baseline_hash = _hash(baseline.get("content", ""))

    clean = []

    for r in results:
        size = r["length"]
        body = r.get("content", "")
        status = r["status"]
        url = r["url"].replace(data["config"]["url"].replace("FUZZ", ""), "")

        if size == baseline_size and _hash(body) == baseline_hash:
            continue  # wildcard

        clean.append({
            "status": status,
            "path": url,
            "size": size
        })

    return clean, baseline_size

