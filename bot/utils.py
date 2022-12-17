import re

from discord import Asset, ClientUser, Member, Message, Thread, User

PATTERN_ICON = r'[iI]con'
PATTERN_CUSTOM = r'[cC]ustom'
PATTERN_BASE = r'[bB]ase'
PATTERN_EGG = r'[eE]gg'

LAZY_PATTERN_FUSION_ID = r'[0-9]+\.[0-9]+'
STRICT_PATTERN_FUSION_ID = r'[0-9]+\.[0-9]+[a-z]{0,1}\.png$'
SPOILER_PATTERN_FUSION_ID = f'SPOILER_{STRICT_PATTERN_FUSION_ID}'

AUTOGEN_FUSION_URL = "https://raw.githubusercontent.com/Aegide/FusionSprites/master/Battlers/"


YAGPDB_ID = 204255221017214977


def log_event(decorator:str, event:Message|Thread):
    if isinstance(event, Message):
        _log_message(decorator, event)
    elif isinstance(event, Thread):
        _log_thread(decorator, event)
    else:
        pass


def _log_thread(decorator:str, thread:Thread):
    pass
    # thread_owner_name = thread.owner_id
    # thread_owner = get_user(thread.owner_id)
    # if thread_owner is not None:
    #     thread_owner_name = thread_owner.name
    # print(decorator, thread_owner_name, ":T:", thread.name)


def _log_message(decorator:str, message:Message):
    print(decorator, message.author.name, message.content)


# is_message_not_from_the_fusion_bot
def is_message_from_human(message:Message, fusion_bot_id:int|None):
    return message.author.id != fusion_bot_id and message.author.id != YAGPDB_ID


def get_thread(message:Message) -> (Thread | None):
    thread = message.channel
    if isinstance(thread, Thread):
        return thread
    return None


def get_filename(message:Message):
    return message.attachments[0].filename


def get_attachment_url(message:Message):
    return message.attachments[0].url


def interesting_results(results:list):
    return results[1] is not None


def have_icon_in_message(message:Message):
    result = re.search(PATTERN_ICON, message.content)
    return result is not None


def have_custom_in_message(message:Message):
    result = re.search(PATTERN_CUSTOM, message.content)
    return result is not None


def have_base_in_message(message:Message):
    result = re.search(PATTERN_BASE, message.content)
    return result is not None


def have_egg_in_message(message:Message):
    result = re.search(PATTERN_EGG, message.content)
    return result is not None


def have_attachment(message:Message):
    return len(message.attachments) >= 1


def get_autogen_url(fusion_id:str):
    return AUTOGEN_FUSION_URL + fusion_id.split(".")[0] + "/" + fusion_id + ".png"


def is_invalid_fusion_id(fusion_id:str):
    head, body = fusion_id.split(".")
    head_id, body_id = int(head), int(body)
    return head_id > 420 or body_id > 420


def get_display_avatar(user: User|Member|ClientUser) -> Asset:
    return user.display_avatar.with_format("png").with_size(256)


def get_fusion_id_from_filename(filename:str):
    fusion_id = None
    result = re.match(STRICT_PATTERN_FUSION_ID, filename)
    if result is not None:
        fusion_id = get_fusion_id_from_text(result[0])
    else:
        result = re.match(SPOILER_PATTERN_FUSION_ID, filename)
        if result is not None:
            fusion_id = get_fusion_id_from_text(result[0])
    return fusion_id


def get_fusion_id_from_text(text:str):
    fusion_id = None
    result = re.search(LAZY_PATTERN_FUSION_ID, text)
    if result:
        fusion_id = result[0]
    return fusion_id


def extract_fusion_id_from_filename(message:Message):
    fusion_id = None
    if have_attachment(message):
        filename = get_filename(message)
        fusion_id = get_fusion_id_from_filename(filename)
    return fusion_id


def extract_fusion_id_from_content(message):
    return get_fusion_id_from_text(message.content)

