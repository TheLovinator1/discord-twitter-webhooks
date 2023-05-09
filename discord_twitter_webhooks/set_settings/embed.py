from loguru import logger
from reader import Reader


def set_send_embed(reader: Reader, name: str, send_embed: bool) -> None:
    """Set the send_embed tag for the group.

    Args:
        reader: The reader to use to set the tag.
        name: The name of the group.
        send_embed: Whether or not to send embeds.
    """
    if send_embed is None:
        logger.error("Send embed is None when setting send embed.")
        return

    logger.debug(f"Setting send_embed for {name} to {send_embed}")
    reader.set_tag((), f"{name}_send_embed", send_embed)  # type: ignore  # noqa: PGH003


def set_embed_color(reader: Reader, name: str, embed_color: str) -> None:
    """Set the embed_color tag for the group.

    Args:
        reader: The reader to use to set the tag.
        name: The name of the group.
        embed_color: The embed_color value.
    """
    if (
        embed_color is None
        or not embed_color.startswith("#")
        or len(embed_color) != 7  # noqa: PLR2004
        or any(char not in "0123456789abcdefABCDEF" for char in embed_color[1:])
        or not embed_color
    ):
        logger.error(f"Embed color is None or does not start with # when setting embed color: {embed_color}")
        return

    logger.debug(f"Setting embed_color for {name} to {embed_color}")
    reader.set_tag((), f"{name}_embed_color", embed_color)  # type: ignore  # noqa: PGH003


def set_embed_color_random(reader: Reader, name: str, embed_color_random: bool) -> None:
    """Set the embed_color_random tag for the group.

    Args:
        reader: The reader to use to set the tag.
        name: The name of the group.
        embed_color_random: Whether or not to use a random color.
    """
    if embed_color_random is None:
        logger.error("Embed color random is None when setting embed color random.")
        return
    logger.debug(f"Setting embed_color_random for {name} to {embed_color_random}")
    reader.set_tag((), f"{name}_embed_color_random", embed_color_random)  # type: ignore  # noqa: PGH003


def set_embed_author_name(reader: Reader, name: str, embed_author_name: str) -> None:
    """Set the embed_author_name tag for the group.

    Args:
        reader: The reader to use to set the tag.
        name: The name of the group.
        embed_author_name: The embed_author_name value.
    """
    if embed_author_name is None or not embed_author_name:
        logger.error(f"Embed author name is None or empty when setting embed author name: {embed_author_name}")
        return

    logger.debug(f"Setting embed_author_name for {name} to {embed_author_name}")
    reader.set_tag((), f"{name}_embed_author_name", embed_author_name)  # type: ignore  # noqa: PGH003


def set_embed_author_url(reader: Reader, name: str, embed_author_url: str) -> None:
    """Set the embed_author_url tag for the group.

    Args:
        reader: The reader to use to set the tag.
        name: The name of the group.
        embed_author_url: The embed_author_url value.
    """
    if embed_author_url is None or not embed_author_url:
        logger.error(f"Embed author url is None or empty when setting embed author url: {embed_author_url}")
        return

    logger.debug(f"Setting embed_author_url for {name} to {embed_author_url}")
    reader.set_tag((), f"{name}_embed_author_url", embed_author_url)  # type: ignore  # noqa: PGH003


def set_embed_author_icon_url(reader: Reader, name: str, embed_author_icon_url: str) -> None:
    """Set the embed_author_icon_url tag for the group.

    Args:
        reader: The reader to use to set the tag.
        name: The name of the group.
        embed_author_icon_url: The embed_author_icon_url value.
    """
    if embed_author_icon_url is None or not embed_author_icon_url:
        logger.error(
            f"Embed author icon url is None or empty when setting embed author icon url: {embed_author_icon_url}",
        )
        return

    logger.debug(f"Setting embed_author_icon_url for {name} to {embed_author_icon_url}")
    reader.set_tag((), f"{name}_embed_author_icon_url", embed_author_icon_url)  # type: ignore  # noqa: PGH003


def set_embed_url(reader: Reader, name: str, embed_url: str) -> None:
    """Set the embed_url tag for the group.

    Args:
        reader: The reader to use to set the tag.
        name: The name of the group.
        embed_url: The embed_url value.
    """
    if embed_url is None or not embed_url:
        logger.error(f"Embed url is None or empty when setting embed url: {embed_url}")
        return

    logger.debug(f"Setting embed_url for {name} to {embed_url}")
    reader.set_tag((), f"{name}_embed_url", embed_url)  # type: ignore  # noqa: PGH003


def set_embed_timestamp(reader: Reader, name: str, embed_timestamp: bool) -> None:
    """Set the embed_timestamp tag for the group.

    Args:
        reader: The reader to use to set the tag.
        name: The name of the group.
        embed_timestamp: The embed_timestamp value.
    """
    if embed_timestamp is None:
        logger.error("Embed timestamp is None when setting embed timestamp.")
        return

    logger.debug(f"Setting embed_timestamp for {name} to {embed_timestamp}")
    reader.set_tag((), f"{name}_embed_timestamp", embed_timestamp)  # type: ignore  # noqa: PGH003


def set_embed_image(reader: Reader, name: str, embed_image: str) -> None:
    """Set the embed_image tag for the group.

    Args:
        reader: The reader to use to set the tag.
        name: The name of the group.
        embed_image: The embed_image value.
    """
    if embed_image is None or not embed_image:
        logger.error(f"Embed image is None or empty when setting embed image: {embed_image}")
        return

    logger.debug(f"Setting embed_image for {name} to {embed_image}")
    reader.set_tag((), f"{name}_embed_image", embed_image)  # type: ignore  # noqa: PGH003


def set_embed_footer_text(reader: Reader, name: str, embed_footer_text: str) -> None:
    """Set the embed_footer_text tag for the group.

    Args:
        reader: The reader to use to set the tag.
        name: The name of the group.
        embed_footer_text: The embed_footer_text value.
    """
    if embed_footer_text is None or not embed_footer_text:
        logger.error(f"Embed footer text is None or empty when setting embed footer text: {embed_footer_text}")
        return

    logger.debug(f"Setting embed_footer_text for {name} to {embed_footer_text}")
    reader.set_tag((), f"{name}_embed_footer_text", embed_footer_text)  # type: ignore  # noqa: PGH003


def set_embed_footer_icon_url(reader: Reader, name: str, embed_footer_icon_url: str) -> None:
    """Set the embed_footer_icon_url tag for the group.

    Args:
        reader: The reader to use to set the tag.
        name: The name of the group.
        embed_footer_icon_url: The embed_footer_icon_url value.
    """
    if embed_footer_icon_url is None or not embed_footer_icon_url:
        logger.error(
            f"Embed footer icon url is None or empty when setting embed footer icon url: {embed_footer_icon_url}",
        )
        return

    logger.debug(f"Setting embed_footer_icon_url for {name} to {embed_footer_icon_url}")
    reader.set_tag((), f"{name}_embed_footer_icon_url", embed_footer_icon_url)  # type: ignore  # noqa: PGH003


def set_embed_show_title(reader: Reader, name: str, embed_show_title: bool) -> None:
    """Set the embed_show_title tag for the group.

    Args:
        reader: The reader to use to set the tag.
        name: The name of the group.
        embed_show_title: Whether or not to show the title.
    """
    if embed_show_title is None:
        logger.error("Embed show title is None when setting embed show title.")
        return

    logger.debug(f"Setting embed_show_title for {name} to {embed_show_title}")
    reader.set_tag((), f"{name}_embed_show_title", embed_show_title)  # type: ignore  # noqa: PGH003


def set_embed_show_author(reader: Reader, name: str, embed_show_author: bool) -> None:
    """Set the embed_show_author tag for the group.

    Args:
        reader: The reader to use to set the tag.
        name: The name of the group.
        embed_show_author: Whether or not to show the author.
    """
    if embed_show_author is None:
        logger.error("Embed show author is None when setting embed show author.")
        return

    logger.debug(f"Setting embed_show_author for {name} to {embed_show_author}")
    reader.set_tag((), f"{name}_embed_show_author", embed_show_author)  # type: ignore  # noqa: PGH003
