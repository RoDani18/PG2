// ...importaciones
import React, { useEffect, useRef, useState } from "react";
import axios from "../Api/backend";
import { FaMicrophone, FaMicrophoneSlash } from "react-icons/fa";

export default function VoiceAssistant() {
  const [activo, setActivo] = useState(false);
  const [estado, setEstado] = useState("🎙 Micrófono apagado");
  const [historial, setHistorial] = useState([]);
  const [alerta, setAlerta] = useState(null);
  const [permisoBloqueado, setPermisoBloqueado] = useState(false);
  const recognitionRef = useRef(null);
  const [rol, setRol] = useState(localStorage.getItem("rol") || "anonimo");
  const [mostrarConfirmacionUbicacion, setMostrarConfirmacionUbicacion] = useState(false);
const [ubicacionConfirmada, setUbicacionConfirmada] = useState(false);

  useEffect(() => {
    const r = localStorage.getItem("rol");
    if (r) setRol(r);
  }, []);

  const comandosPorRol = {
    admin: ["consultar inventario", "agregar producto", "actualizar producto", "eliminar producto", "crear pedido","agregar pedido","ver pedido", "eliminar pedido", "editar pedido","ver rutas", "asignar ruta", "rastrear ruta", "cancelar ruta"],
    empleado: ["consultar inventario", "agregar producto", "actualizar producto", "eliminar producto", "ver pedido", "ver rutas", "asignar ruta", "rastrear ruta", "cancelar ruta"],
    cliente: ["crear pedido", "ver pedido", "eliminar pedido", "editar pedido", "rastrear ruta",],
  };

  useEffect(() => {
    navigator.permissions?.query({ name: "microphone" }).then((result) => {
      if (result.state === "denied") {
        setPermisoBloqueado(true);
        setEstado("🚫 El navegador bloqueó el micrófono");
      }
    });

    const disponibles = comandosPorRol[rol] || [];
    const mensaje = `🧠 Comandos disponibles para ${rol}: ${disponibles.join(", ")}`;
    setHistorial((prev) => [...prev, { tipo: "asistente", texto: mensaje }]);
    hablar(mensaje);
  }, []);

  useEffect(() => {
    if (!("webkitSpeechRecognition" in window)) {
      setEstado("❌ Navegador no soporta reconocimiento de voz");
      return;
    }
  function extraerNombre(texto) {
  const palabras = texto.toLowerCase().split(" ");
  const excluidas = ["precio", "cantidad", "de", "del", "la", "el", "cuánto", "cuanto", "dime"];
  const posibles = palabras.filter(p => !excluidas.includes(p));
  return posibles[posibles.length - 1]; // último término relevante
}


    const recognition = new window.webkitSpeechRecognition();
    recognition.lang = "es-ES";
    recognition.continuous = true;
    recognition.interimResults = false;

    recognition.onstart = () => setEstado("🎧 Escuchando...");
    recognition.onresult = async (event) => {
      const command = event.results[event.results.length - 1][0].transcript;
      setEstado(`🗣 "${command}"`);
      mostrarAlerta(`🗣 Escuchado: "${command}"`);
      setHistorial((prev) => [...prev, { tipo: "usuario", texto: command }]);

      const token = localStorage.getItem("token");
  const rol = localStorage.getItem("rol") || "anonimo";
      
const comandosPermitidos = comandosPorRol[rol] || [];

const res = await axios.post(
  "/ia/probar-ia",
  { texto: command },
  {
    headers: {
      Authorization: `Bearer ${token}`
    }
  }
);

const intencion = res.data.intencion?.toLowerCase();

const intencionNormalizada = intencion.replace(/_/g, " ").trim();
const esPermitido = comandosPermitidos.some(c => c.toLowerCase() === intencionNormalizada);

if (!esPermitido) {
  const msg = `❌ Comando no permitido para tu rol (${rol}). Intención detectada: '${intencion}'`;
  setHistorial((prev) => [...prev, { tipo: "asistente", texto: msg }]);
  hablar(msg);
  return;
}



      // 📦 Consultar inventario
      if (command.toLowerCase().includes("consultar inventario")) {
        try {
          const res = await axios.get("/inventarios");
          const inventario = res.data || [];
          const respuestaTexto = inventario.length
            ? `📦 Tienes ${inventario.length} productos:\n` +
              inventario.map((item) => `• ${item.nombre} (${item.cantidad})`).join("\n")
            : "📦 No se encontraron productos en tu inventario.";
          setHistorial((prev) => [...prev, { tipo: "asistente", texto: respuestaTexto }]);
          hablar(respuestaTexto);
        } catch {
          const error = "❌ Error al consultar inventario";
          setHistorial((prev) => [...prev, { tipo: "asistente", texto: error }]);
          hablar(error);
        }
        return;
      }
      
      if (command.toLowerCase().includes("precio de")) {
        const producto = extraerNombre(command); // función que detecta el nombre del producto
        try {
          const res = await axios.get(`/inventarios/${producto}`);
          const datos = res.data;
          const respuesta = datos?.precio
          ? `💰 El precio de '${producto}' es Q${datos.precio}`
          : `⚠️ No se encontró el producto '${producto}'`;
          setHistorial((prev) => [...prev, { tipo: "asistente", texto: respuesta }]);
          hablar(respuesta);
        } catch {
          const error = "❌ Error al consultar el precio";
          setHistorial((prev) => [...prev, { tipo: "asistente", texto: error }]);
          hablar(error);
        }
        return;
      }

     if (command.toLowerCase().includes("agregar producto")) {
  const tieneDatos = command.match(/\d+.*(precio|quetzales|q)/i);

  // 📝 Modo manual si no hay datos en el texto
  if (!tieneDatos) {
    setTimeout(async () => {
      const nombre = prompt("🛒 Nombre del producto:");
      const cantidad = parseInt(prompt("🔢 Cantidad:"));
      const precio = parseFloat(prompt("💰 Precio:"));

      if (!nombre || isNaN(cantidad) || isNaN(precio)) {
        const msg = "⚠️ Te hace falta nombre, cantidad o precio. Intenta de nuevo.";
        setHistorial((prev) => [...prev, { tipo: "asistente", texto: msg }]);
        hablar(msg);
        return;
      }

      try {
        await axios.post("/inventarios", { nombre, cantidad, precio });
        const msg = `✅ Producto '${nombre}' agregado con éxito.`;
        setHistorial((prev) => [...prev, { tipo: "asistente", texto: msg }]);
        hablar(msg);
      } catch (error) {
        const msg = `❌ Error al agregar producto: ${error.response?.status}`;
        setHistorial((prev) => [...prev, { tipo: "asistente", texto: msg }]);
        hablar(msg);
      }
    }, 500);
    return;
  }

  // 🧠 Modo automático por voz con extracción de entidades
  try {
    const res = await axios.post("/ia/ejecutar-comando", {
      texto: command
    });

    const respuesta = res.data.respuesta || "✅ Comando ejecutado.";
    setHistorial((prev) => [...prev, { tipo: "asistente", texto: respuesta }]);
    hablar(respuesta);
  } catch (error) {
    const msg = `❌ Error al agregar producto por voz: ${error.response?.status || "desconocido"}`;
    setHistorial((prev) => [...prev, { tipo: "asistente", texto: msg }]);
    hablar(msg);
  }
  return;
}




      if (command.toLowerCase().includes("actualizar producto")) {
  const regex = /actualizar producto (.+?) cantidad (\d+) precio (\d+(\.\d+)?)/i;
  const match = command.match(regex);

  let nombre, cantidad, precio;

  if (match) {
    // ✅ Datos extraídos directamente del comando
    nombre = match[1];
    nombre = nombre.replace(/^(es|el|la|producto|actualizar)\s*/i, "").trim();
    nombre = nombre.trim().toLowerCase();
    cantidad = parseInt(match[2]);
    precio = parseFloat(match[3]);
  } else {
    // 📝 Modo manual si no hay datos en el texto
    setTimeout(async () => {
      nombre = prompt("🛒 Producto a actualizar:");
      cantidad = parseInt(prompt("🔢 Nueva cantidad:"));
      precio = parseFloat(prompt("💰 Nuevo precio:"));

      if (!nombre || isNaN(cantidad) || isNaN(precio)) {
        const msg = "⚠️ Te hace falta nombre, cantidad o precio. Intenta de nuevo.";
        setHistorial((prev) => [...prev, { tipo: "asistente", texto: msg }]);
        hablar(msg);
        return;
      }

      try {
        const token = localStorage.getItem("token");
        console.log("🔐 Token usado en PUT:", token);
        await axios.put(`/inventarios/${nombre}`, { cantidad, precio }, {
          headers: {
            Authorization: `Bearer ${token}`
          }
        });
        const msg = `🔄 Producto '${nombre}' actualizado correctamente.`;
        setHistorial((prev) => [...prev, { tipo: "asistente", texto: msg }]);
        hablar(msg);
      } catch (error) {
        const msg = `❌ Error al actualizar el producto '${nombre}': ${error.response?.status}`;
        setHistorial((prev) => [...prev, { tipo: "asistente", texto: msg }]);
        hablar(msg);
      }
    }, 500);
    return;
  }

  // ✅ Si ya tiene datos, ejecuta directo
  try {
    const token = localStorage.getItem("token");
    await axios.put(`/inventarios/${nombre}`, { cantidad, precio }, {
      headers: {
        Authorization: `Bearer ${token}`
      }
    });
    const msg = `🔄 Producto '${nombre}' actualizado correctamente.`;
    setHistorial((prev) => [...prev, { tipo: "asistente", texto: msg }]);
    hablar(msg);
  } catch (error) {
    const msg = `❌ Error al actualizar el producto '${nombre}': ${error.response?.status}`;
    setHistorial((prev) => [...prev, { tipo: "asistente", texto: msg }]);
    hablar(msg);
  }

  return;
}



      if (command.toLowerCase().includes("eliminar producto")) {
  const regex = /eliminar producto (.+)/i;
  const match = command.match(regex);

  let nombre;

  if (match) {
    // ✅ Datos extraídos directamente del comando
    nombre = match[1];
    nombre = nombre.replace(/^(es|el|la|producto|eliminar)\s*/i, "").trim();
    nombre = nombre.trim().toLowerCase();
  } else {
    // 📝 Modo manual si no hay datos en el texto
    setTimeout(async () => {
      nombre = prompt("🗑️ Producto a eliminar:");

      if (!nombre) {
        const msg = "⚠️ Te hace falta el nombre del producto. Intenta de nuevo.";
        setHistorial((prev) => [...prev, { tipo: "asistente", texto: msg }]);
        hablar(msg);
        return;
      }

      try {
        const token = localStorage.getItem("token");
        console.log("🔐 Token usado en DELETE:", token);
        await axios.delete(`/inventarios/${nombre}`, {
          headers: {
            Authorization: `Bearer ${token}`
          }
        });
        const msg = `🗑️ Producto '${nombre}' eliminado correctamente.`;
        setHistorial((prev) => [...prev, { tipo: "asistente", texto: msg }]);
        hablar(msg);
      } catch (error) {
        const msg = `❌ Error al eliminar el producto '${nombre}': "No encontrado"`;
        setHistorial((prev) => [...prev, { tipo: "asistente", texto: msg }]);
        hablar(msg);
      }
    }, 500);
    return;
  }

  // ✅ Si ya tiene datos, ejecuta directo
  try {
    const token = localStorage.getItem("token");
    await axios.delete(`/inventarios/${nombre}`, {
      headers: {
        Authorization: `Bearer ${token}`
      }
    });
    const msg = `🗑️ Producto '${nombre}' eliminado correctamente.`;
    setHistorial((prev) => [...prev, { tipo: "asistente", texto: msg }]);
    hablar(msg);
  } catch (error) {
    const msg = `❌ Error al eliminar el producto '${nombre}': ${error.response?.status}`;
    setHistorial((prev) => [...prev, { tipo: "asistente", texto: msg }]);
    hablar(msg);
  }

  return;
}

if (command.toLowerCase().includes("cuánto cuesta") || command.toLowerCase().includes("precio de") ||
    command.toLowerCase().includes("cuántas unidades") || command.toLowerCase().includes("cantidad de")) {

  try {
    const token = localStorage.getItem("token");
    const res = await axios.post("/ia/ejecutar-comando", {
      texto: command
    }, {
      headers: {
        Authorization: `Bearer ${token}`
      }
    });

    const respuesta = res.data.respuesta || "⚠️ No se obtuvo respuesta.";
    setHistorial((prev) => [...prev, { tipo: "asistente", texto: respuesta }]);
    hablar(respuesta);
  } catch (error) {
    const msg = `❌ Error al consultar: ${error.response?.status || "desconocido"}`;
    setHistorial((prev) => [...prev, { tipo: "asistente", texto: msg }]);
    hablar(msg);
  }

  return;
}

if (command.toLowerCase().includes("consultar producto")) {
  const nombre = prompt("🔍 Nombre del producto:");
  const tipo = prompt("¿Deseas consultar 'precio' o 'cantidad'?");

  if (!nombre || !tipo) {
    const msg = "⚠️ Te hace falta nombre o tipo de consulta.";
    setHistorial((prev) => [...prev, { tipo: "asistente", texto: msg }]);
    hablar(msg);
    return;
  }

  const texto = tipo.toLowerCase() === "precio"
    ? `precio de ${nombre}`
    : `cantidad de ${nombre}`;

  try {
    const token = localStorage.getItem("token");
    const res = await axios.post("/ia/ejecutar-comando", {
      texto
    }, {
      headers: {
        Authorization: `Bearer ${token}`
      }
    });

    const respuesta = res.data.respuesta || "⚠️ No se obtuvo respuesta.";
    setHistorial((prev) => [...prev, { tipo: "asistente", texto: respuesta }]);
    hablar(respuesta);
  } catch (error) {
    const msg = `❌ Error al consultar: ${error.response?.status || "desconocido"}`;
    setHistorial((prev) => [...prev, { tipo: "asistente", texto: msg }]);
    hablar(msg);
  }

  return;
}


      if (command.toLowerCase().includes("crear pedido") || command.toLowerCase().includes("agregar pedido")) {
  const tieneDatos = /pedido.*(de\s+\w+|\d+|\zona\s+\d+|\para\s+\w+)/i.test(command);

  // 📝 Modo manual si no hay datos en el texto
  if (!tieneDatos) {
    setTimeout(async () => {
      const producto = prompt("🛒 Producto:");
      const cantidad = parseInt(prompt("🔢 Cantidad:"));
      const direccion = prompt("📍 Dirección de entrega:");

      if (!producto || isNaN(cantidad) || cantidad <= 0 || !direccion) {
        const msg = "⚠️ Te hace falta producto, cantidad o dirección. Intenta de nuevo.";
        setHistorial((prev) => [...prev, { tipo: "asistente", texto: msg }]);
        hablar(msg);
        return;
      }

      try {
        await axios.post("/pedidos", { producto, cantidad, direccion }, {
          headers: { Authorization: `Bearer ${token}` }
        });
        const msg = `✅ Pedido de '${producto}' creado con éxito.`;
        setHistorial((prev) => [...prev, { tipo: "asistente", texto: msg }]);
        hablar(msg);
      } catch (error) {
        const msg = `❌ Error al crear pedido: ${error.response?.status}`;
        setHistorial((prev) => [...prev, { tipo: "asistente", texto: msg }]);
        hablar(msg);
      }
    }, 500);
    return;
  }

  // 🧠 Modo automático por voz con extracción de entidades
  try {
    const res = await axios.post("/ia/ejecutar-comando", {
      texto: command
    }, {
      headers: { Authorization: `Bearer ${token}` }
    });

    const respuesta = res.data.respuesta || "✅ Comando ejecutado.";
    setHistorial((prev) => [...prev, { tipo: "asistente", texto: respuesta }]);
    hablar(respuesta);
  } catch (error) {
  const msg = `❌ Error al crear pedido por voz: ${error.response?.data?.detail || error.response?.status || "desconocido"}`;
  setHistorial((prev) => [...prev, { tipo: "asistente", texto: msg }]);
  hablar(msg);
  }
  return;
}



// 📋 Ver pedidos (cliente ve los suyos, empleado/admin ve todos)
if (command.includes("ver pedido")) {
  try {
    const endpoint = rol === "cliente" ? "/pedidos/mios" : "/pedidos";
    const res = await axios.get(endpoint);
    const pedidos = res.data || [];

    const respuesta = pedidos.length
      ? `📋 ${rol === "cliente" ? "Tienes" : "Pedidos registrados"}: ${pedidos.length}\n` +
       pedidos.map(p =>
  `• ID ${p.id} - Cliente: ${p.usuario} - Producto: ${p.producto} (${p.cantidad}) - Estado: ${p.estado} - Dirección: ${p.direccion}`
).join("\n")

      : rol === "cliente"
        ? "📭 No tienes pedidos registrados."
        : "📭 No hay pedidos registrados.";

    setHistorial([...historial, { tipo: "asistente", texto: respuesta }]);
    hablar(respuesta);
  } catch {
    const error = "❌ Error al consultar pedidos.";
    setHistorial([...historial, { tipo: "asistente", texto: error }]);
    hablar(error);
  }
  return;
}


//Eliminar pedido
try {
  const res = await axios.post("/ia/ejecutar-comando", { texto: command });
  const respuesta = res.data.respuesta;

  const comandoEsSoloEliminar = command.trim().toLowerCase() === "eliminar pedido";

  // 🧠 Detectar si ya se eliminó por voz
  const yaEliminoPorVoz =
    respuesta.toLowerCase().includes("pedido eliminado") ||
    respuesta.toLowerCase().includes("eliminado correctamente") ||
    respuesta.toLowerCase().includes("intención: eliminar_pedido");

  // ✅ Mostrar solo el mensaje de éxito si ya se ejecutó por voz
  if (yaEliminoPorVoz) {
    if (
      respuesta.toLowerCase().includes("pedido eliminado") ||
      respuesta.toLowerCase().includes("eliminado correctamente")
    ) {
      setHistorial([...historial, { tipo: "asistente", texto: respuesta }]);
      hablar(respuesta);
    }
    return; // ⛔ Evita mostrar mensaje de intención adicional
  }

  // 🗑️ Mostrar prompt solo si el usuario dijo literalmente "eliminar pedido"
  if (comandoEsSoloEliminar) {
    const id = prompt("🗑️ ID del pedido a eliminar:");
    const confirmar = window.confirm(`¿Eliminar pedido ${id}?`);
    if (!confirmar) return;

    try {
      await axios.delete(`/pedidos/${id}`);
      const msg = `🗑️ Pedido ${id} eliminado correctamente.`;
      setHistorial([...historial, { tipo: "asistente", texto: msg }]);
      hablar(msg);
    } catch {
      const error = "❌ Error al eliminar pedido.";
      setHistorial([...historial, { tipo: "asistente", texto: error }]);
      hablar(error);
    }
    return; // ⛔ Evita mostrar respuesta del asistente después del prompt
  }

  // 🧠 Mostrar respuesta del asistente si no fue eliminación por voz ni prompt
  setHistorial([...historial, { tipo: "asistente", texto: respuesta }]);
  hablar(respuesta);
} catch (error) {
  const errorMsg = "❌ Error al procesar el comando.";
  setHistorial([...historial, { tipo: "asistente", texto: errorMsg }]);
  hablar(errorMsg);
}

// 🔄 Actualizar estado del pedido
try {
  const res = await axios.post("/ia/ejecutar-comando", { texto: command });
  const respuesta = res.data.respuesta;

  const comandoEsSoloActualizar = command.trim().toLowerCase() === "actualizar estado";

  // 🧠 Detectar si ya se actualizó por voz
  const yaActualizoPorVoz =
    respuesta.toLowerCase().includes("pedido actualizado") ||
    respuesta.toLowerCase().includes("actualizado a estado") ||
    respuesta.toLowerCase().includes("intención: actualizar_estado_pedido");

  // ✅ Mostrar solo el mensaje de éxito si ya se ejecutó por voz
  if (yaActualizoPorVoz) {
    setHistorial([...historial, { tipo: "asistente", texto: respuesta }]);
    hablar(respuesta);
    return; // ⛔ Cortar ejecución completa
  }

  // 🔄 Mostrar prompt solo si el usuario dijo literalmente "actualizar estado"
  if (comandoEsSoloActualizar) {
    const id = prompt("🔄 ID del pedido:");
    const estado = prompt("📦 Nuevo estado (pendiente, entregado, cancelado):");
    if (!id || !estado) return;

    try {
      await axios.patch(`/pedidos/${id}`, { estado });
      const msg = `🔄 Pedido ${id} actualizado a estado '${estado}'.`;
      setHistorial([...historial, { tipo: "asistente", texto: msg }]);
      hablar(msg);
    } catch {
      const error = "❌ Error al actualizar estado.";
      setHistorial([...historial, { tipo: "asistente", texto: error }]);
      hablar(error);
    }
    return; // ⛔ Cortar ejecución completa
  }

  // 🧠 Mostrar respuesta del asistente si no fue actualización por voz ni prompt
  setHistorial([...historial, { tipo: "asistente", texto: respuesta }]);
  hablar(respuesta);
} catch (error) {
  const errorMsg = "❌ Error al procesar el comando.";
  setHistorial([...historial, { tipo: "asistente", texto: errorMsg }]);
  hablar(errorMsg);
}


// ✏️ Editar pedido
if (command.includes("editar pedido")) {
  const id = prompt("✏️ ID del pedido:");
  const campo = prompt("¿Qué deseas editar? (producto, cantidad, direccion):");
  let payload = {};
  if (campo === "producto") payload.producto = prompt("🛒 Nuevo producto:");
  if (campo === "cantidad") payload.cantidad = parseInt(prompt("🔢 Nueva cantidad:"));
  if (campo === "direccion") payload.direccion = prompt("📍 Nueva dirección:");
  try {
    await axios.put(`/pedidos/cliente/${id}`, payload);
    const msg = `✏️ Pedido ${id} actualizado correctamente.`;
    setHistorial([...historial, { tipo: "asistente", texto: msg }]);
    hablar(msg);
  } catch {
    const error = "❌ Error al modificar pedido.";
    setHistorial([...historial, { tipo: "asistente", texto: error }]);
    hablar(error);
  }
  return;
}

// 🔍 Ver pedido detallado (admin/empleado)
if (command.includes("ver pedido detallado")) {
  const id = prompt("🔍 ID del pedido:");
  try {
    const res = await axios.get(`/pedidos/${id}`);
    const p = res.data;
    const respuesta = `📦 Pedido ${p.id}:\n- Producto: ${p.producto}\n- Cantidad: ${p.cantidad}\n- Estado: ${p.estado}\n- Dirección: ${p.direccion}\n- Fecha: ${p.fecha}\n- Cliente ID: ${p.usuario_id}`;
    setHistorial([...historial, { tipo: "asistente", texto: respuesta }]);
    hablar(respuesta);
  } catch {
    const error = "❌ Error al consultar pedido.";
    setHistorial([...historial, { tipo: "asistente", texto: error }]);
    hablar(error);
  }
  return;
}

// 📋 Ver pedidos por cliente (admin/empleado)
if (command.includes("ver pedidos del cliente")) {
  const clienteId = prompt("🧑 ID del cliente:");
  try {
    const res = await axios.get(`/pedidos/cliente/${clienteId}`);
    const pedidos = res.data || [];
    const respuesta = pedidos.length
      ? `📋 Pedidos del cliente ${clienteId}:\n` +
        pedidos.map(p => `• Pedido ${p.id}: ${p.producto} (${p.cantidad}) - ${p.estado}`).join("\n")
      : `📭 El cliente ${clienteId} no tiene pedidos registrados.`;
    setHistorial([...historial, { tipo: "asistente", texto: respuesta }]);
    hablar(respuesta);
  } catch {
    const error = "❌ Error al consultar pedidos del cliente.";
    setHistorial([...historial, { tipo: "asistente", texto: error }]);
    hablar(error);
  }
  return;
}

// 📊 Historial de pedidos
if (command.includes("ver historial de pedidos")) {
  const clienteId = prompt("🧑 ID del cliente:");
  try {
    const res = await axios.get(`/pedidos/historial/${clienteId}`);
    const pedidos = res.data || [];
    const respuesta = pedidos.length
      ? `📋 Historial de pedidos del cliente ${clienteId}:\n` +
        pedidos.map(p => `• Pedido ${p.id}: ${p.producto} (${p.cantidad}) - ${p.estado} - ${p.fecha}`).join("\n")
      : `📭 El cliente ${clienteId} no tiene historial de pedidos.`;
    setHistorial([...historial, { tipo: "asistente", texto: respuesta }]);
    hablar(respuesta);
  } catch {
    const error = "❌ Error al consultar historial.";
    setHistorial([...historial, { tipo: "asistente", texto: error }]);
    hablar(error);
  }
  return;
}

// 📄 Descargar historial (admin)
if (command.includes("descargar historial de pedidos")) {
  const clienteId = prompt("🧑 ID del cliente:");
  try {
    const res = await axios.get(`/pedidos/historial/${clienteId}`);
    const pedidos = res.data || [];
    if (!pedidos.length) {
      const msg = `📭 El cliente ${clienteId} no tiene historial de pedidos.`;
      setHistorial([...historial, { tipo: "asistente", texto: msg }]);
      hablar(msg);
      return;
    }
    console.log(`📄 Generando reporte para cliente ${clienteId}...`);
    const msg = `📄 Reporte de historial de pedidos del cliente ${clienteId} generado correctamente.`;
    setHistorial([...historial, { tipo: "asistente", texto: msg }]);
    hablar(msg);
  } catch {
    const error = "❌ Error al generar reporte.";
    setHistorial([...historial, { tipo: "asistente", texto: error }]);
    hablar(error);
  }
  return;
}

// ➕ Asignar ruta
if (command.toLowerCase().includes("asignar ruta")) {
  const token = localStorage.getItem("token");
  const resIA = await axios.post("/ia/probar-ia", { texto: command }, {
    headers: { Authorization: `Bearer ${token}` }
  });

  const pedidoId = resIA.data.entidades?.pedido_id;
  const direccion = resIA.data.entidades?.direccion || "zona 6 5ta avenida 2-63 villa Nueva";

  if (!pedidoId || !resIA.data.entidades?.direccion) {
  const msg = "⚠️ No se detectaron datos por voz. Vamos a ingresarlos manualmente.";
  setHistorial((prev) => [...prev, { tipo: "asistente", texto: msg }]);
  hablar(msg);

  const manualId = prompt("📝 ID del pedido:");
  const manualDir = prompt("📍 Dirección de entrega:");

  if (!manualId || !manualDir) {
    const cancelado = "❌ Asignación cancelada. Faltan datos.";
    setHistorial((prev) => [...prev, { tipo: "asistente", texto: cancelado }]);
    hablar(cancelado);
    return;
  }

  // Reasignar variables
  pedidoId = manualId;
  direccion = manualDir;
}


  if (!pedidoId) {
    const msg = "⚠️ No se detectó el ID del pedido.";
    setHistorial((prev) => [...prev, { tipo: "asistente", texto: msg }]);
    hablar(msg);
    return;
  }

  const usarUbicacion = window.confirm("📍 ¿Usar tu ubicación actual como punto de partida?");
  let origen = [-90.5133, 14.6099]; // Default: San Miguel Petapa

  if (usarUbicacion && navigator.geolocation) {
    await new Promise((resolve) => {
      navigator.geolocation.getCurrentPosition((pos) => {
        const lat = pos.coords.latitude;
        const lng = pos.coords.longitude;
        origen = [lng, lat];
        resolve();
      }, () => resolve());
    });
  }

  // 🧠 Mostrar mensaje de carga antes de calcular
  const mensajeCarga = `🧠 Procesando ruta para el pedido ${pedidoId} hacia ${direccion}...`;
  setHistorial((prev) => [...prev, { tipo: "asistente", texto: mensajeCarga }]);
  hablar(mensajeCarga);

  try {
    const res = await axios.post("/rutas/gps", {
      pedido_id: pedidoId,
      direccion,
      origen
    }, {
      headers: { Authorization: `Bearer ${token}` }
    });

    const { distancia_km, tiempo_min, lat, lng } = res.data;

    // 🕒 Formato de tiempo refinado
    const horas = Math.floor(tiempo_min / 60);
    const minutos = Math.round(tiempo_min % 60);
    const tiempoFormateado = horas > 0
      ? `${horas} hora${horas > 1 ? "s" : ""} con ${minutos} minuto${minutos !== 1 ? "s" : ""}`
      : `${minutos} minuto${minutos !== 1 ? "s" : ""}`;

    // 🗺️ Confirmación de trazado
    window.dispatchEvent(new Event("mostrarMapaRuta"));
    window.dispatchEvent(new Event("abrirMapaDesdeAsistente"));

    const mapaMsg = "🗺️ Ruta trazada en el mapa.";
    setHistorial((prev) => [...prev, { tipo: "asistente", texto: mapaMsg }]);
    hablar(mapaMsg);

    // 🚚 Mensaje final limpio
    console.log("✅ Ruta calculada correctamente"); // en lugar de mostrar res.data
    const msg = `🚚 Ruta asignada al pedido ${pedidoId} hacia ${direccion}. 🛣️ Distancia: ${distancia_km} km | Tiempo estimado: ${tiempoFormateado}.`;
    setHistorial((prev) => [...prev, { tipo: "asistente", texto: msg }]);
    hablar(msg);

    localStorage.setItem("lat", lat);
    localStorage.setItem("lng", lng);
    localStorage.setItem("destino", direccion);
    localStorage.setItem("tiempo", tiempoFormateado);
    localStorage.setItem("ruta", JSON.stringify(res.data.ruta)); // se guarda pero no se muestra

  } catch {
    const error = "❌ Error al asignar ruta GPS.";
    setHistorial((prev) => [...prev, { tipo: "asistente", texto: error }]);
    hablar(error);
  }

  return;
}



if (command.toLowerCase().includes("asignar ruta manual")) {
  const pedidoId = prompt("📝 ID del pedido:");
  const destino = prompt("📍 Dirección de entrega:");
  const tiempo = prompt("⏱️ Tiempo estimado:");
  try {
    await axios.post("/rutas", { pedido_id: pedidoId, destino, tiempo_estimado: tiempo });
    const msg = `🚚 Ruta asignada al pedido ${pedidoId} hacia ${destino}.`;
    setHistorial((prev) => [...prev, { tipo: "asistente", texto: msg }]);
    hablar(msg);
  } catch {
    const error = "❌ Error al asignar ruta.";
    setHistorial((prev) => [...prev, { tipo: "asistente", texto: error }]);
    hablar(error);
  }
  return;
}


// 🧭 Rastrear ruta
if (command.toLowerCase().includes("rastrear ruta")) {
  const pedidoId = prompt("📍 ID del pedido:");
  try {
    const res = await axios.get(`/rutas/pedido/${pedidoId}`);
    const rutas = res.data;
    if (!rutas.length) throw new Error("No hay rutas");

    const ruta = rutas.at(-1); // última ruta
    const tiempoMin = parseFloat(ruta.tiempo_estimado);
    const horas = Math.floor(tiempoMin / 60);
    const minutos = Math.round(tiempoMin % 60);
    const tiempoFormateado = horas > 0
      ? `${horas} hora${horas > 1 ? "s" : ""} con ${minutos} minuto${minutos !== 1 ? "s" : ""}`
      : `${minutos} minuto${minutos !== 1 ? "s" : ""}`;

    const msg = `🧭 El repartidor va por ${ruta.destino} y llegará en ${tiempoFormateado}. Estado: ${ruta.estado}.`;
    setHistorial((prev) => [...prev, { tipo: "asistente", texto: msg }]);
    hablar(msg);

    if (ruta.lat_actual && ruta.lng_actual) {
      localStorage.setItem("lat", ruta.lat_actual);
      localStorage.setItem("lng", ruta.lng_actual);
      localStorage.setItem("destino", ruta.destino);
      localStorage.setItem("estado", ruta.estado);
      localStorage.setItem("tiempo", tiempoFormateado);
      window.dispatchEvent(new Event("mostrarMapaRuta"));
      window.dispatchEvent(new Event("abrirMapaDesdeAsistente"));
    }
  } catch {
    const error = "❌ Error al consultar seguimiento.";
    setHistorial((prev) => [...prev, { tipo: "asistente", texto: error }]);
    hablar(error);
  }
  return;
}

// 🗑️ Cancelar ruta
if (command.toLowerCase().includes("cancelar ruta")) {
  const rutaId = prompt("🗑️ ID de la ruta:");
  if (!rutaId || !window.confirm(`¿Seguro que deseas cancelar la ruta ${rutaId}?`)) return;
  try {
    await axios.put(`/rutas/${rutaId}/cancelar`);
    const msg = `🗑️ Ruta ${rutaId} cancelada correctamente.`;
    setHistorial((prev) => [...prev, { tipo: "asistente", texto: msg }]);
    hablar(msg);
  } catch {
    const error = "❌ Error al cancelar ruta.";
    setHistorial((prev) => [...prev, { tipo: "asistente", texto: error }]);
    hablar(error);
  }
  return;
}

// 🔁 Reprogramar ruta
if (command.toLowerCase().includes("reprogramar ruta")) {
  const rutaId = prompt("🔁 ID de la ruta:");
  const nuevoDestino = prompt("📍 Nuevo destino:");
  const nuevoTiempo = prompt("⏱️ Nuevo tiempo estimado:");
  if (!rutaId || !nuevoDestino || !nuevoTiempo) {
    const error = "⚠️ Faltan datos para reprogramar la ruta.";
    setHistorial((prev) => [...prev, { tipo: "asistente", texto: error }]);
    hablar(error);
    return;
  }
  try {
    await axios.put(`/rutas/${rutaId}/reprogramar`, {
      nuevo_destino: nuevoDestino,
      nuevo_tiempo: nuevoTiempo
    });
    const msg = `🔁 Ruta ${rutaId} reprogramada hacia ${nuevoDestino}.`;
    setHistorial((prev) => [...prev, { tipo: "asistente", texto: msg }]);
    hablar(msg);
  } catch {
    const error = "❌ Error al reprogramar ruta.";
    setHistorial((prev) => [...prev, { tipo: "asistente", texto: error }]);
    hablar(error);
  }
  return;
}

// 📦 ¿Cómo va mi pedido?
if (command.toLowerCase().includes("cómo va mi pedido")) {
  const pedidoId = prompt("📦 ID del pedido:");
  try {
    const res = await axios.get(`/rutas/pedido/${pedidoId}/detalle_completo`);
    const { pedido, ruta } = res.data;

    let frase;
    if (!ruta) {
      frase = `📦 Pedido ${pedido.id} de ${pedido.cantidad} unidad(es) de ${pedido.producto} hacia ${pedido.direccion}. Estado del pedido: ${pedido.estado}. 🧭 No hay ruta asignada aún.`;
    } else {
      const tiempoMin = parseFloat(ruta.tiempo_estimado);
      const horas = Math.floor(tiempoMin / 60);
      const minutos = Math.round(tiempoMin % 60);
      const tiempoFormateado = horas > 0
        ? `${horas} hora${horas > 1 ? "s" : ""} con ${minutos} minuto${minutos !== 1 ? "s" : ""}`
        : `${minutos} minuto${minutos !== 1 ? "s" : ""}`;

      frase = `📦 Pedido ${pedido.id} de ${pedido.cantidad} unidad(es) de ${pedido.producto} hacia ${pedido.direccion}. Estado del pedido: ${pedido.estado}. 🧭 Ruta: ${ruta.estado}, destino ${ruta.destino}, tiempo estimado ${tiempoFormateado}.`;

      if (ruta.lat_actual && ruta.lng_actual) {
        localStorage.setItem("lat", ruta.lat_actual);
        localStorage.setItem("lng", ruta.lng_actual);
        localStorage.setItem("destino", ruta.destino);
        localStorage.setItem("estado", ruta.estado);
        localStorage.setItem("tiempo", tiempoFormateado);
        window.dispatchEvent(new Event("mostrarMapaRuta"));
        window.dispatchEvent(new Event("abrirMapaDesdeAsistente"));
      }
    }

    setHistorial((prev) => [...prev, { tipo: "asistente", texto: frase }]);
    hablar(frase);
  } catch {
    const error = "❌ No se pudo consultar el estado del pedido.";
    setHistorial((prev) => [...prev, { tipo: "asistente", texto: error }]);
    hablar(error);
  }
  return;
}

// 📍 Ver rutas generales
if (command.toLowerCase().includes("ver rutas")) {
  try {
    const res = await axios.get("/rutas");
    const rutas = res.data;
    const msg = rutas.length
      ? "📍 Rutas activas:\n" + rutas.map(r =>
          `- Pedido ${r.pedido_id} hacia ${r.destino} | Estado: ${r.estado} | Tiempo: ${r.tiempo_estimado || "sin tiempo"}`
        ).join("\n")
      : "📭 No hay rutas registradas.";
    setHistorial((prev) => [...prev, { tipo: "asistente", texto: msg }]);
    hablar(msg);
  } catch {
    const error = "❌ No se pudo consultar las rutas.";
    setHistorial((prev) => [...prev, { tipo: "asistente", texto: error }]);
    hablar(error);
  }
  return;
}

      // 🧠 Flujo con IA (si no es comando directo)
      try {
console.log("Token en localStorage:", token);

        if (!token) {
  console.error("❌ Token no disponible en localStorage");
  return;
}

        const res = await axios.post(
  "/ia/probar-ia",
  { texto: command },
  {
    headers: {
      Authorization: `Bearer ${token}`
    }
  }
);
        const { intencion, confianza, entidades } = res.data;
        const resumen = `Intención: ${intencion} (${(confianza * 100).toFixed(1)}%)`;
        const entidadesTexto = Object.entries(entidades)
          .map(([k, v]) => `${k}: ${v}`)
          .join(", ");
        const respuestaFinal = `${resumen}${entidadesTexto ? " | Entidades: " + entidadesTexto : ""}`;
        setHistorial((prev) => [...prev, { tipo: "asistente", texto: respuestaFinal }]);
        hablar(respuestaFinal);
      } catch {
        setHistorial((prev) => [...prev, { tipo: "asistente", texto: "❌ Error al procesar" }]);
        hablar("Hubo un error al procesar tu comando.");
      }

      setTimeout(() => setEstado("🎧 Escuchando..."), 3000);
    };

    recognition.onerror = (event) => {
      if (event.error === "not-allowed") {
        setPermisoBloqueado(true);
        setEstado("🚫 Permiso de micrófono denegado");
      } else {
        setEstado("⚠️ Error de voz");
      }
    };

    recognition.onend = () => {
      if (activo) recognition.start();
    };

    recognitionRef.current = recognition;
  }, [activo]);

  const solicitarPermisoMicrofono = async () => {
    try {
      await navigator.mediaDevices.getUserMedia({ audio: true });
      activarMicrofono();
      setPermisoBloqueado(false);
    } catch {
      setPermisoBloqueado(true);
      setEstado("🚫 Permiso de micrófono denegado");
    }
  };

  const activarMicrofono = () => {
    if (!recognitionRef.current) {
      setEstado("❌ Reconocimiento no disponible");
      return;
    }
    try {
      recognitionRef.current.start();
      setActivo(true);
      setEstado("🎧 Escuchando...");
    } catch {
      setEstado("🚫 Error al iniciar reconocimiento");
    }
  };

  const desactivarMicrofono = () => {
    if (!recognitionRef.current) return;
    recognitionRef.current.stop();
    setActivo(false);
    setEstado("🎙 Micrófono apagado");
  };

  const hablar = (texto) => {
    const synth = window.speechSynthesis;
    synth.cancel();
    const utter = new SpeechSynthesisUtterance(texto);
    utter.lang = "es-ES";
    synth.speak(utter);
  };

  const mostrarAlerta = (texto) => {
    setAlerta(texto);
    setTimeout(() => setAlerta(null), 3000);
  };

  return (
    <div className="bg-green-100 p-4 rounded mt-6 shadow relative">
      <button
        onClick={activo ? desactivarMicrofono : solicitarPermisoMicrofono}
        className="absolute top-2 right-2 text-xl text-green-700 transition-transform hover:scale-110"
        title={activo ? "Desactivar micrófono" : "Activar micrófono"}
      >
        {activo ? <FaMicrophone /> : <FaMicrophoneSlash />}
      </button>

      <h2 className="text-lg font-semibold mb-2">{estado}</h2>

      {permisoBloqueado && (
        <div className="mt-2 bg-red-100 text-red-800 p-2 rounded shadow">
          ⚠️ El navegador bloqueó el acceso al micrófono.<br />
          Haz clic en el 🔒 junto a la URL y permite el uso del micrófono.<br />
          Luego presiona <strong>“Activar micrófono”</strong> nuevamente.
        </div>
      )}

      <div className="bg-white rounded p-3 max-h-64 overflow-y-auto shadow-inner">
        {historial.map((item, index) => (
          <div
            key={index}
            className={`mb-2 p-2 rounded ${
              item.tipo === "usuario"
                ? "bg-blue-100 text-blue-800"
                : "bg-gray-100 text-gray-800"
            }`}
          >
            <strong>
              {item.tipo === "usuario" ? "🧑 Tú:" : "🤖 Asistente:"}
            </strong>{" "}
            {item.texto}
          </div>
        ))}
      </div>

      {alerta && (
        <div className="absolute bottom-2 left-2 bg-yellow-200 text-yellow-900 px-3 py-2 rounded shadow">
          {alerta}
        </div>
      )}
    </div>
  );
}
