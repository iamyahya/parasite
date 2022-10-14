import asyncclick as click

from settings import settings
from models import Source, Channel


@click.option(
    "--entity", type=click.Choice(["source", "channel"]), required=True
)
@click.option("--action", type=click.Choice(["add", "delete"]), required=True)
async def main(entity: str, action: str) -> None:
    if entity == "source":
        name = input("Input Source name: ")
        if action == "add":
            Source(name=name).save()
        elif action == "delete":
            Source(name=name).delete()
    elif entity == "channel":
        await settings.setup_telegram()
        external_id = (
            await settings.telegram.get_entity(input("Input Channel name: "))
        ).id
        if action == "add":
            source_name = input("Input Source name: ")
            source = Source.retreive(where=Source.name == source_name)
            if source is not None:
                Channel(external_id=external_id, source_id=source.id).save()
        elif action == "delete":
            Channel(external_id=external_id).delete()
    # TODO: Implement validation errors


if __name__ == "__main__":
    click.command()(main)()
