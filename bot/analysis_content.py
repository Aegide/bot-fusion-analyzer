from discord import Message
from issues import CustomSprite, IncomprehensibleSprite, MissingSprite
import utils
from analyzer import Analysis


def exists(value):
    return value is not None


class ContentContext():
    def __init__(self, message:Message):
        self.filename_fusion_id = utils.extract_fusion_id_from_filename(message)
        self.content_fusion_id = utils.extract_fusion_id_from_content(message)    

    def have_two_values(self):
        return exists(self.filename_fusion_id) and exists(self.content_fusion_id)
    
    def have_two_values(self):
        return exists(self.filename_fusion_id) or exists(self.content_fusion_id)


def main(analysis:Analysis, message:Message):
    if utils.have_attachment(message):
        handle_some_content(analysis, message)
    else:
        handle_no_content(analysis)


def handle_some_content(analysis:Analysis, message:Message):
    content_context = ContentContext(message)
    if content_context.have_two_values():
        handle_two_values()
    elif content_context.have_one_value():
        handle_one_value()
    else:
        handle_zero_value(analysis)



def handle_no_content(analysis:Analysis):
    analysis.issues.append(MissingSprite())


def handle_two_values():
    pass



def handle_one_value():
    pass


def handle_zero_value(analysis:Analysis, message:Message):
    if utils.have_icon_in_message(message):
        analysis.issues.append(MissingSprite())
    elif utils.have_custom_in_message(message):
        analysis.issues.append(CustomSprite())
    elif utils.have_base_in_message(message):
        analysis.issues.append(CustomSprite())
    else:
        analysis.issues.append(IncomprehensibleSprite())





