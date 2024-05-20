from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QDialog, QDialogButtonBox

from FontsSizesClass import Sizes


class AboutWindow(QDialog):
    """Displays an 'About' window."""
    def __init__(self, sizes: Sizes):
        super().__init__()
        self.setWindowTitle("Om Hyndescanneren")
        self.setWindowIcon(QIcon(".\\Data\\barcode-scan.ico"))
        layout = QVBoxLayout(self)
        logo = QPixmap("Data/barcode-logo.png")
        logo_label = QLabel()
        logo_label.setPixmap(logo)
        name_label = QLabel("Hyndescanner 2.0")
        author_label = QLabel("© Toke Henrik Olesen")
        github_label = QLabel("<a href='https://github.com/TokeHOlesen/HyndeScanner/'>https://github.com/TokeHOlesen/HyndeScanner/</a>")
        github_label.setOpenExternalLinks(True)
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        button_box.button(QDialogButtonBox.StandardButton.Ok).setFixedSize(*sizes.dialog_box_ok_button)
        button_box.accepted.connect(self.accept)
        layout.addWidget(logo_label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(name_label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(author_label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(github_label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(button_box, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(16)
        layout.setContentsMargins(20, 20, 20, 20)
