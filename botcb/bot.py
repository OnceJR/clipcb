import subprocess
import time
import os
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from pyrogram import Client, filters as pyrogram_filters  # type: ignore

# Configuración de la API
API_ID = 24738183  # Reemplaza con tu App API ID
API_HASH = '6a1c48cfe81b1fc932a02c4cc1d312bf'  # Reemplaza con tu App API Hash
BOT_TOKEN = "8031762443:AAHCCahQLQvMZiHx4YNoVzuprzN3s_BM8Es"  # Reemplaza con tu Bot Token

# Inicialización de Pyrogram (solo para operaciones relacionadas con Pyrogram)
bot = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Función para obtener el enlace con Proxy (con autenticación)
def obtener_enlace_con_proxy(url):
    proxy_url = "http://donfumeteo:43712899As$@us-ca.proxymesh.com:31280"  # Tu proxy con autenticación
    command_yt_dlp = [
        'yt-dlp',
        '-f', 'best',
        '-g',  # Para obtener el enlace directo del stream
        '--proxy', proxy_url,  # Configura el proxy con autenticación
        url
    ]
    
    try:
        output = subprocess.check_output(command_yt_dlp).decode('utf-8').strip()
        return output  # Regresa el enlace del flujo
    except subprocess.CalledProcessError as e:
        print(f"Error al obtener el enlace: {e}")
        return None

# Función para grabar el clip sin usar Proxy
async def grabar_clip(url):
    output_file = f'clip_{time.strftime("%Y%m%d_%H%M%S")}.mp4'  # Nombre del clip
    duration = 30  # Duración fija a 30 segundos

    # Comando para grabar la transmisión usando FFmpeg
    command_ffmpeg = [
        'ffmpeg',
        '-i', url,
        '-t', str(duration),  # Duración fija a 30 segundos
        '-c:v', 'copy',
        '-c:a', 'copy',
        output_file
    ]

    subprocess.run(command_ffmpeg)  # Ejecuta el comando de grabación
    return output_file

# Función para manejar el comando /grabar
async def handle_grabar(update, context):
    await update.message.reply("Por favor, envía la URL de la transmisión de Chaturbate.")

# Función para procesar la URL y grabar el clip
async def process_url(update, context):
    url = update.message.text
    await update.message.reply("Obteniendo enlace de transmisión...")

    flujo_url = obtener_enlace_con_proxy(url)  # Obtiene el enlace del flujo con proxy

    if flujo_url:
        await update.message.reply("Grabando clip de 30 segundos...")
        clip_path = await grabar_clip(flujo_url)  # Graba el clip sin usar proxy
        
        if clip_path:
            await update.message.reply_video(video=open(clip_path, 'rb'))
            await update.message.reply(f"Descarga completada: {flujo_url} (30 segundos)")
            os.remove(clip_path)  # Elimina el clip después de enviarlo
        else:
            await update.message.reply("No se pudo grabar el clip.")
    else:
        await update.message.reply("No se pudo obtener el enlace de la transmisión.")

# Función de bienvenida
async def send_welcome(update, context):
    welcome_message = (
        "¡Hola! Bienvenido a mi bot.\n\n"
        "Aquí están los comandos disponibles:\n"
        "/grabar - Graba un clip de 30 segundos de una transmisión de Chaturbate."
    )
    await update.message.reply(welcome_message)

# Ejecutar el bot
if __name__ == '__main__':
    # Crear la aplicación del bot
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Agregar los manejadores de comandos
    app.add_handler(CommandHandler("start", send_welcome))
    app.add_handler(CommandHandler("grabar", handle_grabar))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, process_url))

    # Iniciar el bot y comenzar a recibir actualizaciones
    app.run_polling()
