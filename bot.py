import logging
import os
import time
import yt_dlp
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Configuración de logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuración de ChromeDriver con Selenium
def iniciar_driver():
    options = Options()
    options.add_argument("--headless")  # Modo sin interfaz gráfica
    chrome_options.add_argument("--disable-dev-shm-usage")  # Previene problemas de memoria
    options.add_argument("--no-sandbox")  # Necesario para VPS    
    chrome_options.add_argument("--remote-debugging-port=9222")  # Soluciona problemas de puerto
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver

# Función para descargar 30 segundos del stream
def grabar_stream(url):
    # Abre el navegador con Selenium
    driver = iniciar_driver()
    
    # Usa Selenium para cargar la página y obtener el enlace m3u8
    driver.get(url)
    
    # Espera a que el stream esté disponible (ajusta el elemento a esperar)
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'stream-class')))
    except Exception as e:
        logger.error(f"Error al cargar la página: {e}")
        driver.quit()
        return None
    
    # Aquí debes obtener el enlace m3u8 de la página
    # Ajusta el código según la estructura de la página
    m3u8_url = driver.find_element(By.TAG_NAME, "video").get_attribute('src')

    driver.quit()
    return m3u8_url

# Función para grabar 30 segundos usando yt-dlp
def grabar_video(m3u8_url, output_path):
    try:
        ydl_opts = {
            'format': 'best',
            'outtmpl': output_path,
            'quiet': True,
            'postprocessors': [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4',  # Puedes elegir otro formato si quieres
            }],
            'postprocessor_args': ['-t', '30'],  # Graba solo 30 segundos
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([m3u8_url])
        return output_path
    except Exception as e:
        logger.error(f"Error al grabar el video: {e}")
        return None

# Función para manejar el comando /start
def start(update: Update, context: CallbackContext):
    update.message.reply_text('¡Hola! Envía un enlace de stream para grabar 30 segundos.')

# Función para manejar los enlaces enviados
def handle_message(update: Update, context: CallbackContext):
    url = update.message.text
    if "http" in url:  # Verifica si es un enlace
        update.message.reply_text("Procesando tu solicitud...")
        
        # Graba el video
        m3u8_url = grabar_stream(url)
        if m3u8_url:
            # Establece la ruta de salida para el video
            video_path = "/tmp/video_grabado.mp4"
            video_path = grabar_video(m3u8_url, video_path)
            
            if video_path:
                # Envía el video grabado al usuario
                with open(video_path, 'rb') as video_file:
                    update.message.reply_video(video_file)
                # Elimina el video después de enviarlo
                os.remove(video_path)
            else:
                update.message.reply_text("Error al grabar el video.")
        else:
            update.message.reply_text("No se pudo obtener el enlace del stream.")
    else:
        update.message.reply_text("Por favor, envía un enlace válido.")

# Función para manejar los errores del bot
def error(update: Update, context: CallbackContext):
    logger.warning(f"Update {update} caused error {context.error}")

def main():
    # Token de tu bot (cámbialo por tu token)
    TOKEN = '8031762443:AAHCCahQLQvMZiHx4YNoVzuprzN3s_BM8Es'
    
    # Inicializar el Updater y el Dispatcher
    updater = Updater(TOKEN, use_context=True)
    
    # Obtener el dispatcher para registrar los handlers
    dispatcher = updater.dispatcher
    
    # Comandos
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    
    # Manejo de errores
    dispatcher.add_error_handler(error)
    
    # Inicia el bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
