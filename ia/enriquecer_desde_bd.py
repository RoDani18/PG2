# -*- coding: utf-8 -*-
import psycopg2

print("🚀 Script iniciado")

# Validación de importación
try:
    from modelos.entidades import extraer_entidades
    print("✅ Importación exitosa de 'extraer_entidades'")
except Exception as e:
    print(f"❌ Error al importar 'extraer_entidades': {e}")
    exit()

def validar_entidades(entidades):
    """Valida y convierte precio y cantidad si son numéricos"""
    nombre = entidades.get("nombre")
    precio_raw = entidades.get("precio")
    cantidad_raw = entidades.get("cantidad")

    try:
        precio = float(precio_raw) if precio_raw is not None else None
    except ValueError:
        print(f"⚠️ Precio no numérico: {precio_raw}")
        precio = None

    try:
        cantidad = int(cantidad_raw) if cantidad_raw is not None else None
    except ValueError:
        print(f"⚠️ Cantidad no numérica: {cantidad_raw}")
        cantidad = None

    return nombre, precio, cantidad

def enriquecer_desde_pg():
    print("🔌 Conectando a PostgreSQL...")

    try:
        conn = psycopg2.connect(
            dbname="asistentePG",
            user="postgres",
            password="admin123",
            host="localhost",
            port="5432"
        )
        cursor = conn.cursor()
        print("📂 Conexión exitosa")
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return

    print("📋 Consultando frases con intención 'agregar_producto'...")
    try:
        cursor.execute("SELECT id, frase FROM frases_entrenamiento WHERE intencion = 'agregar_producto'")
        filas = cursor.fetchall()
        print(f"🔎 Frases encontradas: {len(filas)}")
    except Exception as e:
        print(f"❌ Error en la consulta: {e}")
        return

    for fila in filas:
        id_, texto = fila
        print(f"\n🧠 Procesando ID {id_} → frase: {texto}")
        try:
            entidades = extraer_entidades(texto)
            print(f"➡️ Extraído: {entidades}")
        except Exception as e:
            print(f"⚠️ Error al extraer entidades: {e}")
            continue

        nombre, precio, cantidad = validar_entidades(entidades)

        try:
            cursor.execute("""
                UPDATE frases_entrenamiento
                SET nombre = %s, precio = %s, cantidad = %s
                WHERE id = %s
            """, (nombre, precio, cantidad, id_))
            print("✅ Frase enriquecida")
        except Exception as e:
            print(f"❌ Error al actualizar frase: {e}")
            conn.rollback()  # Evita que se bloquee la transacción
            continue

    conn.commit()
    conn.close()
    print("\n🎉 Enriquecimiento completado.")

# Ejecutar
enriquecer_desde_pg()
