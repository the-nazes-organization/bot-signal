import sys, json

from signal_bot.backend.message_client.JsonRPCInterface import JsonRPCInterface
from signal_bot.backend.message_client.SignalBot import SignalBot

def get_properties() -> dict:
    properties_json = sys.stdin.read()
    return json.loads(properties_json)

if __name__ == "__main__":
    properties = get_properties()
    socket_file = properties.get("socket_file")
    del properties["socket_file"]

    interface = JsonRPCInterface(socket=socket_file)
    bot = SignalBot(properties=properties, interface=interface)

    bot.start()