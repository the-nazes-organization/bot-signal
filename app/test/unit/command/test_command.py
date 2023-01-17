import pytest
from freezegun import freeze_time

from app.bot.command import Command
from app.bot.schema.data_formated import AttachmentData, Message, Reaction, Typing


def reset_command_func_dict():
    Command._command = {
        "message": [],
        "command": [],
        "typing": [],
        "attachments": [],
        "reaction": [],
    }


def test_command_add_message():
    reset_command_func_dict()

    @Command.add(activation_type="message")
    def test_function(data):
        pass

    assert Command._command["message"][0]["function"] == test_function
    assert Command._command["message"][0]["condition"] is None
    assert Command._command["message"][0]["prefix"] is None


def test_command_add_two_command():
    reset_command_func_dict()

    @Command.add(activation_type="command", prefix="!test")
    def test_function_0(data):
        pass

    @Command.add(activation_type="command", prefix="!test2")
    def test_function_1(data):
        pass

    assert len(Command._command["command"]) == 2
    assert Command._command["command"][0]["function"] == test_function_0
    assert Command._command["command"][0]["prefix"] == "!test"
    assert Command._command["command"][1]["function"] == test_function_1
    assert Command._command["command"][1]["prefix"] == "!test2"


def test_command_add_wrong_activation():
    with pytest.raises(ValueError) as excinfo:

        @Command.add(activation_type="jonas_is_the_best_programmer")
        def test_function(data):
            pass

    assert "activation_type must be" in str(excinfo.value)


def test_command_add_command_no_prefix():
    with pytest.raises(ValueError) as excinfo:

        @Command.add(activation_type="command")
        def test_function(data):
            pass

    assert "Prefix is missing" in str(excinfo.value)


@pytest.mark.skip(reason="Not sure if prefix should start with !")
def test_command_add_command_wrong_prefix():
    with pytest.raises(ValueError) as excinfo:

        @Command.add(activation_type="command", prefix="test")
        def test_function(data):
            pass

    assert "Invalid prefix format" in str(excinfo.value)


def test_command_check_condition_format():
    condition = {
        "users": ["koroga"],
        "timerange": ["23:00", "02:00"],
        "regex": "test",
    }
    Command.check_condition_format(condition)


def test_command_check_condition_format_wrong_user():
    condition = {
        "users": [11233],
        "timerange": ["23:00", "02:00"],
        "regex": "test",
    }
    with pytest.raises(ValueError) as excinfo:
        Command.check_condition_format(condition)
    assert "Invalid user format" in str(excinfo.value)


def test_command_check_condition_format_wrong_timerange():
    condition = {
        "users": ["piroulo"],
        "timerange": ["23:00", "25:00"],
        "regex": "test",
    }
    with pytest.raises(ValueError) as excinfo:
        Command.check_condition_format(condition)
    assert "Invalid timerange format, must be HH:MM" in str(excinfo.value)


def test_command_check_condition_format_wrong_regex():
    condition = {
        "users": ["golagan"],
        "timerange": ["23:00", "02:00"],
        "regex": "[",
    }
    with pytest.raises(ValueError) as excinfo:
        Command.check_condition_format(condition)
    assert "Invalid regex format" in str(excinfo.value)


def test_is_condition_true_user(bdata_formated):
    condition = {
        "users": ["test"],
    }
    assert Command.is_condition_true(condition, bdata_formated) is True


def test_is_condition_false_user(bdata_formated):
    condition = {
        "users": ["gololo"],
    }
    assert Command.is_condition_true(condition, bdata_formated) is False


def test_is_condition_false_no_user_name(bdata_formated):
    condition = {
        "users": ["gololo"],
    }
    bdata_formated.user.db_name = None
    assert Command.is_condition_true(condition, bdata_formated) is False


def test_is_condition_true_regex(bdata_formated):
    condition = {
        "regex": "test",
    }
    bdata_formated.message = Message(text="test")
    assert Command.is_condition_true(condition, bdata_formated) is True


def test_is_condition_false_regex(bdata_formated):
    condition = {
        "regex": "test",
    }
    bdata_formated.message = Message(text="rom le bouf")
    assert Command.is_condition_true(condition, bdata_formated) is False


def test_is_condition_true_regex_no_message(bdata_formated):
    condition = {
        "regex": "test",
    }
    assert Command.is_condition_true(condition, bdata_formated) is False


@freeze_time("23:00")
def test_is_condition_true_timerange(bdata_formated):
    condition = {
        "timerange": ["23:00", "02:00"],
    }
    assert Command.is_condition_true(condition, bdata_formated) is True


@freeze_time("23:00")
def test_is_condition_false_timerange(bdata_formated):
    condition = {
        "timerange": ["23:01", "02:00"],
    }
    assert Command.is_condition_true(condition, bdata_formated) is False


@freeze_time("23:00")
def test_is_condition_true_timerange_and_regex(bdata_formated):
    condition = {
        "timerange": ["23:00", "02:00"],
        "regex": "test",
    }
    bdata_formated.message = Message(text="test")
    assert Command.is_condition_true(condition, bdata_formated) is True


def test_start_functions(capfd, bdata_formated):
    def test_function_0(data):
        print("1 worked")

    def test_function_1(data):
        print("2 worked")

    commands = [
        {"function": test_function_0, "condition": {"users": ["test"]}},
        {"function": test_function_1, "condition": {"regex": "test"}},
    ]
    bdata_formated.message = Message(text="test")
    cmd = Command(threading=False)
    assert cmd._start_functions(commands, bdata_formated) is None
    out, _ = capfd.readouterr()
    assert "1 worked\n2 worked\n" == out


def test_start_functions_exception(caplog, bdata_formated):
    caplog.clear()

    def test_function(data):
        raise ValueError("test")

    commands = [{"function": test_function}]
    cmd = Command(threading=False)
    assert cmd._start_functions(commands, bdata_formated) is None
    assert "Error while handling function: test_function" in caplog.text


def test_handle_reaction(capfd, bdata_formated):
    reset_command_func_dict()

    @Command.add(activation_type="reaction")
    def test_function(data):
        print(data.reaction.reaction)

    bdata_formated.reaction = Reaction(
        reaction="🖖", target_author=bdata_formated.user, sent_at=bdata_formated.sent_at
    )
    cmd = Command(threading=False)
    assert cmd.handle_reaction(bdata_formated) is None
    out, _ = capfd.readouterr()
    assert "🖖\n" == out


def test_handle_attachments(capfd, bdata_formated):
    reset_command_func_dict()

    @Command.add(activation_type="attachments")
    def test_function(data):
        print(data.attachments[0].filename)

    bdata_formated.attachments = [
        AttachmentData(content_type="txt", filename="romfib_passwords", size=999999)
    ]
    cmd = Command(threading=False)
    assert cmd.handle_attachments(bdata_formated) is None
    out, _ = capfd.readouterr()
    assert "romfib_passwords\n" == out


def test_handle_typing(capfd, bdata_formated):
    reset_command_func_dict()

    @Command.add(activation_type="typing")
    def test_function(data):
        print(data.typing.status)

    bdata_formated.typing = Typing(status="STARTED")
    cmd = Command(threading=False)
    assert cmd.handle_typing(bdata_formated) is None
    out, _ = capfd.readouterr()
    assert "TypingStatus.STARTED\n" == out


def test_handle_message(capfd, bdata_formated):
    reset_command_func_dict()

    @Command.add(activation_type="message")
    def test_function(data):
        if data.message.text == "tu marches ?":
            print("oui")

    bdata_formated.message = Message(text="tu marches ?")
    cmd = Command(threading=False)
    assert cmd.handle_message(bdata_formated) is None
    out, _ = capfd.readouterr()
    assert out == "oui\n"


def test_handle_message_command(capfd, bdata_formated):
    reset_command_func_dict()

    @Command.add(activation_type="command", prefix="!test_command")
    def test_function(data):
        print(data.message.text)

    bdata_formated.message = Message(text="!test_command hello")
    cmd = Command(threading=False)
    assert cmd.handle_message(bdata_formated) is None
    out, _ = capfd.readouterr()
    assert "hello\n" in out


def test_handle_message_command_only_prefix(capfd, bdata_formated):
    reset_command_func_dict()

    @Command.add(activation_type="command", prefix="!test_command")
    def test_function(data):
        if data.message.text == "":
            print("empty")

    bdata_formated.message = Message(text="!test_command")
    cmd = Command(threading=False)
    assert cmd.handle_message(bdata_formated) is None
    out, _ = capfd.readouterr()
    assert "empty\n" in out


def test_handle_message_command_no_prefix(capfd, bdata_formated):
    reset_command_func_dict()

    @Command.add(activation_type="command", prefix="!test_command")
    def test_function(data):
        print(data.message.text)

    bdata_formated.message = Message(text="!test_commandhello")
    cmd = Command(threading=False)
    assert cmd.handle_message(bdata_formated) is None
    out, _ = capfd.readouterr()
    assert "hello\n" not in out
