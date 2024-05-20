from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtCore import QSize
from PyQt6.QtGui import QIcon


def show_warning(title: str, message: str) -> None:
    """Spawns a MessageBox with the given title and content."""
    message_box = QMessageBox()
    message_box.setWindowTitle(title)
    message_box.setText(message)
    message_box.setIcon(QMessageBox.Icon.Warning)
    message_box.setWindowIcon(QIcon("Data/barcode-scan.ico"))
    ok_button = message_box.addButton(QMessageBox.StandardButton.Ok)
    ok_button.setFixedSize(QSize(80, 20))
    message_box.exec()
    