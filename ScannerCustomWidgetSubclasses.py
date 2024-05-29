from PyQt6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QGridLayout,
    QLabel,
    QSpacerItem,
    QSizePolicy,
    QVBoxLayout,
    QWidget
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon

from CushionClass import Cushion
from DataLoaderClass import DataLoader
from FontsSizesClass import Fonts, Sizes


class DataLabel(QLabel):
    """A subclass of QLabel with a fixed font for displaying item data."""
    def __init__(self, fonts: Fonts, text=""):
        super().__init__(text)
        self.setFont(fonts.item_data)


class ItemDataDisplayBox(QWidget):
    """Displays the item's data, within a grid layout."""
    def __init__(self, fonts: Fonts, sizes: Sizes):
        super().__init__()
        layout = QGridLayout(self)
        layout.setColumnMinimumWidth(1, sizes.data_box_column)
        item_name_label = DataLabel(fonts, "Varenavn:")
        self.item_name_data = DataLabel(fonts)
        color_label = DataLabel(fonts, "Farve:")
        self.color_data = DataLabel(fonts)
        old_number_label = DataLabel(fonts, "Gammelt nummer:")
        self.old_number_data = DataLabel(fonts)
        new_number_label = DataLabel(fonts, "Nyt nummer:")
        self.new_number_data = DataLabel(fonts)
        ean13_label = DataLabel(fonts, "Stregkode:")
        self.ean13_data = DataLabel(fonts)
        layout.addWidget(item_name_label, 0, 0)
        layout.addWidget(self.item_name_data, 0, 1)
        layout.addWidget(color_label, 1, 0)
        layout.addWidget(self.color_data, 1, 1)
        layout.addWidget(old_number_label, 2, 0)
        layout.addWidget(self.old_number_data, 2, 1)
        layout.addWidget(new_number_label, 3, 0)
        layout.addWidget(self.new_number_data, 3, 1)
        layout.addWidget(ean13_label, 4, 0)
        layout.addWidget(self.ean13_data, 4, 1)
        layout.addItem(QSpacerItem(70, 10, QSizePolicy.Policy.Maximum), 0, 2)
        layout.setSpacing(0)

    def load_data(self, item_data: Cushion, scanned_barcode: str) -> None:
        """Loads a Cushion object and the scanned barcode and displays their data."""
        self.item_name_data.setText(item_data.item_name)
        self.color_data.setText(item_data.color)
        self.old_number_data.setText(item_data.old_number)
        self.new_number_data.setText(item_data.new_number)
        # If the scanned barcode and the item barcode don't match, shows a message that the barcode has been corrected.
        if scanned_barcode == item_data.ean_13:
            self.ean13_data.setText(item_data.ean_13)
        else:
            self.ean13_data.setText(f"{scanned_barcode} rettes til {item_data.ean_13}")

    def reset(self) -> None:
        """Clears the data display box."""
        self.item_name_data.clear()
        self.color_data.clear()
        self.old_number_data.clear()
        self.new_number_data.clear()
        self.ean13_data.clear()


class MultipleBarcodeSelection(QDialog):
    """
    Spawns a dialog box asking the user to identify the scanned item.
    This is necessary if several different item types have been labeled with the same barcode by mistake.
    """
    def __init__(self, barcode_list: list, items: DataLoader, sizes: Sizes) -> None:
        super().__init__()
        self.setWindowIcon(QIcon(".\\Data\\barcode-scan.ico"))
        # Disables the window closing "X" - the window can't be dismissed without selecting an item.
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowCloseButtonHint)
        self.item_data = items
        combobox_entries = []
        # Identifies the items' names by the supplied barcodes, then compares those names to the ones in
        # items.new_number_combobox_entry_list; If there's a match, adds the text to this window's combobox.
        for item_text in items.new_number_combobox_entry_list:
            for barcode in barcode_list:
                item = self.item_data.get_item_by_barcode(barcode)
                # Ignores unknown barcodes - this is useful if the same wrong barcode has been used for several items.
                # An unknown barcode will not show up in the combobox.
                if item is None:
                    continue
                if item.new_number in item_text:
                    combobox_entries.append(item_text)
        self.setWindowTitle("Vælg vare")
        layout = QVBoxLayout(self)
        label = QLabel("Der er flere varer, der pga. fejl er mærket med denne stregkode.\n"
                       "Angiv venligst den scannede varetype:")
        self.combobox = QComboBox()
        self.combobox.addItems(combobox_entries)
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        button_box.button(QDialogButtonBox.StandardButton.Ok).setFixedSize(*sizes.dialog_box_ok_button)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(label)
        layout.addStretch(1)
        layout.addWidget(self.combobox)
        layout.addWidget(button_box)
        layout.setSpacing(16)
        layout.setContentsMargins(20, 20, 20, 20)

    def get_selected_item_barcode(self) -> str:
        """Returns the barcode of the selected item."""
        # Gets the new item number from the currently selected combobox entry.
        item_number = self.combobox.currentText().split(" ")[0]
        # Returns the value of .ean_13 property of the object where the .new_number property matches the selected line.
        for item in self.item_data.cushions:
            if item_number == item.new_number:
                return item.ean_13
