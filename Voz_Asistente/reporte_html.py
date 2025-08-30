# Voz_Asistente/reporte_html.py
from db.conexion import conectar

def generar_reporte_html():
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT usuario, fecha, intencion, entidades, resultado FROM interacciones ORDER BY fecha DESC")
    registros = cur.fetchall()
    cur.close()
    conn.close()

    html = "<html><head><title>Reporte de Interacciones</title></head><body>"
    html += "<h1>📊 Reporte de Interacciones</h1><table border='1'>"
    html += "<tr><th>Usuario</th><th>Fecha</th><th>Intención</th><th>Entidades</th><th>Resultado</th></tr>"

    for usuario, fecha, intencion, entidades, resultado in registros:
        html += f"<tr><td>{usuario}</td><td>{fecha}</td><td>{intencion}</td><td>{entidades}</td><td>{resultado}</td></tr>"

    html += "</table></body></html>"
    return html
