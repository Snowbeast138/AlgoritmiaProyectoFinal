from PyQt5.QtWidgets import QListWidget


class DireccionesList(QListWidget):
    """Widget personalizado para listar direcciones"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlternatingRowColors(True)
        self.setStyleSheet("""
            QListWidget {
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 2px;
            }
            QListWidget::item {
                padding: 5px;
            }
            QListWidget::item:selected {
                background-color: #0078d7;
                color: white;
            }
        """)