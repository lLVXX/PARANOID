# core/engine/scan_result.py

class ScanResult:
    def __init__(
        self,
        raw_output,
        useful_output,
        ports,
        hostnames,
        traffic,
        metadata=None
    ):
        self.raw_output = raw_output
        self.useful_output = useful_output
        self.ports = ports
        self.hostnames = hostnames
        self.traffic = traffic
        self.metadata = metadata or {}