import json
from datetime import datetime

import pytest


def test_get_base_rpc_obj(formater):
    obj = formater._get_base_rpc_obj("test")
    assert obj.get("jsonrpc")
    assert obj.get("method") == "test"
    assert obj.get("params")
    assert obj.get("params").get("account") == formater.account
    assert obj.get("id")
    if formater.receiver_type == "group_id":
        assert obj.get("params").get("groupId")
    elif formater.receiver_type == "recipient":
        assert obj.get("params").get("recipient")


def test_format_reaction(formater):
    emoji = "🐒"
    user = "jacky"
    time = datetime.now()
    data = formater.format_reaction(emoji, user, time)
    obj = json.loads(data)
    params = obj.get("params")
    assert obj.get("method") == "sendReaction"
    assert params.get("emoji") == emoji
    assert params.get("targetAuthor") == user
    assert formater._get_datetime_from_timestamp(params.get("targetTimestamp")) == time


def test_format_typing(formater):
    data = formater.format_typing()
    obj = json.loads(data)
    assert obj.get("method") == "sendTyping"


def test_mention_creation_from_message(formater, phonebook):
    assert formater._create_mentions_from_message("@@popo", phonebook) == [
        "0:6:+309213"
    ]
    assert formater._create_mentions_from_message("@po", phonebook) is None
    assert formater._create_mentions_from_message("@@popo@@pipi", phonebook) == [
        "0:6:+309213",
        "6:6:+309999",
    ]
    assert formater._create_mentions_from_message("@@@popo", phonebook) == [
        "1:6:+309213"
    ]


def test_format_message(formater, phonebook):
    message = "ok"
    attachments = ["image", "pok"]
    quote_author = "meyeurll"
    quote_sent = datetime.now()
    data = formater.format_message(
        phonebook, message, attachments, quote_author, quote_sent
    )
    obj = json.loads(data)
    params = obj.get("params")
    assert obj.get("method") == "send"
    assert params.get("message") == message
    assert params.get("attachments") == attachments
    assert params.get("quoteAuthor") == quote_author
    quote_datetime = formater._get_datetime_from_timestamp(params.get("quoteTimestamp"))
    assert quote_datetime == quote_sent
    assert params.get("mentions") is None


def test_format_message_with_mentions(formater, phonebook):
    message = "@@popo okokok"
    data = formater.format_message(phonebook, message)
    obj = json.loads(data)
    params = obj.get("params")
    assert obj.get("method") == "send"
    assert params.get("message") == message
    assert params.get("attachments") is None
    assert params.get("quoteAuthor") is None
    assert params.get("quoteTimestamp") is None
    assert params.get("mentions") == ["0:6:+309213"]


def test_get_raw_data_from_json(formater):
    assert formater._get_raw_data_from_json('{"1":123}').get("1") == 123


def test_get_raw_data_from_json_fail(formater):
    with pytest.raises(json.JSONDecodeError) as excinfo:
        formater._get_raw_data_from_json("{'ok':")

    assert excinfo is not None


def test_get_data_message_from_envelope(formater, raw_data):
    raw_obj = formater._get_raw_data_from_json(raw_data)
    envelope = raw_obj["params"]["envelope"]
    data_message = formater._get_data_message_from_envelope(envelope)
    assert data_message == envelope.get("dataMessage")


@pytest.mark.parametrize("raw_data", ["self_send"], indirect=True)
def test_get_data_message_from_envelope_debug(formater, raw_data):
    raw_obj = formater._get_raw_data_from_json(raw_data)
    envelope = raw_obj["params"]["envelope"]
    formater.debug = True
    data_message = formater._get_data_message_from_envelope(envelope)
    assert data_message == envelope["syncMessage"]["sentMessage"]
    formater.debug = False


@pytest.mark.parametrize("raw_data", ["message", "typing"], indirect=True)
def test_get_group_id_from_envelope(formater, raw_data):
    raw_obj = formater._get_raw_data_from_json(raw_data)
    envelope = raw_obj["params"]["envelope"]
    valid_group = "dhwq98hwqoud1092u"
    group_envelope = formater._get_group_id_from_envelope(envelope)
    assert valid_group == group_envelope


@pytest.mark.parametrize(
    "formater,raw_data",
    [("recipient", "empty"), ("group_id", "message")],
    indirect=True,
)
def test_get_envelope_and_check_validity(formater, raw_data):
    raw_obj = formater._get_raw_data_from_json(raw_data)
    valid_envelope = raw_obj["params"]["envelope"]
    envelope = formater._get_envelope_and_check_validity(raw_obj)
    assert envelope == valid_envelope


@pytest.mark.parametrize(
    "formater,raw_data",
    [("recipient", "message"), ("group_id", "empty")],
    indirect=True,
)
def test_get_envelope_and_check_validity_wrong_receiver(formater, raw_data):
    raw_obj = formater._get_raw_data_from_json(raw_data)
    envelope = formater._get_envelope_and_check_validity(raw_obj)
    assert envelope is None


def test_get_envelope_and_check_validity_wrong_data(formater, raw_data):
    raw_obj = formater._get_raw_data_from_json(raw_data)
    raw_obj["method"] = "unknown"
    envelope = formater._get_envelope_and_check_validity(raw_obj)
    assert envelope is None

    raw_obj = formater._get_raw_data_from_json(raw_data)
    raw_obj["params"] = {}
    envelope = formater._get_envelope_and_check_validity(raw_obj)
    assert envelope is None

    envelope = formater._get_envelope_and_check_validity({"jsonrpc": "2.0"})
    assert envelope is None


def test_get_basic_formated_data(formater, raw_data):
    raw_obj = formater._get_raw_data_from_json(raw_data)
    envelope = formater._get_envelope_and_check_validity(raw_obj)
    data_formated = formater._get_basic_formated_data(envelope)

    assert data_formated.id is not None
    assert data_formated.user.nickname == envelope.get("sourceName")
    assert data_formated.user.phone == envelope.get("sourceNumber")
    sent_at = formater._get_datetime_from_timestamp(envelope.get("timestamp"))
    assert data_formated.sent_at == sent_at


def mentions_testing_validity(mentions, raw_mentions):
    for idx, mention in enumerate(mentions):
        raw_mention = raw_mentions[idx]
        assert mention.user.nickname == raw_mention["name"]
        assert mention.user.phone == raw_mention["number"]
        assert mention.start == raw_mention["start"]
        assert mention.length == raw_mention["length"]


@pytest.mark.parametrize("raw_data", ["full_message"], indirect=True)
def test_get_mentions_formated_data(formater, raw_data):
    raw_obj = formater._get_raw_data_from_json(raw_data)
    raw_mentions = raw_obj["params"]["envelope"]["dataMessage"]["mentions"]

    assert formater._get_mentions_formated_data(None) is None
    assert formater._get_mentions_formated_data([]) is None

    mentions = formater._get_mentions_formated_data(raw_mentions)
    mentions_testing_validity(mentions, raw_mentions)


@pytest.mark.parametrize("raw_data", ["full_message"], indirect=True)
def test_get_quote_formated_data(formater, raw_data):
    raw_obj = formater._get_raw_data_from_json(raw_data)
    raw_quote = raw_obj["params"]["envelope"]["dataMessage"]["quote"]

    assert formater._get_quote_formated_data(None) is None

    quote = formater._get_quote_formated_data(raw_quote)
    assert quote.text == raw_quote.get("text")
    assert quote.author.nickname == raw_quote.get("author")
    assert quote.author.phone == raw_quote.get("authorNumber")

    mentions_testing_validity(quote.mentions, raw_quote["mentions"])


def test_get_message_formated_data(formater, raw_data):
    assert formater._get_message_formated_data(None) is None
    assert formater._get_message_formated_data({"ok": "ok"}) is None

    raw_obj = formater._get_raw_data_from_json(raw_data)
    data_message = raw_obj["params"]["envelope"]["dataMessage"]
    message = formater._get_message_formated_data(data_message)
    assert message.text == data_message["message"]
    assert message.quote == data_message.get("quote")
    assert message.mentions == data_message.get("mentions")


@pytest.mark.parametrize("raw_data", ["typing"], indirect=True)
def test_get_typing_formated_data(formater, raw_data):
    assert formater._get_typing_formated_data(None) is None

    raw_obj = formater._get_raw_data_from_json(raw_data)
    raw_typing = raw_obj["params"]["envelope"]["typingMessage"]
    typing = formater._get_typing_formated_data(raw_typing)

    assert typing.status == raw_typing.get("action")


@pytest.mark.parametrize("raw_data", ["reaction"], indirect=True)
def test_get_reaction_formated_data(formater, raw_data):
    assert formater._get_reaction_formated_data(None) is None
    assert formater._get_reaction_formated_data({"ok": 1}) is None

    raw_obj = formater._get_raw_data_from_json(raw_data)
    data_message = raw_obj["params"]["envelope"]["dataMessage"]
    raw_reaction = data_message["reaction"]
    reaction = formater._get_reaction_formated_data(data_message)

    assert reaction.reaction == raw_reaction["emoji"]
    assert reaction.target_author.nickname == raw_reaction["targetAuthor"]
    assert reaction.target_author.phone == raw_reaction["targetAuthorNumber"]

    sent_at = formater._get_datetime_from_timestamp(
        raw_reaction.get("targetSentTimestamp")
    )
    assert reaction.sent_at == sent_at


@pytest.mark.parametrize("raw_data", ["attachments"], indirect=True)
def test_get_attachments_formated_data(formater, raw_data):
    assert formater._get_attachments_formated_data(None) is None
    assert formater._get_attachments_formated_data({"ok": 1}) is None
    assert formater._get_attachments_formated_data({"attachments": []}) is None

    raw_obj = formater._get_raw_data_from_json(raw_data)
    data_message = raw_obj["params"]["envelope"]["dataMessage"]
    raw_attachments = data_message["attachments"]
    attachments = formater._get_attachments_formated_data(data_message)
    for idx, attachment in enumerate(attachments):
        raw_attachment = raw_attachments[idx]
        assert attachment.content_type == raw_attachment["contentType"]
        assert attachment.filename == raw_attachment["filename"]
        assert attachment.size == raw_attachment["size"]


def test_deformat_into_data_formated(formater, raw_data):
    raw_obj = formater._get_raw_data_from_json(raw_data)

    data = formater._deformat_into_data_formated(raw_obj)

    assert data.id is not None
    assert data.user is not None
    assert data.sent_at is not None
    assert data.message is not None
    assert data.typing is None
    assert data.reaction is None
    assert data.attachments is None
