from discord import Embed, Message
import discord
from issues import Issue
import utils
from enums import Description, DiscordColour, Title
import analysis_content


class Analysis:
    issues: list[Issue] = []

    def generate_embed(self, message:Message):
        pass


async def generate_analysis(message:Message):
    analysis = Analysis()

    analysis_content.main(analysis, message)
    # analysis_sprite.main(analysis, message)

    analysis.generate_embed(message)


    # valid_fusion, description, attachment_url, autogen_url, fusion_id, warning = extract_data(message)
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
    # embed = create_embed(valid_fusion, description, message.jump_url, fusion_id, warning)
    # author_avatar = utils.get_display_avatar(message.author)
    # embed.set_author(name=message.author.name, icon_url=author_avatar.url)
    # embed.set_footer(text=message.content)
    # embed = apply_display_mode(embed, attachment_url, autogen_url)
    # return embed, warning, valid_fusion, fusion_id


    return analysis

def apply_display_mode(embed, attachment_url, autogen_url):
    if attachment_url:
        embed.set_thumbnail(url=attachment_url)
    if autogen_url:
        embed.set_image(url=autogen_url)
    return embed


def create_embed(valid_fusion, description, jump_url, fusion_id, warning):
    if valid_fusion:
        title = f"__{Title.accepted.value} : {fusion_id}__"
        colour = DiscordColour.green.value
    else:
        if warning is not None:
            title = f"__{Title.refused.value} : {description}__\n{warning}"
            colour = DiscordColour.red.value
        else:
            title = f"__{Title.ignored.value} :  {description}__"
            colour = DiscordColour.orange.value

    return discord.Embed(title=title, colour=colour, description="[Link to message](" + jump_url + ")")


def extract_data(message):
    valid_fusion = False
    description = Description.error.value
    autogen_url = None
    fusion_id = None
    warning = None
    attachment_url = None
    
    # Existing file
    if utils.have_attachment(message):
        attachment_url = utils.get_attachment_url(message)
        filename_fusion_id = utils.extract_fusion_id_from_filename(message)
        content_fusion_id = utils.extract_fusion_id_from_content(message)

        if filename_fusion_id is not None and content_fusion_id is not None:
            autogen_url, valid_fusion, fusion_id, description, warning = handle_two_values(filename_fusion_id, content_fusion_id)

        elif filename_fusion_id is not None or content_fusion_id is not None:
            autogen_url, valid_fusion, fusion_id, description, warning = handle_one_value(filename_fusion_id, content_fusion_id)
        
        else:
            description = handle_zero_value(message)
    
    # Missing file + spoilers
    else:
        description = Description.missing_file.value
    
    # Check fusion id
    valid_fusion, autogen_url, description, warning = handle_verification(fusion_id, valid_fusion, autogen_url, description, warning)

    return valid_fusion, description, attachment_url, autogen_url, fusion_id, warning


def handle_zero_value(message):
    if utils.have_icon_in_message(message):
        description = Description.icon.value
    elif utils.have_custom_in_message(message):
        description = Description.custom.value
    elif utils.have_base_in_message(message):
        description = Description.base.value
    else:
        description = Description.missing_fusion_id.value
    return description


def handle_two_values(filename_fusion_id, content_fusion_id):
    autogen_url = utils.get_autogen_url(filename_fusion_id)
    warning = None
    valid_fusion = False
    
    # Same values
    if filename_fusion_id == content_fusion_id:
        valid_fusion = True
        fusion_id = filename_fusion_id
        description = filename_fusion_id
    # Different values
    else:
        fusion_id = filename_fusion_id
        description = Description.different_fusion_id.value
        warning = f"{filename_fusion_id} =/= {content_fusion_id}"
    return autogen_url, valid_fusion, fusion_id, description, warning


def handle_one_value(filename_fusion_id, content_fusion_id):
    valid_fusion = False
    warning = None

    # Value from file
    if filename_fusion_id is not None:
        valid_fusion = True
        fusion_id = filename_fusion_id
        description = filename_fusion_id
        autogen_url = utils.get_autogen_url(filename_fusion_id)
    
    # Value from text
    else:
        fusion_id = content_fusion_id
        description = Description.missing_file_name.value
        autogen_url = utils.get_autogen_url(content_fusion_id)
        warning = f'File name should be "{content_fusion_id}.png"'
    
    return autogen_url, valid_fusion, fusion_id, description, warning


def handle_verification(fusion_id:str|None, valid_fusion, autogen_url, description, warning):
    if fusion_id is not None:
        if utils.is_invalid_fusion_id(fusion_id):
            valid_fusion = False
            autogen_url = None
            description = Description.invalid_fusion_id.value
            warning = f"{fusion_id} is not in the IF Pokedex"
    return valid_fusion, autogen_url, description, warning




def main():
    analysis = Analysis()

    print(analysis)
    print(analysis.issues)


main()
