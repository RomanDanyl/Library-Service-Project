import os

import aiohttp
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"


async def send_telegram_message(message: str) -> None:

    async with aiohttp.ClientSession() as session:
        data = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
        try:
            async with session.post(TELEGRAM_API_URL, data=data) as response:
                response_data = await response.json()
                if response.status != 200:
                    print(f"Failed to send message: {response_data}")
        except Exception as e:
            print(f"Error: {e}")
