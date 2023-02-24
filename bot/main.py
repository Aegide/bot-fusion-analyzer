# coding: utf-8

import os

from discord.app_commands import CommandTree
from discord.channel import TextChannel
from discord.client import Client
from discord.embeds import Embed
from discord.flags import Intents
from discord.guild import Guild
from discord.interactions import Interaction
from discord.message import Message
from discord.user import User
from PIL import Image
from PIL.PyAccess import PyAccess

from analyzer import Analysis, generate_analysis
from constants import (ERROR_EMOJI, ID_CHANNEL_GALLERY_AEGIDE,
                       ID_CHANNEL_GALLERY_PIF, ID_CHANNEL_LOGS_AEGIDE,
                       ID_CHANNEL_LOGS_PIF, ID_SERVER_AEGIDE, ID_SERVER_PIF,
                       MAX_SEVERITY)
from enums import DiscordColour
from gallery import is_sprite_gallery
from models import GlobalContext, ServerContext
from spritework import handle_spritework, is_mention_from_spritework
from ticket import handle_ticket, is_mention_from_ticket
from utils import get_display_avatar, is_message_from_human, log_event


intents = Intents.default()
intents.guild_messages = True
intents.members = True
intents.message_content = True
bot = Client(intents=intents)
tree = CommandTree(bot)


bot_id = None
bot_avatar_url = None
bot_context = None


ping_aegide = "<@!293496911275622410>"
worksheet_name = "Full dex"


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
        server_aegide = get_server_from_id(bot, ID_SERVER_AEGIDE)
        channel_gallery_aegide = get_channel_from_id(server_aegide, ID_CHANNEL_GALLERY_AEGIDE)
        channel_log_aegide = get_channel_from_id(server_aegide, ID_CHANNEL_LOGS_AEGIDE)

        aegide_context = ServerContext(
            server=server_aegide,
            gallery=channel_gallery_aegide,
            logs=channel_log_aegide,
        )

        server_pif = get_server_from_id(bot, ID_SERVER_PIF)
        channel_gallery_pif = get_channel_from_id(server_pif, ID_CHANNEL_GALLERY_PIF)
        channel_log_pif = get_channel_from_id(server_pif, ID_CHANNEL_LOGS_PIF)

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
    if bot_context is None:
        raise ConnectionError
    return bot_context.context
        

async def send_bot_logs(analysis:Analysis, author_id:int):
    if analysis.severity in MAX_SEVERITY:
        await send_with_content(analysis, author_id)
    else:
        await send_without_content(analysis)
    await send_bonus_content(analysis)


async def send_bonus_content(analysis:Analysis):
    if analysis.transparency is True:
        await ctx().pif.logs.send(embed=analysis.transparency_embed, file=analysis.gen_transparency_file())


async def send_with_content(analysis:Analysis, author_id:int):
    ping_owner = f"<@!{author_id}>"
    await ctx().pif.logs.send(embed=analysis.embed, content=ping_owner)


async def send_without_content(analysis:Analysis):
    await ctx().pif.logs.send(embed=analysis.embed)


async def handle_test_sprite_gallery(message:Message):
    log_event("T-SG>", message)
    analysis = generate_analysis(message)
    await ctx().aegide.logs.send(embed=analysis.embed)
    if analysis.transparency is True:
        await ctx().aegide.logs.send(embed=analysis.transparency_embed, file=analysis.gen_transparency_file())


@tree.command(name="help", description="Get some help")
async def chat(interaction: Interaction):
    if interaction.user == bot.user:
        return
    await interaction.response.send_message("You can contact Aegide, if you need help with anything related to the fusion bot.")


@bot.event
async def on_ready():
    await tree.sync()

    global bot_id
    app_info = await bot.application_info()
    bot_id = app_info.id
    permission_id = "17179929600"

    global bot_avatar_url
    bot_user = bot.user
    if bot_user is not None:
        bot_avatar_url = get_display_avatar(bot_user).url

    global bot_context
    bot_context = BotContext(bot)

    invite_url = f"https://discordapp.com/api/oauth2/authorize?client_id={bot_id}&permissions={permission_id}&scope=bot"
    print(f"\n\nReady! bot invite: {invite_url}\n\n\n\n")

    await ctx().aegide.logs.send(content="(OK)")


def get_pixels(image:Image.Image) -> PyAccess:
    return image.load()  # type: ignore


@bot.event
async def on_guild_join(guild):
    embed = Embed(title="Joined the server", colour=DiscordColour.green.value, description=guild.name+"\n"+str(guild.id))
    embed.set_thumbnail(url=guild.icon_url)
    await ctx().aegide.logs.send(embed=embed)


@bot.event
async def on_guild_remove(guild):
    embed = Embed(title="Removed from server", colour=DiscordColour.red.value, description=guild.name+"\n"+str(guild.id))
    embed.set_thumbnail(url=guild.icon_url)
    await ctx().aegide.logs.send(embed=embed)


@bot.event
async def on_message(message:Message):
    try:
        await handle_message(message)
    except Exception as exception:
        handle_exception(message, exception)


async def handle_message(message:Message):
    if bot_id is None:
        raise RuntimeError
    if is_message_from_human(message, bot_id):
        if is_sprite_gallery(message):
            await handle_sprite_gallery(message)
        elif is_mention_from_ticket(message, bot_id):
            await handle_ticket(message)
        elif is_mention_from_spritework(message, bot_id):
            await handle_spritework(message)
        else:
            log_event(">>", message)


def handle_exception(message:Message, exception:Exception):
    print(" ")
    print(message)
    print(" ")
    raise RuntimeError from exception


async def handle_sprite_gallery(message:Message):
    log_event("SG>", message)
    analysis = generate_analysis(message)
    if analysis.severity in MAX_SEVERITY:
        await message.add_reaction(ERROR_EMOJI)
    await send_bot_logs(analysis, message.author.id)


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
