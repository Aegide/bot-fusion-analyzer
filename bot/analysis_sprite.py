from PIL import Image
import requests

from bot.analyzer import Analysis
from bot.enums import Severity
from discord import Message

from bot.issues import OutOfDex

VALID_SIZE = (288,288)


class SpriteContext():
    def __init__(self, message:Message):
        first_attachment = message.attachments[0].url
        raw_data = requests.get(first_attachment, stream=True).raw
        self.image = Image.open(raw_data)

        




def main(analysis:Analysis):
    if analysis.severity is Severity.accepted:
        handle_valid_sprite(analysis)



def handle_valid_sprite(analysis:Analysis):
    content_context = SpriteContext(analysis.message)
    size = content_context.image.size
    if size != VALID_SIZE:
        analysis.severity = Severity.refused
        analysis.issues.add(OutOfDex(size))




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
