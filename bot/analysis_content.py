import utils
from analysis import Analysis
from enums import Severity
from issues import (CustomSprite, DifferentSprite, EggSprite, IconSprite,
                    IncomprehensibleSprite, MissingFilename, MissingSprite,
                    OutOfDex, FileName)


def exists(value):
    return value is not None


class ContentContext():
    def __init__(self, analysis:Analysis):
        self.filename_fusion_id = utils.extract_fusion_id_from_filename(analysis)
        self.content_fusion_id = utils.extract_fusion_id_from_content(analysis)    

    def have_two_values(self):
        return exists(self.filename_fusion_id) and exists(self.content_fusion_id)
    
    def have_one_value(self):
        return exists(self.filename_fusion_id) or exists(self.content_fusion_id)

    def handle_zero_value(self, analysis:Analysis):
        analysis.severity = Severity.ignored
        if utils.have_egg_in_message(analysis.message):
            analysis.issues.add(EggSprite())
        elif utils.have_icon_in_message(analysis.message):
            analysis.issues.add(IconSprite())
        elif utils.have_custom_in_message(analysis.message):
            analysis.issues.add(CustomSprite())
        elif utils.have_base_in_message(analysis.message):
            analysis.issues.add(CustomSprite())
        else:
            analysis.issues.add(IncomprehensibleSprite())
            filename = utils.get_filename(analysis)
            analysis.issues.add(FileName(filename))
            
    def handle_one_value(self, analysis:Analysis):
        if self.content_fusion_id is not None:
            analysis.severity = Severity.refused
            analysis.issues.add(MissingFilename())
            filename = utils.get_filename(analysis)
            analysis.issues.add(FileName(filename))
            self.handle_dex_verification(analysis, self.content_fusion_id)
        elif self.filename_fusion_id is not None:
            analysis.fusion_id = self.filename_fusion_id
            analysis.autogen_url = utils.get_autogen_url(analysis.fusion_id)
            self.handle_dex_verification(analysis, self.filename_fusion_id)

    def handle_two_values(self, analysis:Analysis):
            if self.filename_fusion_id != self.content_fusion_id:
                self.handle_two_different_values(analysis)
            else:
                self.handle_two_same_values(analysis)
            if self.filename_fusion_id is not None:
                self.handle_dex_verification(analysis, self.filename_fusion_id)

    def handle_two_different_values(self, analysis:Analysis):
        if self.filename_fusion_id is not None and self.content_fusion_id is not None:
            analysis.severity = Severity.refused
            issue = DifferentSprite(self.filename_fusion_id, self.content_fusion_id)
            analysis.issues.add(issue)
            self.handle_dex_verification(analysis, self.content_fusion_id)

    def handle_two_same_values(self, analysis:Analysis):
        if self.filename_fusion_id is not None:
            analysis.fusion_id = self.filename_fusion_id
        if analysis.fusion_id is not None:
            analysis.autogen_url = utils.get_autogen_url(analysis.fusion_id)

    def handle_dex_verification(self, analysis:Analysis, fusion_id:str):
        if utils.is_invalid_fusion_id(fusion_id):
            analysis.severity = Severity.refused
            analysis.issues.add(OutOfDex(fusion_id))


def main(analysis:Analysis):
    if analysis.specific_attachment is None:
        if utils.have_attachment(analysis):
            handle_some_content(analysis)
        else:
            handle_no_content(analysis)
    else:
        handle_some_content(analysis)

def handle_some_content(analysis:Analysis):
    content_context = ContentContext(analysis)
    analysis.attachment_url = utils.get_attachment_url(analysis)
    if content_context.have_two_values():
        content_context.handle_two_values(analysis)
    elif content_context.have_one_value():
        content_context.handle_one_value(analysis)
    else:
        content_context.handle_zero_value(analysis)


def handle_no_content(analysis:Analysis):
    analysis.severity = Severity.ignored
    analysis.issues.add(MissingSprite())

