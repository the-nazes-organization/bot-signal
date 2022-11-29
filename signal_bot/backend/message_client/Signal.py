import subprocess, psutil, json

from signal_bot.backend.core.config import get_settings
from signal_bot.backend import schemas

settings = get_settings()

class SignalCliProcess:

    def __init__(self, account: str) -> None:
        self.account = "+" + account


    def start_cli_daemon(self) -> schemas.SignalCliProcessInfo:
        pid = self.get_daemon_process_from_db()
        if pid != None:
            p = psutil.Process(pid)
            return schemas.SignalCliProcessInfo(pid=p.pid, status=p.status())

        cmd = self.get_full_command(
            "daemon",
            "--socket",
            settings.SOCKET_FILE,
            "--ignore-attachments",
            "--ignore-stories",
            "--send-read-receipts",
            "--no-receive-stdout"
        )
        daemon = subprocess.Popen(cmd)
        p = psutil.Process(daemon.pid)

        if psutil.pid_exists(p.pid):
            self.add_daemon_process_to_db(p.pid)

        return schemas.SignalCliProcessInfo(pid=p.pid, status=p.status())
    
    def stop_cli_daemon(self) -> schemas.SignalCliProcessInfo:
        pid = self.get_daemon_process_from_db()

        if pid == None:
            return schemas.SignalCliProcessInfo(pid=-1, status="No signal_cli process for that account found in db")

        p = psutil.Process(pid)

        p.terminate()
        p.wait()

        if p.is_running():
            return schemas.SignalCliProcessInfo(pid=-1, status="Couldn't terminate signal_cli process")
        else:
            self.delete_daemon_process_from_db()
            return schemas.SignalCliProcessInfo(pid=pid, status="Succesfully terminate signal_cli process")
            


    def register(self, captcha_token: str | None = None) -> schemas.SignalBasicResponse:
        if captcha_token != None:
            cmd = self.get_full_command("register", "--captcha", captcha_token)
        else:
            cmd = self.get_full_command("register")
        return self.run_and_get_process_response(cmd)


    def verify(self, code: str) -> schemas.SignalBasicResponse:
        return self.run_and_get_process_response(self.get_full_command("verify", code))



    ###############
    #### Utils ####
    ###############

    def get_daemon_process_from_db(self) -> int | None :
        with open(settings.PROCESSES_FILE, "r") as processes_file:
            processes_obj: dict = json.load(processes_file)
        
        cli_processes = processes_obj.get("cli")

        return cli_processes.get(self.account)
            

    def add_daemon_process_to_db(self, pid: int):
        with open(settings.PROCESSES_FILE, "r") as processes_file:
            processes_obj: dict = json.load(processes_file)

        processes_obj["cli"][self.account] = pid

        with open(settings.PROCESSES_FILE, "w") as processes_file:
            json.dump(processes_obj, processes_file)
    
    def delete_daemon_process_from_db(self):
        with open(settings.PROCESSES_FILE, "r") as processes_file:
            processes_obj: dict = json.load(processes_file)

        del processes_obj["cli"][self.account]

        with open(settings.PROCESSES_FILE, "w") as processes_file:
            json.dump(processes_obj, processes_file)

    def run_and_get_process_response(self, cmd: list) -> schemas.SignalBasicResponse:
        try:
            process = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            response = schemas.SignalBasicResponse(information_cli=process.stdout, exit_code=process.returncode)
        except subprocess.CalledProcessError as error:
            response = schemas.SignalBasicResponse(information_cli=error.stdout, exit_code=error.returncode)

        return response


    def get_full_command(self, *args) -> list:
        command: list = ["signal-cli", "--account", self.account, "--service-environment", "staging"]

        for arg in args:
            command.append(arg)

        return command