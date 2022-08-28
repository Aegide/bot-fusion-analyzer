# coding: utf-8

import discord
from discord.client import Client, ClientUser
from discord.message import Message
from discord.channel import TextChannel as Channel
from discord import Asset

import re
import os

from bot_enum import Title, Description, Colour


intents = discord.Intents.default()
intents.guild_messages = True
intents.members = True
intents.message_content = True

bot = discord.Client(intents=intents)
# bot = commands.Bot(command_prefix='$')
bot_id = None
bot_avatar_url = None

bot_context = None

autogen_fusion_url = "https://raw.githubusercontent.com/Aegide/FusionSprites/master/Battlers/"
ping_aegide = "<@!293496911275622410>"
worksheet_name = "Full dex"


# Aegide
id_server_aegide = 293500383769133056
id_channel_gallery_aegide = 858107956326826004
id_channel_logs_aegide = 616239403957747742


# Pokémon Infinite Fusion
id_server_pif = 302153478556352513
id_channel_gallery_if = 543958354377179176
id_channel_logs_if = 999653562202214450
id_channel_spritework_if = 307020509856530434


# Type autocompletion at all cost
class BotContext:

    def __init__(self, bot:Client):

        # Aegide
        server_aegide = bot.get_guild(id_server_aegide)
        self.__aegide_gallery = server_aegide.get_channel(id_channel_gallery_aegide)
        self.__aegide_logs = server_aegide.get_channel(id_channel_logs_aegide)

        # Pokémon Infinite Fusion
        server_pif = bot.get_guild(id_server_pif)
        self.__pif_gallery = server_pif.get_channel(id_channel_gallery_if)
        self.__pif_logs = server_pif.get_channel(id_channel_logs_if)
        # self.pif_spritework = server_pif.get_channel(id_channel_spritework_if)

    def aegide_gallery(self)->Channel:
        return self.__aegide_gallery
    
    def aegide_logs(self)->Channel:
        return self.__aegide_logs

    def pif_gallery(self)->Channel:
        return self.__pif_gallery

    def pif_logs(self)->Channel:
        return self.__pif_logs
    

def ctx()->BotContext:
    return bot_context


def apply_display_mode(embed, attachment_url, autogen_url):
    if attachment_url:
        embed.set_thumbnail(url=attachment_url)
    if autogen_url:
        embed.set_image(url=autogen_url)
    return embed


def create_embed(valid_fusion, description, jump_url, fusion_id, warning):
    if valid_fusion:
        title = f"__{Title.accepted.value} : {fusion_id}__"
        colour = Colour.green.value
    else:
        if warning is not None:
            title = f"__{Title.refused.value} : {description}__\n{warning}"
            colour = Colour.red.value
        else:
            title = f"__{Title.ignored.value} :  {description}__"
            colour = Colour.orange.value

    return discord.Embed(title=title, colour=colour, description="[Link to message](" + jump_url + ")")


def have_icon_in_message(message):
    pattern = '[iI]con'
    result = re.search(pattern, message.content)
    return result is not None


def have_custom_in_message(message):
    pattern = '[cC]ustom'
    result = re.search(pattern, message.content)
    return result is not None


def extract_fusion_id_from_attachment(message):
    fusion_id = None
    if len(message.attachments) >= 1:
        filename = message.attachments[0].filename
        pattern = '[0-9]+\.[0-9]+'
        result = re.search(pattern, filename)
        if result:
            fusion_id = result[0]
    return fusion_id


def get_autogen_url(fusion_id):
    return autogen_fusion_url + fusion_id.split(".")[0] + "/" + fusion_id + ".png"


def get_attachment_url(message):
    return message.attachments[0].url


def have_attachment(message):
    return len(message.attachments) >= 1


def extract_fusion_id_from_content(message):
    fusion_id = None
    pattern = '[0-9]+\.[0-9]+'
    result = re.search(pattern, message.content)
    if result:
        fusion_id = result[0]
    return fusion_id


def handle_two_values(attachment_fusion_id, content_fusion_id):
    autogen_url = get_autogen_url(attachment_fusion_id)
    warning = None
    valid_fusion = False
    
    # Same values
    if attachment_fusion_id == content_fusion_id:
        valid_fusion = True
        fusion_id = attachment_fusion_id
        description = attachment_fusion_id
    # Different values
    else:
        fusion_id = attachment_fusion_id
        description = Description.different_fusion_id.value
        warning = attachment_fusion_id + " =/= " + content_fusion_id
    return autogen_url, valid_fusion, fusion_id, description, warning


def handle_one_value(attachment_fusion_id, content_fusion_id):
    valid_fusion = False
    warning = None

    # Value from file
    if attachment_fusion_id is not None:
        valid_fusion = True
        fusion_id = attachment_fusion_id
        description = attachment_fusion_id
        autogen_url = get_autogen_url(attachment_fusion_id)
    
    # Value from text
    else:
        fusion_id = content_fusion_id
        description = Description.missing_file_name.value
        autogen_url = get_autogen_url(content_fusion_id)
        warning = "File name should be \"" + content_fusion_id + ".png\""
    
    return autogen_url, valid_fusion, fusion_id, description, warning


def handle_zero_value(message):
    if have_icon_in_message(message):
        description = Description.icon.value
    elif have_custom_in_message(message):
        description = Description.custom.value
    else:
        description = Description.missing_fusion_id.value
    return description


def is_invalid_fusion_id(fusion_id:str):
    head_id, body_id = fusion_id.split(".")
    head_id, body_id = int(head_id), int(body_id)
    return head_id > 420 or body_id > 420 or head_id < 1 or body_id < 1


def handle_verification(fusion_id:str, valid_fusion, autogen_url, description, warning):
    if fusion_id is not None:
        if is_invalid_fusion_id(fusion_id):
            valid_fusion = False
            autogen_url = None
            description = Description.invalid_fusion_id.value
            warning = f"{fusion_id} is not in the IF Pokedex"
    return valid_fusion, autogen_url, description, warning


def extract_data(message):
    valid_fusion = False
    description = Description.error.value
    autogen_url = None
    fusion_id = None
    warning = None
    attachment_url = None
    
    # Existing file
    if have_attachment(message):
        attachment_url = get_attachment_url(message)
        attachment_fusion_id = extract_fusion_id_from_attachment(message)
        content_fusion_id = extract_fusion_id_from_content(message)

        if attachment_fusion_id is not None and content_fusion_id is not None:
            autogen_url, valid_fusion, fusion_id, description, warning = handle_two_values(attachment_fusion_id, content_fusion_id)

        elif attachment_fusion_id is not None or content_fusion_id is not None:
            autogen_url, valid_fusion, fusion_id, description, warning = handle_one_value(attachment_fusion_id, content_fusion_id)
        
        else:
            description = handle_zero_value(message)
    
    # Missing file + spoilers
    else:
        description = Description.missing_file.value
    
    # Check fusion id
    valid_fusion, autogen_url, description, warning = handle_verification(fusion_id, valid_fusion, autogen_url, description, warning)

    return valid_fusion, description, attachment_url, autogen_url, fusion_id, warning


async def send_bot_logs(embed, have_warning, author_id:str):

    if have_warning:
        ping_owner = f"<@!{author_id}>"
        await ctx().aegide_logs().send(embed=embed, content=ping_aegide)
        await ctx().pif_logs().send(embed=embed, content=ping_owner)
    
    else:
        await ctx().pif_logs().send(embed=embed)
        await ctx().aegide_logs().send(embed=embed)


async def send_test_embed(message):
    print(")>", message.author.name, ":", message.content)
    embed = discord.Embed(title="Title test", colour=Colour.gray.value, description=Description.test.value)
    embed.set_thumbnail(url=bot_avatar_url)
    await ctx().aegide_logs().send(embed=embed)


def log_message(symbol, message:Message):
    print(symbol, message.author.name, ":", message.content)


def interesting_results(results):
    return results[1] is not None


async def generate_embed(message:Message):
    valid_fusion, description, attachment_url, autogen_url, fusion_id, warning = extract_data(message)

    """
    if valid_fusion:
        results = sprite_analyzer.test_sprite(attachment_url)
        if interesting_results(results):
            valid_fusion, description, warning, file_name = results
            if file_name is not None:
                file_path = os.path.join(os.getcwd(), "tmp", file_name)
                file = discord.File(file_path, filename="image.png")
                message_file = await sprite_stash_channel.send(file=file)
                os.remove(file_path)
                autogen_url = message_file.attachments[0].url
    """

    embed = create_embed(valid_fusion, description, message.jump_url, fusion_id, warning)
    author_avatar = get_display_avatar(message.author)
    embed.set_author(name=message.author.name, icon_url=author_avatar.url)
    embed.set_footer(text=message.content)
    embed = apply_display_mode(embed, attachment_url, autogen_url)
    return embed, warning, valid_fusion, fusion_id


async def handle_sprite_gallery(message:Message):
    log_message(">>", message)
    embed, warning, valid_fusion, fusion_id = await generate_embed(message)
    await send_bot_logs(embed, warning is not None, message.author.id)


async def handle_test_sprite_gallery(message:Message):
    log_message("]>", message)
    embed, warning, valid_fusion, fusion_id = await generate_embed(message)
    if warning is None:
        await ctx().aegide_logs().send(embed=embed)
    else:
        await ctx().aegide_logs().send(embed=embed, content=ping_aegide)


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


def is_message_from_human(message):
    return message.author.id != bot_id


def get_display_avatar(user:ClientUser) -> Asset:
    return user.display_avatar.with_format("png").with_size(256)


@bot.event
async def on_ready():

    global bot_id
    app_info = await bot.application_info()
    bot_id = app_info.id
    permission_id = "2048"

    global bot_avatar_url
    # owner = app_info.owner
    bot_avatar_url = get_display_avatar(bot.user).url

    global bot_context
    bot_context = BotContext(bot)

    print("\n\nReady! bot invite:\n\nhttps://discordapp.com/api/oauth2/authorize?client_id=" + str(bot_id) + "&permissions=" + permission_id + "&scope=bot\n\n")


@bot.event
async def on_guild_join(guild):
    embed = discord.Embed(title="Joined the server", colour=Colour.green.value, description=guild.name+"\n"+str(guild.id))
    embed.set_thumbnail(url=guild.icon_url)
    await ctx().aegide_logs().send(embed=embed)


@bot.event
async def on_guild_remove(guild):
    embed = discord.Embed(title="Removed from server", colour=Colour.red.value, description=guild.name+"\n"+str(guild.id))
    embed.set_thumbnail(url=guild.icon_url)
    await ctx().aegide_logs().send(embed=embed)


@bot.event
async def on_message(message:Message):

    if is_message_from_human(message):
        if(message.channel.id == id_channel_gallery_if):
            await handle_sprite_gallery(message)
        
        elif(message.channel.id == id_channel_gallery_aegide):
            await handle_test_sprite_gallery(message)


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