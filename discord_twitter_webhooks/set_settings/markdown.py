from bs4 import BeautifulSoup


def convert_html_to_md(html: str) -> str:  # noqa: C901
    """Convert HTML to markdown.

    Args:
        html: The HTML to convert.

    Returns:
        Our markdown.
    """
    if not html:
        return html

    soup: BeautifulSoup = BeautifulSoup(html, features="lxml")

    for bold in soup.find_all("b") + soup.find_all("strong"):
        bold.replace_with(f"**{bold.text}**")

    for italic in soup.find_all("i") + soup.find_all("em"):
        italic.replace_with(f"*{italic.text}*")

    for blockquote in soup.find_all("blockquote") + soup.find_all("q"):
        blockquote.replace_with(f">>> {blockquote.text}")

    for code in soup.find_all("code") + soup.find_all("pre"):
        code.replace_with(f"`{code.text}`")

    for image in soup.find_all("img"):
        image.decompose()

    for link in soup.find_all("a") + soup.find_all("link"):
        if not link.get_text().strip():
            link.decompose()
        else:
            link_text: str = link.text or link.get("href")
            link.replace_with(f"[{link_text}]({link.get('href')})")

    for strikethrough in soup.find_all("s") + soup.find_all("del") + soup.find_all("strike"):
        strikethrough.replace_with(f"~~{strikethrough.text}~~")

    for br in soup.find_all("br"):
        br.replace_with("\n")

    clean_soup: BeautifulSoup = BeautifulSoup(str(soup).replace("</p>", "</p>\n"), features="lxml")

    # Remove all other tags
    for tag in clean_soup.find_all(True):
        tag.replace_with(tag.text)

    return clean_soup.text.strip()
