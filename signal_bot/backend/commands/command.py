import logging
import re
import time as check_timestamp
import traceback
from datetime import datetime, time

from signal_bot.backend import schemas

logger = logging.getLogger(__name__)


class Command:
    """
    This class is used to manage the commands of the bot
    There is 4 types of triggers:
        - a command that was register (ex: !hello)
        - on all message (ex: "Hello")
        - on typing. This is used to send a message when the user start typing
        - on attachments
        - on reaction

    A message can be added to the command
    (ex: !hello world => "world" is the message)
    if the command is not found, the message is not handled

    To add a command, you need to create a function and decorate it with @Command.add
    """

    # This is the command dictionary. It maps a command to a function.
    _command = {
        "message": [],
        "command": [],
        "typing": [],
        "attachments": [],
        "reaction": []
    }

    def __init__(self):
        pass

    def _start_functions(self, commands, data: schemas.DataFormated):
        """
        This function is used to start a function
        All the function are launched if the condition is true

        TODO : add a timeout to avoid infinite loop
        TODO : start the function in a thread

        """
        for command in commands:

            if self.is_condition_true(
                command.get("condition"), data
            ):
                try:
                    logger.debug(msg=f"Start function {command['function'].__name__}")
                    start_time = check_timestamp.time()

                    command["function"](data)

                    end_time = check_timestamp.time()
                    logger.debug(
                        msg=f"End function executed in {end_time - start_time}"
                    )
                except Exception:
                    logger.error(
                        "Error while handling function: %s: %s",
                        command["function"].__name__,
                        traceback.format_exc(),
                    )

    def handle_reaction(self, data: schemas.DataFormated) -> None:
        """
        This function takes the data formated and call
        the functions associated with a reaction event

        parameters:
            - data: the formated data

        return:
            None
        """
        self._start_functions(self._command["reaction"], data)

    def handle_attachements(self, data: schemas.DataFormated) -> None:
        """
        This function takes the data formated and call
        the functions associated with a attachment event

        parameters:
            - data: the formated data

        return:
            None
        """
        self._start_functions(self._command["attachments"], data)

    def handle_typing(self, data: schemas.DataFormated) -> None:
        """
        This function takes the data formated and call
        the functions associated with a typing event

        parameters:
            - data: the formated data

        return:
            None
        """
        self._start_functions(self._command["typing"], data)

    def handle_message(self, data: schemas.DataFormated) -> None:
        """
        This function takes the data formated and call
        the functions associated with a message event and
        call the functions associated to the command event

        parameters:
            - data: the formated data

        return:
            None
        """
        # Start for all messages
        self._start_functions(self._command["message"], data)

        # Start for command
        message_split = data.message.text.split(" ")
        prefix = message_split[0]
        data.message.text = " ".join(message_split[1:])
        commands = list()
        for command in self._command["command"]:
            if command["prefix"] == prefix:
                commands.append(command)
        self._start_functions(commands, data)

    @staticmethod
    def is_condition_true(condition, data: schemas.DataFormated):
        """
        This function check if the condition is true

        parameters:
            - condition: the condition to check
            - data: formated data with user info and additional
            data about the event

        return:
            True if the condition is true, False otherwise
        """
        # https://stackoverflow.com/questions/10048249/how-do-i-determine-if-current-time-is-within-a-specified-range-using-pythons-da
        def is_time_between(begin_time, end_time, check_time=None):
            # If check time is not given, default to current UTC time
            begin_time = time(*map(int, begin_time.split(":")))
            end_time = time(*map(int, end_time.split(":")))
            check_time = check_time or datetime.utcnow().time()
            if end_time > begin_time:
                return begin_time <= check_time <= end_time
            return check_time >= begin_time or check_time <= end_time

        if condition is None:
            return True

        user = data.user.db_name
        message = data.message.text if data.message is not None else None

        check_user = condition.get("users") is None or user in condition["users"]
        check_date = condition.get("timerange") is None or is_time_between(
            condition["timerange"][0], condition["timerange"][1]
        )
        check_regex = (
            condition.get("regex") is None or
            (message is not None and re.search(condition["regex"], message) is not None)
        )

        return check_user and check_date and check_regex

    @classmethod
    def add(
        cls,
        activation_type: str = "message",
        prefix: str = None,
        condition: dict = None,
    ):
        """
        Parameter of the decorated function:
            - activation_type: the type of activation
                ("command", "message", "typing", "attachments", "reaction")
            - prefix: the prefix of the command (ex: "hello" => "!hello")
            - condition: dict of condition to check before executing the command
        """
        activation_list = ["command", "message", "typing", "attachments", "reaction"]
        if activation_type not in activation_list:
            raise ValueError(f"activation_type must be in {activation_list}")

        if activation_type == "command":
            if prefix is None:
                raise ValueError("Prefix is missing")
            if not isinstance(prefix, str):
                raise ValueError("Invalid prefix format")
            # if not prefix.startswith("!"):
            #     raise ValueError("Invalid prefix format, must start with !")

        if condition is not None:
            cls.check_condition_format(condition)

        def decorator(func):
            cls._command[activation_type].append(
                {
                    "prefix": prefix,
                    "condition": condition,
                    "function": func,
                }
            )
            return func

        return decorator

    @staticmethod
    def check_condition_format(condition: dict) -> None:
        """
        This function check if the condition is valid
        Parameter:
            - condition: dict of condition to check

        condition keys:
        - users: list of users that triggers the command, format name in db number_map
        - timerange: list of 2 datetime, the command is only triggered
        between the 2 dates
        - regex: regex to match the message

        Error:
            - if the condition is not valid

        Exception:
            ValueError: if the condition is not valid


        example:
        {
            "users": ["sofredo", "miguelange"],
            "timerange": [datetime(2021, 1, 1), datetime(2021, 1, 31)],
            "regex": "hello"
        }

        """
        if not all(key in ["users", "timerange", "regex"] for key in condition.keys()):
            raise ValueError("Invalid condition")

        if "users" in condition:
            for user in condition["users"]:
                if not isinstance(user, str):
                    raise ValueError("Invalid user format")

        if "timerange" in condition:
            if len(condition["timerange"]) != 2:
                raise ValueError(
                    "Invalid timerange format, start and end date are required"
                )
            for time_range in condition["timerange"]:
                try:
                    datetime.strptime(time_range, "%H:%M")
                except ValueError as exc:
                    raise ValueError("Invalid timerange format, must be HH:MM") from exc

        if "regex" in condition:
            if not isinstance(condition["regex"], str):
                raise ValueError("Invalid regex format")
            try:
                re.compile(condition["regex"])
            except re.error as exc:
                raise ValueError("Invalid regex format") from exc
