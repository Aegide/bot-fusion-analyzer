from enum import Enum
import discord

class Description(Enum):
    missing_file = "Missing sprite"
    missing_file_name = "Missing file name"
    missing_fusion_id = "Unable to identify fusion sprite"
    different_fusion_id = "Different fusion IDs"
    invalid_fusion_id = "Invalid fusion ID"
    sprite_error = "Invalid sprite"
    sprite_issue = "Controversial sprite"
    icon = "Fusion icon"
    custom = "Custom sprite"
    base = "Custom base"
    error = "Please contact Aegide"
    test = "Description test"

class Title(Enum):
    ignored = "Ignored"
    accepted = "Accepted"
    refused = "Refused"

class Colour(Enum):
    green = discord.Colour(0x2ecc71)
    orange = discord.Colour(0xe67e22)
    red = discord.Colour(0xe74c3c)
    gray = discord.Colour(0xcdcdcd)