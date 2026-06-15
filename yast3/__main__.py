from PySide6.QtWidgets import QApplication

from yast3.main_window import MainWindow
from yast3.i18n import init_i18n


def main() -> int:
    # Initialize internationalization
    init_i18n()

    app = QApplication.instance() or QApplication([])
    app.setApplicationName("YaST3")

    window = MainWindow()
    window.show()

    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
