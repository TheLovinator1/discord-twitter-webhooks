import os
from functools import lru_cache
from pathlib import Path

from loguru import logger
from reader import Reader, make_reader


def get_data_location() -> Path:
    """Get the data location where the database file is stored.

    Raises:
        NotImplementedError: The OS is not supported.

    Returns:
        Path: The path to the data directory.
    """
    if os.name == "nt":
        # C:\Users\username\AppData\Roaming
        default_data_dir: Path = Path.home() / "AppData" / "Roaming"
        data_dir: Path = Path(os.environ.get("APPDATA", default_data_dir)) / "discord_twitter_webhooks"
    elif os.name == "posix":
        # /home/username/.local/share
        default_data_dir: Path = Path.home() / ".local" / "share"
        data_dir: Path = Path(os.environ.get("XDG_DATA_HOME", default_data_dir)) / "discord_twitter_webhooks"
    else:
        msg: str = f"Unsupported OS: {os.name}, please open an issue on GitHub"
        raise NotImplementedError(msg)

    # Create the data directory if it doesn't exist
    data_dir.mkdir(parents=True, exist_ok=True)

    logger.info("Data will be stored in {}", data_dir)
    return data_dir


@lru_cache(maxsize=1)
def get_reader(db_location: Path | None = None) -> Reader:
    """Create the Reader.

    This function is used to create the Reader and handle any errors
    that may occur.

    Args:
        db_location: Where to store the database.

    Returns:
        Reader: The Reader if no errors occurred.
    """
    # Check for errors and return them to the user
    db_location = get_data_location() if db_location is None else db_location
    db_file: Path = db_location / "discord_twitter_webhooks.db"

    # Check if directory exists
    if not db_location.exists():
        msg: str = f"Directory {db_location} does not exist"
        raise FileNotFoundError(msg)

    # Check if the user has write access to the database directory
    if not os.access(db_location, os.W_OK):
        msg: str = f"Write access denied to {db_location}"
        raise PermissionError(msg)

    if os.name == "posix":
        logger.debug(
            "Data directory is owned by {uid}:{gid}",
            uid=Path.owner(db_location),
            gid=Path.group(db_location),
        )

    reader: Reader = make_reader(url=str(db_file))
    if reader is None:
        msg = f"Failed to create reader\ndb_location: {db_location}\ndb_file: {db_file}"
        raise RuntimeError(msg)

    return reader
