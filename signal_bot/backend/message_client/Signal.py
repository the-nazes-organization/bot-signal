import subprocess, psutil, json

from signal_bot.backend import errors

from signal_bot.backend.core.config import get_settings
from signal_bot.backend.db import DbManager

settings = get_settings()

class SignalProcess:

    def __init__(self) -> None:
        self.db = ProcessStorage()

    def start_cli_daemon(self) -> int:
        pid = self.db.get_cli_process_pid()

        if pid != None:
            p = psutil.Process(pid)
            raise errors.SignalCliProcessError(f"SignalCli process already running ({p.name()}:{pid} {p.status()})")

        cmd = self.get_full_command(
            "daemon",
            "--socket",
            settings.SOCKET_FILE,
            "--ignore-attachments",
            "--ignore-stories",
            "--send-read-receipts",
            "--no-receive-stdout"
        )
        daemon = subprocess.Popen(args=cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        self.db.save_cli_process_pid(daemon.pid)

        return daemon.pid
    
    def stop_cli_daemon(self) -> None:
        pid = self.db.get_cli_process_pid()

        if pid == None:
            raise errors.SignalCliProcessError("No SignalCli process alive")

        p = psutil.Process(pid)
        p.terminate()
        try:
            p.wait(timeout=3)
        except psutil.TimeoutExpired:
            raise errors.SignalCliProcessError(f"SignalCli process ({pid}) couldn't terminate properly, please try again!")
            
        self.db.delete_cli_process_pid()
            

    def register(self, account: str, captcha_token: str) -> tuple[str, int]:
        return self.run_and_get_process_response(
            self.get_full_command("--account", account, "register", "--captcha", captcha_token)
        )


    def verify(self, account: str, code: str) -> tuple[str, int]:
        return self.run_and_get_process_response(
            self.get_full_command("--account", account, "verify", code)
        )



    ###############
    #### Utils ####
    ###############

    def run_and_get_process_response(self, cmd: list) -> tuple[str, int]:
        try:
            process = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            return process.stdout, process.returncode

        except subprocess.CalledProcessError as e:
            raise errors.SignalCliError(str(e.stdout) + f"\nExit Code : {e.returncode}")


    def get_full_command(self, *args) -> list:
        command = ["signal-cli", "--service-environment", "staging"]
        return command + list(args)

class ProcessStorage:

    def __init__(self) -> None:
        self.db = DbManager.Db()

    def get_cli_process_pid(self) -> int | None:
        processes_obj = self.db.get_processes_list()
        cli_processes = processes_obj.get("cli")
        return cli_processes.get("alive")


    def save_cli_process_pid(self, pid: int):
        processes_obj = self.db.get_processes_list()
        processes_obj["cli"]["alive"] = pid
        self.db.put_processes_list(processes_obj)

    def delete_cli_process_pid(self):
        processes_obj = self.db.get_processes_list()
        del processes_obj["cli"]["alive"]
        self.db.put_processes_list(processes_obj)