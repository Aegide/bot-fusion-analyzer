from pathlib import Path
from discord import Message
import discord
from bot.analyzer import Analysis
from bot.enums import Severity
import tempfile

def main(analysis:Analysis):
    if analysis.severity is Severity.accepted:
        handle_valid_sprite(analysis)



def handle_valid_sprite(analysis:Analysis):


    # file = discord.File(file_path, filename="image.png")

    with tempfile.TemporaryFile() as tmp:
        print(tmp)


    # """
    # if valid_fusion:
    #     results = sprite_analyzer.test_sprite(attachment_url)
    #     if utils.interesting_results(results):
    #         valid_fusion, description, warning, file_name = results
    #         if file_name is not None:
    #             file_path = os.path.join(os.getcwd(), "tmp", file_name)
    #             file = discord.File(file_path, filename="image.png")
    #             message_file = await sprite_stash_channel.send(file=file)
    #             os.remove(file_path)
    #             autogen_url = message_file.attachments[0].url
    # """
