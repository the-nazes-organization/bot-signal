class SignalCliProcessError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class SignalCliError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)