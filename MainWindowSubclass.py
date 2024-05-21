import os
import sys
from PyQt6.QtGui import QIcon, QGuiApplication, QAction, QActionGroup
from PyQt6.QtWidgets import QMainWindow, QTabWidget

from AboutWindowSubclass import AboutWindow
from DataLoaderClass import DataLoader
from FontsSizesClass import Fonts, Sizes
from ManualTabSubclass import ManualTab
from PrintingClass import Printing
from PrintLoggerClass import PrintLogger
from ScannerTabSubclass import ScannerTab
from warning_messagebox import show_warning


class MainWindow(QMainWindow):
    """Main window, with a tabbed interface."""
    def __init__(self, fonts: Fonts, sizes: Sizes, printers: Printing, item_data: DataLoader):
        super().__init__()
        self.sizes = sizes
        self.printers = printers
        self.item_data = item_data
        self.set_window_properties()
        self.scanner_tab = ScannerTab(fonts, sizes, item_data, printers)
        self.manuel_tab = ManualTab(fonts, sizes, item_data, printers)
        self.setup_tabbed_interface()
        # Creates a "Default printer" menu item and its associated action.
        # When selected, it will set the Windows default printer as the printer to use.
        self.default_printer_action = QAction("Windows Standardprinter", self, checkable=True)
        self.default_printer_action.triggered.connect(self.use_default_printer)
        # A QActionGroup for QActions associated with all printer devices.
        self.printer_group = QActionGroup(self)
        # Runs the menu setup methods.
        menu = self.menuBar()
        self.setup_file_menu(menu)
        self.setup_edit_menu(menu)
        self.setup_help_menu(menu)

    def set_window_properties(self) -> None:
        """Sets the window name, icon and size, and sets its position to the center of the screen."""
        self.setWindowTitle("Hyndescanner")
        self.setWindowIcon(QIcon(".\\Data\\barcode-scan.ico"))
        self.setFixedSize(*self.sizes.main_window)
        screen = QGuiApplication.primaryScreen().geometry()
        center_pos_x = (screen.width() - self.width()) // 2
        center_pos_y = (screen.height() - self.height()) // 2
        self.move(center_pos_x, center_pos_y)

    def setup_file_menu(self, menu) -> None:
        """
        Adds the File menu elements - a 'Choose printer' submenu and an Exit command.
        The 'Choose printer' submenu gets populated with all printers available on the system.
        If the user previously selected a printer, it will be set as selected; otherwise, the Windows default printer
        will be used.
        Puts a checkmark next to the selected printer's name.
        """
        file_menu = menu.addMenu("&Fil")
        printer_submenu = file_menu.addMenu("Vælg &printer")
        printer_submenu.addAction(self.default_printer_action)
        printer_submenu.addSeparator()
        self.add_printers_to_menu(printer_submenu)
        self.set_printer_menu_items_checked_status()
        file_menu.addSeparator()
        exit_action = QAction("&Afslut", self)
        exit_action.triggered.connect(sys.exit)
        exit_action.setShortcut("Ctrl+Q")
        file_menu.addAction(exit_action)

    def add_printers_to_menu(self, printer_submenu) -> None:
        """Loops through available printers, creates actions for them and adds them to the "Choose printer" submenu."""
        for printer_name in self.printers.available_printer_names:
            action = QAction(printer_name, self, checkable=True)
            action.triggered.connect(lambda _, printer=action.text(): self.select_printer(printer))
            printer_submenu.addAction(action)
            self.printer_group.addAction(action)

    def set_printer_menu_items_checked_status(self) -> None:
        """Sets the printer submenu items' checked status according to the currently selected printer."""
        for printer_action in self.printer_group.actions():
            if printer_action.text() == self.printers.selected_printer_name:
                printer_action.setChecked(True)
                self.default_printer_action.setChecked(printer_action.text() == self.printers.default_printer_name)
                break
        else:
            self.default_printer_action.setChecked(True)

    def setup_edit_menu(self, menu) -> None:
        """Sets up an Edit menu, letting the user open the associated text files."""
        edit_menu = menu.addMenu("&Rediger")
        open_database_action = QAction("Vis &BarTender CSV-filen", self)
        open_corrections_action = QAction("Vis listen over rettelser", self)
        open_logfile_action = QAction("Vis logfilen", self)
        edit_menu.addAction(open_database_action)
        edit_menu.addAction(open_corrections_action)
        edit_menu.addSeparator()
        edit_menu.addAction(open_logfile_action)
        open_database_action.triggered.connect(self.open_bartender_file)
        open_corrections_action.triggered.connect(self.open_corrections_file)
        open_logfile_action.triggered.connect(self.open_log_file)

    def setup_help_menu(self, menu) -> None:
        """Sets up the Help menu."""
        help_menu = menu.addMenu("&Hjælp")
        manual_action = QAction("&Brugervejledning", self)
        manual_action.triggered.connect(self.open_manual)
        about_action = QAction("&Om...", self)
        about_action.triggered.connect(self.open_about_window)
        help_menu.addAction(manual_action)
        help_menu.addAction(about_action)

    def setup_tabbed_interface(self) -> None:
        """Creates a QTabWidget, adds the two tab-widgets to it and sets it as the window's central widget."""
        tab_widget = QTabWidget()
        tab_widget.setTabPosition(QTabWidget.TabPosition.North)
        tab_widget.setMovable(False)
        tab_widget.addTab(self.scanner_tab, "Scanner")
        tab_widget.addTab(self.manuel_tab, "Manuel")
        self.setCentralWidget(tab_widget)

    def use_default_printer(self) -> None:
        """Sets the Windows default printers as the selected printer."""
        self.printers.select_default_printer()
        self.default_printer_action.setChecked(True)
        # In the menu, sets the printer name that corresponds to the default printer as checked.
        for printer_action in self.printer_group.actions():
            if printer_action.text() == self.printers.default_printer_name:
                printer_action.setChecked(True)

    def select_printer(self, printer_name: str) -> None:
        """Sets the chosen printer as selected."""
        self.printers.set_selected_printer(printer_name)
        # If the selected printer is the Windows default printers, sets the default one to checked as well.
        self.default_printer_action.setChecked(printer_name == self.printers.default_printer_name)
        # In the menu, sets the chosen printer name as checked.
        for printer_action in self.printer_group.actions():
            if printer_action.text() == printer_name:
                printer_action.setChecked(True)

    def open_bartender_file(self) -> None:
        """Tells Windows to open the BarTender file."""
        os.startfile(self.item_data.bartender_file_path.replace("/", "\\"))

    def open_corrections_file(self) -> None:
        """Tells Windows to open the corrections file."""
        os.startfile(self.item_data.corrections_file_path.replace("/", "\\"))

    @staticmethod
    def open_log_file() -> None:
        """Tells Windows to open the log file."""
        try:
            os.startfile(PrintLogger.path.replace("/", "\\"))
        except FileNotFoundError:
            show_warning("Fejl", "Logfilen kan ikke findes.")

    def open_manual(self) -> None:
        """Tells Windows to open the manual."""
        try:
            os.startfile(self.item_data.manual_file_path)
        except FileNotFoundError:
            show_warning("Fejl", "Brugervejledningen kan ikke findes.")

    def open_about_window(self) -> None:
        """Opens the 'About' dialog window."""
        about_window = AboutWindow(self.sizes)
        about_window.exec()
