#core/telemetry/collector.py

class TelemetryCollector:
    def __init__(self, focus):
        self.focus = focus
        self.events = []

    def feed(self, packets):
        if not packets:
            return
        self.events.append({
            "count": len(packets),
            "data": packets
        })
