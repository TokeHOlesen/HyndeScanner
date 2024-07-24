from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QKeyEvent
from PyQt6.QtWidgets import QWidget, QLabel, QPushButton, QHBoxLayout, QSpinBox

from DataLoaderClass import DataLoader
from Constants import Fonts, Sizes


class Button(QPushButton):
    """A subclass of QPushButton, adding a returnPressed signal and setting the button's properties."""
    returnPressed = pyqtSignal()

    def __init__(self, text: str):
        super().__init__()
        self.setText(text)
        self.setFixedSize(*Sizes.PRINT_BUTTON)
        self.setFont(Fonts.BUTTON)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            self.returnPressed.emit()
        else:
            super().keyPressEvent(event)


class SpinBox(QSpinBox):
    """A subclass of QSpinBox, adding a returnPressed signal and setting the widget's properties."""
    returnPressed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setMinimum(1)
        self.setMaximum(101)
        self.setValue(1)
        self.setFont(Fonts.AMOUNT)
        self.setFixedSize(*Sizes.NUMBER_ENTRY_BOX)

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            self.returnPressed.emit()
        else:
            super().keyPressEvent(event)


class NumberInputEntryBox(QWidget):
    """A container for a label and a QLineEdit widget, next to each other. Used for manual data entry."""
    def __init__(self, button: Button):
        super().__init__()
        self.target_button = button
        layout = QHBoxLayout(self)
        label = QLabel("Ønsket antal: ")
        label.setFont(Fonts.AMOUNT)
        self.entry_box = SpinBox()
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
    def __init__(self, item_data: DataLoader):
        super().__init__()
        self.item_data = item_data
        self.setObjectName("label_preview")
        self.setFixedSize(*Sizes.LABEL_PREVIEW)
        self.setFont(Fonts.PROMPT)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.reset()

    def update_image_preview(self, barcode: str) -> None:
        """Displays the label for the item with the passed barcode number."""
        label_pixmap = self.item_data.label_pixmaps[barcode]
        label_preview_pixmap = label_pixmap.scaled(
            self.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation)
        self.setPixmap(label_preview_pixmap)

    def reset(self) -> None:
        """Clears the preview display."""
        self.setText("Forhåndsvisning")
