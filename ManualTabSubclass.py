from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QComboBox

from CommonCustomWidgetSubclasses import Button, NumberInputEntryBox, LabelPreview
from DataLoaderClass import DataLoader
from FontsSizesClass import Fonts, Sizes
from PrintingClass import Printing
from ManualCustomWidgetSubclasses import SearchEntryBox, OldNewRadioButtons
from PrintLoggerClass import PrintLogger


class ManualTab(QWidget):
    """An interface for manually choosing the type and number of labels to be printed."""
    def __init__(self, fonts: Fonts, sizes: Sizes, item_data: DataLoader, printers: Printing):
        super().__init__()
        self.items = item_data
        self.printers = printers
        self.selected_number_type = item_data.old_number_combobox_entry_list
        layout = QVBoxLayout(self)
        # "Choose type" label
        choose_type_label = QLabel("Vælg type:")
        choose_type_label.setFont(fonts.prompt)
        # Text search box
        self.search_entry_box = SearchEntryBox(fonts, sizes)
        self.search_entry_box.search_box.textChanged.connect(self.update_combobox)
        # Old/New number selection radio buttons
        self.old_new_radio_buttons = OldNewRadioButtons()
        self.old_new_radio_buttons.old_new_radio_btns.buttonClicked.connect(self.change_number_type)
        # item selection combo box
        self.combobox = QComboBox()
        self.combobox.setMinimumWidth(sizes.combobox_width)
        self.combobox.setMinimumHeight(sizes.combobox_height)
        self.combobox.setFont(fonts.combobox)
        self.combobox.currentIndexChanged.connect(self.update_preview)
        # Print button
        self.print_manual_button = Button("Print", fonts, sizes)
        self.print_manual_button.clicked.connect(self.print)
        # "Input amount" entry box
        self.number_input_entry_box = NumberInputEntryBox(fonts, sizes, self.print_manual_button)
        # Label preview box
        self.label_preview = LabelPreview(fonts, sizes, item_data)
        # Adds the widgets to the layout
        layout.addWidget(choose_type_label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.search_entry_box, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.old_new_radio_buttons, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.combobox, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.number_input_entry_box, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.print_manual_button, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch(1)
        layout.addWidget(self.label_preview, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(15)
        self.reset_combobox()

    def change_number_type(self) -> None:
        """Changes the item list to use for the combobox according to which radio button is checked."""
        current_index = self.combobox.currentIndex()
        if self.old_new_radio_buttons.old_radio_button.isChecked():
            self.selected_number_type = self.items.old_number_combobox_entry_list
        elif self.old_new_radio_buttons.new_radio_button.isChecked():
            self.selected_number_type = self.items.new_number_combobox_entry_list
        self.reset_combobox()
        self.update_combobox()
        self.combobox.setCurrentIndex(current_index)

    def reset_combobox(self) -> None:
        """Resets the combobox to its default state, with all item types present."""
        number_list = self.selected_number_type
        self.combobox.clear()
        for entry in number_list:
            self.combobox.addItem(entry)

    def update_combobox(self) -> None:
        """Removes items from the Combobox if they don't contain all the words entered into the search field."""
        self.reset_combobox()
        search_words = self.search_entry_box.search_box.text().split(" ")
        # Iterates backwards to avoid index shifting.
        for i in range(self.combobox.count(), -1, -1):
            for word in search_words:
                if word.lower() not in self.combobox.itemText(i).lower():
                    self.combobox.removeItem(i)

    def get_selected_item_barcode(self) -> str:
        """Returns the barcode number of the currently selected item in the combobox."""
        item_number = self.combobox.currentText().split(" ")[0]
        for item in self.items.cushions:
            if item_number in [item.old_number, item.new_number]:
                return item.ean_13

    def update_preview(self) -> None:
        """In the label preview box, displays the label for the item selected in the combobox."""
        barcode = self.get_selected_item_barcode()
        if barcode is not None:
            self.label_preview.update_image_preview(barcode)

    def print(self) -> None:
        """Prints labels for the selected item."""
        copy_count = self.number_input_entry_box.value
        selected_item_barcode = self.get_selected_item_barcode()
        image_to_print = QPixmap(f"Data/PNG/{selected_item_barcode}.png")
        self.printers.print(image_to_print, copy_count)
        selected_item = self.items.get_item_by_barcode(selected_item_barcode)
        PrintLogger.write_to_log_file(selected_item, copy_count, "Manuel")
