"""Searchable QComboBox widget for Qt6 - global reusable component."""

from __future__ import annotations

from PySide6.QtCore import QStringListModel, Qt
from PySide6.QtWidgets import QComboBox, QCompleter, QLineEdit


class SearchableComboBox(QComboBox):
    """A QComboBox with built-in search functionality using QCompleter."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_search()

    def _init_search(self):
        self.setEditable(True)
        self.setInsertPolicy(QComboBox.NoInsert)

        self._source_model = QStringListModel()

        self._completer = QCompleter(self._source_model, self)
        self._completer.setCaseSensitivity(Qt.CaseInsensitive)
        self._completer.setFilterMode(Qt.MatchContains)
        self._completer.setCompletionMode(QCompleter.PopupCompletion)
        self._completer.setMaxVisibleItems(15)

        line_edit = self.lineEdit()
        line_edit.setCompleter(self._completer)

        self.activated.connect(self._on_activated)
        line_edit.editingFinished.connect(self._on_editing_finished)
        line_edit.focusOutEvent = self._on_focus_out
        self._selection_in_progress = False
        self._last_valid_item = ""

    def set_items(self, items):
        """Set the list of items to display."""
        self.clear()
        for item in items:
            self.addItem(item)
        self._source_model.setStringList(items)

    def add_item(self, item):
        """Add a single item to the list."""
        self.addItem(item)
        items = self._source_model.stringList()
        items.append(item)
        self._source_model.setStringList(items)

    def clear_items(self):
        """Clear all items."""
        self.clear()
        self._source_model.setStringList([])

    def current_item(self):
        """Get the currently selected item."""
        return self.currentText()

    def set_current_item(self, item):
        """Set the currently selected item."""
        self._selection_in_progress = True
        idx = self.findText(item)
        if idx >= 0:
            self.setCurrentIndex(idx)
            self.lineEdit().setText(item)
            self._last_valid_item = item
        self._selection_in_progress = False

    def _on_activated(self, idx):
        self._selection_in_progress = True
        if idx >= 0:
            text = self.itemText(idx)
            self.lineEdit().setText(text)
            self._last_valid_item = text
        self._selection_in_progress = False

    def _on_editing_finished(self):
        self._validate_input()

    def _on_focus_out(self, event):
        self._validate_input()
        QLineEdit.focusOutEvent(self.lineEdit(), event)

    def _validate_input(self):
        if self._selection_in_progress:
            return

        current_text = self.lineEdit().text().strip()
        if not current_text:
            return

        idx = self.findText(current_text)
        if idx >= 0:
            self._last_valid_item = current_text
            self.setCurrentIndex(idx)
        else:
            if self._last_valid_item:
                self.lineEdit().setText(self._last_valid_item)
                idx = self.findText(self._last_valid_item)
                if idx >= 0:
                    self.setCurrentIndex(idx)