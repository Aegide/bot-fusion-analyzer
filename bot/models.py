from discord import Guild
from discord.channel import TextChannel as Channel


class ServerContext():
    server: Guild
    gallery: Channel
    logs: Channel
    def __init__(self,
            server: Guild,
            gallery: Channel,
            logs: Channel
            ) -> None:
        self.server = server
        self.gallery = gallery
        self.logs = logs


class GlobalContext():
    aegide: ServerContext
    pif: ServerContext
    def __init__(self,
            aegide: ServerContext,
            pif: ServerContext
            ) -> None:
        self.aegide = aegide
        self.pif = pif
