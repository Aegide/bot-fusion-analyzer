from enums import Description, Severity


class Issue():
    description: Description
    severity: Severity
    def __str__(self) -> str:
        return self.description.value


class Issues():
    issues: list[Issue]
    def __init__(self):
        self.issues = []
    def __str__(self) -> str:
        if len(self.issues) == 1:
            result = str(self.issues[0])
        else:
            result = ""
            for issue in self.issues:
                result += f"- {issue}\n"
        return result
    def add(self, issue:Issue):
        self.issues.append(issue)


class DifferentSprite(Issue):
    description = Description.different_fusion_id
    severity = Severity.refused
    def __init__(self, filename_fusion_id:str, content_fusion_id:str) -> None:
        self.filename_fusion_id = filename_fusion_id
        self.content_fusion_id = content_fusion_id
    def __str__(self) -> str:
        return f"{self.description.value} ({self.filename_fusion_id}) ({self.content_fusion_id})"


class EggSprite(Issue):
    description = Description.egg
    severity = Severity.ignored


class MissingFilename(Issue):
    description = Description.missing_file_name
    severity = Severity.refused


class MissingSprite(Issue):
    description = Description.missing_file
    severity = Severity.ignored


class IconSprite(Issue):
    description = Description.icon
    severity = Severity.ignored


class CustomSprite(Issue):
    description = Description.custom
    severity = Severity.ignored


class IncomprehensibleSprite(Issue):
    description = Description.incomprehensible
    severity = Severity.ignored


class OutOfDex(Issue):
    description = Description.invalid_fusion_id
    severity = Severity.refused
    def __init__(self, fusion_id:str) -> None:
        self.fusion_id = fusion_id
    def __str__(self) -> str:
        return f"{self.description.value} ({self.fusion_id})"


class InvalidSize(Issue):
    description = Description.invalid_size
    severity = Severity.refused
    def __init__(self, size:tuple) -> None:
        self.size = size
    def __str__(self) -> str:
        return f"{self.description.value} {self.size}"


class FileName(Issue):
    description = Description.file_name
    severity = Severity.accepted
    def __init__(self, filename:str) -> None:
        self.filename = filename
    def __str__(self) -> str:
        return f"{self.description.value} : {self.filename}"


class ColorAmount(Issue):
    description = Description.colour_amount
    severity = Severity.accepted
    def __init__(self, amount:int) -> None:
        self.amount = amount
    def __str__(self) -> str:
        return f"{self.description.value} : {self.amount}"


class ColorExcess(Issue):
    description = Description.colour_excess
    severity = Severity.refused
    def __init__(self, maximum:int) -> None:
        self.maximum = maximum
    def __str__(self) -> str:
        return f"{self.description.value} (max: {self.maximum})"


class ColorOverExcess(Issue):
    description = Description.colour_excess
    severity = Severity.refused
    def __init__(self, maximum:int) -> None:
        self.maximum = maximum
    def __str__(self) -> str:
        return f"{self.description.value} (it's over {self.maximum})"


class MissingTransparency(Issue):
    description = Description.no_transparency
    severity = Severity.refused


class AsepriteUser(Issue):
    description = Description.aseprite_user
    severity = Severity.accepted
    def __init__(self, ratio:float) -> None:
        self.ratio = int(ratio)
    def __str__(self) -> str:
        return f"{self.description.value} (r{self.ratio})"


class GraphicsGaleUser(Issue):
    description = Description.graphics_gale_user
    severity = Severity.accepted


class TransparencyAmount(Issue):
    description = Description.transparency_amount
    severity = Severity.controversial
    def __init__(self, amount:int) -> None:
        self.amount = amount
    def __str__(self) -> str:
        return f"{self.description.value} : {self.amount}"


class SimilarityAmount(Issue):
    description = Description.similarity_amount
    severity = Severity.controversial
    def __init__(self, amount:int, color_color_dict:dict) -> None:
        self.amount = amount
        self.color_color_dict = color_color_dict
    def __str__(self) -> str:
        text = f"{self.description.value} : {self.amount}"
        # for key, value in self.color_color_dict:
        #     text += f"* {key} :: {value}\n"
        return text

class HalfPixelsAmount(Issue):
    description = Description.half_pixels_amount
    severity = Severity.refused
    def __init__(self, amount:int) -> None:
        self.amount = amount
    def __str__(self) -> str:
        return f"{self.description.value} : {self.amount}"
