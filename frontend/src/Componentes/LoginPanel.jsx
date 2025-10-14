import React, { useState } from "react";
import axios from "../Api/backend";

export default function LoginPanel({ onLogin }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const handleLogin = async () => {
    setError("");
    if (!email || !password) {
      setError("⚠️ Ingresá tu correo y contraseña.");
      return;
    }

    try {
      const res = await axios.post("/auth/login", { email, password });
      localStorage.setItem("token", res.data.access_token);
      localStorage.setItem("rol", res.data.rol);
      localStorage.setItem("email", email);
      onLogin(res.data.rol);
    } catch {
      setError("❌ Credenciales inválidas.");
    }
  };

  return (
    <div className="bg-white p-8 rounded-xl shadow-2xl max-w-md w-full mx-auto mt-20 animate-fade-in">
      <div className="flex justify-center mb-6">
        <img src="logo.png" alt="Logo de Voxia"/>
      </div>
      <h2 className="text-3xl font-bold text-center text-gray-800 mb-6">Bienvenido a Voxia</h2>

      <div className="space-y-4">
        <input
          type="email"
          placeholder="Correo electrónico"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-yellow-500 transition duration-200"
        />
        <input
          type="password"
          placeholder="Contraseña"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-yellow-500 transition duration-200"
        />

        {error && (
          <div className="text-red-600 text-sm font-medium text-center animate-shake">{error}</div>
        )}

        <button
          onClick={handleLogin}
          className="w-full bg-yellow-500 hover:bg-yellow-600 text-white font-semibold py-2 rounded-lg transition duration-300 transform hover:scale-105"
        >
          Entrar
        </button>
      </div>

      <p className="text-xs text-center text-gray-500 mt-4">
        Las cuentas son creadas únicamente por el administrador del sistema.
      </p>
    </div>
  );
}
