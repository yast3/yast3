"""Entry point for the TUI application."""

from mast.core.i18n import init_i18n
from mast.tui.main_window import MainWindow


def main() -> int:
    # Initialize internationalization
    init_i18n()

    app = MainWindow()
    return app.run()


if __name__ == "__main__":
    raise SystemExit(main())