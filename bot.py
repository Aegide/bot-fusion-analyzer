# coding: utf-8

import requests
import discord
from discord.ext import commands

bot = discord.Client()
bot_id = None
avatar_url = None
# bot = commands.Bot(command_prefix="?")

sprite_gallery_id = 858107956326826004
bot_log_id = 616239403957747742
infinite_fusion_discord_id = 293500383769133056

bot_log_channel = None

@bot.event
async def on_ready():

    global bot_id
    app_info = await bot.application_info()
    bot_id = app_info.id
    permission_id = "2048"

    global avatar_url
    owner = app_info.owner
    avatar_url = owner.avatar_url_as(static_format='png', size=256)

    global bot_log_channel
    infinite_fusion_discord_server = bot.get_guild(infinite_fusion_discord_id)
    bot_log_channel = infinite_fusion_discord_server.get_channel(bot_log_id)

    print("\n\n")
    print("Ready! bot invite:\n\nhttps://discordapp.com/api/oauth2/authorize?client_id=" + str(bot_id) + "&permissions=" + permission_id + "&scope=bot")
    print("\n\n")

@bot.event
async def on_guild_join(guild):
    print("JOINED THE SERVER :", guild)

@bot.event
async def on_guild_remove(guild):
    print("REMOVED FROM THE SERVER :", guild)

@bot.event
async def on_message(message):
    if(message.channel.id == sprite_gallery_id):
        get_fusion_id(message.content)
        await bot_log_channel.send(content=message.content)
    pass


def get_fusion_id(content):
    print(content.split("."))

"""
@bot.event
async def on_command_error(ctx, error):
    print(ctx.author, ":", ctx.message.content, ":", error)

@bot.command()
async def f(ctx):
    content = ctx.message.content[3:]
    split = content.split(" ")
    poke_head = split[0]
    poke_body = split[1]
    fusion = poke_head + "." + poke_body
    filename = poke_head + "." + poke_body + ".png"
    url = fusion_url + filename

    username = ctx.message.author
    server = ctx.message.guild

    if(requests.get(url).status_code == 200):
        embed = discord.Embed(title=fusion, description="Custom sprite")
        embed.set_footer(text="Aegide", icon_url=avatar_url)
        embed.set_image(url=url)
        print(username, ":", fusion, "(", server, ")")
        await ctx.channel.send(embed=embed)
    else:
        url = japeal_url + poke_head + "/" + filename

        if(requests.get(url).status_code == 200):
            embed = discord.Embed(title=fusion, description="Autogen sprite")
            embed.set_footer(text="Aegide", icon_url=avatar_url)
            embed.set_image(url=url)
            print(username, ":", fusion, "(", server, ")")
            await ctx.channel.send(embed=embed)
        else:
            print(username, ":", fusion, ":", "NOT FOUND", "(", server, ")")
            await ctx.channel.send(content=message_not_found)
"""


# The token of the bot is stored inside a file
token = open("token.txt").read().rstrip()

bot.run(token)