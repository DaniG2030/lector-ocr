import pytesseract
import re
from PIL import Image

def extraer_datos_comprobante(ruta_imagen: str) -> dict:
    try:
        imagen = Image.open(ruta_imagen).convert('L')
        texto_crudo = pytesseract.image_to_string(imagen, lang='spa')
        texto_limpio = texto_crudo.upper().replace('\n', ' ')
        
        # 1. EXTRACCIÓN DE MONTO (Acepta cualquier valor mayor a 0)
        monto_detectado = 0.0
        patrones_monto = [
            r'(?:IMPORTE|TOTAL|MONTO|PAGO)[^\d]*([0-9]{1,3}(?:,\d{3})*(?:\.\d{2})?)',
            r'\$([0-9]{1,3}(?:,\d{3})*(?:\.\d{2})?)',
            r'([0-9]{2,5}\.[0-9]{2})'
        ]
        for patron in patrones_monto:
            for m in re.findall(patron, texto_limpio):
                val = float((m if isinstance(m, str) else m[0]).replace(',', ''))
                if val > 0.0:  # <-- CORREGIDO: Ya acepta transferencias de $1 o $2
                    monto_detectado = val
                    break
            if monto_detectado > 0.0: break

        # 2. EXTRACCIÓN DE FOLIO
        folio_detectado = "S/F"
        palabras_clave = [r'REFERENCIA', r'FOLIO', r'AUTORIZACI[OÓ]N', r'RASTREO', r'OPERACI[OÓ]N', r'AUTORIZA']
        
        for palabra in palabras_clave:
            match = re.search(f"{palabra}[^\dA-Z]*([0-9A-Z]{6,35})", texto_limpio)
            if match:
                folio_detectado = match.group(1)
                break
                
        # Rescate si no dice la palabra clave
        if folio_detectado == "S/F":
            candidatos = re.findall(r'\b([0-9A-Z]{6,35})\b', texto_limpio)
            validos = [c for c in candidatos if any(char.isdigit() for char in c)]
            if validos:
                folio_detectado = max(validos, key=len)

        return {
            "texto_completo": texto_crudo,
            "folio_detectado": folio_detectado,
            "monto_detectado": monto_detectado,
            "banco_detectado": "Detectado"
        }
    except Exception as e:
        print(f"Error en OCR: {e}")
        return {"texto_completo": "", "folio_detectado": "S/F", "monto_detectado": 0.0, "banco_detectado": None}
