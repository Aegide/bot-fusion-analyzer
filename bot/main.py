# coding: utf-8


import re
import os
import discord
from discord.member import Member
from discord.user import User
from discord.message import Message
from discord.channel import TextChannel as Channel
from discord.threads import Thread
from discord.guild import Guild
from discord import Asset, Client, ClientUser, PartialEmoji


from bot_enum import Title, Description, Colour
import utils


PATTERN_ICON = r'[iI]con'
PATTERN_CUSTOM = r'[cC]ustom'
PATTERN_BASE = r'[bB]ase'
LAZY_PATTERN_FUSION_ID = r'[0-9]+\.[0-9]+'
STRICT_PATTERN_FUSION_ID = r'[0-9]+\.[0-9]+[a-z]{0,1}\.png$'
SPOILER_PATTERN_FUSION_ID = f'SPOILER_{STRICT_PATTERN_FUSION_ID}'

EMOJI_NAME = "NANI"
EMOJI_ID = f"<:{EMOJI_NAME}:770390673664114689>"
EMOJI = PartialEmoji(name=EMOJI_NAME).from_str(EMOJI_ID)


"""
commands = []
commands.append("kill")
commands.append("close")
commands.append("end")
commands.append("destroy")
"""


intents = discord.Intents.default()
intents.guild_messages = True
intents.members = True
intents.message_content = True
bot = discord.Client(intents=intents)


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
id_channel_spritework_aegide = 1013429382213279783


# Pokémon Infinite Fusion
id_server_pif = 302153478556352513
id_channel_gallery_pif = 543958354377179176
id_channel_logs_pif = 999653562202214450
id_channel_spritework_pif = 307020509856530434



# Type autocompletion at all cost
class BotContext:

    def __init__(self, bot:Client):

        # Aegide
        self.__server_aegide = bot.get_guild(id_server_aegide)
        if self.__server_aegide is not None:
            self.__aegide_gallery = self.__server_aegide.get_channel(id_channel_gallery_aegide)
            self.__aegide_logs = self.__server_aegide.get_channel(id_channel_logs_aegide)
            self.__aegide_spritework = self.__server_aegide.get_channel(id_channel_spritework_aegide)

        # Pokémon Infinite Fusion
        self.__server_pif = bot.get_guild(id_server_pif)
        if self.__server_pif is not None:
            self.__pif_gallery = self.__server_pif.get_channel(id_channel_gallery_pif)
            self.__pif_logs = self.__server_pif.get_channel(id_channel_logs_pif)
            self.__pif_spritework = self.__server_pif.get_channel(id_channel_spritework_pif)

    # Aegide
    def aegide_server(self)->Guild:
        return self.__server_aegide

    def aegide_gallery(self)->Channel:
        return self.__aegide_gallery
    
    def aegide_logs(self)->Channel:
        return self.__aegide_logs

    def aegide_spritework(self)->Channel:
        return self.__aegide_spritework

    # Pokémon Infinite Fusion
    def pif_server(self)->Guild:
        return self.__server_pif

    def pif_gallery(self)->Channel:
        return self.__pif_gallery

    def pif_logs(self)->Channel:
        return self.__pif_logs
    
    def pif_spritework(self)->Channel:
        return self.__pif_spritework


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
    result = re.search(PATTERN_ICON, message.content)
    return result is not None


def have_custom_in_message(message):
    result = re.search(PATTERN_CUSTOM, message.content)
    return result is not None


def have_base_in_message(message):
    result = re.search(PATTERN_BASE, message.content)
    return result is not None


def has_attachments(message:Message):
    return len(message.attachments) >= 1


def get_filename(message:Message):
    return message.attachments[0].filename


def get_fusion_id_from_filename(filename:str):
    fusion_id = None
    result = re.match(STRICT_PATTERN_FUSION_ID, filename)
    if result is not None:
        fusion_id = result[0]
    else:
        result = re.match(SPOILER_PATTERN_FUSION_ID, filename)
        if result is not None:
            fusion_id = result[0]
    return fusion_id

def get_fusion_id_from_content(filename:str):
    fusion_id = None
    result = re.search(LAZY_PATTERN_FUSION_ID, filename)
    if result:
        fusion_id = result[0]
    return fusion_id


def extract_fusion_id_from_filename(message:Message):
    fusion_id = None
    if has_attachments(message):
        filename = get_filename(message)
        fusion_id = get_fusion_id_from_filename(filename)
    return fusion_id


def get_autogen_url(fusion_id):
    return autogen_fusion_url + fusion_id.split(".")[0] + "/" + fusion_id + ".png"


def get_attachment_url(message):
    return message.attachments[0].url


def have_attachment(message):
    return len(message.attachments) >= 1


def extract_fusion_id_from_content(message):
    return get_fusion_id_from_content(message.content)


def handle_two_values(filename_fusion_id, content_fusion_id):
    autogen_url = get_autogen_url(filename_fusion_id)
    warning = None
    valid_fusion = False
    
    # Same values
    if filename_fusion_id == content_fusion_id:
        valid_fusion = True
        fusion_id = filename_fusion_id
        description = filename_fusion_id
    # Different values
    else:
        fusion_id = filename_fusion_id
        description = Description.different_fusion_id.value
        warning = f"{filename_fusion_id} =/= {content_fusion_id}"
    return autogen_url, valid_fusion, fusion_id, description, warning


def handle_one_value(filename_fusion_id, content_fusion_id):
    valid_fusion = False
    warning = None

    # Value from file
    if filename_fusion_id is not None:
        valid_fusion = True
        fusion_id = filename_fusion_id
        description = filename_fusion_id
        autogen_url = get_autogen_url(filename_fusion_id)
    
    # Value from text
    else:
        fusion_id = content_fusion_id
        description = Description.missing_file_name.value
        autogen_url = get_autogen_url(content_fusion_id)
        warning = f'File name should be "{content_fusion_id}.png"'
    
    return autogen_url, valid_fusion, fusion_id, description, warning


def handle_zero_value(message):
    if have_icon_in_message(message):
        description = Description.icon.value
    elif have_custom_in_message(message):
        description = Description.custom.value
    elif have_base_in_message(message):
        description = Description.base.value
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
        filename_fusion_id = extract_fusion_id_from_filename(message)
        content_fusion_id = extract_fusion_id_from_content(message)

        if filename_fusion_id is not None and content_fusion_id is not None:
            autogen_url, valid_fusion, fusion_id, description, warning = handle_two_values(filename_fusion_id, content_fusion_id)

        elif filename_fusion_id is not None or content_fusion_id is not None:
            autogen_url, valid_fusion, fusion_id, description, warning = handle_one_value(filename_fusion_id, content_fusion_id)
        
        else:
            description = handle_zero_value(message)
    
    # Missing file + spoilers
    else:
        description = Description.missing_file.value
    
    # Check fusion id
    valid_fusion, autogen_url, description, warning = handle_verification(fusion_id, valid_fusion, autogen_url, description, warning)

    return valid_fusion, description, attachment_url, autogen_url, fusion_id, warning


async def send_bot_logs(embed, have_warning, author_id:int):

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
    utils.log_event("SG>", message)
    embed, warning, valid_fusion, fusion_id = await generate_embed(message)
    if warning is not None:
        await message.add_reaction(EMOJI)
    await send_bot_logs(embed, warning is not None, message.author.id)


async def handle_test_sprite_gallery(message:Message):
    utils.log_event("T-SG>", message)
    embed, warning, valid_fusion, fusion_id = await generate_embed(message)
    if warning is None:
        await ctx().aegide_logs().send(embed=embed)
    else:
        await ctx().aegide_logs().send(embed=embed, content=ping_aegide)


    """
    message.channel => (MessageableChannel)

    PartialMessageableChannel = Union[TextChannel, VoiceChannel, Thread, DMChannel, PartialMessageable]
    MessageableChannel = Union[PartialMessageableChannel, GroupChannel]
    """


def is_message_from_spritework_thread(message:Message):
    result = False
    thread = utils.get_thread(message)
    if thread is not None:
        result = is_thread_from_spritework(thread)
    return result


def is_thread_from_spritework(thread:Thread):
    is_spritework_pif = thread.parent_id == id_channel_spritework_aegide
    is_spritework_aegide = thread.parent_id == id_channel_spritework_pif
    return is_spritework_pif or is_spritework_aegide


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




def get_display_avatar(user: User|Member|ClientUser) -> Asset:
    return user.display_avatar.with_format("png").with_size(256)


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
        bot_avatar_url = get_display_avatar(bot_user).url

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
    pass
    # if utils.is_message_from_spritework_thread(message):
    #     await thread.handle_spritework(message)


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