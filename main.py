import sys
from pathlib import Path

# Asegura que Python encuentre el paquete
sys.path.insert(0, str(Path(__file__).parent))

from gestor_direcciones.ui.main_window import MainWindow
from PyQt5.QtWidgets import QApplication

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()