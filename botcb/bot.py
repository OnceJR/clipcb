import subprocess
import time
import os
from telegram.ext import ApplicationBuilder
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import pytz
from pyrogram import Client, filters  # type: ignore
import subprocess
import time
import os
from pyrogram import Client, filters  # type: ignore

# Configuración de la API de Telegram
API_ID = 24738183  # Reemplaza con tu App API ID
API_HASH = '6a1c48cfe81b1fc932a02c4cc1d312bf'  # Reemplaza con tu App API Hash
BOT_TOKEN = '8031762443:AAHCCahQLQvMZiHx4YNoVzuprzN3s_BM8Es'  # Reemplaza con tu Bot Token

# Inicializar el cliente de Pyrogram
bot = Client('my_bot', api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Función para obtener el enlace del stream usando un proxy residencial
def obtener_enlace_con_proxy(url: str) -> str | None:
    proxy_url = 'http://donfumeteo:43712899As$@us-ca.proxymesh.com:31280'
    command_yt_dlp = [
        'yt-dlp',
        '-f', 'best',
        '-g',            # Obtener enlace directo del stream
        '--proxy', proxy_url,
        url
    ]
    try:
        output = subprocess.check_output(command_yt_dlp, stderr=subprocess.DEVNULL)
        return output.decode('utf-8').strip()
    except subprocess.CalledProcessError as e:
        print(f"Error al obtener el enlace: {e}")
        return None

# Función asíncrona para grabar un clip de 30 segundos sin usar proxy
async def grabar_clip(url: str) -> str:
    filename = f'clip_{time.strftime("%Y%m%d_%H%M%S")}.mp4'
    command_ffmpeg = [
        'ffmpeg',
        '-i', url,
        '-t', '30',     # Duración fija: 30 segundos
        '-c:v', 'copy',
        '-c:a', 'copy',
        filename
    ]
    subprocess.run(command_ffmpeg, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return filename

# Handler para el comando /grabar
@bot.on_message(filters.command('grabar'))
async def handle_grabar(client, message):
    await message.reply("Por favor, envía la URL de la transmisión de Chaturbate.")

# Handler para mensajes de texto con la URL
def is_url(_, message):
    return message.text and message.text.startswith('http')

@bot.on_message(filters.create(is_url))
async def process_url(client, message):
    url = message.text.strip()
    await message.reply("Obteniendo enlace de transmisión... 📡")

    flujo_url = obtener_enlace_con_proxy(url)
    if not flujo_url:
        return await message.reply("❌ No se pudo obtener el enlace de la transmisión.")

    await message.reply("Grabando clip de 30 segundos... 🎬")
    clip_path = await grabar_clip(flujo_url)

    if os.path.exists(clip_path):
        await bot.send_video(message.chat.id, clip_path)
        await message.reply(f"✅ Descarga completada: {flujo_url} (30s)")
        os.remove(clip_path)
    else:
        await message.reply("❌ Error al grabar el clip.")

# Handler para el comando /start
@bot.on_message(filters.command('start'))
async def send_welcome(client, message):
    texto = (
        "¡Hola! Bienvenido a mi bot.\n"
        "Usa /grabar para iniciar la captura de un clip de 30 segundos."
    )
    await message.reply(texto)

# Ejecutar el bot
if __name__ == '__main__':
    bot.run()

# Configuracion de la API
API_ID = 24738183  # Reemplaza con tu App API ID
API_HASH = '6a1c48cfe81b1fc932a02c4cc1d312bf'  # Reemplaza con tu App API Hash
BOT_TOKEN = "8031762443:AAHCCahQLQvMZiHx4YNoVzuprzN3s_BM8Es"  # Reemplaza con tu Bot Token

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

@bot.on_message(filters.command('grabar'))
async def handle_grabar(client, message):
    await message.reply("Por favor, envía la URL de la transmisión de Chaturbate.")

@bot.on_message(filters.text & ~filters.command("start"))  # Solo procesar texto que no es el comando /start
async def process_url(client, message):
    url = message.text
    await message.reply("Obteniendo enlace de transmisión...")

    flujo_url = obtener_enlace_con_proxy(url)  # Obtiene el enlace del flujo con proxy

    if flujo_url:
        await message.reply("Grabando clip de 30 segundos...")
        clip_path = await grabar_clip(flujo_url)  # Graba el clip sin usar proxy
        
        if clip_path:
            await bot.send_video(message.chat.id, clip_path)
            await message.reply(f"Descarga completada: {flujo_url} (30 segundos)")
            os.remove(clip_path)  # Elimina el clip después de enviarlo
        else:
            await message.reply("No se pudo grabar el clip.")
    else:
        await message.reply("No se pudo obtener el enlace de la transmisión.")

@bot.on_message(filters.command('start'))
async def send_welcome(client, message):
    welcome_message = (
        "¡Hola! Bienvenido a mi bot.\n\n"
        "Aquí están los comandos disponibles:\n"
        "/grabar - Graba un clip de 30 segundos de una transmisión de Chaturbate."
    )
    await message.reply(welcome_message)

# Ejecutar el bot
if __name__ == '__main__':
    # Crear la aplicación del bot
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Ajustar la zona horaria en el JobQueue
    app.job_queue.scheduler.configure(timezone=pytz.UTC)

    # Iniciar el bot y comenzar a recibir actualizaciones
    app.run_polling()
