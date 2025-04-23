// src/types/map.ts
export interface Coordinates {
  lat: number;
  lng: number;
}

export interface AttractionMarker {
  id: string; // Hacerlo siempre requerido
  lat: number;
  lng: number;
  name: string;
  category: string;
  iconUrl?: string; // Opcional para personalización
}

export interface MapProps {
  center: Coordinates;
  zoom?: number;
  attractions?: AttractionMarker[];
  onMarkerClick?: (marker: AttractionMarker) => void;
  selectedMarkerId?: string | null;
  className?: string;
  style?: React.CSSProperties;
}
