import { MapContainer, TileLayer, Marker, Polyline, Popup } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import L from "leaflet";

const MapaRuta = () => {
  const lat = parseFloat(localStorage.getItem("lat"));
  const lng = parseFloat(localStorage.getItem("lng"));
  const destino = localStorage.getItem("destino");
  const tiempo = localStorage.getItem("tiempo");

  const origen = [
  parseFloat(localStorage.getItem("origen_lat")) || 14.6099,
  parseFloat(localStorage.getItem("origen_lng")) || -90.5133
];

  const destinoCoords = [lat, lng];

  // 🛣️ Ruta real por calles (formato: [[lat, lng], [lat, lng], ...])
  const ruta = JSON.parse(localStorage.getItem("ruta") || "[]");

  const icono = new L.Icon({
    iconUrl: "https://cdn-icons-png.flaticon.com/512/684/684908.png",
    iconSize: [32, 32],
  });

  return (
    <MapContainer center={origen} zoom={13} style={{ height: "400px", width: "100%" }}>
      <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
      
      <Marker position={origen} icon={icono}>
        <Popup>📦 Centro de distribución</Popup>
      </Marker>

      <Marker position={destinoCoords} icon={icono}>
        <Popup>📍 Destino: {destino} <br />⏱️ Tiempo estimado: {tiempo}</Popup>
      </Marker>

      {/* 🛣️ Ruta real trazada */}
      {ruta.length > 0 && <Polyline positions={ruta} color="blue" />}
    </MapContainer>
  );
};

export default MapaRuta;
