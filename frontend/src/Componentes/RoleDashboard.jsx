import PanelAdmin from "./PanelAdmin";
import PanelEmpleado from "./PanelEmpleado";
import PanelCliente from "./PanelCliente";

export default function RoleDashboard({ email }) {
  const rol = localStorage.getItem("rol");

  const logout = () => {
    localStorage.clear();
    window.location.reload();
  };

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-2xl font-bold">Bienvenido, {rol}</h1>
        <button onClick={logout} className="bg-red-500 text-white px-4 py-2 rounded">
          Cerrar sesión
        </button>
      </div>

      {rol === "admin" && <PanelAdmin />}
      {rol === "empleado" && <PanelEmpleado />}
      {rol === "cliente" && <PanelCliente />}
    </div>
  );
}
