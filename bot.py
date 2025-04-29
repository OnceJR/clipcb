import os
import subprocess
import logging
from telegram import Update
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext
import yt_dlp

# Configura tu token de bot de Telegram aquí
TELEGRAM_BOT_TOKEN = "8031762443:AAHCCahQLQvMZiHx4YNoVzuprzN3s_BM8Es"

# Constantes
TEMP_VIDEO_FILENAME = "grabacion.mp4"
GRABAR_SEGUNDOS = 30

# Configurar logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def get_m3u8_url(url):
    """Obtiene el enlace m3u8 usando yt-dlp"""
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'skip_download': True,
        'force_generic_extractor': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if 'url' in info:
                return info['url']
            if 'formats' in info and len(info['formats']) > 0:
                return info['formats'][0]['url']
    except Exception as e:
        logger.error(f"Error obteniendo m3u8: {e}")
    return None

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

            if os.path.exists(TEMP_VIDEO_FILENAME):
                update.message.reply_text("✅ Grabación finalizada, enviando video...")

                try:
                    with open(TEMP_VIDEO_FILENAME, 'rb') as video_file:
                        update.message.reply_video(video_file)
                except Exception as e:
                    logger.error(f"Error enviando video: {e}")
                    update.message.reply_text("⚠️ Error enviando el video.")

                # Siempre intentar borrar el archivo
                try:
                    os.remove(TEMP_VIDEO_FILENAME)
                    logger.info("Archivo de video eliminado correctamente.")
                except Exception as e:
                    logger.error(f"No se pudo eliminar el archivo: {e}")

            else:
                update.message.reply_text("⚠️ Error: no se creó el archivo de video.")
        else:
            update.message.reply_text("⚠️ No pude encontrar el stream. ¿Está online el modelo?")
    except Exception as e:
        logger.error(f"Error inesperado: {e}")
        update.message.reply_text("🚨 Ocurrió un error procesando tu solicitud.")

def main():
    """Inicializa el bot"""
    updater = Updater(TELEGRAM_BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
