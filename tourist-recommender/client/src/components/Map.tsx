// src/components/Map/Map.tsx
import React, { useEffect, useRef } from "react";
import { Loader } from "@googlemaps/js-api-loader";
import { MapProps, AttractionMarker } from "../types/map";

const Map: React.FC<MapProps> = ({
  center,
  zoom = 13,
  attractions = [],
  onMarkerClick,
  selectedMarkerId,
  className = "",
  style = { height: "500px", width: "100%" },
}) => {
  const mapRef = useRef<HTMLDivElement>(null);
  const markersRef = useRef<google.maps.Marker[]>([]);
  const infoWindowRef = useRef<google.maps.InfoWindow | null>(null);

  useEffect(() => {
    const loader = new Loader({
      apiKey: process.env.REACT_APP_GOOGLE_MAPS_API_KEY || "",
      version: "weekly",
      libraries: ["places"],
    });

    loader.load().then((google) => {
      if (mapRef.current) {
        const map = new google.maps.Map(mapRef.current, {
          center,
          zoom,
          streetViewControl: false,
          mapTypeControl: false,
        });

        infoWindowRef.current = new google.maps.InfoWindow();

        // Limpiar marcadores anteriores
        markersRef.current.forEach((marker) => marker.setMap(null));
        markersRef.current = [];

        // Añadir nuevos marcadores
        attractions.forEach((attraction) => {
          const marker = new google.maps.Marker({
            position: { lat: attraction.lat, lng: attraction.lng },
            map,
            title: attraction.name,
            icon: attraction.iconUrl || getDefaultIcon(attraction.category),
            zIndex: selectedMarkerId === attraction.id ? 1000 : undefined,
          });

          marker.addListener("click", () => {
            if (onMarkerClick) {
              onMarkerClick(attraction);
            }
            infoWindowRef.current?.setContent(`
              <div>
                <h3>${attraction.name}</h3>
                <p>Categoría: ${attraction.category}</p>
              </div>
            `);
            infoWindowRef.current?.open(map, marker);
          });

          markersRef.current.push(marker);
        });

        // Ajustar vista para incluir todos los marcadores
        if (attractions.length > 0) {
          const bounds = new google.maps.LatLngBounds();
          attractions.forEach((att) => {
            bounds.extend(new google.maps.LatLng(att.lat, att.lng));
          });
          map.fitBounds(bounds);
        }
      }
    });

    return () => {
      markersRef.current.forEach((marker) => {
        google.maps.event.clearInstanceListeners(marker);
      });
    };
  }, [center, attractions, selectedMarkerId]);

  const getDefaultIcon = (category: string): google.maps.Icon | string => {
    const baseUrl = "https://maps.google.com/mapfiles/ms/icons/";
    switch (category) {
      case "museum":
        return `${baseUrl}red-dot.png`;
      case "park":
        return `${baseUrl}green-dot.png`;
      case "restaurant":
        return `${baseUrl}blue-dot.png`;
      default:
        return `${baseUrl}yellow-dot.png`;
    }
  };

  return <div ref={mapRef} className={className} style={style} />;
};

export default Map;
