from discord import Message
from analysis import Analysis
import analysis_content as analysis_content
import analysis_sprite as analysis_sprite


def generate_analysis(message:Message):
    analysis = Analysis(message)
    analysis_content.main(analysis)
    analysis_sprite.main(analysis)
    analysis.generate_embed()
    return analysis
