from Voz_Asistente.acciones import ejecutar_accion
from db.conexion import conectar

def test_precio_se_guarda():
    ejecutar_accion("agregar_producto", {"nombre": "Pepsi", "cantidad": 20, "precio": 8.50})
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT precio FROM inventario WHERE nombre = 'Pepsi'")
    precio = cur.fetchone()[0]
    cur.close()
    conn.close()
    assert precio == 8.50
