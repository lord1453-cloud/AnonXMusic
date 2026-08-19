import os
import asyncio
from pathlib import Path
import yt_dlp
from pyrogram import Client, filters
from pyrogram.types import Message
from py_yt import VideosSearch
from anony import app

def download_mp3(url: str, output_path: str):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': f'{output_path}/%(title)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '320',
        }],
        'quiet': True,
        'no_warnings': True,
        'geo_bypass': True,
        'nocheckcertificate': True,
        'extractor_args': {
            'youtube': {'player_client': ['tv', 'web_safari', 'android']}
        },
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        mp3_file = str(Path(filename).with_suffix('.mp3'))
        return mp3_file, info.get('title', 'Bilinmeyen'), info.get('uploader', 'Spiderman Music'), info.get('duration', 0)

@app.on_message(filters.command(['song', 'indir', 'muzik', 'music']))
async def song_downloader(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text('🕷️ **Lütfen bir şarkı adı veya YouTube linki girin.**\n\nÖrnek: `/song Eminem Venom`')
    
    query = ' '.join(message.command[1:])
    m = await message.reply_text('🕷️ **Ağ atılıyor, şarkı aranıyor...** 🕸️')
    
    try:
        if not query.startswith('http'):
            search = VideosSearch(query, limit=1)
            res = await search.next()
            if not res or not res.get('result'):
                return await m.edit_text('❌ **Şarkı bulunamadı!**')
            url = res['result'][0]['link']
        else:
            url = query
            
        await m.edit_text('📥 **320kbps MP3 olarak indiriliyor...**')
        os.makedirs('downloads', exist_ok=True)
        
        mp3_file, title, performer, duration = await asyncio.to_thread(download_mp3, url, 'downloads')
        
        if not os.path.exists(mp3_file):
            return await m.edit_text('❌ **İndirme sırasında bir hata oluştu.**')
            
        await m.edit_text('📤 **Telegram'a müzik dosyası olarak yükleniyor...**')
        
        await message.reply_audio(
            audio=mp3_file,
            title=title,
            performer=performer,
            duration=int(duration) if duration else 0,
            caption=f'🕷️ **{title}**\n👤 **Sanatçı:** {performer}\n🕸️ @WebShooterAudioBot'
        )
        await m.delete()
        
        if os.path.exists(mp3_file):
            os.remove(mp3_file)
            
    except Exception as e:
        await m.edit_text(f'❌ **Hata:** `{e}`')
