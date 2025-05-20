import sys
import json
from PyQt5.QtWidgets import (QMainWindow, QTabWidget, QStatusBar, QMessageBox)
from PyQt5.QtCore import Qt

from .tabs.agregar_tab import AgregarTab
from .tabs.conectar_tab import ConectarTab
from .tabs.consultar_tab import ConsultarTab
from .tabs.archivos_tab import ArchivosTab
from .tabs.ruta_tab import RutaTab
from gestor_direcciones.core.gestor import GestorDirecciones


class MainWindow(QMainWindow):
    """Ventana principal de la aplicación"""
    def __init__(self):
        super().__init__()
        self.gestor = GestorDirecciones()
        self._init_ui()
    
    def _init_ui(self):
        self.setWindowTitle("Gestor de Direcciones con Nominatim")
        self.setGeometry(100, 100, 800, 600)
        
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        
        # Crear pestañas
        self.agregar_tab = AgregarTab(self)
        self.conectar_tab = ConectarTab(self)
        self.consultar_tab = ConsultarTab(self)
        self.ruta_tab = RutaTab(self)
        self.archivos_tab = ArchivosTab(self)
        
        self.tabs.addTab(self.agregar_tab, "Agregar Dirección")
        self.tabs.addTab(self.conectar_tab, "Conectar Direcciones")
        self.tabs.addTab(self.consultar_tab, "Consultar Dirección")
        self.tabs.addTab(self.ruta_tab, "Optimizar Ruta")
        self.tabs.addTab(self.archivos_tab, "Archivos")
        
        self.statusBar().showMessage("Listo")
    
    def actualizar_listas_direcciones(self):
        """Actualiza todas las listas de direcciones disponibles"""
        self.consultar_tab.actualizar_lista()
        self.ruta_tab.actualizar_lista()
    
    def mostrar_error(self, mensaje):
        """Muestra un mensaje de error"""
        QMessageBox.warning(self, "Error", mensaje)
    
    def mostrar_mensaje_estado(self, mensaje, tiempo=3000):
        """Muestra un mensaje en la barra de estado"""
        self.statusBar().showMessage(mensaje, tiempo)