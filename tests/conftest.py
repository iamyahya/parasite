import asyncio
import pytest

from settings import settings
from models import Base


asyncio.run(settings.setup_telegram())


@pytest.fixture()
async def client():
    for table in Base.metadata.sorted_tables:
        settings.db.session.execute(table.delete())
    settings.db.session.commit()
    Base.metadata.create_all(settings.db.engine)
    yield
