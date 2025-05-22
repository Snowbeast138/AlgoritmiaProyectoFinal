from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QComboBox, QPushButton, QMessageBox, QListWidget,
                            QListWidgetItem, QGroupBox)
from PyQt5.QtCore import Qt
from gestor_direcciones.ui.widgets.ruta_widget import RutaWidget

class RutaTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.ruta_actual = None
        self._init_ui()
        self._conectar_eventos()
    
    def _init_ui(self):
        """Inicializa la interfaz de usuario"""
        main_layout = QVBoxLayout()
        
        # Grupo de selección de puntos
        group_seleccion = QGroupBox("Selección de Puntos")
        seleccion_layout = QVBoxLayout()
        
        # Lista de direcciones disponibles
        self.lista_direcciones = QListWidget()
        self.lista_direcciones.setSelectionMode(QListWidget.MultiSelection)
        seleccion_layout.addWidget(QLabel("Direcciones disponibles:"))
        seleccion_layout.addWidget(self.lista_direcciones)
        
        # Controles de selección
        controls_layout = QHBoxLayout()
        
        self.btn_agregar_origen = QPushButton("Establecer como Origen")
        self.btn_agregar_destino = QPushButton("Agregar como Destino")
        self.btn_limpiar = QPushButton("Limpiar Selección")
        
        controls_layout.addWidget(self.btn_agregar_origen)
        controls_layout.addWidget(self.btn_agregar_destino)
        controls_layout.addWidget(self.btn_limpiar)
        
        seleccion_layout.addLayout(controls_layout)
        group_seleccion.setLayout(seleccion_layout)
        
        # Grupo de configuración de ruta
        group_config = QGroupBox("Configuración de Ruta")
        config_layout = QHBoxLayout()
        
        # Criterios de optimización
        config_layout.addWidget(QLabel("Optimizar por:"))
        self.cbo_criterio = QComboBox()
        self.cbo_criterio.addItems([
            "Distancia más corta", 
            "Tiempo mínimo",
            "Menos transbordos"
        ])
        config_layout.addWidget(self.cbo_criterio)
        
        # Modo de transporte
        config_layout.addWidget(QLabel("Transporte:"))
        self.cbo_transporte = QComboBox()
        self.cbo_transporte.addItems([
            "Público",
            "Privado",
            "Combinado"
        ])
        config_layout.addWidget(self.cbo_transporte)
        
        # Botón de cálculo
        self.btn_calcular = QPushButton("Calcular Ruta Óptima")
        config_layout.addWidget(self.btn_calcular)
        
        group_config.setLayout(config_layout)
        
        # Widget de visualización de ruta
        self.ruta_widget = RutaWidget()
        
        # Ensamblar layout principal
        main_layout.addWidget(group_seleccion)
        main_layout.addWidget(group_config)
        main_layout.addWidget(self.ruta_widget)
        
        self.setLayout(main_layout)
    
    
    def actualizar_ui(self):
        """Actualiza toda la interfaz de usuario"""
        self.actualizar_lista() 


    def _conectar_eventos(self):
        """Conecta los eventos de los controles"""
        self.btn_agregar_origen.clicked.connect(self._establecer_origen)
        self.btn_agregar_destino.clicked.connect(self._agregar_destino)
        self.btn_limpiar.clicked.connect(self._limpiar_seleccion)
        self.btn_calcular.clicked.connect(self._calcular_ruta)
    
    def actualizar_lista(self):
        """Actualiza la lista de direcciones disponibles"""
        self.lista_direcciones.clear()
        if hasattr(self.parent, 'gestor') and self.parent.gestor.direcciones:
            for direccion in self.parent.gestor.direcciones.keys():
                item = QListWidgetItem(direccion)
                item.setData(Qt.UserRole, direccion)
                self.lista_direcciones.addItem(item)
    
    def _establecer_origen(self):
        """Establece el origen seleccionado"""
        seleccionados = self.lista_direcciones.selectedItems()
        if not seleccionados:
            QMessageBox.warning(self, "Error", "Seleccione al menos una dirección como origen")
            return
        
        self.origen = seleccionados[0].data(Qt.UserRole)
        self.ruta_widget.set_origen(self.origen)
        QMessageBox.information(self, "Origen establecido", f"Origen establecido: {self.origen}")
    
    def _agregar_destino(self):
        """Agrega destinos seleccionados"""
        seleccionados = self.lista_direcciones.selectedItems()
        if not seleccionados:
            QMessageBox.warning(self, "Error", "Seleccione al menos una dirección como destino")
            return
        
        if not hasattr(self, 'destinos'):
            self.destinos = []
        
        for item in seleccionados:
            destino = item.data(Qt.UserRole)
            if destino not in self.destinos:
                self.destinos.append(destino)
                self.ruta_widget.agregar_destino(destino)
        
        QMessageBox.information(self, "Destinos agregados", f"Se agregaron {len(seleccionados)} destinos")
    
    def _limpiar_seleccion(self):
        """Limpia la selección actual"""
        self.lista_direcciones.clearSelection()
        if hasattr(self, 'origen'):
            del self.origen
        if hasattr(self, 'destinos'):
            del self.destinos
        self.ruta_widget.limpiar_ruta()
    
    def _calcular_ruta(self):
        """Versión corregida con manejo robusto de errores y debug"""
        try:
            if not hasattr(self, 'origen') or not hasattr(self, 'destinos') or not self.destinos:
                QMessageBox.warning(self, "Error", "Debe establecer un origen y al menos un destino")
                return

            print("Obteniendo parámetros...")  # Debug
            criterio = self.cbo_criterio.currentText().lower().split()[0]
            transporte = self.cbo_transporte.currentText().lower()

            print(f"Calculando ruta desde {self.origen} a {self.destinos}...")  # Debug
            self.ruta_actual = self.parent.gestor.encontrar_ruta_optima(
                origen=self.origen,
                destinos=self.destinos,
                criterio=criterio,
                transporte=transporte
            )

            print("Ruta calculada:", self.ruta_actual)  # Debug
            
            if not self.ruta_actual:
                raise ValueError("El gestor no devolvió resultados")

            # Verificar estructura de datos
            required_keys = ['ruta', 'geometria', 'instrucciones', 'distancia_total', 'tiempo_total']
            for key in required_keys:
                if key not in self.ruta_actual:
                    raise ValueError(f"Falta clave requerida en resultados: {key}")

            print("Preparando datos para visualización...")  # Debug
            origen_coords = self.parent.gestor.direcciones[self.origen]['coordenadas']
            destinos_coords = []
            for d in self.destinos:
                if d in self.parent.gestor.direcciones:
                    destinos_coords.append(self.parent.gestor.direcciones[d]['coordenadas'])
                else:
                    raise ValueError(f"Destino no encontrado: {d}")

            print("Mostrando ruta en widget...")  # Debug
            self.ruta_widget.mostrar_ruta_completa(
                origen=origen_coords,
                destinos=destinos_coords,
                ruta=self.ruta_actual
            )

            # Actualizar estadísticas e instrucciones
            self._mostrar_estadisticas(self.ruta_actual)
            self._mostrar_instrucciones(self.ruta_actual)

            print("Visualización completada correctamente")  # Debug

        except Exception as e:
            print(f"Error durante cálculo de ruta: {str(e)}")  # Debug
            QMessageBox.critical(self, "Error", 
                            f"No se pudo mostrar la ruta:\n{str(e)}\n\n"
                            f"Detalles técnicos:\n{self._obtener_detalles_error(e)}")
            
    def _obtener_detalles_error(self, error):
        """Obtiene detalles técnicos del error para depuración"""
        detalles = []
        if hasattr(self, 'ruta_actual') and self.ruta_actual:
            detalles.append(f"Tipo de datos recibidos: {type(self.ruta_actual)}")
            detalles.append(f"Claves disponibles: {list(self.ruta_actual.keys())}")
        if hasattr(self, 'origen'):
            detalles.append(f"Origen: {self.origen}")
        if hasattr(self, 'destinos'):
            detalles.append(f"Destinos: {self.destinos}")
        return "\n".join(detalles)

    def _mostrar_estadisticas(self, ruta):
        """Versión mejorada para mostrar estadísticas"""
        try:
            texto = "Estadísticas de la ruta:\n\n"
            
            # Información básica
            texto += f"- Origen: {ruta['ruta'][0]}\n"
            texto += f"- Destinos: {', '.join(ruta['ruta'][1:])}\n\n"
            
            # Métricas
            texto += f"- Distancia total: {ruta.get('distancia_total', 'N/A')} km\n"
            texto += f"- Tiempo estimado: {ruta.get('tiempo_total', 'N/A')/60:.1f} minutos\n"
            texto += f"- Tipo de transporte: {ruta.get('transporte', 'N/A').capitalize()}\n"
            
            # Criterio de optimización
            texto += f"- Criterio: {ruta.get('criterio', 'N/A').capitalize()}\n"
            
            # Transbordos si es transporte público
            if ruta.get('transporte') in ['publico', 'combinado']:
                texto += f"- Número de transbordos: {ruta.get('transbordos', 0)}\n"
            
            self.ruta_widget.estadisticas.setPlainText(texto)
            
        except Exception as e:
            print(f"Error mostrando estadísticas: {str(e)}")
            self.ruta_widget.estadisticas.setPlainText("Error al generar estadísticas")

    def _mostrar_instrucciones(self, ruta):
        """Versión mejorada para mostrar instrucciones"""
        try:
            if not ruta.get('instrucciones'):
                self.ruta_widget.instrucciones.setPlainText("No hay instrucciones disponibles")
                return

            texto = "Instrucciones de la ruta:\n\n"
            for i, inst in enumerate(ruta['instrucciones'], 1):
                texto += f"{i}. {inst.get('instruccion', 'Instrucción no disponible')}\n"
                texto += f"   - Distancia: {inst.get('distancia', 'N/A')} metros\n"
                texto += f"   - Duración: {inst.get('duracion', 'N/A')/60:.1f} minutos\n"
                texto += f"   - Tipo: {inst.get('tipo', 'N/A').capitalize()}\n\n"
            
            self.ruta_widget.instrucciones.setPlainText(texto)
            
        except Exception as e:
            print(f"Error mostrando instrucciones: {str(e)}")
            self.ruta_widget.instrucciones.setPlainText("Error al generar instrucciones")