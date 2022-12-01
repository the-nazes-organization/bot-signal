import subprocess, psutil, json, sys

from signal_bot.backend import errors

from signal_bot.backend.core.config import get_settings
from signal_bot.backend.db import DbManager

settings = get_settings()

ERROR_PROCESS_EXIST = 1
ERROR_PROCESS_INEXISTANT = 2
ERROR_PROCESS_FAIL_TERM = 3

class SignalProcess:
    def __init__(self, type: str) -> None:
        self.db = ProcessStorage(type)

    def error_message(self, type: int, info: str = "") -> str:
        if type == ERROR_PROCESS_EXIST:
            return f"{self.__class__.__name__} already running ({info})"
        elif type == ERROR_PROCESS_INEXISTANT:
            return f"No {self.__class__.__name__} alive"
        elif type == ERROR_PROCESS_FAIL_TERM:
            return f"{self.__class__.__name__} ({info}) couldn't terminate properly, please try again!"


class SignalCliProcess(SignalProcess):
    def __init__(self) -> None:
        super().__init__("cli")
        self.__class__.__name__ = "Signal-cli process"

    def start_cli_daemon(self) -> int:
        pid = self.db.get_process_pid()

        if pid != None:
            p = psutil.Process(pid)
            raise errors.SignalCliProcessError(self.error_message(ERROR_PROCESS_EXIST, f"{p.name()}:{pid} {p.status()}"))

        cmd = self.get_cli_full_command(
            "daemon",
            "--socket",
            settings.SOCKET_FILE,
            "--ignore-attachments",
            "--ignore-stories",
            "--send-read-receipts",
            "--no-receive-stdout"
        )
        daemon = subprocess.Popen(args=cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        self.db.save_process_pid(daemon.pid)

        return daemon.pid
    
    def stop_cli_daemon(self) -> None:
        pid = self.db.get_process_pid()

        if pid == None:
            raise errors.SignalCliProcessError(self.error_message(ERROR_PROCESS_INEXISTANT))

        p = psutil.Process(pid)
        p.terminate()
        try:
            p.wait(timeout=3)
        except psutil.TimeoutExpired:
            raise errors.SignalCliProcessError(self.error_message(ERROR_PROCESS_FAIL_TERM, str(pid)))
            
        self.db.delete_process_pid()            

    def register(self, account: str, captcha_token: str) -> tuple[str, int]:
        return self.run_and_get_process_response(
            self.get_cli_full_command("--account", account, "register", "--captcha", captcha_token)
        )


    def verify(self, account: str, code: str) -> tuple[str, int]:
        return self.run_and_get_process_response(
            self.get_cli_full_command("--account", account, "verify", code)
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


    def get_cli_full_command(self, *args) -> list:
        command = ["signal-cli", "--service-environment", "staging"]
        return command + list(args)


class SignalBotProcess(SignalProcess):
    def __init__(self) -> None:
        super().__init__("bot")
        self.__class__.__name__ = "Signal Bot process"

    def start_bot_daemon(self, properties: any) -> int:
        pid = self.db.get_process_pid()

        if pid != None:
            p = psutil.Process(pid)
            raise errors.SignalBotProcessError(self.error_message(ERROR_PROCESS_EXIST, f"{p.name()}:{pid} {p.status()}"))

        cmd = [sys.executable, settings.PYTHON_BOT_FILE]

        daemon = subprocess.Popen(args=cmd, stdin=subprocess.PIPE)
        self.db.save_process_pid(daemon.pid)

        #Passing to child bot the properties set for his work with socket_file by default property
        properties["socket_file"] = settings.SOCKET_FILE
        daemon.stdin.write(json.dumps(properties).encode("utf-8"))
        daemon.stdin.close()

        return daemon.pid
    
    def stop_bot_daemon(self):
        pid = self.db.get_process_pid()

        if pid == None:
            raise errors.SignalBotProcessError(self.error_message(ERROR_PROCESS_INEXISTANT))
        
        p = psutil.Process(pid)
        p.terminate()

        try:
            p.wait(timeout=3)
        except psutil.TimeoutExpired:
            raise errors.SignalBotProcessError(self.error_message(ERROR_PROCESS_FAIL_TERM, str(pid)))
            
        self.db.delete_process_pid()


class ProcessStorage:

    def __init__(self, type: str) -> None:
        self.db = DbManager.Db()
        self.type = type

    def get_process_pid(self) -> int | None:
        processes_obj = self.db.get_processes_list()
        typed_processes = processes_obj.get(self.type)
        return typed_processes.get("alive")

    def save_process_pid(self, pid: int):
        processes_obj = self.db.get_processes_list()
        processes_obj[self.type]["alive"] = pid
        self.db.put_processes_list(processes_obj)

    def delete_process_pid(self):
        processes_obj = self.db.get_processes_list()
        del processes_obj[self.type]["alive"]
        self.db.put_processes_list(processes_obj)