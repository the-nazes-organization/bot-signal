import socket
import json
import pprint
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

MESSAGE_BUFFER = 8192


class Signal:
    def __init__(self, account, socket_path="/tmp/signal-cli/socket", id=42):
        self.signal = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.signal.connect(socket_path)
        self.id = id
        self.account = account
        self.cached_message = b""

    def _receive_message(self, size=MESSAGE_BUFFER):
        res = self.signal.recv(size)
        return res

    def get_message_end(self, end_marker=b"}}\n"):
        # to handle the buffer of socker.recv, and return complete message
        msg_cache = self.cached_message
        while True:
            msg = self._receive_message()
            msg_cache += msg
            marker = msg_cache.find(end_marker)

            if marker > 0:
                marker += 2
                # send result and cache the remaning data
                res = msg_cache[:marker]
                self.cached_message = msg_cache[marker:]
                logger.debug(
                    f"len msg = {len(res)} | len cache = {len(self.cached_message)}"
                )
                return res
