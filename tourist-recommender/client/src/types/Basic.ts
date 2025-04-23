// Tipos fundamentales reutilizables
export type Coordinates = {
  lat: number;
  lng: number;
};

export type TimeRange = {
  open: number; // Hora en formato 24h (0-23)
  close: number;
};

export type DayOfWeek = 0 | 1 | 2 | 3 | 4 | 5 | 6; // 0=Domingo, 1=Lunes, etc.
