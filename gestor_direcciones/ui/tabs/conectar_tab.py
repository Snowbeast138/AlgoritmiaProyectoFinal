import json
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, 
                             QLineEdit, QPushButton)
from PyQt5.QtCore import Qt


class ConectarTab(QWidget):
    """Pestaña para conectar direcciones"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self._init_ui()
    
    def _init_ui(self):
        layout = QVBoxLayout()
        
        lbl_dir1 = QLabel("Primera dirección:")
        self.txt_dir1 = QLineEdit()
        lbl_dir2 = QLabel("Segunda dirección:")
        self.txt_dir2 = QLineEdit()
        lbl_metadata = QLabel("Metadata (JSON opcional):")
        self.txt_metadata = QLineEdit()
        btn_conectar = QPushButton("Conectar Direcciones")
        btn_conectar.clicked.connect(self._conectar_direcciones)
        
        layout.addWidget(lbl_dir1)
        layout.addWidget(self.txt_dir1)
        layout.addWidget(lbl_dir2)
        layout.addWidget(self.txt_dir2)
        layout.addWidget(lbl_metadata)
        layout.addWidget(self.txt_metadata)
        layout.addWidget(btn_conectar)
        
        self.setLayout(layout)
    
    def _conectar_direcciones(self):
        """Maneja el evento de conectar direcciones"""
        dir1 = self.txt_dir1.text().strip()
        dir2 = self.txt_dir2.text().strip()
        metadata = self.txt_metadata.text().strip()
        
        if not dir1 or not dir2:
            self.parent.mostrar_error("Ambas direcciones son requeridas")
            return
        
        if dir1 not in self.parent.gestor.direcciones or dir2 not in self.parent.gestor.direcciones:
            self.parent.mostrar_error("Una o ambas direcciones no existen")
            return
        
        try:
            meta = json.loads(metadata) if metadata else None
            self.parent.gestor.conectar_direcciones(dir1, dir2, meta)
            self.parent.mostrar_mensaje_estado(f"Direcciones '{dir1}' y '{dir2}' conectadas")
        except json.JSONDecodeError:
            self.parent.mostrar_error("El formato de metadata no es JSON válido")