# Lector OCR de Comprobantes (SIVCB)

Sistema Inteligente de Validación de Comprobantes Bancarios vía WhatsApp. Este proyecto recibe imágenes, extrae datos financieros mediante OCR/IA y los almacena en PostgreSQL.

## Configuración del Entorno (.env)
Por razones de seguridad, el archivo `.env` original no se incluye en este repositorio. 
Para ejecutar el proyecto:
1. Haz una copia del archivo de ejemplo: `cp .env.example .env`
2. Edita el nuevo archivo `.env` con tus credenciales reales (Tokens de Meta y accesos a PostgreSQL).

## Estructura de Carpetas Ignoradas
Este proyecto genera archivos dinámicos que no se suben al repositorio. Al ejecutar el sistema, asegúrate de contar con lo siguiente:
* **`venv/`**: Debes crear tu entorno virtual e instalar las dependencias con `pip install -r requirements.txt`
* **`uploads/`**: Esta carpeta se creará automáticamente cuando Meta envíe la primera imagen.
* **`logs/`**: El sistema generará esta carpeta en automático para guardar el historial de eventos y errores locales.
