from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QLineEdit, 
                             QPushButton, QTextEdit)
from PyQt5.QtCore import Qt


class AgregarTab(QWidget):
    """Pestaña para agregar nuevas direcciones"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self._init_ui()
    
    def _init_ui(self):
        layout = QVBoxLayout()
        
        lbl_direccion = QLabel("Dirección a agregar:")
        self.txt_direccion = QLineEdit()
        btn_agregar = QPushButton("Agregar Dirección")
        btn_agregar.clicked.connect(self._agregar_direccion)
        
        self.txt_resultado = QTextEdit()
        self.txt_resultado.setReadOnly(True)
        
        layout.addWidget(lbl_direccion)
        layout.addWidget(self.txt_direccion)
        layout.addWidget(btn_agregar)
        layout.addWidget(QLabel("Resultado:"))
        layout.addWidget(self.txt_resultado)
        
        self.setLayout(layout)
    
    def _agregar_direccion(self):
        """Maneja el evento de agregar dirección"""
        direccion = self.txt_direccion.text().strip()
        if not direccion:
            self.parent.mostrar_error("La dirección no puede estar vacía")
            return
        
        try:
            info = self.parent.gestor.agregar_direccion(direccion)
            if info:
                self.txt_resultado.setPlainText(
                    f"Dirección agregada:\n\n"
                    f"Dirección formal: {info['direccion']}\n"
                    f"Coordenadas: Lat {info['coordenadas']['lat']}, Lon {info['coordenadas']['lon']}\n"
                    f"Tipo: {info['tipo']}\n"
                    f"Componentes:\n{json.dumps(info['componentes'], indent=2, ensure_ascii=False)}"
                )
                self.parent.actualizar_listas_direcciones()
                self.parent.mostrar_mensaje_estado(f"Dirección '{direccion}' agregada exitosamente")
            else:
                self.parent.mostrar_error("No se pudo encontrar la dirección")
        except Exception as e:
            self.parent.mostrar_error(f"Error al agregar dirección: {str(e)}")