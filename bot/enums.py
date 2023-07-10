from enum import Enum

import discord


class Description(str, Enum):
    missing_file        = "Missing sprite"
    missing_file_name   = "Missing file name"
    missing_fusion_id   = "Unable to identify fusion sprite"
    different_fusion_id = "Different ID"
    colour_excess       = "Too many colours"
    transparency_amount = "Transparency"
    half_pixels_amount  = "Half-pixels"
    colour_amount       = "Colours"
    file_name           = "Filename"
    invalid_fusion_id   = "Invalid fusion ID"
    sprite_error        = "Invalid sprite"
    invalid_size        = "Invalid size"
    icon                = "Icon sprite"
    custom              = "Custom sprite"
    egg                 = "Egg sprite"
    incomprehensible    = "Incomprehensible name"
    test                = "Description test"
    no_transparency     = "Missing transparency"
    aseprite_user       = "Aseprite user detected"
    graphics_gale_user  = "GraphicsGale user detected"


class Severity(Enum):
    accepted        = "Valid"
    ignored         = "Ignored"
    controversial   = "Controversial"
    refused         = "Invalid"


class DiscordColour(Enum):
    green   = discord.Colour(0x2ecc71)
    orange  = discord.Colour(0xe67e22)
    red     = discord.Colour(0xe74c3c)
    gray    = discord.Colour(0xcdcdcd)
    pink    = discord.Colour(0xff00ff)
