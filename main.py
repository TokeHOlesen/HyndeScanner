import json
import os
import pymupdf
import sys
import styles
from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QTabWidget,
    QLineEdit,
    QComboBox,
    QMessageBox,
    QSpinBox,
    QSpacerItem,
    QSizePolicy,
    QRadioButton,
    QButtonGroup,
    QDialog,
    QDialogButtonBox,
    QMenu
)
from PyQt6.QtCore import Qt, QSize, pyqtSignal
from PyQt6.QtGui import QIcon, QGuiApplication, QFont, QKeyEvent, QPixmap, QPainter, QAction, QActionGroup
from PyQt6.QtPrintSupport import QPrinter, QPrinterInfo, QPrintDialog


def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(styles.style_sheet)
    item_data = DataLoader("Data/Hay - Hynder.txt", "Data/Rettelser.txt")
    fonts = Fonts()
    sizes = Sizes()
    printers = Printers()
    printers.load_printer_settings()
    main_window = MainWindow(fonts, sizes, printers, item_data)
    main_window.scanner_tab.scan_entry_box.setFocus()
    main_window.show()
    app.exec()


def show_warning(title: str, message: str) -> None:
    message_box = QMessageBox()
    message_box.setWindowTitle(title)
    message_box.setText(message)
    message_box.setIcon(QMessageBox.Icon.Warning)
    message_box.setWindowIcon(QIcon("Data/barcode-scan.ico"))
    ok_button = message_box.addButton(QMessageBox.StandardButton.Ok)
    ok_button.setFixedSize(QSize(80, 20))
    message_box.exec()


class Cushion:
    def __init__(self, csv_line: str):
        csv_data = csv_line.split(";")
        self.old_number = csv_data[0]
        self.item_name = csv_data[1]
        self.color = csv_data[2]
        self.ean_13 = csv_data[3]
        self.new_number = csv_data[4]


class DataLoader:
    def __init__(self, bartender_file_path: str, corrections_file_path: str):
        # A list of Cushion class objects - one for each known item.
        self.cushions = []
        # A list of ean-13 numbers that must be directly replaced with another number, without user input.
        self.replacements = {}
        # A list of ean-13 numbers that are potentially incorrect and have more than one potential replacement.
        # User input is necessary to find the correct replacement.
        self.multiple_choice_replacements = {}
        # Reads the BarTender file and constructs a Cushion object from each line; appends them to self.cushions
        try:
            with open(bartender_file_path, "r") as bartender_file:
                next(bartender_file)
                for line in bartender_file:
                    self.cushions.append(Cushion(line.strip()))
        except FileNotFoundError:
            show_warning("Fejl", "Kan ikke finde BarTender filen.")
            raise SystemExit
        # Reads the corrections file and saves the wrong and correct barcodes as a key - value pair in self.corrections
        try:
            with open(corrections_file_path, "r") as corrections_file:
                next(corrections_file)
                for line in corrections_file:
                    line = line.strip().split(";")
                    if line[0] == "erstat":
                        wrong_barcode = line[1]
                        correct_barcode = line[2]
                        self.replacements[wrong_barcode] = correct_barcode
                    elif line[0] == "flere":
                        self.multiple_choice_replacements[line[1]] = line[1:]
        except FileNotFoundError:
            show_warning("Fejl", "Filen \"Rettelser.txt\" findes ikke.")
            raise SystemExit

        # Builds two lists of text entries for the Combobox in the Manual tab - one each for old and new numbers.
        self.old_number_combobox_entry_list = self.build_combobox_elements("old")
        self.new_number_combobox_entry_list = self.build_combobox_elements("new")

        # Checks if there exists a .png file for every .pdf file; converts the pdf into png if not.
        for cushion in self.cushions:
            barcode = cushion.ean_13
            if not os.path.isfile(f"Data/PNG/{barcode}.png"):
                self.convert_pdf_to_png(barcode)

    def build_combobox_elements(self, number_type: str):
        combobox_element_list = []
        for cushion in self.cushions:
            if number_type == "old":
                combobox_entry = f"{cushion.old_number} - {cushion.item_name} - {cushion.color}"
            else:
                combobox_entry = f"{cushion.new_number} - {cushion.item_name} - {cushion.color}"
            combobox_entry = combobox_entry.replace(" FR", "")
            combobox_entry = combobox_entry.replace("Palissade ", "")
            combobox_entry = combobox_entry.replace(" textile", "")
            combobox_entry = combobox_entry.replace(" foam", "")
            combobox_entry = combobox_entry.replace(" for Palissade", "")
            combobox_entry = combobox_entry.replace(" Interliner", "")
            combobox_element_list.append(combobox_entry)
        return combobox_element_list

    @staticmethod
    def convert_pdf_to_png(barcode: str) -> None:
        """Converts PDF into PNG."""
        label_pdf = pymupdf.open(f"Data/PDF/{barcode}.pdf")
        label = label_pdf.load_page(0)
        label_pix = label.get_pixmap(dpi=300)
        label_pix.save(f"Data/PNG/{barcode}.png")

    def item_exists(self, barcode: str) -> bool:
        """Returns True if the barcode exists and is correct."""
        for item in self.cushions:
            if item.ean_13 == barcode:
                return True
        return False

    def get_item_by_barcode(self, barcode: str) -> Cushion:
        """Returns the Cushion class object with the .ean_13 property equal to barcode."""
        for item in self.cushions:
            if item.ean_13 == barcode:
                return item

    def barcode_must_be_replaced(self, barcode: str) -> bool:
        """Returns true if the barcode exists and is known to be incorrect."""
        if barcode in self.replacements:
            return True
        return False

    def get_replacement_barcode(self, barcode: str) -> str:
        """Returns the correct version of an incorrect barcode."""
        return self.replacements[barcode]

    def multiple_replacements_exist(self, barcode: str) -> bool:
        """
        Returns true if the barcode exists, is known to potentially be incorrect and there is more than one
        possible replacement; user input is necessary.
        """
        if barcode in self.multiple_choice_replacements:
            return True
        return False


class Fonts:
    """A container for QFont objects used within the project."""
    def __init__(self):
        self.prompt = QFont()
        self.ean13 = QFont()
        self.amount = QFont()
        self.button = QFont()
        self.item_data = QFont()
        self.combobox = QFont()
        self.prompt.setPointSize(24)
        self.ean13.setPointSize(36)
        self.amount.setPointSize(16)
        self.button.setPointSize(18)
        self.item_data.setPointSize(11)
        self.combobox.setPointSize(10)


class Sizes:
    """A container for size constants for widgets used within the project."""
    def __init__(self):
        self.main_window = (580, 710)
        self.scan_entry_box = (360, 64)
        self.number_entry_box = (80, 32)
        self.print_button = (140, 48)
        self.dialog_box_ok_button = (80, 24)
        self.clear_button = (48, 24)
        self.data_box_column = 330
        self.label_preview = (540, 260)
        self.search_box_width = 300
        self.combobox_width = 540
        self.combobox_height = 36


class Printers:
    def __init__(self):
        self.available_printer_names = [printer.printerName() for printer in QPrinterInfo.availablePrinters()]
        if len(self.available_printer_names) <= 0:
            show_warning("Fejl", "Der er ingen printerenheder tilgængelige.\n"
                                 "Programmet lukker nu.")
            sys.exit(1)
        self.selected_printer_name = None
        self.load_printer_settings()
        self.default_printer_name = QPrinterInfo.defaultPrinter().printerName()
        if self.selected_printer_name not in self.available_printer_names:
            self.selected_printer_name = self.default_printer_name

    def print(self, image_to_print: QPixmap, copy_count: int) -> None:
        printer = QPrinter()
        if self.selected_printer_name is not None:
            printer.setPrinterName(self.selected_printer_name)
            page_rect = printer.pageRect(QPrinter.Unit.Millimeter)
            # scaled_image_to_print = image_to_print.scaled(page_rect.size(), Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
            painter = QPainter(printer)
            for i in range(copy_count):
                painter.drawPixmap(page_rect.topLeft(), image_to_print)
                if i < copy_count - 1:
                    printer.newPage()
            painter.end()
        else:
            show_warning("Fejl", "Kan ikke printe: ingen printer valgt.")

    def save_printer_settings(self):
        try:
            with open("Data/printer.json", "w") as out_file:
                json.dump({"printer": self.selected_printer_name}, out_file)
        except OSError:
            show_warning("Fejl", "Indstillingen kan i øjeblikket ikke gemmes.")

    def load_printer_settings(self):
        try:
            with open("Data/printer.json", "r") as in_file:
                printer_settings = json.load(in_file)
                loaded_printer_name = printer_settings.get("printer")
                if loaded_printer_name in self.available_printer_names:
                    self.selected_printer_name = loaded_printer_name
                else:
                    show_warning("Printer fejl", "Den foretrukne printer er ikke tilgængelig.\n"
                                                 "Skifter til Windows standardprinter.")
                    self.select_default_printer()
        except FileNotFoundError:
            self.select_default_printer()
            self.save_printer_settings()

    def set_selected_printer(self, printer_name: str) -> None:
        if printer_name in self.available_printer_names:
            self.selected_printer_name = printer_name
            self.save_printer_settings()
        else:
            show_warning("Fejl", "Den valgte printer er i øjeblikket ikke tilgængelig.\n")

    def select_default_printer(self) -> None:
        self.selected_printer_name = self.default_printer_name


class MainWindow(QMainWindow):
    """Main window, with a tabbed interface."""
    def __init__(self, fonts: Fonts, sizes: Sizes, printers: Printers, item_data: DataLoader):
        super().__init__()
        # Printer data.
        self.printers = printers
        # Sets window properties.
        self.setWindowTitle("Hyndescanner")
        self.setWindowIcon(QIcon(".\\Data\\barcode-scan.ico"))
        self.setFixedSize(*sizes.main_window)
        # File menu.
        menu = self.menuBar()
        file_menu = menu.addMenu("&Fil")
        # Creates a "Choose printer" submenu and adds it to the File menu.
        printer_submenu = file_menu.addMenu("Vælg &printer")
        # Creates a "Default printer" menu item and its associated action. When selected, it will set the Windows
        # default printer as the printer to use, and set the corresponding menu items as checked.
        self.default_printer_action = QAction("Windows Standardprinter", self, checkable=True)
        self.default_printer_action.triggered.connect(self.select_default_printer)
        printer_submenu.addAction(self.default_printer_action)
        printer_submenu.addSeparator()
        # Creates a QActionGroup for all printer devices; adds their corresponding menu items to the printer submenu.
        self.printer_group = QActionGroup(self)
        for printer_name in printers.available_printer_names:
            action = QAction(printer_name, self, checkable=True)
            action.triggered.connect(lambda _, printer=action.text(): self.select_printer(printer))
            printer_submenu.addAction(action)
            self.printer_group.addAction(action)
        # Sets the printer submenu items' checked status according to the currently selected printer.
        for printer_action in self.printer_group.actions():
            if printer_action.text() == printers.selected_printer_name:
                printer_action.setChecked(True)
                self.default_printer_action.setChecked(printer_action.text() == printers.default_printer_name)
                break
        else:
            self.default_printer_action.setChecked(True)
        # Adds additional menus and items.
        file_menu.addSeparator()
        exit_action = QAction("&Afslut", self)
        exit_action.triggered.connect(sys.exit)
        exit_action.setShortcut("Ctrl+Q")
        file_menu.addAction(exit_action)
        edit_menu = menu.addMenu("&Rediger")
        help_menu = menu.addMenu("&Hjælp")
        about_action = QAction("&Om...", self)
        help_menu.addAction(about_action)

        # Moves the window to the center of the screen
        screen = QGuiApplication.primaryScreen().geometry()
        center_pos_x = (screen.width() - self.width()) // 2
        center_pos_y = (screen.height() - self.height()) // 2
        self.move(center_pos_x, center_pos_y)
        # Instantiates the main widgets
        self.scanner_tab = ScannerTab(fonts, sizes, item_data, printers)
        self.manuel_tab = ManualTab(fonts, sizes, item_data, printers)
        # Instantiates the tabs
        tab_widget = QTabWidget()
        tab_widget.setTabPosition(QTabWidget.TabPosition.North)
        tab_widget.setMovable(False)
        tab_widget.addTab(self.scanner_tab, "Scanner")
        tab_widget.addTab(self.manuel_tab, "Manuel")
        # Sets the central widget
        self.setCentralWidget(tab_widget)

    def select_default_printer(self):
        """Sets the Windows default printers as the selected printer."""
        self.printers.select_default_printer()
        self.default_printer_action.setChecked(True)
        # In the menu, sets the printer name that corresponds to the default printer as checked.
        for printer_action in self.printer_group.actions():
            if printer_action.text() == self.printers.default_printer_name:
                printer_action.setChecked(True)

    def select_printer(self, printer_name: str):
        """Sets the chosen printer as selected."""
        self.printers.set_selected_printer(printer_name)
        # If the selected printer is the Windows default printers, sets the default one to checked as well.
        self.default_printer_action.setChecked(printer_name == self.printers.default_printer_name)
        # In the menu, sets the chosen printer name as checked.
        for printer_action in self.printer_group.actions():
            if printer_action.text() == printer_name:
                printer_action.setChecked(True)


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
        self.target_button.setFocus()

    @property
    def value(self) -> int:
        return int(self.entry_box.text())

    def reset(self):
        self.entry_box.setValue(1)


class SearchEntryBox(QWidget):
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


class DataLabel(QLabel):
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

    def reset(self):
        self.item_name_data.clear()
        self.color_data.clear()
        self.old_number_data.clear()
        self.new_number_data.clear()
        self.ean13_data.clear()


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
        path_to_png = f"Data/PNG/{barcode}.png"
        label_preview_pix = QPixmap(path_to_png).scaled(
            self.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation)
        self.setPixmap(label_preview_pix)

    def reset(self):
        self.setText("Forhåndsvisning")


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


class ScannerTab(QWidget):
    """An interface for entering a barcode and choosing the number of labels to be printed."""
    def __init__(self, fonts: Fonts, sizes: Sizes, item_data: DataLoader, printers: Printers):
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

    def clear_and_reset(self):
        """Clears all data and resets the tab in preparation for new input."""
        self.scan_entry_box.clear()
        self.number_input_entry_box.reset()
        self.item_data_display_box.reset()
        self.label_preview.reset()
        self.scan_entry_box.setFocus()

    def print(self) -> None:
        copy_count = self.number_input_entry_box.value
        if self.scanned_item is not None:
            image_to_print = QPixmap(f"Data/PNG/{self.scanned_item.ean_13}.png")
            self.printers.print(image_to_print, copy_count)
            self.clear_and_reset()
        else:
            show_warning("Fejl", "Du skal scanne en vare, før du printer.")
            self.scan_entry_box.clear()
            self.scan_entry_box.setFocus()


class ManualTab(QWidget):
    """An interface for manually choosing the type and number of labels to be printed."""
    def __init__(self, fonts: Fonts, sizes: Sizes, items: DataLoader, printers: Printers):
        super().__init__()
        self.items = items
        self.printers = printers
        self.selected_number_type = items.old_number_combobox_entry_list
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
        self.label_preview = LabelPreview(fonts, sizes)
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
        barcode = self.get_selected_item_barcode()
        self.label_preview.update_image_preview(barcode)

    def print(self) -> None:
        copy_count = self.number_input_entry_box.value
        selected_item_barcode = self.get_selected_item_barcode()
        image_to_print = QPixmap(f"Data/PNG/{selected_item_barcode}.png")
        self.printers.print(image_to_print, copy_count)


if __name__ == "__main__":
    main()
