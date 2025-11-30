import os
import asyncio
import zipfile
import rarfile
import py7zr
from aiogram import Bot, Dispatcher, types

TOKEN = os.getenv("TOKEN")
bot = Bot(TOKEN)
dp = Dispatcher()

async def extract_archive(filepath, extract_to):
    os.makedirs(extract_to, exist_ok=True)

    if zipfile.is_zipfile(filepath):
        with zipfile.ZipFile(filepath, 'r') as z:
            z.extractall(extract_to)
    elif filepath.lower().endswith(".rar"):
        with rarfile.RarFile(filepath) as r:
            r.extractall(extract_to)
    elif filepath.lower().endswith(".7z"):
        with py7zr.SevenZipFile(filepath, 'r') as z:
            z.extractall(extract_to)
    else:
        return False

    return True


@dp.message()
async def handle_files(message: types.Message):
    if not message.document:
        return

    file = message.document
    filename = file.file_name.lower()

    if not (filename.endswith(".zip") or filename.endswith(".rar") or filename.endswith(".7z")):
        return

    await message.reply("📦 Разархивирую...")

    file_path = f"downloads/{file.file_unique_id}_{file.file_name}"
    os.makedirs("downloads", exist_ok=True)
    await bot.download(file, file_path)

    extract_path = f"extracted/{file.file_unique_id}"
    success = await extract_archive(file_path, extract_path)

    if not success:
        await message.reply("❌ Не удалось распознать архив.")
        return

    for root, dirs, files in os.walk(extract_path):
        for f in files:
            full_path = os.path.join(root, f)
            await message.reply_document(types.FSInputFile(full_path))

    await message.reply("✅ Готово!")


async def main():
    await dp.start_polling(bot)

asyncio.run(main())
