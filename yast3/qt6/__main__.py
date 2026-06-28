"""Entry point for the Qt6 GUI application."""

from PySide6.QtWidgets import QApplication

from yast3.core.i18n import init_i18n
from yast3.qt6.main_window import MainWindow


def main() -> int:
    # Initialize internationalization
    init_i18n()

    app = QApplication.instance() or QApplication([])
    app.setApplicationName("YaST3")
    app.setDesktopFileName("yast3-qt6")

    window = MainWindow()
    window.show()

    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())