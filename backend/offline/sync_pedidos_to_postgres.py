# offline/sync_pedidos_to_postgres.py
import psycopg2
from backend.offline import pedidos_fallback
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
        pedidos = pedidos_fallback.listar_pedidos_no_sincronizados()
        if not pedidos:
            print("✅ No hay pedidos pendientes de sincronizar.")
            return

        conn_pg = psycopg2.connect(**PG_CONN)
        cur_pg = conn_pg.cursor()

        for p in pedidos:
            cur_pg.execute("""
                INSERT INTO pedidos (id, cliente, productos, total, fecha)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                p.id,
                p.cliente,
                ', '.join(p.productos),  # o usar JSON si la tabla lo permite
                p.total,
                p.fecha.isoformat()
            ))

        conn_pg.commit()
        cur_pg.close()
        conn_pg.close()

        for p in pedidos:
            pedidos_fallback.marcar_como_sincronizado(p.id)

        print(f"✅ Sincronizados {len(pedidos)} pedidos a PostgreSQL.")

    except Exception as e:
        print(f"❌ Error sincronizando pedidos: {e}")
