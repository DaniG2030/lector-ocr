from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.database import get_db_connection

router = APIRouter(prefix="/pagos", tags=["pagos"])

class RevisionPago(BaseModel):
    estado_validacion: str
    clave_rastreo: Optional[str] = None
    monto: float = 0.0

@router.get("/")
def obtener_todos_los_pagos():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT  
                p.id,  
                p.cliente_id,  
                COALESCE(c.telefono, 'Desconocido') AS cliente_telefono,  
                COALESCE(c.nombre, 'Sin Nombre') AS cliente_nombre,  
                COALESCE(p.clave_rastreo, 'S/F') AS clave_rastreo,  
                COALESCE(p.monto, 0.00) AS monto,  
                COALESCE(p.url_comprobante_imagen, '') AS url_comprobante_imagen,  
                COALESCE(p.estado_validacion, 'PENDIENTE_REVISION_HUMANA') AS estado_validacion
            FROM pagos p
            LEFT JOIN clientes c ON p.cliente_id = c.id
            ORDER BY p.id DESC;
        """)
        
        filas = cursor.fetchall()
        lista_pagos = []
        
        for fila in filas:
            ruta_bd = str(fila[6]).strip() if fila[6] else ""
            url_absoluta = ""
            
            if ruta_bd:
                nombre_archivo = ruta_bd.split("/")[-1]
                # URL Absoluta con tu IP para forzar al frontend a renderizar la imagen
                url_absoluta = f"http://100.71.191.79:8080/uploads/{nombre_archivo}"

            lista_pagos.append({
                "id": fila[0],
                "cliente_id": fila[1],
                "cliente_telefono": fila[2],
                "cliente_nombre": fila[3],
                "clave_rastreo": fila[4],
                "monto": float(fila[5]),
                # BOMBARDEO DE VARIABLES: Cubre cualquier nombre que el frontend esté buscando
                "url_comprobante_imagen": url_absoluta,
                "ruta_imagen": url_absoluta,
                "url_imagen": url_absoluta,
                "imagen": url_absoluta,
                "comprobante": url_absoluta,
                "url_comprobante": url_absoluta,
                "url": url_absoluta,
                "estado_validacion": fila[7]
            })
        
        cursor.close()
        conn.close()
        return {"total": len(lista_pagos), "pagos": lista_pagos}
    except Exception as e:
        print(f"Error en GET /pagos/: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{pago_id}/revision")
def procesar_revision_manual(pago_id: int, revision: RevisionPago):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE pagos  
            SET estado_validacion = %s, clave_rastreo = %s, monto = %s  
            WHERE id = %s;
        """, (revision.estado_validacion, revision.clave_rastreo, revision.monto, pago_id))
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Pago no encontrado")
            
        conn.commit()
        cursor.close()
        conn.close()
        return {"status": "success"}
    except Exception as e:
        print(f"Error en PUT /pagos/revision: {e}")
        raise HTTPException(status_code=500, detail=str(e))
