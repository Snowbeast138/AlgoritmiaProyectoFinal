// client/src/pages/Results.tsx
import React from "react";
import Map from "../components/Map";
import { IAttraction } from "../types/Attraction"; // Asegúrate que la importación es correcta

interface ResultsProps {
  attractions: IAttraction[];
}

const Results: React.FC<ResultsProps> = ({ attractions }) => {
  // Obtener coordenadas del primer atractivo o usar Madrid como fallback
  const firstAttraction = attractions[0]?.location || {
    lat: 40.4168,
    lng: -3.7038,
  };

  // Convertir IAttraction a AttractionMarker (para el componente Map)
  const mapAttractions = attractions.map((att) => ({
    id: att.id, // Asegurar que el id está incluido
    lat: att.location.lat,
    lng: att.location.lng,
    name: att.name,
    category: att.categories[0] || "generic", // Tomar la primera categoría
    averageVisitDuration: att.averageVisitDuration, // Opcional: incluir si lo necesitas
  }));

  return (
    <div className="results-container">
      <h2>Rutas Recomendadas</h2>

      <div className="map-container">
        <Map
          center={firstAttraction}
          attractions={mapAttractions}
          zoom={12}
          onMarkerClick={(marker) => {
            console.log("Atracción seleccionada:", marker);
            // Puedes añadir lógica adicional al hacer clic
          }}
        />
      </div>

      <div className="attractions-list">
        <h3>Itinerario</h3>
        <ul>
          {attractions.map((att, index) => (
            <li key={att.id} className="attraction-item">
              <span className="attraction-number">{index + 1}.</span>
              <div className="attraction-info">
                <h4>{att.name}</h4>
                <p>
                  <strong>Duración:</strong> {att.averageVisitDuration} minutos
                  {att.price && (
                    <span>
                      , <strong>Precio:</strong> {att.price.adult}€ (Adulto)
                      {att.price.child && `, ${att.price.child}€ (Niño)`}
                      {att.price.senior && `, ${att.price.senior}€ (Senior)`}
                    </span>
                  )}
                </p>
                {att.categories.length > 0 && (
                  <div className="categories">
                    {att.categories.map((cat) => (
                      <span key={cat} className="category-tag">
                        {cat}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
};

export default Results;
