import logging
import subprocess
import os
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from selenium_utils import get_m3u8_url

# === CONFIGURACIÓN ===
TELEGRAM_TOKEN = '8031762443:AAHCCahQLQvMZiHx4YNoVzuprzN3s_BM8Es'
TEMP_VIDEO_FILENAME = "grabacion.mp4"
GRABAR_SEGUNDOS = 30  # Duración de la grabación

# === LOGS ===
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# === COMANDOS DEL BOT ===
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('👋 Hola! Envíame un enlace de Stripchat para grabarlo.')

def handle_message(update: Update, context: CallbackContext) -> None:
    text = update.message.text

    if "stripchat.com" not in text:
        update.message.reply_text("❌ Este bot solo acepta enlaces de Stripchat.")
        return

    update.message.reply_text("🔍 Procesando enlace, buscando transmisión...")

    try:
        m3u8_url = get_m3u8_url(text)

        if m3u8_url:
            update.message.reply_text("🎥 Stream encontrado, grabando 30 segundos...")

            # Comando ffmpeg para grabar
            cmd = [
                "ffmpeg", "-y", "-i", m3u8_url,
                "-t", str(GRABAR_SEGUNDOS),
                "-c", "copy", TEMP_VIDEO_FILENAME
            ]
            subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            # Verificar si el archivo realmente existe
            if os.path.exists(TEMP_VIDEO_FILENAME):
                update.message.reply_text("✅ Grabación finalizada, enviando video...")
                with open(TEMP_VIDEO_FILENAME, 'rb') as video_file:
                    update.message.reply_video(video_file)

                # Eliminar el archivo luego de enviar
                os.remove(TEMP_VIDEO_FILENAME)
            else:
                update.message.reply_text("⚠️ Error: no se creó el archivo de video.")
        else:
            update.message.reply_text("⚠️ No pude encontrar el stream. ¿Está online el modelo?")
    except Exception as e:
        logger.error(f"Error inesperado: {e}")
        update.message.reply_text("🚨 Ocurrió un error procesando tu solicitud.")

# === INICIO DEL BOT ===
def main():
    updater = Updater(TELEGRAM_TOKEN)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
