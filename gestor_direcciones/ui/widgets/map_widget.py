from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl
import folium
import tempfile
import os

class MapWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.web_view = QWebEngineView()
        self.layout.addWidget(self.web_view)
        self.setLayout(self.layout)
        
        # Inicializar variables
        self.html_file = None
        self.marcador_actual = None
        self.mapa = None
        
        # Crear mapa inicial
        self._crear_mapa_inicial()
        
    def _crear_mapa_inicial(self):
        """Crea el mapa inicial"""
        self.mapa = folium.Map(location=[20.66682, -103.39182], zoom_start=15)
        self._actualizar_mapa()
        
    def _actualizar_mapa(self):
        """Actualiza el mapa mostrado en el widget"""
        # Cerrar archivo anterior si existe
        if self.html_file:
            try:
                os.unlink(self.html_file.name)
            except:
                pass
        
        # Crear nuevo archivo temporal
        self.html_file = tempfile.NamedTemporaryFile(delete=False, suffix='.html')
        self.mapa.save(self.html_file.name)
        self.html_file.close()
        
        # Cargar el archivo HTML
        self.web_view.setUrl(QUrl.fromLocalFile(self.html_file.name))
        
    def centrar_mapa(self, lat, lon, zoom=15):
        """Centra el mapa en las coordenadas especificadas"""
        if not self.mapa:
            self._crear_mapa_inicial()
            
        self.mapa.location = [lat, lon]
        self.mapa.zoom_start = zoom
        self._actualizar_mapa()
        
    def agregar_marcador(self, lat, lon, direccion):
        """Añade un marcador al mapa y centra la vista"""
        # Crear nuevo mapa si no existe
        if not self.mapa:
            self._crear_mapa_inicial()
        
        # Limpiar marcadores anteriores
        if self.marcador_actual:
            self.mapa = folium.Map(location=[lat, lon], zoom_start=15)
        
        # Añadir nuevo marcador
        self.marcador_actual = folium.Marker(
            location=[lat, lon],
            popup=direccion,
            icon=folium.Icon(color='green')
        ).add_to(self.mapa)
        
        self.centrar_mapa(lat, lon)
        
    def limpiar_mapa(self):
        """Limpia completamente el mapa"""
        self._crear_mapa_inicial()
        
    def __del__(self):
        """Limpia el archivo temporal al destruir el widget"""
        if hasattr(self, 'html_file') and self.html_file:
            try:
                if os.path.exists(self.html_file.name):
                    os.unlink(self.html_file.name)
            except:
                pass