# bot-signal

Signal-bot is a bot that will be used to add command and funny stuff in a group
chat on signal.


## How does it work?

Bot signal is compose of 3 main parts:
- api : the api that will be used to start and stop the bot and the signal-cli
- bot : the bot that will be used to send and receive messages 
- commands : the command that will be used to add command to the bot

The bot is deploy on GCP and use the [signal-cli](https://github.com/AsamK/signal-cli) to send and receive messages.

## How to add a command?

To add a command you need to add a python function in the command folder. 
The function must be decorated with the `@command` decorator and must take 2 arguments:

- data -> DataFormated: the data based on the activation type [here](app/bot/schema/data_formated.py)

The command decorator take 3 arguments:

- activation_type: the type of activation ("command", "message", "typing", "reaction", "attachments")
- prefix: the prefix of the command, example "!tiresurmondoigt"
- condition: dict of condition to check before executing the command

```python

@Command.add(activation_type="command", prefix="!tiresurmondoigt", condition={"users": ["jeanluc"]})
def my_command(data: DataFormated):
	"""This is the docstring of the command"""
    chatter.send_message("prout")

```

basic example are available in the command folder, inside function.py [here](app/commands/basic.py)

### Detail of the activation_type

- command: the command will be activated when the message start with the prefix
- message: the command will be activated for every message
- reaction: the command will be activated for every reaction
- typing: the command will be activated when the user start typing
- attachments: the command will be activated when the user send an attachment

If the activation_type is "command", the prefix is required. It is preferable that the prefix start with a "!".

example:
```python
activation_type = "command"
prefix = "!tiresurmondoigt"
```

### Detail of the condition

Condition are used to check if the command can be executed or not. It is a dict with the
following keys:

- users: list of users that triggers the command, format is name based on the number map file
- timerange: list of 2 datetimes, the command is only triggered between the 2 dates
- regex: regex to match the message

example:
```python
condition = {
    "users": ["michel"],
    "timerange": [datetime(2021, 1, 1), datetime(2021, 1, 31)],
    "regex": "hello"
}
```

### Detail of the chatter

The chatter is the object that will be used to send message. It is a wrapper around the signal-cli.
It has the following methods:

- send_message: send a message with options:
    - attachments : files to send with
    - quote : a message to quote
    - mention : a link to the use ryou are referencing
- send_reaction: send a reaction to a user message
- send_typing: send a typing notification

example:
```python
#to import the chatter
from signal_bot.backend.chat_client.chatter_holder import ChatterHolder
chatter = ChatterHolder.get_chatter()

#to send a message
chatter.send_message("prout")

#to send a reaction
data : DataFormated

chatter.send_reaction(emoji="💨", target_author=data.user.phone, target_timestamp=data.sent_at)

#to send a typing notification
chatter.send_typing()
```

## Access to message history

The bot can access to the message history of the group. It is possible to get the last 50 messages.
history can be access with the chatter object.

example:
```python
#to import the chatter
from signal_bot.backend.chat_client.chatter_holder import ChatterHolder
chatter = ChatterHolder.get_chatter()

#to get the last 50 messages
messages = chatter.get_history(nb_messages=50)
```

## Roadmap

- Add more method to the chatter:
- Add possibility to add command from the api
- Add possibility to add command in an other language than python
