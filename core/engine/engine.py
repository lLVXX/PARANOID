
#core/engine/engine.py

class ScanEngine:
    def __init__(self, tool):
        self.tool = tool
        self.sniffer = PacketSniffer()
        self.window = WindowController(
            self.sniffer,
            tool.profile.window_size
        )
        self.analyzer = TelemetryAnalyzer()

    def run(self):
        self.sniffer.start()

        def stdout_cb(line):
            window = self.window.tick()
            if window is not None:
                self.analyzer.analyze(
                    window,
                    self.tool.profile.name
                )

        self.tool.run(stdout_cb)

        self.sniffer.stop()
