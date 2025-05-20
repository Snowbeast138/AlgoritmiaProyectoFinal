import json
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QListWidget, 
                             QTextEdit)
from PyQt5.QtCore import Qt


class ConsultarTab(QWidget):
    """Pestaña para consultar direcciones"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self._init_ui()
    
    def _init_ui(self):
        layout = QVBoxLayout()
        
        lbl_consulta = QLabel("Dirección a consultar:")
        self.txt_consulta = QLineEdit()
        btn_consultar = QPushButton("Consultar")
        btn_consultar.clicked.connect(self._consultar_direccion)
        
        self.lista_direcciones = QListWidget()
        self.lista_direcciones.itemDoubleClicked.connect(self._seleccionar_direccion_consulta)
        
        self.txt_info = QTextEdit()
        self.txt_info.setReadOnly(True)
        
        layout.addWidget(lbl_consulta)
        layout.addWidget(self.txt_consulta)
        layout.addWidget(btn_consultar)
        layout.addWidget(QLabel("Direcciones disponibles:"))
        layout.addWidget(self.lista_direcciones)
        layout.addWidget(QLabel("Información:"))
        layout.addWidget(self.txt_info)
        
        self.setLayout(layout)
    
    def actualizar_lista(self):
        """Actualiza la lista de direcciones disponibles"""
        self.lista_direcciones.clear()
        self.lista_direcciones.addItems(self.parent.gestor.direcciones.keys())
    
    def _seleccionar_direccion_consulta(self, item):
        """Selecciona una dirección para consultar al hacer doble clic"""
        self.txt_consulta.setText(item.text())
        self._consultar_direccion()
    
    def _consultar_direccion(self):
        """Maneja el evento de consultar dirección"""
        direccion = self.txt_consulta.text().strip()
        if not direccion:
            item = self.lista_direcciones.currentItem()
            if not item:
                self.parent.mostrar_error("Seleccione o ingrese una dirección")
                return
            direccion = item.text()
        
        if direccion not in self.parent.gestor.direcciones:
            self.parent.mostrar_error("Dirección no encontrada")
            return
        
        info = self.parent.gestor.direcciones[direccion]
        vecinos = self.parent.gestor.obtener_vecinos(direccion)
        
        self.txt_info.setPlainText(
            f"Información de '{direccion}':\n\n"
            f"Dirección formal: {info['direccion']}\n"
            f"Coordenadas: Lat {info['coordenadas']['lat']}, Lon {info['coordenadas']['lon']}\n"
            f"Tipo: {info['tipo']}\n"
            f"Componentes:\n{json.dumps(info['componentes'], indent=2, ensure_ascii=False)}\n\n"
            f"Direcciones conectadas:\n{', '.join(vecinos) if vecinos else 'Ninguna'}"
        )