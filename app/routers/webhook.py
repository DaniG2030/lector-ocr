import logging
import os
from dotenv import load_dotenv
import uuid
from pathlib import Path
import requests
from fastapi import APIRouter, BackgroundTasks, HTTPException, Query, Request
from fastapi.responses import JSONResponse, PlainTextResponse

load_dotenv()

from app.database import get_db_connection
from app.services.ocr_service import extraer_datos_comprobante
from app.services.ia_validator import validar_pago_con_ia

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/webhook", tags=["Webhook WhatsApp"])

VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN", "WHATSAPP_VERIFY_TOKEN")
WHATSAPP_TOKEN = os.getenv("WHATSAPP_API_TOKEN", "WHATSAPP_API_TOKEN")
UPLOADS_DIR = Path(os.getenv("UPLOADS_DIR", "/var/www/redyon-app/uploads"))
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

def _descargar_imagen_desde_meta(image_id: str) -> Path | None:
    if not image_id: 
        return None
    if not WHATSAPP_TOKEN or WHATSAPP_TOKEN == "WHATSAPP_API_TOKEN":
        logger.error("WHATSAPP_API_TOKEN no está configurado")
        return None
        
    headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}"}
    try:
        metadata_resp = requests.get(f"https://graph.facebook.com/v20.0/{image_id}", headers=headers, timeout=30)
        metadata_resp.raise_for_status()
        media_info = metadata_resp.json()
        media_url = media_info.get("url")
        mime_type = media_info.get("mime_type", "image/jpeg")

        if not media_url: 
            return None

        image_resp = requests.get(media_url, headers=headers, timeout=30)
        image_resp.raise_for_status()

        extension = "jpg"
        if "png" in mime_type: extension = "png"
        elif "webp" in mime_type: extension = "webp"

        nombre = f"{uuid.uuid4()}.{extension}"
        ruta_local = UPLOADS_DIR / nombre
        ruta_local.write_bytes(image_resp.content)
        return ruta_local
    except Exception as e:
        logger.exception("Error descargando la imagen")
        return None

def _obtener_o_crear_cliente(telefono: str, nombre: str = "Desconocido") -> int:
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id FROM clientes WHERE telefono = %s;", (telefono,))
        result = cursor.fetchone()
        if result:
            return result[0]
        cursor.execute("INSERT INTO clientes (telefono, nombre) VALUES (%s, %s) RETURNING id;", (telefono, nombre))
        new_id = cursor.fetchone()[0]
        conn.commit()
        return new_id
    finally:
        cursor.close()
        conn.close()

# CORRECCIÓN DEFINITIVA: Quitamos 'confianza_ia' y cualquier columna que no exista en tu BD
def _guardar_pago(cliente_id: int, clave_rastreo: str, monto: float, ruta_local: str, estado: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO pagos (cliente_id, clave_rastreo, monto, url_comprobante_imagen, estado_validacion)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (cliente_id, clave_rastreo, monto, str(ruta_local), estado),
        )
        conn.commit()
    except Exception as e:
        logger.error(f"Error guardando el pago en PostgreSQL: {e}")
    finally:
        cursor.close()
        conn.close()

@router.get("/")
async def verificar_webhook(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_challenge: str = Query(None, alias="hub.challenge"),
    hub_verify_token: str = Query(None, alias="hub.verify_token"),
):
    if hub_mode == "subscribe" and hub_verify_token == VERIFY_TOKEN:
        return PlainTextResponse(content=hub_challenge, status_code=200)
    raise HTTPException(status_code=403, detail="Token de verificación inválido")

def procesar_payload_whatsapp(payload: dict):
    try:
        for entry in payload.get("entry", []):
            for change in entry.get("changes", []):
                value = change.get("value", {})
                messages = value.get("messages", [])
                contacts = value.get("contacts", [])
                
                nombre_contacto = contacts[0].get("profile", {}).get("name", "Desconocido") if contacts else "Desconocido"

                for message in messages:
                    telefono = message.get("from")
                    
                    if message.get("type") == "image":
                        image_id = message["image"].get("id")
                        ruta_imagen = _descargar_imagen_desde_meta(image_id)
                        
                        if ruta_imagen:
                            cliente_id = _obtener_o_crear_cliente(telefono, nombre_contacto)
                            
                            ocr_res = extraer_datos_comprobante(str(ruta_imagen))
                            
                            texto_crudo = ocr_res.get("texto_completo", "")
                            folio_detectado = ocr_res.get("folio_detectado", "S/F")
                            monto_detectado = ocr_res.get("monto_detectado", 0.0)
                            
                            estado_ia = validar_pago_con_ia(texto_crudo, monto_detectado)
                            
                            # ACTUALIZADO: Solo mandamos los datos que PostgreSQL acepta
                            _guardar_pago(
                                cliente_id=cliente_id,
                                clave_rastreo=folio_detectado,
                                monto=monto_detectado,
                                ruta_local=str(ruta_imagen),
                                estado=estado_ia
                            )
    except Exception as e:
        logger.error(f"Error procesando webhook: {e}")

@router.post("/")
async def recibir_webhook(request: Request, background_tasks: BackgroundTasks):
    payload = await request.json()
    background_tasks.add_task(procesar_payload_whatsapp, payload)
    return JSONResponse(content={"status": "ok"}, status_code=200)
