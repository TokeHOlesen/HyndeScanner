from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QLineEdit, QDialog

from CommonCustomWidgetSubclasses import Button, NumberInputEntryBox, LabelPreview
from CushionClass import Cushion
from DataLoaderClass import DataLoader
from FontsSizesClass import Fonts, Sizes
from ScannerCustomWidgetSubclasses import ItemDataDisplayBox, MultipleBarcodeSelection
from PrintingClass import Printing
from PrintLoggerClass import PrintLogger
from warning_messagebox import show_warning


class ScannerTab(QWidget):
    """An interface for entering a barcode and choosing the number of labels to be printed."""
    def __init__(self, fonts: Fonts, sizes: Sizes, item_data: DataLoader, printers: Printing):
        super().__init__()
        layout = QVBoxLayout(self)
        # "Scan an item" label
        scan_prompt_label = QLabel("Scan en stregkode:")
        scan_prompt_label.setFont(fonts.prompt)
        # Scan entry box
        self.scan_entry_box = QLineEdit()
        self.scan_entry_box.setFixedSize(*sizes.scan_entry_box)
        self.scan_entry_box.setFont(fonts.ean13)
        self.scan_entry_box.returnPressed.connect(self.validate_and_set_barcode)
        # Print button
        self.print_button = Button("Print", fonts, sizes)
        self.print_button.returnPressed.connect(self.print)
        self.print_button.clicked.connect(self.print)
        # "Input amount" entry box
        self.number_input_entry_box = NumberInputEntryBox(fonts, sizes, self.print_button)
        # Item data display box
        self.item_data_display_box = ItemDataDisplayBox(fonts, sizes)
        # Label preview box
        self.label_preview = LabelPreview(fonts, sizes)
        # Adds the widgets to the layout
        layout.addWidget(scan_prompt_label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.scan_entry_box, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.number_input_entry_box, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.print_button, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.item_data_display_box)
        layout.addWidget(self.label_preview, alignment=Qt.AlignmentFlag.AlignCenter)
        # Item data
        self.sizes = sizes
        self.item_data = item_data
        self.printers = printers
        self.scanned_item = None

    def validate_and_set_barcode(self) -> None:
        """
        Checks if the barcode is valid. If yes, sets self.scanned_item to the item corresponding to the scanned barcode.
        If the scanned barcode is known to be incorrect, looks up the correct one and uses it instead.
        For items where the same barcode has been used for several items, asks the user for clarification.
        """
        entered_barcode = self.scan_entry_box.text()
        if entered_barcode.isnumeric() and len(entered_barcode) == 13:
            # If the barcode is known to have been put on several different items, asks user for clarification.
            if self.item_data.multiple_replacements_exist(entered_barcode):
                self.scanned_item = self.get_item_info_from_user(entered_barcode)
            # If the barcode is correct, uses it to identify the item.
            elif self.item_data.item_exists(entered_barcode):
                self.scanned_item = self.item_data.get_item_by_barcode(entered_barcode)
            # If the barcode is known to be incorrect and only used for one item type, looks up the correct barcode.
            elif self.item_data.barcode_must_be_replaced(entered_barcode):
                corrected_barcode = self.item_data.get_replacement_barcode(entered_barcode)
                self.scanned_item = self.item_data.get_item_by_barcode(corrected_barcode)
            # If the barcode is unknown, displays an error message.
            else:
                show_warning("Ukendt stregkode", "Stregkoden er ukendt.")
                return
        else:
            show_warning("Ugyldig stregkode", "Stregkoden er ikke gyldig.")
            return
        # Populates the item info box with data, displays a preview of the label and moves focus to the next widget.
        self.item_data_display_box.load_data(self.scanned_item, entered_barcode)
        self.label_preview.update_image_preview(self.scanned_item.ean_13)
        self.number_input_entry_box.entry_box.setFocus()
        self.number_input_entry_box.entry_box.selectAll()

    def get_item_info_from_user(self, entered_barcode: str) -> Cushion:
        """Spawns a dialog box asking the user to select the correct item from a list."""
        item_selection_dialog = MultipleBarcodeSelection(
            self.item_data.multiple_choice_replacements[entered_barcode],
            self.item_data,
            self.sizes)
        if item_selection_dialog.exec() == QDialog.DialogCode.Accepted:
            corrected_barcode = item_selection_dialog.get_selected_item_barcode()
            return self.item_data.get_item_by_barcode(corrected_barcode)

    def clear_and_reset(self) -> None:
        """Clears all data and resets the tab in preparation for new input."""
        self.scan_entry_box.clear()
        self.number_input_entry_box.reset()
        self.item_data_display_box.reset()
        self.label_preview.reset()
        self.scan_entry_box.setFocus()

    def print(self) -> None:
        """Prints the scanned item."""
        copy_count = self.number_input_entry_box.value
        if self.scanned_item is not None:
            image_to_print = QPixmap(f"Data/PNG/{self.scanned_item.ean_13}.png")
            self.printers.print(image_to_print, copy_count)
            self.clear_and_reset()
            PrintLogger.write_to_log_file(self.scanned_item, copy_count, "Scanner")
        else:
            show_warning("Fejl", "Du skal scanne en vare, før du printer.")
            self.scan_entry_box.clear()
            self.scan_entry_box.setFocus()
