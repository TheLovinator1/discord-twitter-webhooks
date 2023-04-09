import os
from functools import lru_cache
from pathlib import Path

from loguru import logger
from platformdirs import user_data_dir
from reader import (
    InvalidPluginError,
    PluginError,
    PluginInitError,
    Reader,
    ReaderError,
    SearchError,
    StorageError,
    make_reader,
)

from discord_twitter_webhooks.webhooks import send_error_webhook


@lru_cache
def get_reader(custom_location: Path | None = None) -> Reader:
    """Get the reader.

    Args:
        custom_location: The location of the database file.

    """
    data_dir: Path = get_data_location()
    db_location: Path = custom_location or Path(data_dir) / "discord_twitter_webhooks.sqlite3"

    return make_reader(url=str(db_location))


def get_data_location() -> Path:
    """Get the data location."""
    _user_data_dir: str = user_data_dir(appname="discord_twitter-webhooks", appauthor="TheLovinator", roaming=True)
    data_dir: str = os.getenv("DISCORD_TWITTER_WEBHOOKS_DATA_DIR", default=_user_data_dir)
    Path.mkdir(Path(data_dir), exist_ok=True)
    return Path(data_dir)


def init_reader(
    db_location: Path | None = None,
) -> Reader | None:
    """Create the Reader.

    This function is used to create the Reader and handle any errors
    that may occur.

    Args:
        db_location: Where to store the database.

    Raises:
        StorageError: An error occurred while connecting to storage
        while creating the Reader database.
        SearchError: An error occurred while enabling/disabling search.
        InvalidPluginError: An error occurred while loading plugins.
        PluginInitError: A plugin failed to initialize.
        PluginError: An ambiguous plugin-related error occurred.
        ReaderError: An ambiguous exception occurred while creating
        the reader.

    Returns:
        Reader: The Reader if no errors occurred.
    """
    db_location = get_data_location() if db_location is None else db_location
    db_file: Path = db_location / "discord_twitter_webhooks.db"

    try:
        reader: Reader = make_reader(url=str(db_file))
    except StorageError as e:
        send_error_webhook(
            f"An error occurred while connecting to storage while creating the Reader database.\n{e}",
        )
    except SearchError as e:
        send_error_webhook(f"An error occurred while enabling/disabling search.\n{e}")
    except InvalidPluginError as e:
        send_error_webhook(f"An error occurred while loading plugins.\n{e}")
    except PluginInitError as e:
        send_error_webhook(f"A plugin failed to initialize.\n{e}")
    except PluginError as e:
        send_error_webhook(f"An ambiguous plugin-related error occurred.\n{e}")
    except ReaderError as e:
        msg: str = f"An ambiguous exception occurred while creating the reader.\n{e}"
        send_error_webhook(msg)
    else:
        logger.info("Successfully created Reader at {}", db_location)
        return reader
