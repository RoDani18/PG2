import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import "leaflet/dist/leaflet.css";

function MapaRutas() {
  return (
    <div className="h-64 rounded overflow-hidden shadow">
      <MapContainer center={[14.6349, -90.5069]} zoom={13} style={{ height: "100%", width: "100%" }}>
        <TileLayer
          attribution='&copy; OpenStreetMap'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        <Marker position={[14.6349, -90.5069]}>
          <Popup>📦 Ruta asignada aquí</Popup>
        </Marker>
      </MapContainer>
    </div>
  );
}
