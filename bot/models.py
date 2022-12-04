from discord import Guild
from pydantic import BaseModel

from discord.channel import TextChannel as Channel


class ServerContext(BaseModel):
    server: Guild
    gallery: Channel
    logs: Channel
    spritework: Channel


class GlobalContext(BaseModel):
    aegide: ServerContext
    pif: ServerContext




