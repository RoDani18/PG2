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
                INSERT INTO rutas (pedido_id, destino, estado, tiempo_estimado, lat_actual, lng_actual)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (r["pedido_id"], r["destino"], r["estado"], r["tiempo_estimado"], r["lat_actual"], r["lng_actual"]))

        conn_pg.commit()
        cur_pg.close()
        conn_pg.close()

        rutas_fallback.marcar_como_sincronizado([r["id"] for r in rutas])
        print(f"✅ Sincronizadas {len(rutas)} rutas a PostgreSQL.")

    except Exception as e:
        print(f"❌ Error sincronizando rutas: {e}")
