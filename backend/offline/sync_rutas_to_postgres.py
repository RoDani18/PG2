# offline/sync_rutas_to_postgres.py
import psycopg2
from backend.offline import rutas_fallback
from backend.config import settings

PG_CONN = {
    "host": "localhost",
    "database": "asistentePG",
    "user": "postgres",
    "password": "admin123",
    "port": 5432
}

def sync():
    try:
        rutas = rutas_fallback.listar_rutas_no_sincronizadas()
        if not rutas:
            print("✅ No hay rutas pendientes de sincronizar.")
            return

        conn_pg = psycopg2.connect(**PG_CONN)
        cur_pg = conn_pg.cursor()

        for r in rutas:
            cur_pg.execute("""
                        INSERT INTO rutas (pedido_id, destino, estado, tiempo_estimado, lat_actual, lng_actual) VALUES (%s, %s, %s, %s, %s, %s)""", (r[1], r[2], r[3], r[4], r[5], r[6]))

        conn_pg.commit()
        cur_pg.close()
        conn_pg.close()

        for r in rutas:
            rutas_fallback.marcar_como_sincronizado([r[0]])

    except Exception as e:
        print(f"❌ Error sincronizando rutas: {e}")
