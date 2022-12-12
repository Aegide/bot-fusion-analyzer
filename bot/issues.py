from enums import Description, Severity


class Issue():
    description: Description
    severity: Severity
    mention_aegide: bool = False
    def __str__(self) -> str:
        return self.description.value


class Issues():
    issues: list[Issue] = []
    def __str__(self) -> str:
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
    description = Description.error
    severity = Severity.ignored
    mention_aegide: bool = True


class OutOfDex(Issue):
    description = Description.error
    severity = Severity.refused
    def __init__(self, fusion_id:str) -> None:
        self.fusion_id = fusion_id
