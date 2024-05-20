from PyQt6.QtWidgets import QWidget, QLabel, QHBoxLayout, QLineEdit, QRadioButton, QButtonGroup

from CommonCustomWidgetSubclasses import Button
from FontsSizesClass import Fonts, Sizes


class SearchEntryBox(QWidget):
    """
    A search box consiting of a QLineEdit and a button to clear its contents.
    Used to search for items by their names in manual mode.
    """
    def __init__(self, fonts: Fonts, sizes: Sizes):
        super().__init__()
        layout = QHBoxLayout(self)
        label = QLabel("Søg:")
        label.setFont(fonts.combobox)
        self.search_box = QLineEdit()
        self.search_box.setFixedWidth(sizes.search_box_width)
        self.search_box.textChanged.connect(self.update_clear_button_state)
        self.clear_button = Button("Ryd", fonts, sizes)
        self.clear_button.setFont(fonts.combobox)
        self.clear_button.setFixedSize(*sizes.clear_button)
        self.clear_button.clicked.connect(self.clear_entry_box)
        self.clear_button.setEnabled(False)
        layout.addWidget(label)
        layout.addWidget(self.search_box)
        layout.addWidget(self.clear_button)

    def clear_entry_box(self) -> None:
        """Clears the search box."""
        self.search_box.clear()

    def update_clear_button_state(self) -> None:
        """Sets the 'Clear' buttons active state to disabled if the search box is empty."""
        self.clear_button.setDisabled(self.search_box.text() == "")


class OldNewRadioButtons(QWidget):
    """Implements a widget holding two radio buttons to choose between old and new numbers."""
    def __init__(self):
        super().__init__()
        self.old_radio_button = QRadioButton("Gamle varenumre")
        self.new_radio_button = QRadioButton("Nye varenumre")
        self.old_new_radio_btns = QButtonGroup()
        self.old_new_radio_btns.addButton(self.old_radio_button)
        self.old_new_radio_btns.addButton(self.new_radio_button)
        self.old_radio_button.setChecked(True)
        self.layout = QHBoxLayout(self)
        self.layout.addWidget(self.old_radio_button)
        self.layout.addWidget(self.new_radio_button)
