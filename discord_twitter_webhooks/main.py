from pathlib import Path
from typing import Annotated

from fastapi import FastAPI, Form, Request, Response
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from reader import Reader

from discord_twitter_webhooks.add_new_feed import create_group
from discord_twitter_webhooks.get_feed_list import FeedList, get_feed_list
from discord_twitter_webhooks.remove_group import remove_group
from discord_twitter_webhooks.search import create_html_for_search_results
from discord_twitter_webhooks.settings import get_reader

app = FastAPI()
app.mount("/static", StaticFiles(directory=Path(__file__).parent / "static"), name="static")
templates = Jinja2Templates(directory=Path(__file__).parent / "templates")

reader: Reader | None = get_reader()

if not reader:
    msg = "Failed to initialize reader."
    raise RuntimeError(msg)


@app.get("/", response_class=HTMLResponse)
def index(request: Request) -> Response:
    """Return the index page.

    Returns:
        The index page.
    """
    feeds: list[FeedList] = get_feed_list(reader)
    return templates.TemplateResponse("index.html", {"request": request, "feed_list": feeds})


@app.get("/add", response_class=HTMLResponse)
def add(request: Request) -> Response:
    """Return the add page.

    Returns:
        The add page.
    """
    return templates.TemplateResponse("add.html", {"request": request})


@app.post("/add")
def add_post(
    name: Annotated[str, Form()],
    url: Annotated[str, Form()],
    usernames: Annotated[str, Form()],
    include_retweets: Annotated[bool, Form()] = False,  # noqa: FBT002
    include_replies: Annotated[bool, Form()] = False,  # noqa: FBT002
) -> str:
    """Create a new group.

    Returns:
        str: The add page.
    """
    return create_group(
        name=name,
        webhook_value=url,
        usernames_value=usernames,
        include_retweets=include_retweets,
        include_replies=include_replies,
        reader=reader,
    )


@app.post("/remove_group")
def remove_group_post(name: Annotated[str, Form()]) -> str:
    """Remove a group.

    Returns:
        str: The index page.
    """
    return remove_group(name=name, reader=reader)


@app.get("/search", response_class=HTMLResponse)
async def search(request: Request, query: str) -> Response:
    """Get entries matching a full-text search query.

    Args:
        query: The query to search for.
        request: The request object.

    Returns:
        HTMLResponse: The search page.
    """
    reader.update_search()

    context = {
        "request": request,
        "search_html": create_html_for_search_results(query),
        "query": query,
        "search_amount": reader.search_entry_counts(query),
    }
    return templates.TemplateResponse("search.html", context)
