import os
import re
import asyncio
import tempfile
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
import yt_dlp

# Токен берется из настроек сервера
BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

URL_RE = re.compile(r"(https?://(?:www\.)?(?:instagram\.com|tiktok\.com)/\S+)")

def download_video(url: str, out_dir: str):
    ydl_opts = {
        "outtmpl": os.path.join(out_dir, "%(id)s.%(ext)s"),
        "format": "mp4/bestvideo+bestaudio/best",
        "merge_output_format": "mp4",
        "quiet": True,
        "noplaylist": True,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            return ydl.prepare_filename(info)
    except Exception as e:
        print("Ошибка скачивания:", e)
        return None

@dp.message(F.text)
async def on_message(message: Message):
    match = URL_RE.search(message.text or "")
    if not match:
        return
    
    url = match.group(1)
    status = await message.reply("⏳ Скачиваю видео...")

    with tempfile.TemporaryDirectory() as tmp:
        path = download_video(url, tmp)
        if not path or not os.path.exists(path):
            await status.edit_text("❌ Не удалось скачать видео.")
            return
        
        with open(path, "rb") as f:
            await message.reply_video(video=f)
        
        await status.delete()

async def main():
    print("Бот запущен...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
