import json

from signal_bot.backend.core.config import get_settings

settings = get_settings()

class Db:

    def __init__(self) -> None:
        pass

    def get_users_whitelisted(self) -> any:
        return self.get_data_from_file(settings.WHITELIST_FILE)

    def get_antiforgery_tokens(self) -> any:
        return self.get_data_from_file(settings.GOOGLE.AUTH_ANTIFORGERY_FILE)

    def get_processes_list(self) -> any:
        return self.get_data_from_file(settings.PROCESSES_FILE)



    def put_antiforgery_tokens(self, data: any):
        return self.put_data_into_file(
            settings.GOOGLE.AUTH_ANTIFORGERY_FILE,
            data
        )
    
    def put_processes_list(self, data: any):
        return self.put_data_into_file(
            settings.PROCESSES_FILE,
            data
        )


    def get_data_from_file(self, file: str) -> any:
        with open(file, "r") as fd:
            data = json.load(fd)
        return data
    
    def put_data_into_file(self, file: str, data: any):
        with open(file, "w") as fd:
            json.dump(data, fd)