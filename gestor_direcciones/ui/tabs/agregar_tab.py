import json
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QLineEdit, QPushButton, 
                            QTextEdit, QMessageBox)
from gestor_direcciones.ui.widgets.map_widget import MapWidget

class AgregarTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self._init_ui()
        self.direccion_actual = None
    
    def _init_ui(self):
        layout = QVBoxLayout()
        
        # Widgets de dirección
        lbl_direccion = QLabel("Dirección a agregar:")
        self.txt_direccion = QLineEdit()
        btn_buscar = QPushButton("Buscar en Mapa")
        btn_buscar.clicked.connect(self._buscar_en_mapa)
        btn_confirmar = QPushButton("Confirmar Dirección")
        btn_confirmar.clicked.connect(self._confirmar_direccion)
        
        # Mapa interactivo
        self.mapa_widget = MapWidget()
        
        # Área de resultados
        self.txt_resultado = QTextEdit()
        self.txt_resultado.setReadOnly(True)
        
        # Layout horizontal para botones
        hbox = QHBoxLayout()
        hbox.addWidget(btn_buscar)
        hbox.addWidget(btn_confirmar)
        
        # Organizar widgets
        layout.addWidget(lbl_direccion)
        layout.addWidget(self.txt_direccion)
        layout.addLayout(hbox)
        layout.addWidget(self.mapa_widget)
        layout.addWidget(QLabel("Resultado:"))
        layout.addWidget(self.txt_resultado)
        
        self.setLayout(layout)
    
    def _buscar_en_mapa(self):
        """Busca la dirección y la muestra en el mapa"""
        direccion = self.txt_direccion.text().strip()
        if not direccion:
            QMessageBox.warning(self, "Error", "La dirección no puede estar vacía")
            return
        
        try:
            # Limpiar resultado anterior
            self.txt_resultado.clear()
            
            # Buscar nueva dirección
            info = self.parent.gestor.agregar_direccion(direccion)
            if info:
                self.direccion_actual = info
                lat = info['coordenadas']['lat']
                lon = info['coordenadas']['lon']
                
                # Actualizar mapa
                self.mapa_widget.agregar_marcador(lat, lon, info['direccion'])
                
                # Mostrar información
                self.txt_resultado.setPlainText(
                    f"Dirección encontrada:\n{info['direccion']}\n"
                    f"Coordenadas: Lat {lat:.6f}, Lon {lon:.6f}\n"
                    f"Tipo: {info.get('tipo', 'N/A')}"
                )
            else:
                QMessageBox.warning(self, "Error", "No se pudo encontrar la dirección")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al buscar dirección: {str(e)}")
            print(f"Error completo: {e}")  # Para depuración
    
    def _confirmar_direccion(self):
        """Confirma y guarda la dirección mostrada en el mapa"""
        if not self.direccion_actual:
            QMessageBox.warning(self, "Error", "Primero busque una dirección válida")
            return
        
        try:
            # Guardar la dirección en el gestor
            self.parent.gestor.direcciones[self.direccion_actual['direccion']] = self.direccion_actual
            self.parent.actualizar_listas_direcciones()
            QMessageBox.information(self, "Éxito", "Dirección agregada correctamente")
            
            # Limpiar para nueva entrada
            self.txt_direccion.clear()
            self.txt_resultado.clear()
            self.direccion_actual = None
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al agregar dirección: {str(e)}")

    def agregar_marcador(self, lat, lon, direccion, precision):
        zoom = {
            'high': 18,
            'medium': 15,
            'low': 12
        }.get(precision, 15)
        self.centrar_mapa(lat, lon, zoom)
    # ... resto del código ...

    def centrar_mapa(self, lat, lon, zoom=25):
        self.web_view.page().runJavaScript(
            f"map.setView([{lat}, {lon}], {zoom});"
        )