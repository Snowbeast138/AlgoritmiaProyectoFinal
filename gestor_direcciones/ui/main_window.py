import sys
import json
import os
import webbrowser
from PyQt5.QtWidgets import (QMainWindow, QTabWidget, QStatusBar, QMessageBox, 
                            QVBoxLayout, QWidget, QLabel, QComboBox)
from PyQt5.QtCore import Qt

from .tabs.agregar_tab import AgregarTab
from .tabs.conectar_tab import ConectarTab
from .tabs.consultar_tab import ConsultarTab
from .tabs.archivos_tab import ArchivosTab
from .tabs.ruta_tab import RutaTab
from gestor_direcciones.core.gestor import GestorDirecciones


class MainWindow(QMainWindow):
    """Ventana principal de la aplicación con gestión completa de direcciones y rutas"""
    
    def __init__(self):
        super().__init__()
        self.gestor = GestorDirecciones()
        self.ruta_actual = None  # Para almacenar la última ruta calculada
        self._init_ui()
        self._cargar_configuracion()
    
    def _init_ui(self):
        """Inicializa la interfaz de usuario"""
        self.setWindowTitle("Gestor de Direcciones y Rutas Óptimas")
        self.setGeometry(100, 100, 1000, 700)
        
        # Widget central con tabs
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        
        # Crear pestañas
        self._crear_tabs()
        
        # Barra de estado
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.mostrar_mensaje_estado("Aplicación lista")
        
        # Barra de herramientas para rutas (opcional)
        self._init_toolbar()
    
    def _crear_tabs(self):
        """Crea e inicializa todas las pestañas"""
        self.agregar_tab = AgregarTab(self)
        self.conectar_tab = ConectarTab(self)
        self.consultar_tab = ConsultarTab(self)
        self.ruta_tab = RutaTab(self)
        self.archivos_tab = ArchivosTab(self)
        
        # Añadir pestañas
        self.tabs.addTab(self.agregar_tab, "➕ Agregar")
        self.tabs.addTab(self.conectar_tab, "🔗 Conectar")
        self.tabs.addTab(self.consultar_tab, "🔍 Consultar")
        self.tabs.addTab(self.ruta_tab, "🗺️ Optimizar Ruta")
        self.tabs.addTab(self.archivos_tab, "💾 Archivos")
        
        # Conectar señales
        self.tabs.currentChanged.connect(self._on_tab_changed)
    
    def _init_toolbar(self):
        """Inicializa la barra de herramientas para rutas"""
        toolbar = self.addToolBar("Rutas")
        
        # Selector de criterio de optimización
        self.criterio_combo = QComboBox()
        self.criterio_combo.addItems([
            "Distancia más corta", 
            "Tiempo mínimo", 
            "Menos transbordos"
        ])
        toolbar.addWidget(QLabel("Optimizar por:"))
        toolbar.addWidget(self.criterio_combo)
        
        # Botón para mostrar mapa
        self.mapa_action = toolbar.addAction("🗺️ Ver Mapa")
        self.mapa_action.setEnabled(False)
        self.mapa_action.triggered.connect(self._mostrar_mapa_ruta)
    
    def _cargar_configuracion(self):
        """Carga la configuración inicial"""
        try:
            if os.path.exists("config.json"):
                with open("config.json", "r") as f:
                    config = json.load(f)
                    if "ultimo_archivo" in config and os.path.exists(config["ultimo_archivo"]):
                        self.gestor.cargar_json(config["ultimo_archivo"])
                        self.actualizar_listas_direcciones()
                        self.mostrar_mensaje_estado(f"Datos cargados de {config['ultimo_archivo']}")
        except Exception as e:
            self.mostrar_error(f"No se pudo cargar configuración: {str(e)}")
    
    def _guardar_configuracion(self):
        """Guarda la configuración al cerrar"""
        try:
            config = {
                "ultimo_archivo": getattr(self, "ultimo_archivo", "")
            }
            with open("config.json", "w") as f:
                json.dump(config, f)
        except Exception as e:
            print(f"Error guardando configuración: {str(e)}")
    
    def _on_tab_changed(self, index):
        """Maneja el cambio de pestaña"""
        current_tab = self.tabs.widget(index)
        if current_tab == self.ruta_tab:
            self.ruta_tab.actualizar_lista()  # Cambiado de actualizar_ui a actualizar_lista
    
    def _mostrar_mapa_ruta(self):
        """Muestra el mapa con la ruta actual"""
        if self.ruta_actual:
            try:
                archivo_mapa = self.gestor.obtener_mapa_rutas(self.ruta_actual)
                webbrowser.open('file://' + os.path.abspath(archivo_mapa))
                self.mostrar_mensaje_estado(f"Mapa generado en {archivo_mapa}")
            except Exception as e:
                self.mostrar_error(f"No se pudo mostrar el mapa: {str(e)}")
    
    def actualizar_listas_direcciones(self):
        """Actualiza todas las listas de direcciones en las pestañas"""
        self.consultar_tab.actualizar_lista()
        # self.conectar_tab.actualizar_listas()  # Eliminar esta línea ya que ConectarTab no usa listas
        self.ruta_tab.actualizar_lista()
        
        tiene_direcciones = len(self.gestor.direcciones) > 0
        self.tabs.setTabEnabled(1, tiene_direcciones)  # Conectar
        self.tabs.setTabEnabled(2, tiene_direcciones)  # Consultar
        self.tabs.setTabEnabled(3, tiene_direcciones)  # Ruta
    
    def _cargar_configuracion(self):
        """Carga la configuración inicial"""
        try:
            if os.path.exists("config.json"):
                with open("config.json", "r") as f:
                    config = json.load(f)
                    if "ultimo_archivo" in config and os.path.exists(config["ultimo_archivo"]):
                        self.cargar_datos_desde_json(config["ultimo_archivo"])
        except Exception as e:
            self.mostrar_error(f"No se pudo cargar configuración: {str(e)}")
    
    def cargar_datos_desde_json(self, archivo):
        """Carga datos desde un archivo JSON"""
        try:
            self.gestor.cargar_json(archivo)
            self.ultimo_archivo = archivo
            self.actualizar_listas_direcciones()
            self.mostrar_mensaje_estado(f"Datos cargados desde {archivo}")
            return True
        except Exception as e:
            self.mostrar_error(f"Error al cargar datos: {str(e)}")
            return False
    
    def mostrar_error(self, mensaje):
        """Muestra un mensaje de error en un diálogo"""
        QMessageBox.critical(self, "Error", mensaje)
    
    def mostrar_mensaje_estado(self, mensaje, tiempo=3000):
        """Muestra un mensaje en la barra de estado"""
        self.status_bar.showMessage(mensaje, tiempo)
    
    def closeEvent(self, event):
        """Maneja el cierre de la ventana"""
        self._guardar_configuracion()
        
        # Guardar datos si hay cambios
        if hasattr(self, "datos_modificados") and self.datos_modificados:
            reply = QMessageBox.question(
                self, 'Guardar cambios',
                '¿Desea guardar los cambios antes de salir?',
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
                QMessageBox.Yes
            )
            
            if reply == QMessageBox.Yes:
                try:
                    if hasattr(self, "ultimo_archivo"):
                        self.gestor.guardar_json(self.ultimo_archivo)
                    else:
                        self.archivos_tab.guardar_como()
                except Exception as e:
                    self.mostrar_error(f"No se pudieron guardar los datos: {str(e)}")
                    event.ignore()
                    return
            elif reply == QMessageBox.Cancel:
                event.ignore()
                return
        
        event.accept()