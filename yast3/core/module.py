"""Base module class for YaST3 modules."""

from textual.screen import Screen


class Module:
    """Base class for YaST3 modules."""

    name: str
    icon_names: tuple[str, ...]
    emoji: str

    def __init__(self, name: str, icon_names: tuple[str, ...], emoji: str = "⚙️"):
        self.name = name
        self.icon_names = icon_names
        self.emoji = emoji

    def launch(self) -> None:
        """Launch the module window (deprecated, use create_window)."""
        raise NotImplementedError("Module launch not implemented.")

    def create_window(self) -> Screen | None:
        """Create and return the module window screen.

        Returns:
            A Screen instance, or None if the module cannot be launched.
        """
        raise NotImplementedError("Module window creation not implemented.")
