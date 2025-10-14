import { useState } from "react";
import React from "react";
import LoginPanel from "./Componentes/LoginPanel";
import RoleDashboard from "./Componentes/RoleDashboard";
import VoiceAssistant from "./Componentes/VoiceAssistant";
import ReactDOM from "react-dom/client";

function App() {
  const [email, setEmail] = useState(localStorage.getItem("email"));

  return (
    <div className="min-h-screen bg-gradient-to-br from-yellow-100 to-yellow-300 flex items-center justify-center px-4 py-8">
      <div className="w-full max-w-5xl bg-white rounded-xl shadow-xl p-6">
        {!email ? (
          <LoginPanel onLogin={(e) => setEmail(e)} />
        ) : (
          <RoleDashboard email={email} />
        )}
      </div>
    </div>
  );
}

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);

export default App;
