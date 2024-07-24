from PyQt6.QtWidgets import QApplication

import styles
from DataLoaderClass import DataLoader
from PrintingClass import Printing
from MainWindowSubclass import MainWindow


def main():
    app = QApplication([])
    app.setStyleSheet(styles.style_sheet)
    item_data = DataLoader("Data/HyndeData.txt", "Data/Rettelser.txt")
    printing = Printing()
    main_window = MainWindow(printing, item_data)
    main_window.scanner_tab.scan_entry_box.setFocus()
    main_window.show()
    app.exec()


if __name__ == "__main__":
    main()
