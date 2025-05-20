import json
import networkx as nx
from math import radians, sin, cos, sqrt, atan2
from typing import Dict, Optional, List
import requests
import polyline
from datetime import datetime


from ..api.nominatim import NominatimAPI


class GestorDirecciones:
    """Clase para gestionar las direcciones y sus relaciones"""
    def __init__(self):
        self.api = NominatimAPI()
        self.direcciones = {}
        self.grafo = nx.Graph()

    def agregar_direccion(self, direccion: str) -> Optional[Dict]:
        """Agrega una nueva dirección consultando Nominatim API"""
        if not direccion:
            return None
            
        if direccion in self.direcciones:
            return self.direcciones[direccion]
            
        params = {
            'q': direccion,
            'format': 'json',
            'addressdetails': 1,
            'limit': 1
        }
        
        data = self.api.hacer_peticion(params)
        if not data or len(data) == 0:
            return None
            
        resultado = data[0]
        info_direccion = {
            'direccion': resultado.get('display_name'),
            'coordenadas': {
                'lat': float(resultado['lat']),
                'lon': float(resultado['lon'])
            },
            'componentes': resultado.get('address', {}),
            'osm_id': resultado['osm_id'],
            'tipo': resultado['type'],
            'categoria': resultado.get('class')
        }
        
        self.direcciones[direccion] = info_direccion
        self.grafo.add_node(direccion, **info_direccion)
        return info_direccion
    
    def conectar_direcciones(self, dir1: str, dir2: str, metadata: Dict = None):
        """Conecta dos direcciones en el grafo"""
        if dir1 in self.direcciones and dir2 in self.direcciones:
            self.grafo.add_edge(dir1, dir2, **metadata if metadata else {})
    
    def obtener_vecinos(self, direccion: str) -> List[str]:
        """Obtiene direcciones conectadas a una dirección dada"""
        return list(self.grafo.neighbors(direccion)) if direccion in self.grafo else []
    
    def guardar_json(self, archivo: str):
        """Guarda las direcciones en un archivo JSON"""
        with open(archivo, 'w', encoding='utf-8') as f:
            json.dump({
                'direcciones': self.direcciones,
                'grafo_edges': list(self.grafo.edges(data=True))
            }, f, ensure_ascii=False, indent=2)
    
    def cargar_json(self, archivo: str):
        """Carga direcciones desde un archivo JSON"""
        try:
            with open(archivo, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.direcciones = data.get('direcciones', {})
                self.grafo = nx.Graph()
                
                for direccion, info in self.direcciones.items():
                    self.grafo.add_node(direccion, **info)
                
                for edge in data.get('grafo_edges', []):
                    self.grafo.add_edge(edge[0], edge[1], **edge[2])
        except Exception as e:
            raise IOError(f"Error al cargar archivo: {str(e)}")

    def calcular_distancia(self, dir1: str, dir2: str) -> float:
        """
        Calcula la distancia en kilómetros entre dos direcciones usando la fórmula haversine.
        """
        if dir1 not in self.direcciones or dir2 not in self.direcciones:
            raise ValueError("Una o ambas direcciones no existen")
            
        coords1 = self.direcciones[dir1]['coordenadas']
        coords2 = self.direcciones[dir2]['coordenadas']
        
        lat1, lon1 = radians(coords1['lat']), radians(coords1['lon'])
        lat2, lon2 = radians(coords2['lat']), radians(coords2['lon'])
        
        # Fórmula haversine
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        distancia = 6371 * c  # Radio de la Tierra en km
        
        return distancia
    
    def encontrar_ruta_optima(self, origen: str, destinos: List[str]) -> Dict:
        """
        Encuentra la ruta óptima para visitar todas las direcciones desde el origen.
        """
        if origen not in self.direcciones:
            raise ValueError("El origen no existe")
            
        for destino in destinos:
            if destino not in self.direcciones:
                raise ValueError(f"La dirección {destino} no existe")
        
        if not destinos:
            return {
                'ruta': [origen],
                'distancias': [],
                'distancia_total': 0
            }
        
        todas = [origen] + destinos
        
        distancias = {}
        for i in range(len(todas)):
            for j in range(i+1, len(todas)):
                dist = self.calcular_distancia(todas[i], todas[j])
                distancias[(i, j)] = dist
                distancias[(j, i)] = dist
        
        visitados = set([0])
        ruta = [0]
        distancia_total = 0
        
        while len(visitados) < len(todas):
            ultimo = ruta[-1]
            min_dist = float('inf')
            mejor_idx = -1
            
            for i in range(len(todas)):
                if i not in visitados:
                    dist = distancias[(ultimo, i)]
                    if dist < min_dist:
                        min_dist = dist
                        mejor_idx = i
            
            if mejor_idx == -1:
                break
                
            visitados.add(mejor_idx)
            ruta.append(mejor_idx)
            distancia_total += min_dist
        
        ruta_nombres = [todas[i] for i in ruta]
        
        distancias_pasos = []
        for i in range(len(ruta)-1):
            distancias_pasos.append(distancias[(ruta[i], ruta[i+1])])
        
        return {
            'ruta': ruta_nombres,
            'distancias': distancias_pasos,
            'distancia_total': distancia_total
        }
    
    def obtener_ruta_transporte_publico(self, origen, destino):
            """
            Obtiene la ruta óptima de transporte público entre dos direcciones
            Devuelve una lista de instrucciones y geometría de la ruta
            """
            if origen not in self.direcciones or destino not in self.direcciones:
                raise ValueError("Una o ambas direcciones no existen")
                
            coords_origen = self.direcciones[origen]['coordenadas']
            coords_destino = self.direcciones[destino]['coordenadas']
            
            # Configuración para OTP (OpenTripPlanner)
            otp_url = "http://router.project-osrm.org/route/v1/driving/"
            
            try:
                # Obtener la ruta de OTP
                response = requests.get(
                    f"{otp_url}{coords_origen['lon']},{coords_origen['lat']};{coords_destino['lon']},{coords_destino['lat']}?overview=full&geometries=polyline"
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return self._procesar_ruta_otp(data)
                else:
                    return {"error": "No se pudo obtener la ruta"}
                    
            except Exception as e:
                return {"error": str(e)}
        
    def _procesar_ruta_otp(self, data):
            """Procesa la respuesta de OTP para extraer instrucciones"""
            route = data['routes'][0]
            decoded_path = polyline.decode(route['geometry'])
            
            instrucciones = []
            for leg in route['legs']:
                for step in leg['steps']:
                    instrucciones.append({
                        'instruccion': step['name'],
                        'distancia': step['distance'],
                        'duracion': step['duration'],
                        'tipo': step['mode']
                    })
            
            return {
                'duracion_total': route['duration'],
                'distancia_total': route['distance'],
                'instrucciones': instrucciones,
                'geometria': decoded_path
            }