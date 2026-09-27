from app.database import get_db_connection

try:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT count(*) FROM pagos;")
    resultado = cursor.fetchone()
    print(f"✅ Conexión exitosa. Número de pagos en tabla: {resultado[0]}")
    cursor.close()
    conn.close()
except Exception as e:
    print(f"❌ ERROR CRÍTICO: {e}")
