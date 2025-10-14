import { useState } from "react";
import axios from "/api/backend";

export default function LoginForm({ onLogin }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const handleLogin = async () => {
    try {
      const res = await axios.post("/auth/login", { email, password });
      localStorage.setItem("token", res.data.access_token);
      onLogin(res.data.rol);
    } catch (err) {
      alert("Credenciales inválidas");
    }
  };

  return (
    <div className="p-4 max-w-md mx-auto">
      <h2 className="text-xl font-bold mb-4">Iniciar sesión</h2>
      <input type="email" placeholder="Correo" value={email} onChange={e => setEmail(e.target.value)} className="input" />
      <input type="password" placeholder="Contraseña" value={password} onChange={e => setPassword(e.target.value)} className="input mt-2" />
      <button onClick={handleLogin} className="btn mt-4">Entrar</button>
    </div>
  );
}
