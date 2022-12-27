# bot-signal

Signal-bot is a bot that will be used to add command and funny stuff in a group
chat on signal.


## How does it work?

Bot signal is compose of 3 main parts:
- api	: the api that will be used to start and stop the bot
- bot	: the bot that will be used to send and receive messages 
- command: the command that will be used to add command to the bot

The bot is deploy on GCP and use the [signal-cli](https://github.com/AsamK/signal-cli) to send and receive messages.

## How to add a command?

To add a command you need to add a python function in the command folder. 
The function must be decorated with the `@command` decorator and must take 2 arguments:
	- message: the message that trigger the command. The prefix of the command is removed
	- user: the user that send the message

The command decorator take 3 arguments:
	- activation_type: the type of activation ("command", "message", "typing", "attachements")
	- prefix: the prefix of the command, example "!tiresurmondoigt"
	- condition: dict of condition to check before executing the command

```python

@Command.add(activation_type="command", prefix="!tiresurmondoigt", condition={"users": ["+33642424242"]})
def my_command(message, user):
	"""This is the docstring of the command"""
    chatter.send_message("prout")

```

basic example are available in the command folder, inside function.py [here](signal_bot/backend/commands/functions/basic.py)

### Detail of the activation_type

- command: the command will be activated when the message start with the prefix
- message: the command will be activated for every message
- typing: the command will be activated when the user start typing
- attachements: the command will be activated when the user send an attachement

If the activation_type is "command" or "message", the prefix is required. A prefix must start with a "!".

example:
```python
activation_type = "command"
prefix = "!tiresurmondoigt"
```

### Detail of the condition

Condition are used to check if the command can be executed or not. It is a dict with the
following keys:
    - users: list of users that triggers the command, format is phone number
    - timerange: list of 2 datetimes, the command is only triggered between the 2 dates
    - regex: regex to match the message

example:
```python
condition = {
    "users": ["+33642424242", "+33624242424"],
    "timerange": [datetime(2021, 1, 1), datetime(2021, 1, 31)],
    "regex": "hello"
}
```

### Detail of the chatter

The chatter is the object that will be used to send message. It is a wrapper around the signal-cli.
It has the following methods:
	- send_message: send a message to the user
	- send_reaction: send a reaction to the user
	- send_typing: send a typing notification to the user

example:
```python
#to import the chatter
from signal_bot.backend.bot.bot import chatter

#to send a message
chatter.send_message("prout")

#to send a reaction
chatter.send_reaction(emoji="💨", target_author="+33642424242", target_timestamp="1611234567890)

#to send a typing notification
chatter.send_typing()
```

## Access to message history

The bot can access to the message history of the group. It is possible to get the last 50 messages.
history can be access with the chatter object.

example:
```python
#to import the chatter
from signal_bot.backend.bot.bot import chatter

#to get the last 50 messages
messages = chatter.get_messages(last=50)
```

## Roadmap

- Add more method to the chatter:
	- send_image
	- send_video
	- send_audio
	- send_file

- Add possibility to add command from the api
- Add possibility to add command in an other language than python


