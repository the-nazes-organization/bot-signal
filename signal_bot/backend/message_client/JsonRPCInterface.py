import socket

READ_BUFFER = 4096

class JsonRPCInterface:
    def __init__(self, socket_file: str) -> None:
        self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.socket.connect(socket_file)
        self.cache = []

