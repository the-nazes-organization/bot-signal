import sys
import json

def get_properties() -> dict:
    properties_json = sys.stdin.read()
    return json.loads(properties_json)

if __name__ == "__main__":
    properties = get_properties()
    socket_file = properties.get("socket_file")
    del properties["socket_file"]
