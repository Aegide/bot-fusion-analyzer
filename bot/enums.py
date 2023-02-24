from enum import Enum

from discord.colour import Colour


class Description(str, Enum):
    missing_file        = "Missing sprite"
    missing_file_name   = "Missing file name"
    missing_fusion_id   = "Unable to identify fusion sprite"
    different_fusion_id = "Different ID"
    colour_excess       = "Too many colours"
    transparency_amount = "Transparency"
    colour_amount       = "Colours"
    file_name           = "Filename"
    invalid_fusion_id   = "Invalid fusion ID"
    sprite_error        = "Invalid sprite"
    invalid_size        = "Invalid size"
    icon                = "Icon sprite"
    custom              = "Custom sprite"
    egg                 = "Egg sprite"
    incomprehensible    = "Incomprehensible sprite"
    test                = "Description test"
    aseprite_user       = "Aseprite user detected"


class Severity(Enum):
    accepted        = "Valid"
    ignored         = "Ignored"
    controversial   = "Controversial"
    refused         = "Invalid"


class DiscordColour(Enum):
    green   = Colour(0x2ecc71)
    orange  = Colour(0xe67e22)
    red     = Colour(0xe74c3c)
    gray    = Colour(0xcdcdcd)
    pink    = Colour(0xff00ff)
