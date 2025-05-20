import sys
import os
from pathlib import Path

# Esto asegura que Python encuentre tus módulos
sys.path.append(str(Path(__file__).parent))

from gestor_direcciones.ui.main_window import MainWindow
from PyQt5.QtWidgets import QApplication

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()