# coding: utf-8

import os

import discord
import utils
from analysis import generate_bonus_file
from analyzer import Analysis, generate_analysis
from discord import Client, PartialEmoji, app_commands
from discord.channel import TextChannel
from discord.guild import Guild
from discord.message import Message
from discord.user import User
from enums import DiscordColour, Severity
from exceptions import MissingBotContext
from models import GlobalContext, ServerContext
from PIL import Image
from PIL.PyAccess import PyAccess


ERROR_EMOJI_NAME = "NANI"
ERROR_EMOJI_ID = f"<:{ERROR_EMOJI_NAME}:770390673664114689>"
ERROR_EMOJI = PartialEmoji(name=ERROR_EMOJI_NAME).from_str(ERROR_EMOJI_ID)
MAX_SEVERITY = [Severity.refused, Severity.controversial]


intents = discord.Intents.default()
intents.guild_messages = True
intents.members = True
intents.message_content = True
bot = discord.Client(intents=intents)
tree = app_commands.CommandTree(bot)


bot_id = None
bot_avatar_url = None
bot_context = None


ping_aegide = "<@!293496911275622410>"
worksheet_name = "Full dex"


# Aegide
id_server_aegide = 293500383769133056
id_channel_gallery_aegide = 858107956326826004
id_channel_logs_aegide = 616239403957747742
# id_channel_debug = None


# Pokémon Infinite Fusion
id_server_pif = 302153478556352513
id_channel_gallery_pif = 543958354377179176
id_channel_logs_pif = 999653562202214450
id_channel_debug_pif = 703351286019653762


def get_channel_from_id(server:Guild, channel_id) -> TextChannel :
    channel = server.get_channel(channel_id)
    if channel is None:
        raise KeyError(channel_id)
    if not isinstance(channel, TextChannel):
        raise TypeError(channel)
    return channel


def get_server_from_id(client:Client, server_id) -> Guild:
    server = client.get_guild(server_id)
    if server is None:
        raise KeyError(server_id)
    return server


class BotContext:
    def __init__(self, client:Client):
        server_aegide = get_server_from_id(client, id_server_aegide)
        channel_gallery_aegide = get_channel_from_id(server_aegide, id_channel_gallery_aegide)
        channel_log_aegide = get_channel_from_id(server_aegide, id_channel_logs_aegide)

        aegide_context = ServerContext(
            server=server_aegide,
            gallery=channel_gallery_aegide,
            logs=channel_log_aegide,
            debug=None
        )

        server_pif = get_server_from_id(client, id_server_pif)
        channel_gallery_pif = get_channel_from_id(server_pif, id_channel_gallery_pif)
        channel_log_pif = get_channel_from_id(server_pif, id_channel_logs_pif)
        channel_debug_pif = get_channel_from_id(server_pif, id_channel_debug_pif)

        pif_context = ServerContext(
            server=server_pif,
            gallery=channel_gallery_pif,
            logs=channel_log_pif,
            debug=channel_debug_pif
        )

        self.context = GlobalContext(
            aegide= aegide_context,
            pif = pif_context
        )


def ctx()->GlobalContext:
    if bot_context is not None:
        return bot_context.context
    else:
        raise MissingBotContext


async def send_bot_logs(analysis:Analysis, author_id:int):
    if analysis.severity in MAX_SEVERITY:
        await send_with_content(analysis, author_id)
    else:
        await send_without_content(analysis)
    await send_bonus_content(analysis)


async def send_bonus_content(analysis:Analysis):
    if analysis.transparency_issue:
        await ctx().pif.logs.send(
            embed=analysis.transparency_embed,
            file=generate_bonus_file(analysis.transparency_image)
        )
    if analysis.half_pixels_issue:
        await ctx().pif.logs.send(
            embed=analysis.half_pixels_embed,
            file=generate_bonus_file(analysis.half_pixels_image)
        )


async def send_with_content(analysis:Analysis, author_id:int):
    ping_owner = f"<@!{author_id}>"
    # await ctx().aegide.logs.send(embed=analysis.embed, content=ping_aegide)
    await ctx().pif.logs.send(embed=analysis.embed, content=ping_owner)


async def send_without_content(analysis:Analysis):
    # await ctx().aegide.logs.send(embed=analysis.embed)
    await ctx().pif.logs.send(embed=analysis.embed)


async def handle_sprite_gallery(message:Message):
    utils.log_event("SG>", message)
    analysis = generate_analysis(message)
    if analysis.severity in MAX_SEVERITY:
        await message.add_reaction(ERROR_EMOJI)
    await send_bot_logs(analysis, message.author.id)


async def handle_test_sprite_gallery(message:Message):
    utils.log_event("T-SG>", message)
    analysis = generate_analysis(message)
    await ctx().aegide.logs.send(embed=analysis.embed)
    if analysis.transparency_issue:
        await ctx().aegide.logs.send(
            embed=analysis.transparency_embed,
            file=generate_bonus_file(analysis.transparency_image)
        )
    if analysis.half_pixels_issue:
        await ctx().aegide.logs.send(
            embed=analysis.half_pixels_embed,
            file=generate_bonus_file(analysis.half_pixels_image)
        )


async def handle_reply_message(message:Message):
    utils.log_event("R>", message)
    for specific_attachment in message.attachments:
        analysis = generate_analysis(message, specific_attachment, True)
        try:
            await message.channel.send(embed=analysis.embed)
            if analysis.transparency_issue:
                await message.channel.send(
                    embed=analysis.transparency_embed,
                    file=generate_bonus_file(analysis.transparency_image)
                )
            if analysis.half_pixels_issue:
                await message.channel.send(
                    embed=analysis.half_pixels_embed,
                    file=generate_bonus_file(analysis.half_pixels_image)
                )
        except discord.Forbidden:
            print(f"R>> Missing permissions in {message.channel}")


@tree.command(name="help", description="Get some help")
async def help_command(interaction: discord.Interaction):
    text = "You can contact Aegide, if you need help with anything related to the fusion bot."
    await interaction.response.send_message(text)


@tree.command(name="similar", description="Get the list of similar colors")
async def similar_command(interaction: discord.Interaction):
    text = "soon TM."
    await interaction.response.send_message(text)


@bot.event
async def on_ready():
    await tree.sync()

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

    invite_parameters = f"client_id={str(bot_id)}&permissions={permission_id}&scope=bot"
    invite_link = f"https://discordapp.com/api/oauth2/authorize?{invite_parameters}"
    print(f"\n\nReady! bot invite:\n\n{invite_link}\n\n")

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


@bot.event
async def on_message(message:Message):
    try:
        if utils.is_message_from_human(message, bot_id):
            if is_sprite_gallery(message):
                await handle_sprite_gallery(message)
            elif is_mentioning_reply(message):
                await handle_reply(message)

    except Exception as message_exception:
        print(" ")
        print(message)
        print(" ")
        ping_author = f"<@!{message.author.id}>"
        error_message = "An error occurred while processing your message from"
        await ctx().pif.debug.send(f"{ping_aegide}/{ping_author} : {error_message} #{message.channel} ({message.jump_url})")  # type: ignore
        raise RuntimeError from message_exception


def is_sprite_gallery(message:Message):
    return message.channel.id == id_channel_gallery_pif


def is_mentioning_reply(message:Message):
    return is_mentioning_bot(message) and is_reply(message)


def is_reply(message:Message):
    return message.reference is not None


def is_mentioning_bot(message:Message):
    result = False
    for user in message.mentions:
        if bot_id == user.id:
            result = True
            break
    return result


async def handle_reply(message:Message):
    reply_message = await get_reply_message(message)
    await handle_reply_message(reply_message)


async def get_reply_message(message:Message):
    if message.reference is None:
        raise RuntimeError(message)

    reply_id = message.reference.message_id
    if reply_id is None:
        raise RuntimeError(message)

    return await message.channel.fetch_message(reply_id)


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
