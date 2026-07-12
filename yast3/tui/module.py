"""Base module class for YaST3 TUI modules."""

from textual.screen import Screen


class Module:
    """Base class for YaST3 TUI modules."""

    name: str
    emoji: str
    experimental: bool = False

    def __init__(self, name: str, emoji: str = "⚙️", experimental: bool = False) -> None:
        self.name = name
        self.emoji = emoji
        self.experimental = experimental

    def create_window(self) -> Screen:
        """Create and return the module window screen.

        Returns:
            A Screen instance.
        """
        raise NotImplementedError("Module window creation not implemented.")
