import json
import sys
from PyQt6.QtCore import QSizeF, Qt
from PyQt6.QtGui import QPixmap, QPainter, QPageLayout, QPageSize
from PyQt6.QtPrintSupport import QPrinter, QPrinterInfo

from warning_messagebox import show_warning


class Printing:
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
        """Prints the specified QPixmap a set number of times."""
        printer = QPrinter()
        if self.selected_printer_name is not None:
            printer.setPrinterName(self.selected_printer_name)
            printer.setResolution(300)
            painter = QPainter(printer)
            for i in range(copy_count):
                painter.drawPixmap(0, 0, image_to_print)
                if i < copy_count - 1:
                    printer.newPage()
            painter.end()
        else:
            show_warning("Fejl", "Kan ikke printe: ingen printer valgt.")

    def save_printer_settings(self) -> None:
        """Saves the selected printer to a file."""
        try:
            with open("Data/printer.json", "w") as out_file:
                json.dump({"printer": self.selected_printer_name}, out_file)
        except OSError:
            show_warning("Fejl", "Indstillingen kan i øjeblikket ikke gemmes.")

    def load_printer_settings(self) -> None:
        """
        Attempts to load the selected printer data from the file. If the file or the printer doesn't exist,
        uses Windows default printer instead.
        """
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
        """Writes the selected printer name to the file."""
        if printer_name in self.available_printer_names:
            self.selected_printer_name = printer_name
            self.save_printer_settings()
        else:
            show_warning("Fejl", "Den valgte printer er i øjeblikket ikke tilgængelig.\n")

    def select_default_printer(self) -> None:
        """Selects the Windows default printer."""
        self.selected_printer_name = self.default_printer_name
