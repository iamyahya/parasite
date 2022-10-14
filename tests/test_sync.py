import pytest
from datetime import datetime
from types import SimpleNamespace

from models import Channel, Post, Comment, User
from sync import sync_posts, sync_comments, sync_user


@pytest.mark.asyncio
async def test_sync_posts(client, mocker):
    mocker.patch(
        "telethon.client.telegramclient.TelegramClient.get_entity",
        return_value=None,
    )
    mocker.patch(
        "telethon.client.telegramclient.TelegramClient.get_messages",
        return_value=[
            SimpleNamespace(
                id=34,
                date=datetime.utcnow(),
                message="Post-1 message",
                views=56,
                forwards=67,
            )
        ],
    )
    await sync_posts(Channel(external_id=12))
    # TODO: Tests about post time (doublicated posts in response)


@pytest.mark.asyncio
async def test_sync_comments(client, mocker):
    mocker.patch(
        "telethon.client.telegramclient.TelegramClient.get_entity",
        return_value=None,
    )
    mocker.patch(
        "telethon.client.telegramclient.TelegramClient.get_messages",
        return_value=[
            SimpleNamespace(
                id=34,
                from_id=SimpleNamespace(user_id=56),
                date=datetime.utcnow(),
                message="First comment under post-1",
                reply_to=SimpleNamespace(reply_to_top_id=None),
            ),
            SimpleNamespace(
                id=78,
                from_id=SimpleNamespace(channel_id=90),
                date=datetime.utcnow(),
                message="First comment under post-1",
                reply_to=SimpleNamespace(reply_to_top_id=None),
            ),
        ],
    )
    channel = Channel(
        external_id=1,
        posts=[Post(external_id=12, comments=[], published=datetime.utcnow())],
    )
    await sync_comments(channel)
    post = Post.retreive()
    assert post.external_id == 12
    assert len(post.comments) == 2
    assert post.comments[-1].external_id == 34
    assert post.comments[-1].user.external_id == 56
    assert post.comments[0].external_id == 78
    assert post.comments[0].channel.external_id == 90
    # TODO: Test about reply on comments


@pytest.mark.asyncio
async def test_sync_user(client, mocker):
    mocker.patch(
        "telethon.client.telegramclient.TelegramClient.get_entity",
        return_value=SimpleNamespace(username="admin"),
    )
    assert not User.retreive(where=User.login == "admin")
    await sync_user(User(external_id=12345))
    assert User.retreive(where=User.login == "admin")
    # TODO: Test about users with hidden usernames
