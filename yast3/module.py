class Module:
    name: str
    icon_names: tuple[str, ...]

    def __init__(self, name: str, icon_names: tuple[str, ...]):
        self.name = name
        self.icon_names = icon_names
