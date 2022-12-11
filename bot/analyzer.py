from discord import Message
from bot.analysis import Analysis
import bot.analysis_content as analysis_content
import bot.analysis_sprite as analysis_sprite


def generate_analysis(message:Message):
    analysis = Analysis(message)
    analysis_content.main(analysis)
    analysis_sprite.main(analysis)
    analysis.generate_embed()
    return analysis
