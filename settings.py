import os
import logging
from types import SimpleNamespace
from datetime import timedelta

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from telethon import TelegramClient

load_dotenv()

logging.basicConfig(level=logging.INFO)


class Settings:

    DATABASE_DSN = os.getenv("DATABASE_DSN")

    TELEGRAM_APP_NAME = os.getenv("TELEGRAM_APP_NAME")

    TELEGRAM_API_ID = os.getenv("TELEGRAM_API_ID")

    TELEGRAM_API_HASH = os.getenv("TELEGRAM_API_HASH")

    POST_EXPIRED = timedelta(days=int(os.getenv("POST_EXPIRED")))

    def __new__(cls):
        cls.setup_database()
        # TODO: next
        # if not hasattr(cls, "telegram"):
        #     asyncio.run(cls.setup_telegram())
        return cls

    @classmethod
    def setup_database(cls):
        engine = create_engine(cls.DATABASE_DSN)
        session = sessionmaker(bind=engine)()
        cls.db = SimpleNamespace(engine=engine, session=session)
        return cls

    @classmethod
    async def setup_telegram(cls):
        # Creds can be got here -> https://my.telegram.org/apps
        cls.telegram = TelegramClient(
            cls.TELEGRAM_APP_NAME,
            cls.TELEGRAM_API_ID,
            cls.TELEGRAM_API_HASH,
        )
        if not "test" in cls.TELEGRAM_APP_NAME:
            await cls.telegram.start()
        return cls


settings = Settings()
