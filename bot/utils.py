from discord import Message, Thread

from bot.main import get_user


def log_event(decorator:str, event:Message|Thread):
    if isinstance(event, Thread):
        _log_thread(decorator, event)
    else:
        _log_message(decorator, event)


def _log_thread(decorator:str, thread:Thread):
    thread_owner_name = thread.owner_id
    thread_owner = get_user(thread.owner_id)
    if thread_owner is not None:
        thread_owner_name = thread_owner.name
    print(decorator, thread_owner_name, ":T:", thread.name)


def _log_message(decorator:str, message:Message):
    print(decorator, message.author.name, ":M:", message.content)


# is_message_not_from_the_fusion_bot
def is_message_from_human(message:Message, bot_id:int|None):
    return message.author.id != bot_id


def get_thread(message:Message) -> (Thread | None):
    thread = message.channel
    if isinstance(thread, Thread):
        return thread
    return None

