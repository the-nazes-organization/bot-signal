import logging
import subprocess
import threading
from time import sleep

import psutil

logger = logging.getLogger(__name__)


class ProcessHandler:
    @staticmethod
    def start_process(cmd: list, background: bool = False) -> subprocess.Popen:
        process = subprocess.Popen(
            args=cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
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

    @staticmethod
    def log_process(process: subprocess.Popen):
        def log():
            logger.info("Logging process pid: %s", process.pid)
            while True:
                output = process.stdout.readline()
                if output == b"" and process.poll() is not None:
                    logger.info("Process finished: %s", process.pid)
                    break
                if output != b"":
                    logger.info(
                        "%s - %s", process.pid, output.rstrip().decode("utf-8")
                    )
                else:
                    sleep(1)

        thread = threading.Thread(target=log)
        thread.start()

    @staticmethod
    def is_process_alive(pid: int):
        try:
            process = psutil.Process(pid)
        except psutil.NoSuchProcess:
            return False
        if process.is_running():
            return True
        return False
