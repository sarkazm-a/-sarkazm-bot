import os
import re
import asyncio
import tempfile
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
import yt_dlp

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
        "socket_timeout": 15,
        "nocheckcertificate": True,
        "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1"
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            return ydl.prepare_filename(info)
    except Exception as e:
        print(f"Ошибка скачивания: {e}")
        return None

@dp.message(F.text)
async def on_message(message: Message):
    match = URL_RE.search(message.text or "")
    if not match:
        return
    
    url = match.group(1)
    status = await message.reply("⏳ Скачиваю видео...")

    loop = asyncio.get_event_loop()
    with tempfile.TemporaryDirectory() as tmp:
        path = await loop.run_in_executor(None, download_video, url, tmp)
        
        if not path or not os.path.exists(path):
            await status.edit_text("❌ Не удалось скачать видео. Возможно, оно приватное или соцсеть заблокировала скачивание.")
            return
        
        with open(path, "rb") as f:
            await message.reply_video(video=f)
        
        await status.delete()

async def main():
    print("Бот запущен...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
