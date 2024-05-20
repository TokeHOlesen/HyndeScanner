from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QKeyEvent, QPixmap
from PyQt6.QtWidgets import QWidget, QLabel, QPushButton, QHBoxLayout, QSpinBox

from FontsSizesClass import Fonts, Sizes


class Button(QPushButton):
    """A subclass of QPushButton, adding a returnPressed signal and setting the button's properties."""
    returnPressed = pyqtSignal()

    def __init__(self, text: str, fonts: Fonts, sizes: Sizes):
        super().__init__()
        self.setText(text)
        self.setFixedSize(*sizes.print_button)
        self.setFont(fonts.button)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            self.returnPressed.emit()
        else:
            super().keyPressEvent(event)


class SpinBox(QSpinBox):
    """A subclass of QSpinBox, adding a returnPressed signal and setting the widget's properties."""
    returnPressed = pyqtSignal()

    def __init__(self, fonts: Fonts, sizes: Sizes):
        super().__init__()
        self.setMinimum(1)
        self.setMaximum(101)
        self.setValue(1)
        self.setFont(fonts.amount)
        self.setFixedSize(*sizes.number_entry_box)

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            self.returnPressed.emit()
        else:
            super().keyPressEvent(event)


class NumberInputEntryBox(QWidget):
    """A container for a label and a QLineEdit widget, next to each other. Used for manual data entry."""
    def __init__(self, fonts: Fonts, sizes: Sizes, button: Button):
        super().__init__()
        self.target_button = button
        layout = QHBoxLayout(self)
        label = QLabel("Ønsket antal: ")
        label.setFont(fonts.amount)
        self.entry_box = SpinBox(fonts, sizes)
        self.entry_box.returnPressed.connect(self.move_focus_to_button)
        layout.addWidget(label)
        layout.addWidget(self.entry_box)

    def move_focus_to_button(self) -> None:
        """Moves focus to the associated button (normally the tab's 'Print' button)."""
        self.target_button.setFocus()

    @property
    def value(self) -> int:
        """Returns the contents of the number entry box."""
        return int(self.entry_box.text())

    def reset(self) -> None:
        """Resets the number entry box to 1 (the lowest allowed value)."""
        self.entry_box.setValue(1)


class LabelPreview(QLabel):
    """Implements a widget showing a preview of the label to be printed."""
    def __init__(self, fonts: Fonts, sizes: Sizes):
        super().__init__()
        self.setObjectName("label_preview")
        self.setFixedSize(*sizes.label_preview)
        self.setFont(fonts.prompt)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.reset()

    def update_image_preview(self, barcode: str) -> None:
        """Displays the label for the item with the passed barcode number."""
        path_to_png = f"Data/PNG/{barcode}.png"
        label_preview_pix = QPixmap(path_to_png).scaled(
            self.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation)
        self.setPixmap(label_preview_pix)

    def reset(self) -> None:
        """Clears the preview display."""
        self.setText("Forhåndsvisning")
