import { Marker } from "google.maps";

declare global {
  interface Window {
    google: typeof google;
  }
}

// Extender los tipos de marcador si es necesario
declare module "google.maps" {
  interface Marker {
    customData?: any;
  }
}
