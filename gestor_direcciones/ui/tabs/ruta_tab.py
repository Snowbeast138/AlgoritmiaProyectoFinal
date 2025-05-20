from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QLineEdit, QPushButton, 
                             QListWidget, QTextEdit)
from PyQt5.QtCore import Qt


class RutaTab(QWidget):
    """Pestaña para optimización de rutas"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self._init_ui()
    
    def _init_ui(self):
        layout = QVBoxLayout()
        
        lbl_origen = QLabel("Dirección de origen:")
        self.txt_origen = QLineEdit()
        btn_seleccionar_origen = QPushButton("Seleccionar de lista")
        btn_seleccionar_origen.clicked.connect(self._seleccionar_origen)
        
        self.lista_destinos = QListWidget()
        self.lista_destinos.setSelectionMode(QListWidget.MultiSelection)
        
        btn_agregar_todos = QPushButton("Seleccionar todos")
        btn_agregar_todos.clicked.connect(self._seleccionar_todos_destinos)
        btn_limpiar = QPushButton("Limpiar selección")
        btn_limpiar.clicked.connect(self._limpiar_seleccion_destinos)
        
        btn_calcular = QPushButton("Calcular Ruta Óptima")
        btn_calcular.clicked.connect(self._calcular_ruta_optima)
        
        self.txt_ruta = QTextEdit()
        self.txt_ruta.setReadOnly(True)
        
        hbox_origen = QHBoxLayout()
        hbox_origen.addWidget(self.txt_origen)
        hbox_origen.addWidget(btn_seleccionar_origen)
        
        hbox_botones = QHBoxLayout()
        hbox_botones.addWidget(btn_agregar_todos)
        hbox_botones.addWidget(btn_limpiar)
        
        layout.addWidget(lbl_origen)
        layout.addLayout(hbox_origen)
        layout.addWidget(QLabel("Direcciones a incluir en la ruta:"))
        layout.addWidget(self.lista_destinos)
        layout.addLayout(hbox_botones)
        layout.addWidget(btn_calcular)
        layout.addWidget(QLabel("Ruta óptima:"))
        layout.addWidget(self.txt_ruta)
        
        self.setLayout(layout)
    
    def actualizar_lista(self):
        """Actualiza la lista de direcciones disponibles"""
        self.lista_destinos.clear()
        self.lista_destinos.addItems(self.parent.gestor.direcciones.keys())
    
    def _seleccionar_origen(self):
        """Selecciona el origen de la lista de direcciones"""
        item = self.lista_destinos.currentItem()
        if item:
            self.txt_origen.setText(item.text())
    
    def _seleccionar_todos_destinos(self):
        """Selecciona todas las direcciones para la ruta"""
        for i in range(self.lista_destinos.count()):
            self.lista_destinos.item(i).setSelected(True)
    
    def _limpiar_seleccion_destinos(self):
        """Limpia la selección de direcciones"""
        for i in range(self.lista_destinos.count()):
            self.lista_destinos.item(i).setSelected(False)
    
    def _calcular_ruta_optima(self):
        """Calcula y muestra la ruta óptima"""
        origen = self.txt_origen.text().strip()
        if not origen:
            self.parent.mostrar_error("Debe especificar un origen")
            return
        
        if origen not in self.parent.gestor.direcciones:
            self.parent.mostrar_error("El origen no existe en el sistema")
            return
        
        destinos = [item.text() for item in self.lista_destinos.selectedItems()]
        
        try:
            resultado = self.parent.gestor.encontrar_ruta_optima(origen, destinos)
            
            texto_ruta = "Ruta óptima:\n\n"
            texto_ruta += f"Origen: {resultado['ruta'][0]}\n\n"
            
            for i in range(1, len(resultado['ruta'])):
                texto_ruta += (
                    f"{i}. {resultado['ruta'][i]} "
                    f"(Distancia desde anterior: {resultado['distancias'][i-1]:.2f} km)\n"
                )
            
            texto_ruta += f"\nDistancia total: {resultado['distancia_total']:.2f} km"
            
            self.txt_ruta.setPlainText(texto_ruta)
            self.parent.mostrar_mensaje_estado("Ruta calculada exitosamente")
            
        except Exception as e:
            self.parent.mostrar_error(f"No se pudo calcular la ruta: {str(e)}")