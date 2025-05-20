import time
import requests
from typing import Dict, Optional


class NominatimAPI:
    """Clase para manejar las interacciones con la API de Nominatim"""
    def __init__(self):
        self.base_url = "https://nominatim.openstreetmap.org/search"
        self.user_agent = "CETI_Algoritmia_Direcciones/1.0"
        self.last_request_time = 0

    def hacer_peticion(self, params: Dict) -> Optional[Dict]:
        """Realiza una petición a la API respetando el rate limiting"""
        elapsed = time.time() - self.last_request_time
        if elapsed < 1.0:
            time.sleep(1.0 - elapsed)
        
        headers = {'User-Agent': self.user_agent}
        
        try:
            response = requests.get(self.base_url, params=params, headers=headers)
            self.last_request_time = time.time()
            return response.json() if response.status_code == 200 else None
        except requests.exceptions.RequestException:
            return None