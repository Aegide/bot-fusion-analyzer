from io import BytesIO

import utils
from discord.colour import Colour
from discord.embeds import Embed
from discord.file import File
from discord.message import Attachment, Message
from enums import DiscordColour, Severity
from issues import Issues
from PIL.Image import Image


DICT_SEVERITY_COLOUR = {
    Severity.accepted : DiscordColour.green,
    Severity.ignored : DiscordColour.orange,
    Severity.controversial : DiscordColour.pink,
    Severity.refused : DiscordColour.red
}


class Analysis:
    message: Message
    issues: Issues
    severity: Severity
    embed: Embed
    fusion_id: str = "DEFAULT_VALUE"

    autogen_url: str|None = None
    attachment_url: str|None = None
    specific_attachment: Attachment|None = None

    size_issue: bool = False

    transparency_issue: bool = False
    transparency_image: Image
    transparency_embed: Embed

    half_pixels_issue: bool = False
    half_pixels_image: Image
    half_pixels_embed: Embed

    def __init__(self, message:Message, specific_attachment:Attachment|None) -> None:
        self.message = message
        self.specific_attachment = specific_attachment
        self.issues = Issues()
        self.severity = Severity.accepted

    def generate_embed(self):
        self.embed = Embed()
        self.apply_title()
        self.apply_description()
        self.apply_colour()
        self.apply_author()
        self.apply_footer()
        self.apply_image()
        self.apply_thumbnail()
        self.handle_bonus_embed()

    def generate_transparency_file(self):
        if self.transparency_image is None:
            raise RuntimeError()
        bytes = BytesIO()
        self.transparency_image.save(bytes, format="PNG")
        bytes.seek(0)
        return File(bytes, filename="image.png")

    def generate_half_pixels_file(self):
        if self.half_pixels_image is None:
            raise RuntimeError()
        bytes = BytesIO()
        self.half_pixels_image.save(bytes, format="PNG")
        bytes.seek(0)
        return File(bytes, filename="image.png")

    def handle_bonus_embed(self):
        if self.transparency_issue is True:
            self.transparency_embed = get_bonus_embed(DiscordColour.pink.value)
        if self.half_pixels_issue is True:
            self.half_pixels_embed = get_bonus_embed(DiscordColour.red.value)

    def apply_title(self):
        if self.severity == Severity.accepted:
            self.embed.title = f"__{self.severity.value}: {self.fusion_id}__\n{str(self.issues)}"
        else:
            self.embed.title = f"__{self.severity.value}:__\n{str(self.issues)}"

    def apply_colour(self):
        self.embed.colour = DICT_SEVERITY_COLOUR.get(self.severity, DiscordColour.gray).value

    def apply_description(self):
        self.embed.description = f"[Link to message]({self.message.jump_url})"

    def apply_author(self):
        author_avatar = utils.get_display_avatar(self.message.author)
        self.embed.set_author(name=self.message.author.name, icon_url=author_avatar.url)

    def apply_footer(self):
        self.embed.set_footer(text=self.message.content)

    def apply_image(self):
        # TODO : uncomment this when "get_autogen_url" works
        # if self.autogen_url is not None:
        #     self.embed.set_image(url=self.autogen_url)
        pass

    def apply_thumbnail(self):
        if self.attachment_url is not None:
            self.embed.set_thumbnail(url=self.attachment_url)

def get_bonus_embed(discord_colour:Colour):
    bonus_embed = Embed()
    bonus_embed.colour = discord_colour
    bonus_embed.set_image(url="attachment://image.png")
    return bonus_embed

def generate_bonus_file(image:Image):
    if image is None:
        raise RuntimeError()
    io_bytes = BytesIO()
    image.save(io_bytes, format="PNG")
    io_bytes.seek(0)
    return File(io_bytes, filename="image.png")
