from typing import TYPE_CHECKING

from loguru import logger
from reader import EntrySearchResult, Feed, HighlightedString, Reader
from reader.exceptions import FeedNotFoundError

from discord_twitter_webhooks.settings import get_reader

if TYPE_CHECKING:
    from collections.abc import Iterable


def create_html_for_search_results(query: str, custom_reader: Reader | None = None) -> str:
    """Create HTML for the search results.

    Args:
        query: Our search query
        custom_reader: The reader. If None, we will get the reader from the settings.

    Returns:
        str: The HTML.
    """
    # TODO: There is a .content that also contains text, we should use that if .summary is not available.
    # TODO: We should also add <span> tags to the title.

    # Get the default reader if we didn't get a custom one.
    reader: Reader = get_reader() if custom_reader is None else custom_reader  # type: ignore  # noqa: PGH003

    search_results: Iterable[EntrySearchResult] = reader.search_entries(query)

    html: str = ""
    for result in search_results:
        if ".summary" in result.content:
            try:
                feed: Feed = reader.get_feed(result.feed_url)
            except FeedNotFoundError:
                logger.error(f"Feed not found for {result.feed_url} when creating HTML for search results.")
                continue
            result_summary: str = add_span_with_slice(result.content[".summary"])

            html += f"""
            <div class="p-2 mb-2 border border-dark">
                <a class="text-muted text-decoration-none" href="{feed.link}">
                    <h2>{feed.title}</h2>
                </a>
                {result_summary}
            </div>
            """

    return html


def add_span_with_slice(highlighted_string: HighlightedString) -> str:
    """Add span tags to the string to highlight the search results.

    Args:
        highlighted_string: The highlighted string.

    Returns:
        str: The string with added <span> tags.
    """
    # TODO: We are looping through the highlights and only using the last one. We should use all of them.
    before_span, span_part, after_span = "", "", ""

    for txt_slice in highlighted_string.highlights:
        before_span: str = f"{highlighted_string.value[: txt_slice.start]}"
        span_part: str = f"<span class='bg-warning'>{highlighted_string.value[txt_slice.start: txt_slice.stop]}</span>"
        after_span: str = f"{highlighted_string.value[txt_slice.stop:]}"

    return f"{before_span}{span_part}{after_span}"
