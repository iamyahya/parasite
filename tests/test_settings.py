import os
import pytest

from settings import settings


@pytest.mark.asyncio
async def test_project_variables(client):
    assert settings.DATABASE_DSN == "sqlite://"
