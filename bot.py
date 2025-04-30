import os
import logging
import subprocess
from uuid import uuid4
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

# Configura tu token aquí
TOKEN = "8031762443:AAHCCahQLQvMZiHx4YNoVzuprzN3s_BM8Es"

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def descargar_stream(url: str, output_path: str, duracion: int = 30):
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
        logging.error(f"Error al ejecutar ffmpeg: {e}")
        return False

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    chat_id = update.message.chat_id
    if not text.startswith("http"):
        return

    unique_name = f"{uuid4().hex}.mp4"
    ruta_salida = os.path.join("/tmp", unique_name)

    await context.bot.send_message(chat_id, "Procesando el enlace, espera un momento...")

    exito = await descargar_stream(text, ruta_salida)
    if exito:
        try:
            await context.bot.send_video(chat_id=chat_id, video=open(ruta_salida, 'rb'))
        except Exception as e:
            logging.error(f"Error al enviar video: {e}")
            await context.bot.send_message(chat_id, "Hubo un error al enviar el video.")
        finally:
            os.remove(ruta_salida)
    else:
        await context.bot.send_message(chat_id, "No se pudo procesar el enlace.")

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    app.run_polling()
