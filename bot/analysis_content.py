from discord import Message
from bot.enums import Severity
from bot.issues import DifferentSprite, EggSprite, IconSprite, MissingFilename, OutOfDex, CustomSprite, IncomprehensibleSprite, MissingSprite
import bot.utils as utils
from bot.analyzer import Analysis


def exists(value):
    return value is not None


class ContentContext():
    def __init__(self, message:Message):
        self.filename_fusion_id = utils.extract_fusion_id_from_filename(message)
        self.content_fusion_id = utils.extract_fusion_id_from_content(message)    

    def have_two_values(self):
        return exists(self.filename_fusion_id) and exists(self.content_fusion_id)
    
    def have_one_value(self):
        return exists(self.filename_fusion_id) or exists(self.content_fusion_id)

    def handle_zero_value(self, analysis:Analysis):
        analysis.severity = Severity.ignored
        if utils.have_egg_in_message(analysis.message):
            analysis.issues.append(EggSprite())
        elif utils.have_icon_in_message(analysis.message):
            analysis.issues.append(IconSprite())
        elif utils.have_custom_in_message(analysis.message):
            analysis.issues.append(CustomSprite())
        elif utils.have_base_in_message(analysis.message):
            analysis.issues.append(CustomSprite())
        else:
            analysis.issues.append(IncomprehensibleSprite())

    def handle_one_value(self, analysis:Analysis):
        if self.filename_fusion_id is None:
            analysis.severity = Severity.refused
            analysis.issues.append(MissingFilename())
        else:
            analysis.fusion_id = self.filename_fusion_id

    def handle_two_values(self, analysis:Analysis):
        if self.filename_fusion_id is not None and self.content_fusion_id is not None:
            if self.filename_fusion_id != self.content_fusion_id:
                analysis.severity = Severity.refused
                issue = DifferentSprite(self.filename_fusion_id, self.content_fusion_id)
                analysis.issues.append(issue)
                self.handle_dex_verification(analysis, self.content_fusion_id)
            else:
                analysis.fusion_id = self.filename_fusion_id
            self.handle_dex_verification(analysis, self.filename_fusion_id)

    def handle_dex_verification(self, analysis:Analysis, fusion_id:str):
        if utils.is_invalid_fusion_id(fusion_id):
            analysis.severity = Severity.refused
            analysis.issues.append(OutOfDex(fusion_id))


def main(analysis:Analysis):
    if utils.have_attachment(analysis.message):
        handle_some_content(analysis)
    else:
        handle_no_content(analysis)


def handle_some_content(analysis:Analysis):
    content_context = ContentContext(analysis.message)
    if content_context.have_two_values():
        content_context.handle_two_values(analysis)
    elif content_context.have_one_value():
        content_context.handle_one_value(analysis)
    else:
        content_context.handle_zero_value(analysis)


def handle_no_content(analysis:Analysis):
    analysis.severity = Severity.ignored
    analysis.issues.append(MissingSprite())
