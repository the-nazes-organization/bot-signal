import pytest
from freezegun import freeze_time

from signal_bot.backend.core.command import Command


def test_command_add_message():
    @Command.add(activation_type="message")
    def test_function(message, user):
        pass

    assert Command._command["message"][0]["function"] == test_function
    assert Command._command["message"][0]["condition"] == None
    assert Command._command["message"][0]["prefix"] == None


def test_command_add_two_command():
    @Command.add(activation_type="command", prefix="!test")
    def test_function_0(message, user):
        pass

    @Command.add(activation_type="command", prefix="!test2")
    def test_function_1(message, user):
        pass

    assert len(Command._command["command"]) == 2
    assert Command._command["command"][0]["function"] == test_function_0
    assert Command._command["command"][0]["prefix"] == "!test"
    assert Command._command["command"][1]["function"] == test_function_1
    assert Command._command["command"][1]["prefix"] == "!test2"


def test_command_add_wrong_activation():
    with pytest.raises(ValueError) as excinfo:

        @Command.add(activation_type="jonas_is_the_best_programmer")
        def test_function(message, user):
            pass

    assert "activation_type must be
    " in str(excinfo.value)


def test_command_add_command_no_prefix():
    with pytest.raises(ValueError) as excinfo:

        @Command.add(activation_type="command")
        def test_function(message, user):
            pass

    assert "Prefix is missing" in str(excinfo.value)


def test_command_add_command_wrong_prefix():
    with pytest.raises(ValueError) as excinfo:

        @Command.add(activation_type="command", prefix="test")
        def test_function(message, user):
            pass

    assert "Invalid prefix format" in str(excinfo.value)


def test_command_check_condition_format():
    condition = {
        "users": ["+33612345679"],
        "timerange": ["23:00", "02:00"],
        "regex": "test",
    }
    Command.check_condition_format(condition)


def test_command_check_condition_format_wrong_user():
    condition = {
        "users": ["33633633633"],
        "timerange": ["23:00", "02:00"],
        "regex": "test",
    }
    with pytest.raises(ValueError) as excinfo:
        Command.check_condition_format(condition)
    assert "Invalid user format" in str(excinfo.value)


def test_command_check_condition_format_wrong_timerange():
    condition = {
        "users": ["+33633633633"],
        "timerange": ["23:00", "25:00"],
        "regex": "test",
    }
    with pytest.raises(ValueError) as excinfo:
        Command.check_condition_format(condition)
    assert "Invalid timerange format, must be HH:MM" in str(excinfo.value)


def test_command_check_condition_format_wrong_regex():
    condition = {
        "users": ["+33633633633"],
        "timerange": ["23:00", "02:00"],
        "regex": "[",
    }
    with pytest.raises(ValueError) as excinfo:
        Command.check_condition_format(condition)
    assert "Invalid regex format" in str(excinfo.value)


def test_is_condition_true():
    condition = {
        "users": ["+33642424242"],
    }
    assert Command.is_condition_true(condition, "test", "+33642424242") == True


def test_is_condition_false():
    condition = {
        "users": ["+33642424242"],
    }
    assert Command.is_condition_true(condition, "test", "+33642424241") == False


def test_is_condition_true_regex():
    condition = {
        "regex": "test",
    }
    assert Command.is_condition_true(condition, "test", "+33642424241") == True


def test_is_condition_false_regex():
    condition = {
        "regex": "test",
    }
    assert Command.is_condition_true(condition, "jj le bg", "+33642424241") == False


@freeze_time("23:00")
def test_is_condition_true_timerange():
    condition = {
        "timerange": ["23:00", "02:00"],
    }
    assert Command.is_condition_true(condition, "test", "+33642424241") == True


@freeze_time("23:00")
def test_is_condition_false_timerange():
    condition = {
        "timerange": ["23:01", "02:00"],
    }
    assert Command.is_condition_true(condition, "test", "+33642424241") == False


@freeze_time("23:00")
def test_is_condition_true_timerange_and_regex():
    condition = {
        "timerange": ["23:00", "02:00"],
        "regex": "test",
    }
    assert Command.is_condition_true(condition, "test", "+33642424241") == True


def test_handle_message(capfd):
    @Command.add(activation_type="message")
    def test_function(message, user):
        print("Test1")

    c = Command()
    assert c.handle_message("test", "+33642424242") == None
    out, err = capfd.readouterr()
    assert out == "Test1\n"


def test_handle_message_function_exception(caplog):
    @Command.add(activation_type="message")
    def test_function(message, user):
        raise ValueError("test")

    c = Command()
    assert c.handle_message("test", "+33642424242") == None
    assert "Error while handling function: test_function" in caplog.text


def test_handle_message_command(capfd):
    Command._command = {"command": [], "message": []}

    @Command.add(activation_type="command", prefix="!test_command")
    def test_function_command(message, user, *args, **kwargs):
        print(message)

    c = Command()
    assert c.handle_message(message="!test_command hello", user="+33642424242") == None
    out, err = capfd.readouterr()
    assert "hello\n" in out


def test_handle_message_command_no_prefix(capfd):
    Command._command = {"command": [], "message": []}

    @Command.add(activation_type="command", prefix="!test_command")
    def test_function_command(message, user, *args, **kwargs):
        print(message)

    c = Command()
    assert c.handle_message(message="!test_commandhello", user="+33642424242") == None
    out, err = capfd.readouterr()
    assert "hello\n" not in out

def test_handle_typing(capfd):
    Command._command = {"command": [], "message": [], "typing": [], "attachements": []}

    @Command.add(activation_type="typing")
    def test_function_command(user, *args, **kwargs):
        print(user)

    c = Command()
    assert c.handle_typing(user="+33642424242") == None
    out, err = capfd.readouterr()
    assert "+33642424242" in out

def test_handle_attachements(capfd):
    Command._command = {"command": [], "message": [], "typing": [], "attachements": []}

    @Command.add(activation_type="attachements")
    def test_function_command(user, *args, **kwargs):
        print(kwargs["attachements"][0])

    c = Command()
    assert c.handle_attachements(user="+33642424242", attachements=["image"]) == None
    out, err = capfd.readouterr()
    assert "image" in out
