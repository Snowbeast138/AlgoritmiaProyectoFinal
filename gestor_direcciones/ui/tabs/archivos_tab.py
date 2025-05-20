from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QPushButton, 
                             QLabel, QInputDialog)


class ArchivosTab(QWidget):
    """Pestaña para manejo de archivos"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self._init_ui()
    
    def _init_ui(self):
        layout = QVBoxLayout()
        
        btn_guardar = QPushButton("Guardar Datos")
        btn_guardar.clicked.connect(self._guardar_datos)
        btn_cargar = QPushButton("Cargar Datos")
        btn_cargar.clicked.connect(self._cargar_datos)
        
        self.lbl_archivo = QLabel("Archivo: datos_direcciones.json")
        
        layout.addWidget(btn_guardar)
        layout.addWidget(btn_cargar)
        layout.addWidget(self.lbl_archivo)
        layout.addStretch()
        
        self.setLayout(layout)
    
    def _guardar_datos(self):
        """Maneja el evento de guardar datos"""
        archivo, ok = QInputDialog.getText(
            self, "Guardar Datos", "Nombre del archivo:", 
            text="datos_direcciones.json"
        )
        
        if ok and archivo:
            try:
                self.parent.gestor.guardar_json(archivo)
                self.parent.mostrar_mensaje_estado(f"Datos guardados en {archivo}")
                self.lbl_archivo.setText(f"Archivo: {archivo}")
            except Exception as e:
                self.parent.mostrar_error(f"Error al guardar: {str(e)}")
    
    def _cargar_datos(self):
        """Maneja el evento de cargar datos"""
        archivo, ok = QInputDialog.getText(
            self, "Cargar Datos", "Nombre del archivo:", 
            text="datos_direcciones.json"
        )
        
        if ok and archivo:
            try:
                self.parent.gestor.cargar_json(archivo)
                self.parent.actualizar_listas_direcciones()
                self.parent.mostrar_mensaje_estado(f"Datos cargados desde {archivo}")
                self.lbl_archivo.setText(f"Archivo: {archivo}")
            except Exception as e:
                self.parent.mostrar_error(f"Error al cargar: {str(e)}")