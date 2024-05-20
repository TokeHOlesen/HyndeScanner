from PyQt6.QtGui import QFont


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
