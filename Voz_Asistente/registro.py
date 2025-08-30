import requests

def registrar_usuario(nombre):
    try:
        response = requests.post("http://localhost:8000/usuarios/registrar", json={
            "username": nombre,
            "rol": "usuario",
            "is_active": True
        })
        if not nombre or not isinstance(nombre, str):
            return "Nombre de usuario inválido."
        
        if response.status_code == 200:
            return f"Usuario {nombre} registrado correctamente."
        else:
            return "No se pudo registrar el usuario."

    except Exception as e:
        print("❌ Error al registrar usuario:", e)
        return "Error al registrar usuario."
