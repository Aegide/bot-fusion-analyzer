import re

from discord.message import Message
from discord.asset import Asset
from discord.user import User, ClientUser
from discord.member import Member
from discord.threads import Thread

from analysis import Analysis


MAX_DEX_ID = 500
MISSING_DEX_ID = 469

PATTERN_ICON = r'[iI]con'
PATTERN_CUSTOM = r'[cC]ustom'
PATTERN_BASE = r'[bB]ase'
PATTERN_EGG = r'[eE]gg'

LAZY_PATTERN_FUSION_ID = r'([1-9]+[0-9]*)\.([1-9]+[0-9]*)'
STRICT_PATTERN_FUSION_ID = LAZY_PATTERN_FUSION_ID + r'[a-z]{0,1}\.png$'

REGULAR_PATTERN_FUSION_ID = rf'^{STRICT_PATTERN_FUSION_ID}'
SPOILER_PATTERN_FUSION_ID = rf'^SPOILER_{STRICT_PATTERN_FUSION_ID}'

RAW_GITHUB = "https://raw.githubusercontent.com"
RAW_GITLAB = "https://gitlab.com"

AUTOGEN_FUSION_URL = f"{RAW_GITLAB}/pokemoninfinitefusion/autogen-fusion-sprites/-/raw/master/Battlers/"
QUESTION_URL = f"{RAW_GITHUB}/Aegide/bot-fusion-analyzer/main/bot/question.png"

YAGPDB_ID = 204255221017214977

LCB = "{"
RCB = "}"


def log_event(decorator:str, event:Message|Thread):
    if isinstance(event, Message):
        _log_message(decorator, event)


def _log_message(decorator:str, message:Message):
    channel_name = get_channel_name(message)
    print(f"{decorator} [{message.author.name}] {LCB}{channel_name}{RCB} {message.content}")


def get_channel_name(message:Message):
    try:
        channel_name = message.channel.name  # type: ignore
        if not isinstance(channel_name, str):
            channel_name = "INVALID"
    except:
        channel_name = "INVALID"
    return channel_name


# is_message_not_from_a_bot
def is_message_from_human(message:Message, fusion_bot_id:int|None):
    return message.author.id not in (fusion_bot_id, YAGPDB_ID)


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


def have_attachment(analysis:Analysis):
    return len(analysis.message.attachments) >= 1


def is_missing_autogen(fusion_id:str):
    split_fusion_id = fusion_id.split(".")
    head_id = int(split_fusion_id[0])
    body_id = int(split_fusion_id[1])
    return head_id > MISSING_DEX_ID or body_id > MISSING_DEX_ID


def get_autogen_url(fusion_id:str):
    if is_missing_autogen(fusion_id):
        return QUESTION_URL
    return AUTOGEN_FUSION_URL + fusion_id.split(".")[0] + "/" + fusion_id + ".png"


def is_invalid_fusion_id(fusion_id:str):
    head, body = fusion_id.split(".")
    head_id, body_id = int(head), int(body)
    return head_id > MAX_DEX_ID or body_id > MAX_DEX_ID


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
    result = re.match(REGULAR_PATTERN_FUSION_ID, filename)
    if result is not None:
        fusion_id = get_fusion_id_from_text(result[0])
    else:
        result = re.match(SPOILER_PATTERN_FUSION_ID, filename)
        if result is not None:
            fusion_id = get_fusion_id_from_text(result[0])
    return fusion_id


def extract_fusion_id_from_content(analysis:Analysis):
    return get_fusion_id_from_text(analysis.message.content)


def get_fusion_id_from_text(text:str):
    fusion_id = None
    result = re.search(LAZY_PATTERN_FUSION_ID, text)
    if result:
        fusion_id = result[0]
    return fusion_id
