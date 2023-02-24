from discord.errors import Forbidden
from discord.message import Message

from analyzer import generate_analysis
from utils import get_reply_message, is_mentioning, is_reply, log_event


TICKET_CATEGORY_ID = 1073799466773127178


def is_mention_from_ticket(message:Message, bot_id:int):
    return is_ticket_category(message) and is_reply(message) and is_mentioning(message, bot_id)


def is_ticket_category(message:Message):
    result = False
    try:
        result = message.channel.category_id == TICKET_CATEGORY_ID
    except:
        pass
    return result


async def handle_ticket(message:Message):
    reply_message = await get_reply_message(message)
    await handle_ticket_gallery(reply_message)


async def handle_ticket_gallery(message:Message):
    log_event("T>", message)
    for specific_attachment in message.attachments:
        analysis = generate_analysis(message, specific_attachment)
        try:
            await message.channel.send(embed=analysis.embed)
            if analysis.transparency is True:
                await message.channel.send(embed=analysis.transparency_embed, file=analysis.gen_transparency_file())
        except Forbidden:
           print("T>> Missing permissions in %s" % message.channel)
