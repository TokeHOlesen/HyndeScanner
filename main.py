import os
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
    QSizePolicy
)
from PyQt6.QtCore import Qt, QSize, pyqtSignal
from PyQt6.QtGui import QIcon, QGuiApplication, QFont, QKeyEvent


def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(styles.style_sheet)
    item_data = DataLoader("Data/Hay - Hynder.txt", "Data/Rettelser.txt")
    fonts = Fonts()
    sizes = Sizes()
    main_window = MainWindow(fonts, sizes, item_data)
    main_window.scanner_tab.scan_entry_box.setFocus()
    main_window.show()
    app.exec()


def show_warning(title: str, message: str):
    message_box = QMessageBox()
    message_box.setWindowTitle(title)
    message_box.setText(message)
    message_box.setIcon(QMessageBox.Icon.Warning)
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
        self.cushions = []
        self.corrections = {}
        # Reads the corrections file and saves the wrong and correct barcodes as a key - value pair in self.corrections
        try:
            with open(corrections_file_path, "r") as corrections_file:
                next(corrections_file)
                for line in corrections_file:
                    line = line.strip().split(";")
                    wrong_barcode = line[0]
                    correct_barcode = line[1]
                    self.corrections[wrong_barcode] = correct_barcode
        except FileNotFoundError:
            show_warning("Fejl", "Filen \"Rettelser.txt\" findes ikke.")
            raise SystemExit
        # Reads the BarTender file and constructs a Cushion object from each line; appends them to self.cushions
        try:
            with open(bartender_file_path, "r") as bartender_file:
                next(bartender_file)
                for line in bartender_file:
                    self.cushions.append(Cushion(line.strip()))
        except FileNotFoundError:
            show_warning("Fejl", "Kan ikke finde BarTender filen.")
            raise SystemExit

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

    def incorrect_barcode_exists(self, barcode: str) -> bool:
        """Returns true if the barcode exists and is known to be incorrect."""
        if barcode in self.corrections:
            return True
        return False

    def get_corrected_barcode(self, barcode: str) -> str:
        """Returns the correct version of an incorrect barcode."""
        return self.corrections[barcode]


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
        self.main_window = (580, 430)
        self.scan_entry_box = (360, 64)
        self.number_entry_box = (80, 32)
        self.print_button = (140, 48)
        self.data_box_column = 330
        self.combobox_width = 540
        self.combobox_height = 36


class MainWindow(QMainWindow):
    """Main window, with a tabbed interface."""
    def __init__(self, fonts: Fonts, sizes: Sizes, item_data: DataLoader):
        super().__init__()
        # Sets window properties
        self.setWindowTitle("Hyndescanner")
        self.setWindowIcon(QIcon(".\\Data\\barcode-scan.ico"))
        self.setFixedSize(*sizes.main_window)
        # Moves the window to the center of the screen
        screen = QGuiApplication.primaryScreen().geometry()
        center_pos_x = (screen.width() - self.width()) // 2
        center_pos_y = (screen.height() - self.height()) // 2
        self.move(center_pos_x, center_pos_y)
        # Instantiates the main widgets
        self.scanner_tab = ScannerTab(fonts, sizes, item_data)
        self.manuel_tab = ManualTab(fonts, sizes, item_data)
        # Instantiates the tabs
        tab_widget = QTabWidget()
        tab_widget.setTabPosition(QTabWidget.TabPosition.North)
        tab_widget.setMovable(False)
        tab_widget.addTab(self.scanner_tab, "Scanner")
        tab_widget.addTab(self.manuel_tab, "Manuel")
        # Sets the central widget
        self.setCentralWidget(tab_widget)


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

    def move_focus_to_button(self):
        self.target_button.setFocus()

    @property
    def value(self) -> int:
        return int(self.entry_box.text())


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

    def load_data(self, item_data: Cushion, scanned_barcode: str):
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


class ScannerTab(QWidget):
    """An interface for entering a barcode and choosing the number of labels to be printed."""
    def __init__(self, fonts: Fonts, sizes: Sizes, item_data: DataLoader):
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
        # "Input amount" entry box
        self.number_input_entry_box = NumberInputEntryBox(fonts, sizes, self.print_button)
        # Item data display box
        self.item_data_display_box = ItemDataDisplayBox(fonts, sizes)
        # Adds the widgets to the layout
        layout.addWidget(scan_prompt_label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.scan_entry_box, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.number_input_entry_box, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.print_button, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.item_data_display_box)
        # Item data
        self.item_data = item_data
        self.scanned_item = None

    def validate_and_set_barcode(self):
        entered_barcode = self.scan_entry_box.text()
        if entered_barcode.isnumeric() and len(entered_barcode) == 13:
            if self.item_data.item_exists(entered_barcode):
                self.scanned_item = self.item_data.get_item_by_barcode(entered_barcode)
            elif self.item_data.incorrect_barcode_exists(entered_barcode):
                corrected_barcode = self.item_data.get_corrected_barcode(entered_barcode)
                self.scanned_item = self.item_data.get_item_by_barcode(corrected_barcode)
            else:
                show_warning("Ukendt stregkode", "Stregkoden er ukendt.")
                return
        else:
            show_warning("Ugyldig stregkode", "Stregkoden er ikke gyldig.")
            return
        self.item_data_display_box.load_data(self.scanned_item, entered_barcode)
        self.number_input_entry_box.entry_box.setFocus()
        self.number_input_entry_box.entry_box.selectAll()


class ManualTab(QWidget):
    """An interface for manually choosing the type and number of labels to be printed."""
    def __init__(self, fonts: Fonts, sizes: Sizes, items: DataLoader):
        super().__init__()
        layout = QVBoxLayout(self)
        # "Choose type" label
        choose_type_label = QLabel("Vælg type:")
        choose_type_label.setFont(fonts.prompt)
        # item selection combo box
        self.combobox = QComboBox()
        self.combobox.setMinimumWidth(sizes.combobox_width)
        self.combobox.setMinimumHeight(sizes.combobox_height)
        self.combobox.setFont(fonts.combobox)
        # Print button
        print_manual_button = Button("Print", fonts, sizes)
        # "Input amount" entry box
        self.input_number_manual_widget = NumberInputEntryBox(fonts, sizes, print_manual_button)
        # Adds the widgets to the layout
        layout.addWidget(choose_type_label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.combobox, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.input_number_manual_widget, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(print_manual_button, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch(1)
        layout.setSpacing(20)
        self.populate_combobox(items)

    def populate_combobox(self, items):
        for cushion in items.cushions:
            combobox_entry = f"{cushion.old_number} - {cushion.item_name} - {cushion.color}"
            combobox_entry = combobox_entry.replace(" FR", "")
            combobox_entry = combobox_entry.replace("Palissade ", "")
            combobox_entry = combobox_entry.replace(" textile", "")
            combobox_entry = combobox_entry.replace(" foam", "")
            combobox_entry = combobox_entry.replace(" for Palissade", "")
            combobox_entry = combobox_entry.replace(" Interliner", "")
            self.combobox.addItem(combobox_entry)


if __name__ == "__main__":
    main()
