from enum import Enum

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
    error = "Please contact Aegide"
    test = "Description test"