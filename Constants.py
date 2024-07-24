from PyQt6.QtGui import QFont

VERSION = "2.0.1"


class Fonts:
    """A container for QFont objects used within the project."""
    PROMPT = QFont()
    EAN13 = QFont()
    AMOUNT = QFont()
    BUTTON = QFont()
    ITEM_DATA = QFont()
    COMBOBOX = QFont()
    PROMPT.setPointSize(24)
    EAN13.setPointSize(36)
    AMOUNT.setPointSize(16)
    BUTTON.setPointSize(18)
    ITEM_DATA.setPointSize(10)
    COMBOBOX.setPointSize(10)


class Sizes:
    """A container for size constants for widgets used within the project."""
    TASKBAR_OFFSET = 40
    MAIN_WINDOW = (580, 680)
    SCAN_ENTRY_BOX = (360, 64)
    NUMBER_ENTRY_BOX = (80, 32)
    PRINT_BUTTON = (140, 40)
    DIALOG_BOX_OK_BUTTON = (80, 24)
    CLEAR_BUTTON = (48, 24)
    DATA_BOX_COLUMN = 330
    LABEL_PREVIEW = (540, 260)
    SEARCH_BOX_WIDTH = 300
    COMBOBOX_WIDTH = 540
    COMBOBOX_HEIGHT = 36
