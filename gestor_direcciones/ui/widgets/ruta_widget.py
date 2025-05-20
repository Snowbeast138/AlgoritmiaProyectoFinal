from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTextEdit
from PyQt5.QtWebEngineWidgets import QWebEngineView
import folium
import tempfile

class RutaWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        
        # Mapa para mostrar la ruta
        self.mapa = QWebEngineView()
        
        # Detalles de la ruta
        self.detalles_ruta = QTextEdit()
        self.detalles_ruta.setReadOnly(True)
        
        self.layout.addWidget(self.mapa)
        self.layout.addWidget(self.detalles_ruta)
        self.setLayout(self.layout)
    
    def mostrar_ruta(self, origen, destino, instrucciones, geometria):
        """Muestra la ruta en el mapa y las instrucciones"""
        # Crear mapa centrado en el punto medio
        lat_medio = (origen['lat'] + destino['lat']) / 2
        lon_medio = (origen['lon'] + destino['lon']) / 2
        
        m = folium.Map(location=[lat_medio, lon_medio], zoom_start=13)
        
        # Añadir marcadores
        folium.Marker(
            location=[origen['lat'], origen['lon']],
            popup="Origen",
            icon=folium.Icon(color='green')
        ).add_to(m)
        
        folium.Marker(
            location=[destino['lat'], destino['lon']],
            popup="Destino",
            icon=folium.Icon(color='red')
        ).add_to(m)
        
        # Añadir línea de ruta
        folium.PolyLine(
            locations=geometria,
            color='blue',
            weight=5,
            opacity=0.7
        ).add_to(m)
        
        # Guardar mapa temporal
        temp_file = tempfile.NamedTemporaryFile(suffix='.html', delete=False)
        m.save(temp_file.name)
        self.mapa.setUrl(QUrl.fromLocalFile(temp_file.name))
        
        # Mostrar instrucciones
        texto = "Ruta de transporte público:\n\n"
        for i, inst in enumerate(instrucciones, 1):
            texto += f"{i}. {inst['instruccion']} ({inst['distancia']}m) - {inst['tipo']}\n"
        
        self.detalles_ruta.setPlainText(texto)