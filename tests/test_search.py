from pathlib import Path
from typing import TYPE_CHECKING

from reader import Feed, Reader, make_reader

from discord_twitter_webhooks.search import create_html_for_search_results

if TYPE_CHECKING:
    from collections.abc import Iterable


def test_create_html_for_search_results(tmp_path: Path) -> None:
    """Test create_html_for_search_results.

    Args:
        tmp_path: The temporary directory.
    """
    # Create a reader.

    # Create the temp directory.
    Path.mkdir(Path(tmp_path), exist_ok=True)
    assert Path.exists(Path(tmp_path))

    # Create a temporary reader.
    reader: Reader = make_reader(url=str(Path(tmp_path, "test_db.sqlite")))
    assert reader is not None

    # Add a feed to the reader.
    reader.add_feed("https://lovinator.space/rss_test.xml", exist_ok=True)

    # Check that the feed was added.
    feeds: Iterable[Feed] = reader.get_feeds()
    assert feeds is not None
    assert len(list(feeds)) == 1

    # Update the feed to get the entries.
    reader.update_feeds()

    # Get the feed.
    feed: Feed = reader.get_feed("https://lovinator.space/rss_test.xml")
    assert feed is not None

    # Update the search index.
    reader.enable_search()
    reader.update_search()

    # Create the HTML and check if it is not empty.
    search_html: str = create_html_for_search_results("a", reader)
    assert search_html is not None
    assert len(search_html) > 10  # noqa: PLR2004

    # Close the reader, so we can delete the directory.
    reader.close()
