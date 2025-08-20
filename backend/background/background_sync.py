# background/background_sync.py
import time
from threading import Event
from backend.offline import sync_to_postgres
from backend.offline import sync_pedidos_to_postgres
from backend.offline import sync_rutas_to_postgres

def sync_loop(stop_event: Event, interval_seconds=60):
    while not stop_event.is_set():
        try:
            print("🔄 Iniciando sincronización...")
            sync_to_postgres.sync()
            sync_pedidos_to_postgres.sync()
            sync_rutas_to_postgres.sync()
            print("✅ Sincronización completa.")
        except Exception as e:
            print(f"[SyncLoop] Error: {e}")
        stop_event.wait(interval_seconds)
