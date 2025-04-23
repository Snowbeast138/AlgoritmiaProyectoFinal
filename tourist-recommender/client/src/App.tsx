// src/App.tsx
import React, { useState } from "react";
import Map from "./components/Map";
import { AttractionMarker } from "./types/map";

const App = () => {
  const [selectedMarker, setSelectedMarker] = useState<AttractionMarker | null>(
    null
  );

  const attractions: AttractionMarker[] = [
    {
      id: "1",
      lat: 40.4168,
      lng: -3.7038,
      name: "Palacio Real",
      category: "museum",
      iconUrl: "https://maps.google.com/mapfiles/ms/icons/red-dot.png",
    },
    {
      id: "2",
      lat: 40.4135,
      lng: -3.6921,
      name: "Parque del Retiro",
      category: "park",
    },
  ];

  return (
    <div style={{ height: "100vh", width: "100%" }}>
      <Map
        center={{ lat: 40.4168, lng: -3.7038 }}
        attractions={attractions}
        onMarkerClick={(marker) => setSelectedMarker(marker)}
        selectedMarkerId={selectedMarker?.id}
        style={{ height: "80vh" }}
      />
    </div>
  );
};

export default App;
