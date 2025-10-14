import Inventario from "../pages/Inventario";
import Pedidos from "../pages/Pedidos";

export default function Dashboard({ rol }) {
  return (
    <div>
      <h1 className="text-2xl font-bold">Bienvenido, {rol}</h1>
      {rol === "admin" && <Inventario />}
      {rol === "empleado" && <Pedidos />}
      {/* Puedes agregar más vistas por rol */}
    </div>
  );
}
