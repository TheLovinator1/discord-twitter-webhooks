from typing import TYPE_CHECKING

from reader import Reader

from discord_twitter_webhooks.reader_settings import get_data_location, get_reader

if TYPE_CHECKING:
    from pathlib import Path


def test_get_data_location() -> None:
    """Test get_data_location."""
    data_location: Path = get_data_location()
    assert data_location.exists()
    assert data_location.is_dir()


def test_get_reader() -> None:
    """Test get_reader."""
    reader: Reader | None = get_reader()
    assert reader is not None
    assert isinstance(reader, Reader)
