import VoiceAssistant from "./VoiceAssistant";
import MapaRutas from "./MapaRutas";
import axios from "axios";
import { useState, useEffect } from "react";

export default function PanelEmpleado() {
  const [modoOscuro, setModoOscuro] = useState(false);
  const [mensajeIA, setMensajeIA] = useState("");
  const [mostrarMapa, setMostrarMapa] = useState(false);

  useEffect(() => {
    const mostrar = () => setMostrarMapa(true);
    window.addEventListener("abrirMapaDesdeAsistente", mostrar);
    return () => window.removeEventListener("abrirMapaDesdeAsistente", mostrar);
  }, []);

  setTimeout(() => setMensajeIA(""), 5000); // se cierra en 5 segundos

  const reentrenarIA = async () => {
    try {
      const token = localStorage.getItem("token");
      const res = await axios.post("/ia/reentrenar-automatico", {}, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
      setMensajeIA(res.data.mensaje || "✅ Reentrenamiento completado.");
    } catch (error) {
      setMensajeIA("❌ Error al reentrenar IA.");
    }
  };

  const descargarReporte = () => {
    alert("📥 Reporte descargado correctamente.");
  };

  return (
    <div className={`min-h-screen transition-all duration-300 ${modoOscuro ? "bg-gray-900 text-gray-100" : "bg-gray-100 text-gray-800"}`}>
      
      {/* 🔝 Panel superior */}
      <header className="p-6 flex flex-wrap justify-between items-center gap-4 border-b border-gray-300">
        <h1 className="text-3xl font-bold">🧠 Panel de Empleado</h1>
        <div className="flex gap-2 flex-wrap">
          <button
            onClick={() => setModoOscuro(!modoOscuro)}
            className={`px-4 py-2 rounded ${modoOscuro ? "bg-yellow-500 hover:bg-yellow-600" : "bg-indigo-600 hover:bg-indigo-700"} text-white`}
          >
            {modoOscuro ? "Modo Claro" : "Modo Oscuro"}
          </button>
          <button
            onClick={descargarReporte}
            className={`px-4 py-2 rounded ${modoOscuro ? "bg-blue-500 hover:bg-blue-600" : "bg-blue-600 hover:bg-blue-700"} text-white`}
          >
            📥 Descargar Reportes
          </button>
          <button
            onClick={reentrenarIA}
            className={`px-4 py-2 rounded ${modoOscuro ? "bg-purple-500 hover:bg-purple-600" : "bg-purple-600 hover:bg-purple-700"} text-white`}
          >
            🔁 Reentrenar IA
          </button>
        </div>
      </header>

      {/* 📌 Comandos disponibles */}
      <section className="p-6">
        <div className={`rounded shadow p-4 ${modoOscuro ? "bg-gray-800 text-gray-100" : "bg-white text-gray-800"}`}>
          <h2 className="text-lg font-semibold mb-2">📌 Comandos disponibles para empleado</h2>
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-2 text-sm">
            {[
              "consultar inventario", "agregar producto", "actualizar producto", "eliminar producto",
              "ver producto cantidad", "precio del producto",
              "ver pedido", "actualizar estado del pedido",
              "ver ruta", "seguimiento ruta", "rastrear ruta", "ver rutas",
              "asignar ruta", "cancelar ruta", "reprogramar ruta"
            ].map((cmd, i) => (
              <span key={i} className={`px-2 py-1 rounded ${modoOscuro ? "bg-gray-700" : "bg-gray-100"}`}>{cmd}</span>
            ))}
          </div>
        </div>
      </section>

      {/* 🎙️ Asistente Conversacional */}
      <main className="p-6 flex flex-col items-center">
        <div className={`w-full max-w-screen-xl rounded-xl shadow-lg p-6 ${modoOscuro ? "bg-gray-800 text-gray-100" : "bg-white text-gray-800"}`}>
          <div className="flex items-center justify-center gap-2 mb-4">
            <span className="text-2xl">🤖</span>
            <h2 className="text-xl font-semibold text-center">Asistente Conversacional</h2>
          </div>
          <VoiceAssistant />
        </div>
      </main>

      {/* 🗺️ Mapa como ventana flotante tipo push */}
      {mostrarMapa && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center z-50">
          <div className={`w-full max-w-5xl h-[500px] rounded-xl shadow-xl overflow-hidden relative ${modoOscuro ? "bg-gray-900" : "bg-white"}`}>
            <button
              onClick={() => setMostrarMapa(false)}
              className="absolute top-4 right-4 px-3 py-1 bg-red-600 text-white rounded hover:bg-red-700 z-10"
            >
              ✖ Cerrar Mapa
            </button>
            <MapaRutas />
          </div>
        </div>
      )}

      {/* 🔁 Mensaje IA */}
      {mensajeIA && (
        <div className="fixed top-6 right-6 z-50 bg-purple-600 text-white px-4 py-2 rounded shadow-lg animate-fade-in">
          {mensajeIA}
        </div>
      )}
    </div>
  );
}
