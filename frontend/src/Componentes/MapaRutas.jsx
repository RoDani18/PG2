import { useEffect, useState } from "react";
import { MapContainer, TileLayer, Marker, Popup, useMap } from "react-leaflet";
import "leaflet/dist/leaflet.css";

// 🔄 Componente para recentrar el mapa cuando cambian las coordenadas
function RecentrarMapa({ lat, lng }) {
  const map = useMap();
  useEffect(() => {
    if (lat && lng && !isNaN(lat) && !isNaN(lng)) {
      map.setView([lat, lng], 15);
    }
  }, [lat, lng]);
  return null;
}

export default function MapaRutas() {
  const [lat, setLat] = useState(null);
  const [lng, setLng] = useState(null);
  const [destino, setDestino] = useState("");
  const [estado, setEstado] = useState("");
  const [tiempo, setTiempo] = useState("");

  useEffect(() => {
    const update = () => {
      setLat(parseFloat(localStorage.getItem("lat")));
      setLng(parseFloat(localStorage.getItem("lng")));
      setDestino(localStorage.getItem("destino") || "");
      setEstado(localStorage.getItem("estado") || "");
      setTiempo(localStorage.getItem("tiempo") || "");
    };

    update(); // primera carga

    const interval = setInterval(update, 10000); // 🔁 actualiza cada 10 segundos

    window.addEventListener("mostrarMapaRuta", update);

    return () => {
      clearInterval(interval);
      window.removeEventListener("mostrarMapaRuta", update);
    };
  }, []);

  // 🧼 Validación de coordenadas
  if (!lat || !lng || isNaN(lat) || isNaN(lng)) {
    return <div className="p-4">📭 Ubicación no disponible.</div>;
  }

  return (
    <MapContainer center={[lat, lng]} zoom={15} style={{ height: "300px", width: "100%", borderRadius: "8px" }}>
      <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
      <RecentrarMapa lat={lat} lng={lng} />
      <Marker position={[lat, lng]}>
        <Popup>
          🧭 Repartidor en ruta<br />
          Destino: {destino}<br />
          Estado: {estado}<br />
          Tiempo estimado: {tiempo}
        </Popup>
      </Marker>
    </MapContainer>
  );
}
