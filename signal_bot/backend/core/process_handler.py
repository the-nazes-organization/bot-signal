import subprocess

import psutil

from signal_bot.backend.core.config import get_settings

settings = get_settings()


class ProcessHanlder:
    def start_process(self, cmd: list, background: bool = False) -> subprocess.Popen:
        process = subprocess.Popen(
            args=cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        if background is False:
            process.wait()
        return process

    def stop_process(self, pid: int):
        process = psutil.Process(pid)
        process.terminate()
        process.wait(timeout=3)
