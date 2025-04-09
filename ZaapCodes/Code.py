class Code:
    title = ""
    short_description = ""
    full_description = ""
    source_link = ""

    def __init__(
        self,
        title: str=title,
        short_description: str=short_description,
        full_description: str=full_description,
        source_link: str=source_link
    ):
        self.title = title
        self.short_description = short_description
        self.full_description = full_description
        self.source_link = source_link