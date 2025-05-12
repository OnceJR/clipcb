import os
import logging
import asyncio
import tempfile
from uuid import uuid4

import pytz
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# Carga el token desde la variable de entorno TELEGRAM_TOKEN
TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TOKEN:
    raise RuntimeError("La variable de entorno TELEGRAM_TOKEN no está definida")

# Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def descargar_stream(url: str, salida: str, duracion: int = 30) -> bool:
    """
    Graba un fragmento de stream usando ffmpeg de forma asíncrona.
    """
    cmd = [
        "ffmpeg",
        "-y",
        "-i", url,
        "-t", str(duracion),
        "-c", "copy",
        salida
    ]
    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()
        if proc.returncode != 0:
            logger.error(f"ffmpeg falló ({proc.returncode}): {stderr.decode().strip()}")
            return False
        return True
    except asyncio.CancelledError:
        logger.warning("Descarga cancelada por timeout")
        return False
    except Exception as e:
        logger.exception(f"Error ejecutando ffmpeg: {e}")
        return False

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 ¡Hola! Envíame un enlace de vídeo o stream y te devolveré un clip de 30 segundos."
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    chat_id = update.message.chat_id

    if not url.lower().startswith(("http://", "https://")):
        # Ignorar mensajes que no sean enlaces
        return

    # Creamos un archivo temporal único
    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
        ruta_salida = tmp.name

    await context.bot.send_message(chat_id, "🔄 Procesando enlace, esto puede tardar unos segundos...")

    # Ejecutamos la descarga con un timeout razonable
    try:
        tarea = descargar_stream(url, ruta_salida, duracion=30)
        exito = await asyncio.wait_for(tarea, timeout=60.0)
    except asyncio.TimeoutError:
        logger.error("Timeout al grabar el clip")
        exito = False

    if exito and os.path.exists(ruta_salida):
        try:
            # Enviamos el vídeo y permitimos streaming
            with open(ruta_salida, "rb") as video:
                await context.bot.send_video(chat_id=chat_id, video=video, supports_streaming=True)
        except Exception as e:
            logger.exception(f"Error enviando vídeo: {e}")
            await context.bot.send_message(chat_id, "❌ Hubo un error al enviar el vídeo.")
        finally:
            try:
                os.remove(ruta_salida)
            except OSError:
                logger.warning(f"No se pudo borrar el archivo {ruta_salida}")
    else:
        await context.bot.send_message(chat_id, "❌ No se pudo procesar el enlace. Verifica que sea válido.")

def main():
    # Construye la aplicación
    app = (
        ApplicationBuilder()
        .token(TOKEN)
        .timezone(pytz.UTC)
        .build()
    )

    # Handlers
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(
        MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message)
    )

    # Ejecuta el bot
    logger.info("Bot iniciado. Esperando mensajes...")
    app.run_polling()

if __name__ == "__main__":
    main()
