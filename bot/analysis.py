from io import BytesIO
import utils
from discord.message import Attachment, Message
from discord.embeds import Embed
from discord.file import File
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
    transparency: bool = False
    transparency_image: Image
    transparency_embed: Embed

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
        self.apply_attachment_url()
        self.handle_bonus_embed()

    def gen_transparency_file(self):
        if self.transparency_image is None:
            raise ValueError
        bytes = BytesIO()
        self.transparency_image.save(bytes, format="PNG")
        bytes.seek(0)
        return File(bytes, filename="image.png")

    def handle_bonus_embed(self):
        if self.transparency is True:
            self.transparency_embed = Embed()
            self.transparency_embed.colour = DiscordColour.pink.value
            self.transparency_embed.set_image(url="attachment://image.png")

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
        if self.autogen_url is not None:
            self.embed.set_image(url=self.autogen_url)

    def apply_attachment_url(self):
        if self.attachment_url is not None:
            self.embed.set_thumbnail(url=self.attachment_url)
