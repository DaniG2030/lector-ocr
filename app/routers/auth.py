from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import jwt
import os
from datetime import datetime, timedelta

router = APIRouter(tags=["Autenticación"])

# Extraemos la clave secreta directamente de tus variables de entorno (.env)
SECRET_KEY = os.getenv("SECRET_KEY", "clave_de_respaldo_insegura")
ALGORITHM = "HS256"

class LoginData(BaseModel):
    username: str
    password: str

@router.post("/login")
def login(data: LoginData):
    # Aquí validamos las credenciales maestras (admin / redyon_secure_2026)
    if data.username == "admin" and data.password == "redyon_secure_2026":
        # El token será válido por 12 horas
        expiracion = datetime.utcnow() + timedelta(hours=12)
        
        # Generamos el token criptográfico firmado con tu SECRET_KEY
        token = jwt.encode(
            {"sub": data.username, "exp": expiracion}, 
            SECRET_KEY, 
            algorithm=ALGORITHM
        )
        return {"access_token": token, "token_type": "bearer"}
    
    # Si envían datos incorrectos, bloqueamos el acceso
    raise HTTPException(status_code=401, detail="Credenciales inválidas")
