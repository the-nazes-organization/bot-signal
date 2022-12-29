import subprocess
import psutil

class ProcessHandler:
    @staticmethod
    def start_process(cmd: list, background: bool = False) -> subprocess.Popen:
        process = subprocess.Popen(
            args=cmd,
            stdin=subprocess.PIPE,
            # stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        if background is False:
            process.wait()
        return process

    @staticmethod
    def stop_process(pid: int):
        process = psutil.Process(pid)
        process.terminate()
        process.wait(timeout=3)
