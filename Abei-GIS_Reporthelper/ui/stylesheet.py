STYLESHEET = """
            QDockWidget {
                background: #f8f9fa;
                border: 1px solid #dee2e6;
                titlebar-close-icon: url(:/icons/close.svg);
                titlebar-normal-icon: url(:/icons/dock.svg);
                font-family: Segoe UI, Arial;
            }
            QDockWidget::title {
                color: black;
                padding: 4px;
                text-align: center;
                font-weight: bold;
            }
            QWidget {
                background: white;
            }
            QLabel {
                color: #495057;
                font-size: 12px;
                margin-top: 8px;
            }
            QComboBox {
                background: white;
                border: 1px solid #ced4da;
                border-radius: 4px;
                padding: 3px;
                min-height: 24px;
                color: #212529;
            }
            QComboBox:hover {
                border-color: #adb5bd;
            }
            QComboBox:on {  /* When the combo box is open */
                color: #212529;
            }
            QComboBox QAbstractItemView {
                background: white;
                color: #212529;
                selection-background-color: #0d6efd;
                selection-color: white;
                outline: 0;  /* Remove focus border */
            }
            QLineEdit {
                background: #f8f9fa;
                border: 1px solid #ced4da;
                border-radius: 4px;
                padding: 5px;
                color: #212529;
            }
            QPushButton {
                background: #0d6efd;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: 500;
            }
            QPushButton:hover {
                background: #0b5ed7;
            }
            QPushButton:disabled {
                background: #6c757d;
            }
        """