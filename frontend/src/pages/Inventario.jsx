import { useEffect, useState } from "react";
import axios from "../backend";

export default function Inventario() {
  const [productos, setProductos] = useState([]);
  const [editando, setEditando] = useState(null);
  const [nuevoNombre, setNuevoNombre] = useState("");

  useEffect(() => {
    cargarProductos();
  }, []);

  const cargarProductos = async () => {
    try {
      const res = await axios.get("/inventarios");
      setProductos(res.data);
    } catch (err) {
      alert("Error al cargar productos");
    }
  };

  const eliminarProducto = async (id) => {
    if (!confirm("¿Eliminar este producto?")) return;
    try {
      await axios.delete(`/inventarios/${id}`);
      cargarProductos();
    } catch (err) {
      alert("Error al eliminar");
    }
  };

  const editarProducto = async (id) => {
    try {
      await axios.put(`/inventarios/${id}`, { nombre: nuevoNombre });
      setEditando(null);
      setNuevoNombre("");
      cargarProductos();
    } catch (err) {
      alert("Error al editar");
    }
  };

  return (
    <div className="p-4">
      <h2 className="text-xl font-bold mb-4">Inventario</h2>
      <table className="table-auto w-full border">
        <thead>
          <tr className="bg-gray-200">
            <th>ID</th>
            <th>Nombre</th>
            <th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          {productos.map(p => (
            <tr key={p.id} className="border-t">
              <td>{p.id}</td>
              <td>
                {editando === p.id ? (
                  <input value={nuevoNombre} onChange={e => setNuevoNombre(e.target.value)} />
                ) : (
                  p.nombre
                )}
              </td>
              <td>
                {editando === p.id ? (
                  <>
                    <button onClick={() => editarProducto(p.id)} className="btn mr-2">Guardar</button>
                    <button onClick={() => setEditando(null)} className="btn">Cancelar</button>
                  </>
                ) : (
                  <>
                    <button onClick={() => {
                      setEditando(p.id);
                      setNuevoNombre(p.nombre);
                    }} className="btn mr-2">Editar</button>
                    <button onClick={() => eliminarProducto(p.id)} className="btn">Eliminar</button>
                  </>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
