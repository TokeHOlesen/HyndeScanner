style_sheet = """
        QLineEdit {
            border: 1px solid #AAAAAA;
            border-radius: 4px;
            padding: 2px;
            background: white;
        }
        QPushButton {
            background-color: #F4F4F4;
            border: 1px solid #AAAAAA;
            border-radius: 4px;
        }
        QPushButton:hover {
            background-color: #FFFFFF;
        }
        QPushButton:focus {
            border: 2px solid #AAAAAA;
        }
        QPushButton:disabled {
            color: #BBBBBB;
        }
        QSpinBox {
            border: 1px solid #AAAAAA;
            border-radius: 4px;
        }
        QSpinBox:up-button {
            subcontrol-origin: content;
            subcontrol-position: top right;
            width: 20px;
        }
        QSpinBox:down-button {
            subcontrol-origin: content;
            subcontrol-position: bottom right;
            width: 20px;
        }
        QScrollBar {
            border: 0px;
        }
        QLabel#label_preview {
            border: 2px solid #AAAAAA;
            color: #CCCCCC;
        }
    """
