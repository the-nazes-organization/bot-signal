import json
import logging
import os
import requests
import subprocess
import time
import signal
import pprint
import argparse

from dotenv import load_dotenv

from messages_client.Facebook import Facebook
from messages_client.Signal import Signal

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

load_dotenv()

parser = argparse.ArgumentParser(
    description='Bot to send message from signal to facebook',
)
parser.add_argument(
    '--signal_id', '-s',
    required=True,
    type=str,
    help='signal group id',
)
parser.add_argument(
    '--facebook_id', '-f',
    required=True,
    type=str,
    help='facebook group id',
)
args = parser.parse_args()
signal.signal(signal.SIGINT, exit_ctl_c)

def exit_ctl_c(signum, frame):
    #clean selenium session if exit with ctl c
    res = requests.get("http://selenium:4444/status")
    id = input("Id to delete:")
    res_del = requests.delete(f"http://selenium:4444/session/{id}")
    logger.info(f"Clean session {res_del}: {res_del.content}")
    exit(1)
 

def extract_info(res):
    message = {}
    data = {}
    try:
        data = res["params"]["envelope"]
        message["from"] = data["sourceName"].split(" ")[0]
    except Exception as e:
        logger.error(f"Can't read data: {e}")

    if data.get("dataMessage"):
        try:
            message["message"] = data["dataMessage"]["message"]
            message["timesamp"] = data["dataMessage"]["timestamp"]
        except Exception as e:
            logger.error(f"Error parsing dataMessage: {e}")
    elif data.get("syncMessage"):
        try:
            message["message"] = data["syncMessage"]["sentMessage"]["message"]
            message["timesamp"] = data["syncMessage"]["sentMessage"]["timestamp"]
        except Exception as e:
            logger.error(f"Error parsing syncMessage: {e}")
        return message
    return message


def is_group(res, group_id):
    group_id_res = ""
    try:
        group_id_res = res["params"]["envelope"]["dataMessage"]["groupInfo"]["groupId"]
    except Exception as e:
        logger.error(f"Error group: {e}")
    try:
        group_id_res = res["params"]["envelope"]["syncMessage"]["sentMessage"][
            "groupInfo"
        ]["groupId"]
    except Exception as e:
        logger.error(f"Error group: {e}")
    logger.info(f"Group id find: {group_id_res} / {group_id}")
    return group_id_res == group_id


def send_messenger(info, facebook):
    if info is None:
        return
    msg = info.get("message")
    if msg is None:
        logger.info("No message")
        return
    len_msg = len(msg)
    msg_to_send = f"Coucou Benjamin, ton ami {info.get('from')} vient d'envoyer : \"{msg}\" sur le groupe signal. Tu lui manques 🥺🥺, rejoins nous --> https://signal.group/#CjQKIK0ogEma3X3fHwZNKzn6WWJrAOyvR9XhW3RlxXU33KjgEhBvIlDLQ0G1N8pOL1ID4xdE"
    facebook.send_message(msg_to_send, args.facebook_id)


def handler(signal, facebook):
    while 1:
        res = json.loads(signal.get_message_end())
        pprint.pprint(res)
        if is_group(res, args.signal_id):
            infos = extract_info(res)
            pprint.pprint(infos)
            send_messenger(infos, facebook)


def main():
    facebook = Facebook(os.getenv("EMAIL"), os.getenv("PASSWORD"))
    facebook.auth()
    logger.info("Waiting to auth facebook")
    time.sleep(20)
    
    signal = Signal("+33681155580")

    handler(signal=signal, facebook=facebook)


if __name__ == "__main__":
    try:
        logger.info(f"Start with args: {args.signal_id}, {args.facebook_id}")
        main()
    except Exception as e:
        logger.error(f"Main error : {e}")
        #clean selenium session
        res = requests.get("http://selenium:4444/status")
        id = res.json()["value"]["nodes"][0]["slots"][0]["session"]["sessionId"]
        res_del = requests.delete(f"http://selenium:4444/session/{id}")
        logger.info(f"Clean session {res_del}: {res_del.content}")
