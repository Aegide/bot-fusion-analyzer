


from enums import Description, Severity


class Issue():
    description: Description = "MISSING_DESCRIPTION"
    severity: Severity
    def __str__(self) -> str:
        return self.description


class ContentIssue(Issue):
    pass


class MissingSprite(ContentIssue):
    description = "Missing sprite"
    severity = Severity.ignored


class IconSprite(ContentIssue):
    description = "Icon sprite"
    severity = Severity.ignored


class CustomSprite(ContentIssue):
    description = "Custom sprite"
    severity = Severity.ignored


class IncomprehensibleSprite(ContentIssue):
    description = "Incomprehensible sprite"
    severity = Severity.ignored