from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, 
                            QTabWidget, QLabel, QToolButton)
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl, Qt
import folium
import tempfile
import webbrowser
import os

class RutaWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.origen = None
        self.destinos = []
        self._init_ui()
    
    def _init_ui(self):
        """Inicializa la interfaz de usuario"""
        self.layout = QVBoxLayout(self)
        
        # Widget de pestañas
        self.tabs = QTabWidget()
        
        # Pestaña de Mapa
        self.tab_mapa = QWidget()
        self.mapa_layout = QVBoxLayout()
        
        self.mapa = QWebEngineView()
        self.mapa.setMinimumHeight(400)
        
        # Controles del mapa
        self.controls_layout = QHBoxLayout()
        self.btn_abrir_mapa = QToolButton()
        self.btn_abrir_mapa.setText("Abrir en navegador")
        self.btn_abrir_mapa.clicked.connect(self._abrir_mapa_externo)
        self.btn_abrir_mapa.setEnabled(False)
        
        self.lbl_ruta_info = QLabel()
        self.lbl_ruta_info.setAlignment(Qt.AlignRight)
        
        self.controls_layout.addWidget(self.btn_abrir_mapa)
        self.controls_layout.addWidget(self.lbl_ruta_info)
        
        self.mapa_layout.addLayout(self.controls_layout)
        self.mapa_layout.addWidget(self.mapa)
        self.tab_mapa.setLayout(self.mapa_layout)
        
        # Pestaña de Instrucciones
        self.tab_instrucciones = QWidget()
        instrucciones_layout = QVBoxLayout()
        
        self.instrucciones = QTextEdit()
        self.instrucciones.setReadOnly(True)
        
        instrucciones_layout.addWidget(QLabel("Detalles de la ruta:"))
        instrucciones_layout.addWidget(self.instrucciones)
        self.tab_instrucciones.setLayout(instrucciones_layout)
        
        # Pestaña de Estadísticas
        self.tab_estadisticas = QWidget()
        estadisticas_layout = QVBoxLayout()
        
        self.estadisticas = QTextEdit()
        self.estadisticas.setReadOnly(True)
        
        estadisticas_layout.addWidget(QLabel("Estadísticas de la ruta:"))
        estadisticas_layout.addWidget(self.estadisticas)
        self.tab_estadisticas.setLayout(estadisticas_layout)
        
        # Añadir pestañas
        self.tabs.addTab(self.tab_mapa, "🗺️ Mapa")
        self.tabs.addTab(self.tab_instrucciones, "📝 Instrucciones")
        self.tabs.addTab(self.tab_estadisticas, "📊 Estadísticas")
        
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)
    
    def set_origen(self, origen: str):
        """Establece el origen de la ruta"""
        self.origen = origen
    
    def agregar_destino(self, destino: str):
        """Agrega un destino a la ruta"""
        if destino not in self.destinos:
            self.destinos.append(destino)
    
    def limpiar_ruta(self):
        """Limpia la ruta actual"""
        self.origen = None
        self.destinos = []
        self.mapa.setHtml("")
        self.instrucciones.clear()
        self.estadisticas.clear()
        self.btn_abrir_mapa.setEnabled(False)
        self.lbl_ruta_info.setText("")
    
    def mostrar_ruta_completa(self, origen: dict, destinos: list, ruta: dict):
        """Muestra una ruta completa en el widget"""
        if not origen or not destinos or not ruta:
            return
        
        # Crear mapa
        m = self._crear_mapa(origen, destinos, ruta)
        
        # Mostrar instrucciones
        self._mostrar_instrucciones(ruta)
        
        # Mostrar estadísticas
        self._mostrar_estadisticas(ruta)
        
        # Actualizar UI
        self.btn_abrir_mapa.setEnabled(True)
        self.lbl_ruta_info.setText(
            f"Ruta optimizada por {ruta.get('criterio', 'distancia')} | "
            f"Distancia: {ruta.get('distancia_total', 0):.2f} km | "
            f"Tiempo: {ruta.get('tiempo_total', 0)/60:.1f} min"
        )
    
    def _crear_mapa(self, origen: dict, destinos: list, ruta: dict) -> folium.Map:
        """Crea un mapa Folium con la ruta"""
        # Calcular centro del mapa
        lats = [origen['lat']] + [d['lat'] for d in destinos]
        lons = [origen['lon']] + [d['lon'] for d in destinos]
        centro = [sum(lats)/len(lats), sum(lons)/len(lons)]
        
        m = folium.Map(location=centro, zoom_start=13)
        
        # Añadir origen
        folium.Marker(
            location=[origen['lat'], origen['lon']],
            popup=f"Origen: {self.origen}",
            icon=folium.Icon(color='green', icon='home')
        ).add_to(m)
        
        # Añadir destinos
        for i, destino in enumerate(destinos, 1):
            folium.Marker(
                location=[destino['lat'], destino['lon']],
                popup=f"Destino {i}: {self.destinos[i-1]}",
                icon=folium.Icon(color='red', icon='flag')
            ).add_to(m)
        
        # Añadir ruta si existe geometría
        if 'geometria' in ruta:
            folium.PolyLine(
                locations=ruta['geometria'],
                color='blue',
                weight=5,
                opacity=0.7,
                popup="Ruta calculada"
            ).add_to(m)
        
        # Guardar mapa temporal y mostrarlo
        temp_file = tempfile.NamedTemporaryFile(suffix='.html', delete=False)
        m.save(temp_file.name)
        self.mapa.setUrl(QUrl.fromLocalFile(temp_file.name))
        self.temp_map_file = temp_file.name  # Guardar referencia para abrir después
        
        return m
    
    def _mostrar_instrucciones(self, ruta: dict):
        """Muestra las instrucciones detalladas de la ruta"""
        texto = "Instrucciones de la ruta:\n\n"
        
        if 'instrucciones' in ruta and ruta['instrucciones']:
            for i, inst in enumerate(ruta['instrucciones'], 1):
                texto += f"{i}. {inst.get('instruccion', '')}\n"
                texto += f"   - Distancia: {inst.get('distancia', 0)} m\n"
                texto += f"   - Duración: {inst.get('duracion', 0)/60:.1f} min\n"
                texto += f"   - Tipo: {inst.get('tipo', '')}\n\n"
        else:
            texto += "No hay instrucciones detalladas disponibles.\n"
            if 'ruta' in ruta:
                for i, punto in enumerate(ruta['ruta'], 1):
                    texto += f"{i}. {punto}\n"
        
        self.instrucciones.setPlainText(texto)
    
    def _mostrar_estadisticas(self, ruta: dict):
        """Muestra estadísticas de la ruta"""
        texto = "Estadísticas de la ruta:\n\n"
        
        texto += f"- Criterio de optimización: {ruta.get('criterio', 'distancia')}\n"
        texto += f"- Distancia total: {ruta.get('distancia_total', 0):.2f} km\n"
        texto += f"- Tiempo estimado: {ruta.get('tiempo_total', 0)/60:.1f} minutos\n"
        texto += f"- Número de paradas: {len(ruta.get('ruta', []))-1 if 'ruta' in ruta else 0}\n"
        
        if 'transbordos' in ruta:
            texto += f"- Número de transbordos: {ruta['transbordos']}\n"
        
        self.estadisticas.setPlainText(texto)
    
    def _abrir_mapa_externo(self):
        """Abre el mapa en el navegador externo"""
        if hasattr(self, 'temp_map_file') and os.path.exists(self.temp_map_file):
            webbrowser.open('file://' + os.path.abspath(self.temp_map_file))