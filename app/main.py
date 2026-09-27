import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.database import get_db_connection
from app.routers import clientes, pagos, webhook, auth

# Obligamos a cargar el archivo .env para que el Token de WhatsApp funcione siempre
load_dotenv()

# RUTAS ABSOLUTAS: Evita que las imágenes fallen si el servidor se ejecuta en segundo plano
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(BASE_DIR, "static")
UPLOADS_DIR = os.path.join(BASE_DIR, "uploads")

os.makedirs(STATIC_DIR, exist_ok=True)
os.makedirs(UPLOADS_DIR, exist_ok=True)

app = FastAPI(
    title="API Redyon - Sistema de Verificación de Comprobantes",
    version="1.0.0"
)

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir los módulos de rutas
app.include_router(auth.router)
app.include_router(clientes.router)
app.include_router(pagos.router)
app.include_router(webhook.router)

# Montaje con rutas absolutas
app.mount("/panel", StaticFiles(directory=STATIC_DIR, html=True), name="panel")
app.mount("/uploads", StaticFiles(directory=UPLOADS_DIR), name="uploads")  

@app.get("/")
def read_root():
    return {
        "status": "online",
        "service": "SIVCB Redyon API",
        "version": "1.0.0"
    }

@app.get("/health")
def health_check():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1;")
        cursor.close()
        conn.close()
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/planes")
def obtener_planes():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM planes;")
        planes = cursor.fetchall()
        cursor.close()
        conn.close()
        return {"total": len(planes), "planes": planes}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
