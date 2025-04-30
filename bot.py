import os
import logging
import subprocess
from uuid import uuid4

from apscheduler.util import get_localzone
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    ContextTypes,
    filters,
)

# Tu token de Telegram
TOKEN = "8031762443:AAHCCahQLQvMZiHx4YNoVzuprzN3s_BM8Es"

# Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def descargar_stream(url: str, output_path: str, duracion: int = 30) -> bool:
    comando = [
        "ffmpeg",
        "-y",
        "-i", url,
        "-t", str(duracion),
        "-c", "copy",
        output_path
    ]
    try:
        subprocess.run(comando, check=True)
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Error al ejecutar ffmpeg: {e}")
        return False

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    chat_id = update.message.chat_id

    if not text.startswith("http"):
        return  # ignorar mensajes que no sean enlaces

    unique_name = f"{uuid4().hex}.mp4"
    ruta_salida = os.path.join("/tmp", unique_name)

    await context.bot.send_message(chat_id, "🔄 Procesando el enlace, espera un momento...")

    exito = await descargar_stream(text, ruta_salida)
    if exito:
        try:
            with open(ruta_salida, 'rb') as video_file:
                await context.bot.send_video(chat_id=chat_id, video=video_file)
        except Exception as e:
            logger.error(f"Error al enviar video: {e}")
            await context.bot.send_message(chat_id, "❌ Hubo un error al enviar el video.")
        finally:
            os.remove(ruta_salida)
    else:
        await context.bot.send_message(chat_id, "❌ No se pudo procesar el enlace.")

if __name__ == "__main__":
    app = (
        ApplicationBuilder()
        .token(TOKEN)
        .timezone(get_localzone())   # Zona horaria compatible con pytz via apscheduler
        .build()
    )

    app.add_handler(
        MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message)
    )

    app.run_polling()
