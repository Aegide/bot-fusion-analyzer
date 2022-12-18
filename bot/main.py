# coding: utf-8

import os

import discord
import utils
from analyzer import Analysis, generate_analysis
from discord import Client, PartialEmoji
from discord.channel import TextChannel
from discord.guild import Guild
from discord.message import Message
from discord.threads import Thread
from discord.user import User
from discord.file import File
from enums import Description, DiscordColour, Severity
from models import GlobalContext, ServerContext


from PIL import Image
from PIL.PyAccess import PyAccess

ERROR_EMOJI_NAME = "NANI"
ERROR_EMOJI_ID = f"<:{ERROR_EMOJI_NAME}:770390673664114689>"
ERROR_EMOJI = PartialEmoji(name=ERROR_EMOJI_NAME).from_str(ERROR_EMOJI_ID)


intents = discord.Intents.default()
intents.guild_messages = True
intents.members = True
intents.message_content = True
bot = discord.Client(intents=intents)


bot_id = None
bot_avatar_url = None
bot_context = None


ping_aegide = "<@!293496911275622410>"
worksheet_name = "Full dex"


# Aegide
id_server_aegide = 293500383769133056
id_channel_gallery_aegide = 858107956326826004
id_channel_logs_aegide = 616239403957747742
# id_channel_spritework_aegide = 1013429382213279783


# Pokémon Infinite Fusion
id_server_pif = 302153478556352513
id_channel_gallery_pif = 543958354377179176
id_channel_logs_pif = 999653562202214450
# id_channel_spritework_pif = 307020509856530434


def get_channel_from_id(server:Guild, channel_id) -> TextChannel :
    channel = server.get_channel(channel_id)
    if channel is None:
        raise KeyError(channel_id)
    if not isinstance(channel, TextChannel):
        raise TypeError(channel)
    return channel


def get_server_from_id(bot:Client, server_id) -> Guild:
    server = bot.get_guild(server_id)
    if server is None:
        raise KeyError(server_id)
    return server


class BotContext:
    def __init__(self, bot:Client):
        server_aegide = get_server_from_id(bot, id_server_aegide)
        channel_gallery_aegide = get_channel_from_id(server_aegide, id_channel_gallery_aegide)
        channel_log_aegide = get_channel_from_id(server_aegide, id_channel_logs_aegide)

        aegide_context = ServerContext(
            server=server_aegide,
            gallery=channel_gallery_aegide,
            logs=channel_log_aegide,
        )

        server_pif = get_server_from_id(bot, id_server_pif)
        channel_gallery_pif = get_channel_from_id(server_pif, id_channel_gallery_pif)
        channel_log_pif = get_channel_from_id(server_pif, id_channel_logs_pif)

        pif_context = ServerContext(
            server=server_pif,
            gallery=channel_gallery_pif,
            logs=channel_log_pif,
        )

        self.context = GlobalContext(
            aegide= aegide_context,
            pif = pif_context
        )


def ctx()->GlobalContext:
    if bot_context is not None:
        return bot_context.context
    else:
        raise ConnectionError


async def send_bot_logs(analysis:Analysis, author_id:int):
    if analysis.severity is Severity.refused:
        await send_with_content(analysis, author_id)
    else:
        await send_without_content(analysis)
    await send_bonus_content(analysis)


async def send_bonus_content(analysis:Analysis):
    if analysis.transparency is True:
        await ctx().pif.logs.send(embed=analysis.transparency_embed, file=analysis.transparency_file)
        await ctx().aegide.logs.send(embed=analysis.transparency_embed, file=analysis.transparency_file)


async def send_with_content(analysis:Analysis, author_id:int):
    ping_owner = f"<@!{author_id}>"
    await ctx().aegide.logs.send(embed=analysis.embed, content=ping_aegide)
    await ctx().pif.logs.send(embed=analysis.embed, content=ping_owner)


async def send_without_content(analysis:Analysis):
    await ctx().aegide.logs.send(embed=analysis.embed)
    await ctx().pif.logs.send(embed=analysis.embed)


async def send_test_embed(message):
    utils.log_event("T>", message)
    embed = discord.Embed(title="Title test", colour=DiscordColour.gray.value, description=Description.test.value)
    embed.set_thumbnail(url=bot_avatar_url)
    await ctx().aegide.logs.send(embed=embed)


async def handle_sprite_gallery(message:Message):
    utils.log_event("SG>", message)
    analysis = generate_analysis(message)
    if analysis.severity is Severity.refused:
        await message.add_reaction(ERROR_EMOJI)
    await send_bot_logs(analysis, message.author.id)
    

async def handle_test_sprite_gallery(message:Message):
    utils.log_event("T-SG>", message)
    analysis = generate_analysis(message)
    if analysis.severity is Severity.refused:
        await ctx().aegide.logs.send(embed=analysis.embed, content=ping_aegide)
    else:
        await ctx().aegide.logs.send(embed=analysis.embed)
    if analysis.transparency is True:
        await ctx().aegide.logs.send(embed=analysis.transparency_embed, file=analysis.get_transparency_file())
        await ctx().aegide.logs.send(embed=analysis.transparency_embed, file=analysis.get_transparency_file())
        await ctx().aegide.logs.send(embed=analysis.transparency_embed, file=analysis.get_transparency_file())


def is_message_from_spritework_thread(message:Message):
    result = False
    thread = utils.get_thread(message)
    if thread is not None:
        result = is_thread_from_spritework(thread)
    return result


def is_thread_from_spritework(thread:Thread):
    # is_spritework_pif = thread.parent_id == id_channel_spritework_aegide
    # is_spritework_aegide = thread.parent_id == id_channel_spritework_pif
    # return is_spritework_pif or is_spritework_aegide
    return False

def get_help_content():
    help_content = """
    hello - makes the bot say "hello"
test - sends a test embed message
add - turns a channel into a "log channel"
remove - turns a "log channel" into a channel
update - does nothing, yet
aegide - pings Aegide
help - shows this information
    """
    return help_content


@bot.event
async def on_ready():

    global bot_id
    app_info = await bot.application_info()
    bot_id = app_info.id
    permission_id = "17179929600"

    global bot_avatar_url
    # owner = app_info.owner

    bot_user = bot.user
    if bot_user is not None:
        bot_avatar_url = utils.get_display_avatar(bot_user).url

    global bot_context
    bot_context = BotContext(bot)

    print("\n\nReady! bot invite:\n\nhttps://discordapp.com/api/oauth2/authorize?client_id=" + str(bot_id) + "&permissions=" + permission_id + "&scope=bot\n\n")

    await ctx().aegide.logs.send(content="(OK)")



def get_pixels(image:Image.Image) -> PyAccess:
    return image.load()  # type: ignore


@bot.event
async def on_guild_join(guild):
    embed = discord.Embed(title="Joined the server", colour=DiscordColour.green.value, description=guild.name+"\n"+str(guild.id))
    embed.set_thumbnail(url=guild.icon_url)
    await ctx().aegide.logs.send(embed=embed)


@bot.event
async def on_guild_remove(guild):
    embed = discord.Embed(title="Removed from server", colour=DiscordColour.red.value, description=guild.name+"\n"+str(guild.id))
    embed.set_thumbnail(url=guild.icon_url)
    await ctx().aegide.logs.send(embed=embed)


CHANNEL_HANDLER = {
    id_channel_gallery_pif:handle_sprite_gallery,
    id_channel_gallery_aegide:handle_test_sprite_gallery
}


@bot.event
async def on_message(message:Message):
    if utils.is_message_from_human(message, bot_id):
        channel_handler = CHANNEL_HANDLER.get(message.channel.id)
        if channel_handler is not None:
            await channel_handler(message)
        else:
            await handle_rest(message)

 
async def handle_rest(_message:Message):
    # if utils.is_message_from_spritework_thread(message):
    #     await thread.handle_spritework(message)
    pass


def get_user(user_id) -> (User | None):
    return bot.get_user(user_id)


def get_discord_token():
    token = None
    try:
        # Heroku
        token = os.environ["DISCORD_KEY"]
    except:
        # Local
        token = open("../token/discord.txt").read().rstrip()
    return token


if __name__== "__main__" :
    discord_token = get_discord_token()
    bot.run(discord_token)


"""
if sheet_disabled or sheet.init(worksheet_name):
else:
    print("FAILED TO CONNECT TO GSHEET")
"""

