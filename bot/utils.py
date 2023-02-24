from re import search, match

from discord.asset import Asset
from discord.member import Member
from discord.message import Message
from discord.threads import Thread
from discord.user import ClientUser, User

from analysis import Analysis


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
    else:
        _log_other(decorator, event)


def _log_message(decorator:str, message:Message):
    print(f"{decorator} [{message.author.name}] {message.content}")


def _log_other(decorator:str, other):
    print(f"{decorator} [{other}]")


# is_message_not_from_a_bot
def is_message_from_human(message:Message, fusion_bot_id:int):
    return message.author.id != fusion_bot_id and message.author.id != YAGPDB_ID


def get_thread(message:Message) -> (Thread | None):
    thread = message.channel
    if isinstance(thread, Thread):
        return thread
    return None


def get_filename(analysis:Analysis):
    if analysis.specific_attachment is None:
        return  analysis.message.attachments[0].filename
    return analysis.specific_attachment.filename


def get_attachment_url(analysis:Analysis):
    if analysis.specific_attachment is None:
        return  analysis.message.attachments[0].url
    return analysis.specific_attachment.url


def interesting_results(results:list):
    return results[1] is not None


def have_icon_in_message(analysis:Analysis):
    result = search(PATTERN_ICON, analysis.message.content)
    return result is not None


def have_custom_in_message(analysis:Analysis):
    result = search(PATTERN_CUSTOM, analysis.message.content)
    return result is not None


def have_base_in_message(analysis:Analysis):
    result = search(PATTERN_BASE, analysis.message.content)
    return result is not None


def have_egg_in_message(analysis:Analysis):
    result = search(PATTERN_EGG, analysis.message.content)
    return result is not None


def have_attachment(analysis:Analysis):
    return len(analysis.message.attachments) >= 1


def get_autogen_url(fusion_id:str):
    return AUTOGEN_FUSION_URL + fusion_id.split(".")[0] + "/" + fusion_id + ".png"


def is_invalid_fusion_id(fusion_id:str):
    head, body = fusion_id.split(".")
    head_id, body_id = int(head), int(body)
    return head_id > 420 or body_id > 420


def get_display_avatar(user: User|Member|ClientUser) -> Asset:
    return user.display_avatar.with_format("png").with_size(256)


def extract_fusion_id_from_filename(analysis:Analysis):
    fusion_id = None
    if have_attachment(analysis):
        filename = get_filename(analysis)
        fusion_id = get_fusion_id_from_filename(filename)
    return fusion_id


def get_fusion_id_from_filename(filename:str):
    fusion_id = None
    result = match(STRICT_PATTERN_FUSION_ID, filename)
    if result is not None:
        fusion_id = get_fusion_id_from_text(result[0])
    else:
        result = match(SPOILER_PATTERN_FUSION_ID, filename)
        if result is not None:
            fusion_id = get_fusion_id_from_text(result[0])
    return fusion_id


def extract_fusion_id_from_content(analysis:Analysis):
    return get_fusion_id_from_text(analysis.message.content)


def get_fusion_id_from_text(text:str):
    fusion_id = None
    result = search(LAZY_PATTERN_FUSION_ID, text)
    if result:
        fusion_id = result[0]
    return fusion_id


def is_reply(message:Message):
    return message.reference is not None


def is_mentioning(message:Message, target_id:int):
    result = False
    for user in message.mentions:
        if target_id == user.id:
            result = True
            break
    return result


async def get_reply_message(message:Message):
    if message.reference is None:
        raise RuntimeError(message)
    reply_id = message.reference.message_id
    if reply_id is None:
        raise RuntimeError(message)
    return await message.channel.fetch_message(reply_id)


def exists(value):
    return value is not None
