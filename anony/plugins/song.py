import os
from pyrogram import Client, filters
from pyrogram.types import Message
from anony import app
from anony.core.youtube import YouTube

yt = YouTube()

@app.on_message(filters.command(['song', 'indir', 'music']))
async def song_download(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text('Lütfen bir şarkı adı veya YouTube linki girin.\nÖrn: `/song Venom`')
    query = ' '.join(message.command[1:])
    m = await message.reply_text('🔍 Şarkı aranıyor...')
    try:
        track = await yt.search(query, message.id)
        if not track:
            return await m.edit_text('❌ Şarkı bulunamadı.')
        await m.edit_text('📥 İndiriliyor...')
        file_path = await yt.download(track.id)
        if not file_path or not os.path.exists(file_path):
            return await m.edit_text('❌ İndirme başarısız oldu.')
        await m.edit_text('📤 Yükleniyor...')
        await message.reply_audio(
            audio=file_path,
            title=track.title,
            performer=track.channel_name,
            duration=track.duration_sec,
            caption=f'🎵 **{track.title}**\n👤 {track.channel_name}'
        )
        await m.delete()
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        await m.edit_text(f'❌ Hata oluştu: {e}')
