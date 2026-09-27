from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Optional
from app.database import get_db_connection

router = APIRouter(
    prefix="/clientes",
    tags=["Clientes"]
)

class ClienteCreate(BaseModel):
    nombre: str
    telefono: str
    ip_ont: Optional[str] = None

@router.get("/")
def listar_clientes():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM clientes ORDER BY id DESC;")
        clientes = cursor.fetchall()
        cursor.close()
        conn.close()
        return {"total": len(clientes), "clientes": clientes}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/", status_code=status.HTTP_201_CREATED)
def crear_cliente(cliente: ClienteCreate):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO clientes (nombre, telefono, ip_ont)
            VALUES (%s, %s, %s)
            RETURNING *;
            """,
            (cliente.nombre, cliente.telefono, cliente.ip_ont)
        )
        nuevo_cliente = cursor.fetchone()
        conn.commit()
        cursor.close()
        conn.close()
        return {"message": "Cliente registrado exitosamente", "cliente": nuevo_cliente}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error al registrar cliente: {str(e)}")
