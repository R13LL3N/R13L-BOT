import asyncio
from bot import create_bot
from config import TOKEN
from flask import Flask
from threading import Thread
from dotenv import load_dotenv

load_dotenv()

app = Flask('')

@app.route('/')
def home():
    return "Hello. I am alive!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

async def start_bot():
    bot = await create_bot()
    try:
        await bot.start(TOKEN)
    except KeyboardInterrupt:
        await bot.close()

async def main():
    keep_alive()
    await start_bot()

if __name__ == "__main__":
    asyncio.run(main())
