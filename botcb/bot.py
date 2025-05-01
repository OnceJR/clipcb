```python
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

# Función para obtener el enlace del stream usando ProxyMesh
def obtener_enlace_con_proxy(url: str) -> str | None:
    proxy_url = 'http://donfumeteo:43712899As$@us-ca.proxymesh.com:31280'
    command = [
        'yt-dlp',
        '-f', 'best',       # mejor calidad
        '-g',               # obtener enlace directo
        '--proxy', proxy_url,
        url
    ]
    try:
        result = subprocess.check_output(command, stderr=subprocess.DEVNULL)
        return result.decode('utf-8').strip()
    except subprocess.CalledProcessError as e:
        print('Error al obtener enlace:', e)
        return None

# Función para grabar un clip de 30 segundos sin usar proxy
def grabar_clip(url: str) -> str:
    output_file = f'clip_{time.strftime('%Y%m%d_%H%M%S')}.mp4'
    command = [
        'ffmpeg',
        '-i', url,
        '-t', '30',         # duración en segundos
        '-c:v', 'copy',
        '-c:a', 'copy',
        output_file
    ]
    subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return output_file

# Handler /start
a@bot.on_message(filters.command('start'))
async def send_welcome(client, message):
    await message.reply(
        '¡Hola! Bienvenido. Usa /grabar <URL> para capturar un clip de 30 s de una transmisión de Chaturbate.'
    )

# Handler /grabar\@bot.on_message(filters.command('grabar'))
async def handle_grabar(client, message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        return await message.reply('Uso: /grabar <URL_de_Chaturbate>')

    url = parts[1].strip()
    await message.reply('Obteniendo enlace de transmisión... 📡')

    flujo = obtener_enlace_con_proxy(url)
    if not flujo:
        return await message.reply('❌ No se pudo obtener el enlace.')

    await message.reply('Grabando clip de 30 segundos... 🎬')
    clip_path = grabar_clip(flujo)

    if os.path.exists(clip_path):
        await bot.send_video(message.chat.id, clip_path)
        await message.reply(f'✅ Clip guardado: {clip_path}')
        os.remove(clip_path)
    else:
        await message.reply('❌ Error al grabar el clip.')

# Ejecutar el bot
if __name__ == '__main__':
    bot.run()
```
