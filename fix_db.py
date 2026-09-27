from app.database import get_db_connection
conn = get_db_connection()
cursor = conn.cursor()
cursor.execute('ALTER TABLE pagos DROP CONSTRAINT IF EXISTS unique_clave_rastreo;')
conn.commit()
print("✅ Candado eliminado")
cursor.close()
conn.close()
