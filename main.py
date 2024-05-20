from PyQt6.QtWidgets import QApplication

import styles
from DataLoaderClass import DataLoader
from FontsSizesClass import Fonts, Sizes
from PrintingClass import Printing
from MainWindowSubclass import MainWindow


def main():
    app = QApplication([])
    app.setStyleSheet(styles.style_sheet)
    item_data = DataLoader("Data/Hay - Hynder.txt", "Data/Rettelser.txt")
    fonts = Fonts()
    sizes = Sizes()
    printing = Printing()
    printing.load_printer_settings()
    main_window = MainWindow(fonts, sizes, printing, item_data)
    main_window.scanner_tab.scan_entry_box.setFocus()
    main_window.show()
    app.exec()


if __name__ == "__main__":
    main()
