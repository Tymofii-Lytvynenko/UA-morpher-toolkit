"""Offline table UI for bulk Ukrainian full-name inflection (PySide6)."""

from __future__ import annotations

import sys

from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QColor, QKeySequence
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QHeaderView,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from batch import CASE_NAMES, InflectionRow, inflect_rows, parse_clipboard, results_to_clipboard


class ClipboardTable(QTableWidget):
    """Make Ctrl+V replace the input range with an Excel clipboard paste."""

    paste_requested = Signal()

    def keyPressEvent(self, event):
        if event.matches(QKeySequence.StandardKey.Paste):
            self.paste_requested.emit()
            event.accept()
            return
        super().keyPressEvent(event)


class InflectionWorker(QThread):
    completed = Signal(object)
    failed = Signal(str)

    def __init__(self, names: list[str], case: str, uppercase_surname: bool):
        super().__init__()
        self.names = names
        self.case = case
        self.uppercase_surname = uppercase_surname

    def run(self):
        try:
            # Initialize the morphology engine within the worker thread.
            from morpher import NameMorpher, SentenceMorpher

            processor = NameMorpher(SentenceMorpher())
            results = inflect_rows(
                self.names,
                self.case,
                processor.morph_name,
                uppercase_surname=self.uppercase_surname,
            )
            self.completed.emit(results)
        except Exception as exc:
            self.failed.emit(f"{type(exc).__name__}: {exc}")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Відмінювання ПІБ — масова обробка")
        self.resize(950, 610)
        self._results: list[InflectionRow] | None = None
        self._worker: InflectionWorker | None = None
        self._setup_ui()

    def _setup_ui(self):
        root = QWidget(self)
        layout = QVBoxLayout(root)

        hint = QLabel(
            "Скопіюйте з Excel один стовпець із ПІБ або три стовпці "
            "(Прізвище / Ім’я / По батькові). Ctrl+V — вставити."
        )
        hint.setWordWrap(True)
        layout.addWidget(hint)

        toolbar = QHBoxLayout()
        self.paste_button = QPushButton("Вставити з буфера")
        self.paste_button.clicked.connect(self.paste_names)
        toolbar.addWidget(self.paste_button)

        toolbar.addWidget(QLabel("Відмінок:"))
        self.case_selector = QComboBox()
        for code, title in CASE_NAMES.items():
            self.case_selector.addItem(title, userData=code)
        self.case_selector.setCurrentIndex(1)  # Родовий
        self.case_selector.currentIndexChanged.connect(self.invalidate_results)
        toolbar.addWidget(self.case_selector)

        self.uppercase_checkbox = QCheckBox("Прізвище великими літерами")
        self.uppercase_checkbox.setChecked(False)
        self.uppercase_checkbox.toggled.connect(self.invalidate_results)
        toolbar.addWidget(self.uppercase_checkbox)
        toolbar.addStretch()
        layout.addLayout(toolbar)

        self.table = ClipboardTable(0, 2)
        self.table.setHorizontalHeaderLabels(["ПІБ — оригінал", "Результат"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.ExtendedSelection)
        self.table.setAlternatingRowColors(True)
        self.table.setSortingEnabled(False)
        self.table.paste_requested.connect(self.paste_names)
        self.table.itemChanged.connect(self._on_item_changed)
        layout.addWidget(self.table)

        actions = QHBoxLayout()
        self.process_button = QPushButton("Відмінити всі")
        self.process_button.setDefault(True)
        self.process_button.clicked.connect(self.process_names)
        actions.addWidget(self.process_button)

        self.copy_button = QPushButton("Скопіювати всі результати")
        self.copy_button.setEnabled(False)
        self.copy_button.clicked.connect(self.copy_results)
        actions.addWidget(self.copy_button)

        self.clear_button = QPushButton("Очистити")
        self.clear_button.clicked.connect(self.clear_rows)
        actions.addWidget(self.clear_button)
        actions.addStretch()
        layout.addLayout(actions)

        self.status = QLabel("Дані не завантажені")
        layout.addWidget(self.status)
        self.setCentralWidget(root)

    def _on_item_changed(self, item: QTableWidgetItem):
        if item.column() == 0:
            self.invalidate_results()

    def invalidate_results(self, *_):
        self._results = None
        self.copy_button.setEnabled(False)
        self.table.blockSignals(True)
        try:
            for row in range(self.table.rowCount()):
                result_cell = self.table.item(row, 1)
                if result_cell is not None:
                    result_cell.setText("")
                    result_cell.setToolTip("")
                    result_cell.setBackground(QColor(Qt.GlobalColor.transparent))
        finally:
            self.table.blockSignals(False)
        if self.table.rowCount():
            self.status.setText("Дані змінені — натисніть «Відмінити всі»")

    def paste_names(self):
        names = parse_clipboard(QApplication.clipboard().text())
        if not names:
            QMessageBox.information(self, "Буфер порожній", "Скопіюйте діапазон із Excel або список ПІБ.")
            return
        self._set_names(names)

    def _set_names(self, names: list[str]):
        self.table.blockSignals(True)
        try:
            self.table.setRowCount(len(names))
            for row, name in enumerate(names):
                self.table.setItem(row, 0, QTableWidgetItem(name))
                self.table.setItem(row, 1, self._readonly_item(""))
        finally:
            self.table.blockSignals(False)
        self._results = None
        self.copy_button.setEnabled(False)
        self.status.setText(f"Завантажено рядків: {len(names)}. Порядок збережено.")

    @staticmethod
    def _readonly_item(text: str) -> QTableWidgetItem:
        item = QTableWidgetItem(text)
        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        return item

    def _names(self) -> list[str]:
        return [self.table.item(i, 0).text() if self.table.item(i, 0) else "" for i in range(self.table.rowCount())]

    def _busy(self, is_busy: bool):
        for widget in (self.paste_button, self.process_button, self.clear_button, self.case_selector, self.uppercase_checkbox, self.table):
            widget.setEnabled(not is_busy)
        self.copy_button.setEnabled(not is_busy and self._results is not None)

    def process_names(self):
        names = self._names()
        if not names:
            QMessageBox.information(self, "Немає ПІБ", "Спочатку вставте список із буфера.")
            return
        self.invalidate_results()
        self._busy(True)
        self.status.setText(f"Відмінювання {len(names)} рядків…")
        self._worker = InflectionWorker(names, self.case_selector.currentData(), self.uppercase_checkbox.isChecked())
        self._worker.completed.connect(self._show_results)
        self._worker.failed.connect(self._show_error)
        self._worker.finished.connect(self._on_worker_finished)
        self._worker.start()

    def _show_results(self, rows: list[InflectionRow]):
        self._results = rows
        errors = 0
        self.table.blockSignals(True)
        try:
            for index, row in enumerate(rows):
                cell = self.table.item(index, 1)
                cell.setText(row.result)
                if row.error:
                    errors += 1
                    cell.setToolTip(f"Помилка: {row.error}")
                    cell.setBackground(QColor("#ffe6e6"))
        finally:
            self.table.blockSignals(False)
        self.status.setText(f"Готово: {len(rows)} рядків; помилок: {errors}. "
                            "За неоднозначних ПІБ перевіряйте результат вручну.")

    def _show_error(self, message: str):
        self.status.setText("Обробку не виконано")
        QMessageBox.critical(self, "Помилка відмінювання", message)

    def _on_worker_finished(self):
        self._busy(False)
        if self._worker is not None:
            self._worker.deleteLater()
            self._worker = None

    def copy_results(self):
        if self._results is None:
            return
        QApplication.clipboard().setText(results_to_clipboard(self._results))
        self.status.setText(f"Скопійовано {len(self._results)} рядків у тому самому порядку.")

    def clear_rows(self):
        self.table.setRowCount(0)
        self._results = None
        self.copy_button.setEnabled(False)
        self.status.setText("Таблицю очищено")


def main() -> int:
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
