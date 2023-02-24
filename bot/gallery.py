from discord.message import Message

from constants import ID_CHANNEL_GALLERY_PIF


def is_sprite_gallery(message:Message):
    return message.channel.id == ID_CHANNEL_GALLERY_PIF
