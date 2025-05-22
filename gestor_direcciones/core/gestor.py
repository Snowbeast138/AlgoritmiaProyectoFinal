# Importaciones estándar
import json
import heapq
import math
import itertools
from math import radians, sin, cos, sqrt, atan2
from typing import Dict, List, Optional, Tuple
from datetime import datetime

# Importaciones de terceros
import networkx as nx
import requests
import polyline
import folium
import branca

# Importaciones propias
from ..api.nominatim import NominatimAPI

class GestorDirecciones:
    """Clase mejorada para gestionar direcciones, rutas y transporte público"""
    
    def __init__(self):
        self.api = NominatimAPI()
        self.direcciones = {}
        self.grafo = nx.Graph()
        self.transporte_grafo = nx.MultiDiGraph()  # Grafo para transporte público
    
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
        """Conecta dos direcciones en el grafo con metadatos opcionales"""
        if dir1 in self.direcciones and dir2 in self.direcciones:
            if metadata is None:
                metadata = {}
            if 'distancia' not in metadata:
                metadata['distancia'] = self.calcular_distancia(dir1, dir2)
            self.grafo.add_edge(dir1, dir2, **metadata)
    
    def cargar_json(self, archivo: str):
        """Carga direcciones desde un archivo JSON y reconstruye grafos"""
        try:
            with open(archivo, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.direcciones = data.get('direcciones', {})
                self.grafo = nx.Graph()
                self.transporte_grafo = nx.MultiDiGraph()
                
                # Reconstruir nodos
                for direccion, info in self.direcciones.items():
                    self.grafo.add_node(direccion, **info)
                    self.transporte_grafo.add_node(direccion, **info)
                
                # Reconstruir aristas
                for edge in data.get('grafo_edges', []):
                    self.grafo.add_edge(edge[0], edge[1], **edge[2])
                    
                # Reconstruir rutas de transporte si existen
                if 'transporte_rutas' in data:
                    for ruta in data['transporte_rutas']:
                        self._agregar_ruta_transporte(ruta)
                        
        except Exception as e:
            raise IOError(f"Error al cargar archivo: {str(e)}")
    
    def guardar_json(self, archivo: str):
        """Guarda las direcciones y rutas en un archivo JSON"""
        data = {
            'direcciones': self.direcciones,
            'grafo_edges': list(self.grafo.edges(data=True)),
            'transporte_rutas': self._obtener_rutas_transporte_para_guardar()
        }
        with open(archivo, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def calcular_distancia(self, dir1: str, dir2: str) -> float:
        """Versión robusta del cálculo de distancia haversine"""
        try:
            if dir1 not in self.direcciones or dir2 not in self.direcciones:
                raise ValueError("Una o ambas direcciones no existen")
                
            coords1 = self.direcciones[dir1]['coordenadas']
            coords2 = self.direcciones[dir2]['coordenadas']
            
            # Validación de coordenadas
            for coord in [coords1['lat'], coords1['lon'], coords2['lat'], coords2['lon']]:
                if not isinstance(coord, (int, float)):
                    raise ValueError(f"Coordenada inválida: {coord}")
            
            lat1, lon1 = radians(float(coords1['lat'])), radians(float(coords1['lon']))
            lat2, lon2 = radians(float(coords2['lat'])), radians(float(coords2['lon']))
            
            dlat = lat2 - lat1
            dlon = lon2 - lon1
            a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
            return 6371 * 2 * atan2(sqrt(a), sqrt(1-a))  # Radio Tierra en km
            
        except Exception as e:
            raise ValueError(f"Error calculando distancia: {str(e)}")
    
    # --- Métodos para rutas óptimas ---
    
    def encontrar_ruta_optima(self, origen: str, destinos: List[str], 
                         criterio: str = 'distancia', transporte: str = 'privado') -> Dict:
        """Versión con manejo robusto de errores"""
        try:
            # Validación inicial de parámetros
            if not isinstance(origen, str) or not all(isinstance(d, str) for d in destinos):
                raise ValueError("Las direcciones deben ser strings")
                
            # Convertir criterio a minúsculas
            criterio = criterio.lower()
            if criterio not in ['distancia', 'tiempo', 'transbordos']:
                raise ValueError("Criterio debe ser 'distancia', 'tiempo' o 'transbordos'")
                
            # Resto de la implementación...
            # ... (mantener el resto de tu implementación actual)
            
        except Exception as e:
            raise ValueError(f"No se pudo calcular la ruta: {str(e)}")

        def _formatear_ruta_para_ui(self, ruta, criterio, transporte):
            """Formatea los resultados para la interfaz gráfica"""
            # Calcular métricas adicionales
            distancia_total = sum(
                self.calcular_distancia(ruta['ruta'][i], ruta['ruta'][i+1])
                for i in range(len(ruta['ruta'])-1)
            )
            
            tiempo_total = ruta['coste'] if criterio == 'tiempo' else (
                distancia_total * 2 if transporte == 'privado' else ruta['coste']
            )
            
            transbordos = sum(
                1 for i in range(len(ruta['ruta'])-1)
                if self._es_transbordo(ruta['ruta'][i], ruta['ruta'][i+1])
            ) if transporte != 'privado' else 0
            
            return {
                'ruta': ruta['ruta'],
                'geometria': ruta['geometria'],
                'instrucciones': ruta['instrucciones'],
                'distancia_total': distancia_total,
                'tiempo_total': tiempo_total,
                'transbordos': transbordos,
                'criterio': criterio,
                'transporte': transporte
            }

    def _es_transbordo(self, origen, destino):
        """Determina si hay transbordo entre dos puntos"""
        # Implementar lógica según tu modelo de transporte
        return False
    
    def _calcular_ruta_multidestino(self, grafo, origen, destinos, criterio, transporte):
        """Algoritmo mejorado para múltiples destinos con optimización"""
        # Generar todas las permutaciones posibles de destinos
        permutaciones = itertools.permutations(destinos)
        
        mejor_ruta = None
        mejor_coste = float('inf')
        
        # Evaluar cada posible orden de visita
        for perm in permutaciones:
            ruta_actual = [origen]
            coste_actual = 0
            geometria = []
            instrucciones = []
            
            # Calcular segmentos
            previo = origen
            for destino in perm:
                segmento = self._calcular_ruta_simple(grafo, previo, destino, criterio, transporte)
                ruta_actual.extend(segmento['ruta'][1:])
                coste_actual += segmento['coste']
                geometria.extend(segmento['geometria'])
                instrucciones.extend(segmento['instrucciones'])
                previo = destino
            
            # Verificar si es la mejor ruta hasta ahora
            if coste_actual < mejor_coste:
                mejor_ruta = {
                    'ruta': ruta_actual,
                    'coste': coste_actual,
                    'geometria': geometria,
                    'instrucciones': instrucciones
                }
                mejor_coste = coste_actual
        
        return mejor_ruta
    
    def _calcular_ruta_simple(self, grafo, origen, destino, criterio, transporte):
        """Calcula ruta entre dos puntos usando Dijkstra"""
        try:
            if criterio == 'distancia':
                peso = 'distancia'
            elif criterio == 'tiempo':
                peso = 'duracion' if transporte != 'privado' else 'distancia'
            else:  # transbordos
                peso = None  # Cuenta nodos
            
            if peso:
                path = nx.dijkstra_path(grafo, origen, destino, weight=peso)
                cost = nx.dijkstra_path_length(grafo, origen, destino, weight=peso)
            else:
                path = nx.shortest_path(grafo, origen, destino)
                cost = len(path) - 1
            
            return {
                'ruta': path,
                'coste': cost,
                'geometria': self._obtener_geometria(path),
                'instrucciones': self._generar_instrucciones(path, transporte)
            }
        except nx.NetworkXNoPath:
            # Fallback a ruta directa si no hay conexión
            return {
                'ruta': [origen, destino],
                'coste': self.calcular_distancia(origen, destino),
                'geometria': self._obtener_geometria([origen, destino]),
                'instrucciones': self._generar_instrucciones([origen, destino], transporte)
            }
        
    
    def _obtener_geometria(self, ruta: List[str]) -> List[Dict[str, float]]:
        """Versión segura para obtener coordenadas"""
        geometria = []
        for punto in ruta:
            try:
                coords = self.direcciones[punto]['coordenadas']
                # Validar y convertir coordenadas
                lat = float(coords['lat'])
                lon = float(coords['lon'])
                geometria.append({'lat': lat, 'lon': lon})
            except (KeyError, ValueError, TypeError) as e:
                raise ValueError(f"Coordenadas inválidas para {punto}: {str(e)}")
        return geometria
    
    def _generar_instrucciones(self, ruta, transporte):
        """Genera instrucciones de navegación"""
        instrucciones = []
        for i in range(len(ruta)-1):
            origen = ruta[i]
            destino = ruta[i+1]
            
            distancia = self.calcular_distancia(origen, destino)
            duracion = distancia * 2 if transporte == 'privado' else 3  # mins/km
            
            instrucciones.append({
                'instruccion': f"De {origen} a {destino}",
                'distancia': distancia,
                'duracion': duracion * 60,  # en segundos
                'tipo': transporte
            })
        
        return instrucciones
    
    def _vecino_mas_cercano(self, matriz_costos: List[List[float]], inicio: int) -> Tuple[List[int], float]:
        """Implementación del algoritmo del vecino más cercano"""
        n = len(matriz_costos)
        visitados = set([inicio])
        ruta = [inicio]
        costo_total = 0.0
        
        while len(visitados) < n:
            ultimo = ruta[-1]
            mejor_costo = float('inf')
            mejor_idx = -1
            
            for i in range(n):
                if i not in visitados and matriz_costos[ultimo][i] < mejor_costo:
                    mejor_costo = matriz_costos[ultimo][i]
                    mejor_idx = i
            
            if mejor_idx == -1:  # No se encontró conexión
                break
                
            visitados.add(mejor_idx)
            ruta.append(mejor_idx)
            costo_total += mejor_costo
        
        # Regresar al inicio para completar el ciclo (opcional)
        # costo_total += matriz_costos[ruta[-1]][ruta[0]]
        # ruta.append(ruta[0])
        
        return ruta, costo_total
    
    # --- Métodos para transporte público ---
    
    def obtener_ruta_transporte_publico(self, origen: str, destino: str) -> Dict:
        """
        Obtiene ruta de transporte público usando OSRM/OpenTripPlanner.
        
        Args:
            origen: Dirección de inicio
            destino: Dirección destino
            
        Returns:
            Dict con información de la ruta
        """
        if origen not in self.direcciones or destino not in self.direcciones:
            raise ValueError("Una o ambas direcciones no existen")
            
        coords_origen = self.direcciones[origen]['coordenadas']
        coords_destino = self.direcciones[destino]['coordenadas']
        
        # Usando OSRM (Open Source Routing Machine)
        try:
            url = f"http://router.project-osrm.org/route/v1/driving/" \
                  f"{coords_origen['lon']},{coords_origen['lat']};" \
                  f"{coords_destino['lon']},{coords_destino['lat']}" \
                  f"?overview=full&geometries=polyline"
            
            response = requests.get(url)
            if response.status_code != 200:
                return self._ruta_alternativa(origen, destino)
                
            data = response.json()
            return self._procesar_ruta_osrm(data)
            
        except Exception as e:
            print(f"Error al obtener ruta: {str(e)}")
            return self._ruta_alternativa(origen, destino)
    
    def _procesar_ruta_osrm(self, data: Dict) -> Dict:
        """Procesa la respuesta de OSRM para extraer información de la ruta"""
        route = data['routes'][0]
        decoded_path = polyline.decode(route['geometry'])
        
        instrucciones = []
        for leg in route['legs']:
            for step in leg['steps']:
                instrucciones.append({
                    'instruccion': step.get('name', ''),
                    'distancia': step['distance'],
                    'duracion': step['duration'],
                    'tipo': 'conducción'  # OSRM solo provee conducción
                })
        
        return {
            'duracion_total': route['duration'],
            'distancia_total': route['distance'],
            'instrucciones': instrucciones,
            'geometria': decoded_path,
            'modo': 'conducción'
        }
    
    def _ruta_alternativa(self, origen: str, destino: str) -> Dict:
        """Crea una ruta alternativa cuando falla la API"""
        distancia = self.calcular_distancia(origen, destino)
        return {
            'duracion_total': distancia * 3 * 60,  # Estimado: 3 min/km
            'distancia_total': distancia,
            'instrucciones': [{
                'instruccion': f"Conducir de {origen} a {destino}",
                'distancia': distancia,
                'duracion': distancia * 3 * 60,
                'tipo': 'conducción_estimada'
            }],
            'geometria': [
                (self.direcciones[origen]['coordenadas']['lat'], 
                self.direcciones[origen]['coordenadas']['lon']),
                (self.direcciones[destino]['coordenadas']['lat'], 
                self.direcciones[destino]['coordenadas']['lon'])
            ],
            'modo': 'estimado'
        }
    
    def _agregar_ruta_transporte(self, ruta_data: Dict):
        """Agrega una ruta de transporte al grafo"""
        for i in range(len(ruta_data['paradas'])-1):
            origen = ruta_data['paradas'][i]
            destino = ruta_data['paradas'][i+1]
            
            self.transporte_grafo.add_edge(
                origen, destino,
                tipo=ruta_data['tipo'],
                linea=ruta_data['linea'],
                duracion=ruta_data.get('duraciones', [])[i] if 'duraciones' in ruta_data else 5,
                distancia=self.calcular_distancia(origen, destino)
            )
    
    def _obtener_rutas_transporte_para_guardar(self) -> List[Dict]:
        """Prepara datos de rutas de transporte para guardar en JSON"""
        rutas = []
        # Implementación simplificada - deberías expandir esto
        for edge in self.transporte_grafo.edges(data=True):
            rutas.append({
                'paradas': [edge[0], edge[1]],
                'tipo': edge[2].get('tipo', 'bus'),
                'linea': edge[2].get('linea', ''),
                'duraciones': [edge[2].get('duracion', 5)]
            })
        return rutas
    
    def obtener_mapa_rutas(self, ruta: Dict) -> str:
   
        if not ruta or not ruta.get('ruta'):
            raise ValueError("La ruta está vacía o es inválida")
            
        # Crear mapa centrado en el primer punto
        primera_dir = ruta['ruta'][0]
        coords_inicio = self.direcciones[primera_dir]['coordenadas']
        
        mapa = folium.Map(
            location=[coords_inicio['lat'], coords_inicio['lon']],
            zoom_start=13,
            tiles='cartodbpositron'  # Más limpio para rutas
        )
        
        # Añadir marcadores para cada punto con iconos según su posición
        for i, direccion in enumerate(ruta['ruta']):
            coords = self.direcciones[direccion]['coordenadas']
            
            # Personalizar popup con información relevante
            popup_text = f"""
            <b>{i+1}. {direccion}</b><br>
            <i>Tipo: {self.direcciones[direccion].get('tipo', 'N/A')}</i>
            """
            
            if i == 0:
                # Marcador de inicio
                icono = folium.Icon(color='green', icon='home', prefix='fa')
            elif i == len(ruta['ruta'])-1:
                # Marcador de fin
                icono = folium.Icon(color='red', icon='flag', prefix='fa')
            else:
                # Marcadores intermedios
                icono = folium.Icon(color='blue', icon='circle', prefix='fa')
            
            folium.Marker(
                [coords['lat'], coords['lon']],
                popup=folium.Popup(popup_text, max_width=300),
                icon=icono,
                tooltip=f"Punto {i+1}"
            ).add_to(mapa)
        
        # Añadir línea de la ruta principal
        if 'geometria' in ruta and ruta['geometria']:
            puntos_ruta = [
                [p['lat'], p['lon']] for p in ruta['geometria']
            ]
        else:
            # Fallback: línea recta entre puntos si no hay geometría detallada
            puntos_ruta = [
                [self.direcciones[p]['coordenadas']['lat'], 
                self.direcciones[p]['coordenadas']['lon']] 
                for p in ruta['ruta']
            ]
        
        # Color según tipo de transporte
        color_ruta = {
            'privado': 'blue',
            'publico': 'green',
            'combinado': 'purple'
        }.get(ruta.get('transporte', 'privado'), 'blue')
        
        folium.PolyLine(
            puntos_ruta,
            color=color_ruta,
            weight=3,
            opacity=0.8,
            popup=f"""
            <b>Ruta {ruta.get('transporte', '').capitalize()}</b><br>
            Distancia: {ruta.get('distancia_total', 0):.2f} km<br>
            Tiempo: {ruta.get('tiempo_total', 0)/60:.1f} minutos<br>
            Criterio: {ruta.get('criterio', 'N/A')}
            """
        ).add_to(mapa)
        
        # Añadir capa de transbordos si es transporte público
        if ruta.get('transporte') in ['publico', 'combinado'] and ruta.get('transbordos', 0) > 0:
            self._agregar_transbordos_mapa(mapa, ruta)
        
        # Añadir leyenda
        self._agregar_leyenda_mapa(mapa, ruta.get('transporte'))
        
        # Guardar mapa
        archivo_mapa = f"ruta_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        mapa.save(archivo_mapa)
        
        return archivo_mapa

def _agregar_transbordos_mapa(self, mapa, ruta):
    """Añade marcadores especiales para transbordos"""
    # Implementación básica - deberías mejorarla según tu modelo de transporte
    for i in range(len(ruta['ruta'])-1):
        origen = ruta['ruta'][i]
        destino = ruta['ruta'][i+1]
        
        if self._es_transbordo(origen, destino):
            coords = self.direcciones[origen]['coordenadas']
            folium.Marker(
                [coords['lat'], coords['lon']],
                icon=folium.Icon(color='orange', icon='exchange-alt', prefix='fa'),
                popup=f"Transbordo en {origen}",
                tooltip="Transbordo"
            ).add_to(mapa)

def _agregar_leyenda_mapa(self, mapa, tipo_transporte):
    """Añade una leyenda informativa al mapa"""
    leyenda_html = f"""
    <div style="
        position: fixed; 
        bottom: 50px; 
        left: 50px; 
        width: 180px; 
        height: auto;
        background: white;
        padding: 10px;
        border-radius: 5px;
        border: 1px solid grey;
        z-index: 9999;
        font-size: 12px;
    ">
        <b>Leyenda del Mapa</b><br>
        <i class="fa fa-home" style="color: green"></i> Origen<br>
        <i class="fa fa-flag" style="color: red"></i> Destino<br>
        <i class="fa fa-circle" style="color: blue"></i> Puntos intermedios<br>
    """
    
    if tipo_transporte in ['publico', 'combinado']:
        leyenda_html += """
        <i class="fa fa-exchange-alt" style="color: orange"></i> Transbordo<br>
        """
    
    leyenda_html += f"""
        <div style="height: 3px; background: {{
            'privado': 'blue',
            'publico': 'green',
            'combinado': 'purple'
        }}.get('{tipo_transporte}', 'blue'); margin-top: 5px;"></div>
        Ruta {tipo_transporte.capitalize() if tipo_transporte else ''}
    </div>
    """
    
    mapa.get_root().html.add_child(folium.Element(leyenda_html))