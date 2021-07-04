# coding: utf-8

import discord
# from discord.ext import commands
import re
import sheet

# Custom sprite is displayed in the thumbnail
compact_mode = "compact_mode"

# Custom sprite is displayed in the thumbnail, autogen equivalent is displayed
safe_mode = "safe_mode"

# Custom sprite is displayed, autogen equivalent is displayed in the thumbnail
extended_mode = "extended_mode"

display_mode = safe_mode


bot = discord.Client()
# bot = commands.Bot(command_prefix='$')
bot_id = None
avatar_url = None

autogen_fusion_url = "https://raw.githubusercontent.com/Aegide/FusionSprites/master/Japeal/"

# Servers
aegide_server_id = 293500383769133056
infinite_fusion_server_id = 302153478556352513
# katten_server_id = 750734964823294033

# Input(s)
infinite_fusion_sprite_gallery_id = 543958354377179176
aegide_sprite_gallery_id = 858107956326826004

# Output - aegide
aegide_log_id = 616239403957747742
aegide_log_channel = None

# Output - IF
infinite_fusion_log_id = 703351286019653762
infinite_fusion_log_channel = None

# Output - katten
# katten_log_id = 750734964823294036
# katten_log_channel = None


# Output - regular
log_channels = set()

green_colour = discord.Colour(0x2ecc71)
orange_colour = discord.Colour(0xe67e22)
red_colour = discord.Colour(0xe74c3c)
gray_colour = discord.Colour(0xcdcdcd)

title_ignored = "Ignored"
title_accepted = "Accepted"

description_missing_file = "Missing sprite"
description_missing_file_name = "Invalid file name"
description_missing_fusion_id = "Unable to identify fusion sprite"
description_icon = "Fusion icon"

description_different_fusion_id = "Incoherent fusion name"
description_error = "Please contact Aegide"

def apply_compact_mode(embed, attachment_url, autogen_url):
    if attachment_url:
        embed.set_thumbnail(url=attachment_url)
    return embed

def apply_safe_mode(embed, attachment_url, autogen_url):
    if attachment_url:
        embed.set_thumbnail(url=attachment_url)
    if autogen_url:
        embed.set_image(url=autogen_url)
    return embed

def apply_extended_mode(embed, attachment_url, autogen_url):
    if attachment_url:
        embed.set_image(url=attachment_url)
    if autogen_url:
        embed.set_thumbnail(url=autogen_url)
    return embed

def apply_display_mode(embed, display_mode, attachment_url, autogen_url):
    if display_mode == compact_mode:
        embed = apply_compact_mode(embed, attachment_url, autogen_url)

    elif display_mode == safe_mode:
        embed = apply_safe_mode(embed, attachment_url, autogen_url)

    elif display_mode == extended_mode:
        embed = apply_extended_mode(embed, attachment_url, autogen_url)

    return embed

def create_embed(valid_fusion, description, jump_url, fusion_id, warning):
    if warning is not None:
        title = title_accepted + " : " + fusion_id + "\n(" + warning + ")"
        colour = orange_colour
    elif valid_fusion:
        title = title_accepted + " : " + fusion_id
        colour = green_colour
    else:
        title = title_ignored + " : " + description
        colour = red_colour

    return discord.Embed(title=title, colour=colour, description="[Link to message](" + jump_url + ")")
        
def have_icon_in_content(message):
    fusion_id = None
    pattern = 'icon'
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

def extract_data(message):
    valid_fusion = False
    description = description_error
    autogen_url = None
    fusion_id = None
    attachment_url = None
    warning = None
    # Existing file
    if have_attachment(message):
        attachment_url = get_attachment_url(message)
        attachment_fusion_id = extract_fusion_id_from_attachment(message)
        content_fusion_id = extract_fusion_id_from_content(message)
        # Two values
        if attachment_fusion_id is not None and content_fusion_id is not None:
            autogen_url = get_autogen_url(attachment_fusion_id)
            # Same values
            if attachment_fusion_id == content_fusion_id:
                valid_fusion = True
                fusion_id = attachment_fusion_id
                description = attachment_fusion_id
            # Different values
            else:
                fusion_id = attachment_fusion_id
                description = description_different_fusion_id + "\n( " + attachment_fusion_id + " =/= " + content_fusion_id + " )"
        # One value
        elif attachment_fusion_id is not None or content_fusion_id is not None:
            valid_fusion = True
            # Value from file
            if attachment_fusion_id is not None:
                fusion_id = attachment_fusion_id
                description = attachment_fusion_id
                autogen_url = get_autogen_url(attachment_fusion_id)
            # Value from text
            else:
                fusion_id = content_fusion_id
                description = content_fusion_id
                autogen_url = get_autogen_url(content_fusion_id)
                warning = description_missing_file_name
            pass
        # Zero values
        else:
            if have_icon_in_content:
                description = description_icon
            else:
                description = description_missing_fusion_id
    # Missing file + spoilers
    else:
        description = description_missing_file
    return valid_fusion, description, attachment_url, autogen_url, fusion_id, warning

async def send_bot_logs(embed):
    for log_channel in log_channels:
        print(">", log_channel.guild.name, ":", log_channel.name)
        await log_channel.send(embed=embed)

async def send_test_embed(message):
    print(">>", message.author.name, ":", message.content)
    embed = discord.Embed(title="Title test", colour=gray_colour, description="Description test")
    embed.set_thumbnail(url=avatar_url)
    await send_bot_logs(embed)

async def add_log_channel(channel):
    global log_channels
    log_channels.add(channel)
    embed = discord.Embed(title="Added log channel", colour=green_colour, description=channel.name+"\n"+str(channel.id))
    embed.set_thumbnail(url=channel.guild.icon_url)
    await aegide_log_channel.send(embed=embed)

async def remove_log_channel(channel):
    global log_channels
    log_channels.remove(channel)
    embed = discord.Embed(title="Removed log channel", colour=red_colour, description=channel.name+"\n"+str(channel.id))
    embed.set_thumbnail(url=channel.guild.icon_url)
    await aegide_log_channel.send(embed=embed)

async def handle_sprite_gallery(message):
    print(">>", message.author.name, ":", message.content)
    valid_fusion, description, attachment_url, autogen_url, fusion_id, warning = extract_data(message)
    embed = create_embed(valid_fusion, description, message.jump_url, fusion_id, warning)
    embed.set_author(name=message.author.name, icon_url=message.author.avatar_url)
    embed.set_footer(text=message.content)
    embed = apply_display_mode(embed, display_mode, attachment_url, autogen_url)
    await send_bot_logs(embed)
    if valid_fusion:
        sheet.validate_fusion(fusion_id)

def handle_test_sprite_gallery(message):
    print("]>", message.author.name, ":", message.content)
    valid_fusion, description, attachment_url, autogen_url, fusion_id, warning = extract_data(message)
    embed = create_embed(valid_fusion, description, message.jump_url, fusion_id, warning)
    embed.set_author(name=message.author.name, icon_url=message.author.avatar_url)
    embed.set_footer(text=message.content)
    embed = apply_display_mode(embed, display_mode, attachment_url, autogen_url)
    return embed

async def handle_command(message):
    content = message.content
    if(message.channel in log_channels):
        if(content.startswith("%" + "hello")):
            await message.channel.send(content=content)
        elif(content.startswith("%" + "update")):
            pass
        elif(content.startswith("%" + "test")):
            await send_test_embed(message)
        elif(content.startswith("%" + "remove")):
            await message.channel.send(content="Channel removed")
            await remove_log_channel(message.channel)
        elif(content.startswith("%" + "add")):
            await message.channel.send(content="Channel already added")
    else:
        if(content.startswith("%" + "add")):
            await message.channel.send(content="Channel added")
            await add_log_channel(message.channel)

@bot.event
async def on_ready():

    global bot_id
    app_info = await bot.application_info()
    bot_id = app_info.id
    permission_id = "2048"

    global avatar_url
    # owner = app_info.owner
    avatar_url = bot.user.avatar_url_as(static_format='png', size=256)

    global aegide_log_channel
    aegide_server = bot.get_guild(aegide_server_id)
    aegide_log_channel = aegide_server.get_channel(aegide_log_id)
    log_channels.add(aegide_log_channel)

    global infinite_fusion_log_channel
    infinite_fusion_server = bot.get_guild(infinite_fusion_server_id)
    infinite_fusion_log_channel = infinite_fusion_server.get_channel(infinite_fusion_log_id)
    log_channels.add(infinite_fusion_log_channel)

    print("\n\n")
    print("Ready! bot invite:\n\nhttps://discordapp.com/api/oauth2/authorize?client_id=" + str(bot_id) + "&permissions=" + permission_id + "&scope=bot")
    print("\n\n")

@bot.event
async def on_guild_join(guild):
    embed = discord.Embed(title="Joined the server", colour=green_colour, description=guild.name+"\n"+str(guild.id))
    embed.set_thumbnail(url=guild.icon_url)
    await aegide_log_channel.send(embed=embed)

@bot.event
async def on_guild_remove(guild):
    embed = discord.Embed(title="Removed from server", colour=red_colour, description=guild.name+"\n"+str(guild.id))
    embed.set_thumbnail(url=guild.icon_url)
    await aegide_log_channel.send(embed=embed)

@bot.event
async def on_message(message):
    if message.author.id != bot_id:
        if(message.channel.id == infinite_fusion_sprite_gallery_id):
            await handle_sprite_gallery(message)
        elif(message.channel.id == aegide_sprite_gallery_id):
            embed = handle_test_sprite_gallery(message)
            await aegide_log_channel.send(embed=embed)
        else:
            await handle_command(message)

if sheet.init():
    token = open("token.txt").read().rstrip()
    bot.run(token)