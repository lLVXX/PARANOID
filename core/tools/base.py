#core/tools/base.py

import subprocess

class ToolAdapter:
    def __init__(self, cmd, profile):
        self.cmd = cmd
        self.profile = profile

    def run(self, stdout_cb):
        proc = subprocess.Popen(
            self.cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )

        for line in proc.stdout:
            stdout_cb(line)

        proc.wait()
