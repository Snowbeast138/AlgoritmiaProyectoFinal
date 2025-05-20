from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QLineEdit, QPushButton, QMessageBox)
from gestor_direcciones.ui.widgets.ruta_widget import RutaWidget

class RutaTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self._init_ui()
    
    def _init_ui(self):
        layout = QVBoxLayout()
        
        # Widgets para selección de ruta
        lbl_origen = QLabel("Origen:")
        self.txt_origen = QLineEdit()
        
        lbl_destino = QLabel("Destino:")
        self.txt_destino = QLineEdit()
        
        btn_buscar = QPushButton("Buscar Ruta Óptima")
        btn_buscar.clicked.connect(self._buscar_ruta)
        
        # Widget de visualización de ruta
        self.ruta_widget = RutaWidget()
        
        # Layout
        hbox = QHBoxLayout()
        hbox.addWidget(lbl_origen)
        hbox.addWidget(self.txt_origen)
        hbox.addWidget(lbl_destino)
        hbox.addWidget(self.txt_destino)
        hbox.addWidget(btn_buscar)
        
        layout.addLayout(hbox)
        layout.addWidget(self.ruta_widget)
        
        self.setLayout(layout)
    
    def _buscar_ruta(self):
        origen = self.txt_origen.text().strip()
        destino = self.txt_destino.text().strip()
        
        if not origen or not destino:
            QMessageBox.warning(self, "Error", "Debe especificar origen y destino")
            return
            
        try:
            resultado = self.parent.gestor.obtener_ruta_transporte_publico(origen, destino)
            
            if 'error' in resultado:
                QMessageBox.warning(self, "Error", resultado['error'])
                return
                
            # Obtener coordenadas para el mapa
            coords_origen = self.parent.gestor.direcciones[origen]['coordenadas']
            coords_destino = self.parent.gestor.direcciones[destino]['coordenadas']
            
            # Mostrar resultados
            self.ruta_widget.mostrar_ruta(
                coords_origen,
                coords_destino,
                resultado['instrucciones'],
                resultado['geometria']
            )
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al buscar ruta: {str(e)}")