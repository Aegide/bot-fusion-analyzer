import analysis_content as analysis_content
import analysis_sprite as analysis_sprite
from analysis import Analysis
from discord.message import Message, Attachment


def generate_analysis(
        message: Message,
        specific_attachment: Attachment|None = None,
        is_reply: bool = False):
    analysis = Analysis(message, specific_attachment)
    analysis_content.main(analysis)
    analysis_sprite.main(analysis, is_reply)
    analysis.generate_embed()
    return analysis
