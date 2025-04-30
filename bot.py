import os
import logging
import subprocess
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from apscheduler.schedulers.background import BackgroundScheduler

# Configura el bot
TOKEN = '8031762443:AAHCCahQLQvMZiHx4YNoVzuprzN3s_BM8Es'
VIDEO_OUTPUT = 'salida.ts'

# Configura logs
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Función para grabar Stripchat
async def grabar_stripchat(url: str) -> str | None:
    try:
        comando = [
            'streamlink',
            '--hls-duration', '30s',
            url, 'best',
            '-o', VIDEO_OUTPUT
        ]
        subprocess.run(comando, check=True)
        return VIDEO_OUTPUT
    except subprocess.CalledProcessError as e:
        logger.error(f"Error al ejecutar streamlink: {e}")
        return None

# Handler para mensajes con URLs
async def manejar_mensaje(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mensaje = update.message.text
    chat_id = update.message.chat_id

    if not mensaje.startswith("http"):
        await context.bot.send_message(chat_id, "Envíame un enlace válido de Stripchat.")
        return

    await context.bot.send_message(chat_id, "Grabando 30 segundos de la transmisión, espera...")
    path = await grabar_stripchat(mensaje)

    if path and os.path.exists(path):
        try:
            await context.bot.send_video(chat_id, video=open(path, 'rb'))
        finally:
            os.remove(path)
            logger.info("Archivo eliminado del servidor.")
    else:
        await context.bot.send_message(chat_id, "No se pudo grabar el video. Asegúrate de que el enlace esté activo.")

# Start command opcional
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Envíame un enlace de Stripchat para grabar 30 segundos.")

# Scheduler (si necesitas tareas programadas)
scheduler = BackgroundScheduler()
scheduler.start()

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, manejar_mensaje))

    logger.info("Bot iniciado")
    app.run_polling()
