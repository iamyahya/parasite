import datetime
import logging

import asyncclick as click
from telethon.errors.rpcerrorlist import MsgIdInvalidError
from telethon.tl.types import PeerChannel, PeerUser

from settings import settings
from models import Source, Channel, Post, Comment, User


async def sync_posts(channel: Channel):
    offset_date = None
    posts_len = len(channel.posts)
    if posts_len:
        offset_date = channel.posts[0].published + datetime.timedelta(
            seconds=1
        )
    telegram_channel = await settings.telegram.get_entity(
        PeerChannel(channel.external_id)
    )
    for post in await settings.telegram.get_messages(
        telegram_channel,
        limit=999,
        offset_date=offset_date,
        reverse=True,
    ):
        if post.date != offset_date:
            channel.posts.append(
                Post(
                    external_id=post.id,
                    published=post.date,
                    content=post.message,
                    views=post.views,
                    forwards=post.forwards,
                )
            )
    channel.save()
    logging.info("Add new %i posts", len(channel.posts) - posts_len)


async def sync_comments(channel: Channel):
    telegram_channel = await settings.telegram.get_entity(
        PeerChannel(channel.external_id)
    )
    for post in channel.posts:
        comments_len = len(post.comments)
        post_expired = (
            post.published < datetime.datetime.utcnow() - settings.POST_EXPIRED
        )
        if comments_len and post_expired:
            continue
        try:
            for comment in await settings.telegram.get_messages(
                telegram_channel,
                limit=999,
                reply_to=post.external_id,
                reverse=True,
            ):
                if comment.id in [c.external_id for c in post.comments]:
                    continue
                from_id = comment.from_id
                user_, channel_ = None, None
                if hasattr(from_id, "user_id"):
                    user_ = User(
                        external_id=from_id.user_id
                    ).retreive_or_create()
                else:
                    channel_ = Channel(
                        external_id=from_id.channel_id
                    ).retreive_or_create()
                comment_new = Comment(
                    external_id=comment.id,
                    published=comment.date,
                    content=comment.message,
                    user=user_,
                    channel=channel_,
                )
                post.comments.append(comment_new)
                if comment.reply_to.reply_to_top_id:
                    try:
                        parent_id = comment.reply_to.reply_to_msg_id
                        comments_parent = [
                            c
                            for c in post.comments
                            if c.external_id == parent_id
                        ]
                        comments_parent[0].comments.append(comment_new)
                    except IndexError:
                        logging.warning(
                            "Parent comment #%s not found for reply from #%s",
                            comment_new.external_id,
                            parent_id,
                        )
            post.save()
            logging.info(
                "Parsed new %i comments", len(post.comments) - comments_len
            )
        except MsgIdInvalidError:
            # TODO: Mark post as uncommentable
            logging.info("No comments under %s", post)


async def sync_user(user: User) -> None:
    try:
        user.login = (
            await settings.telegram.get_entity(PeerUser(user.external_id))
        ).username
        if user.login is not None:
            logging.info("User %s updated", user.login)
            user.save()
    except ValueError:
        logging.warning("Can`t update login for %s", user)
    # TODO: Mark user as synced or deleted


@click.option(
    "--entity",
    type=click.Choice(["posts", "comments", "users"]),
    required=True,
)
async def main(entity: str) -> None:
    await settings.setup_telegram()
    if entity == "users":
        for user in User.list(where=User.login.is_(None)):
            await sync_user(user)
    else:
        if entity == "posts":
            handler = sync_posts
        elif entity == "comments":
            handler = sync_comments
        for source in Source.list():
            for channel in source.channels:
                await handler(channel)


if __name__ == "__main__":
    click.command()(main)()
