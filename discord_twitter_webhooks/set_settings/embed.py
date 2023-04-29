from loguru import logger
from reader import Reader


def set_send_embed(reader: Reader, name: str, send_embed: bool) -> None:
    """Set the send_embed tag for the group.

    Args:
        reader: The reader to use to set the tag.
        name: The name of the group.
        send_embed: Whether or not to send embeds.
    """
    logger.debug(f"Setting send_embed for {name} to {send_embed}")
    reader.set_tag((), f"{name}_send_embed", send_embed)  # type: ignore  # noqa: PGH003


def set_embed_color(reader: Reader, name: str, embed_color: str) -> None:
    """Set the embed_color tag for the group.

    Args:
        reader: The reader to use to set the tag.
        name: The name of the group.
        embed_color: The embed_color value.
    """
    logger.debug(f"Setting embed_color for {name} to {embed_color}")
    reader.set_tag((), f"{name}_embed_color", embed_color)  # type: ignore  # noqa: PGH003


def set_embed_color_random(reader: Reader, name: str, embed_color_random: bool) -> None:
    """Set the embed_color_random tag for the group.

    Args:
        reader: The reader to use to set the tag.
        name: The name of the group.
        embed_color_random: Whether or not to use a random color.
    """
    logger.debug(f"Setting embed_color_random for {name} to {embed_color_random}")
    reader.set_tag((), f"{name}_embed_color_random", embed_color_random)  # type: ignore  # noqa: PGH003


def set_embed_author_name(reader: Reader, name: str, embed_author_name: str) -> None:
    """Set the embed_author_name tag for the group.

    Args:
        reader: The reader to use to set the tag.
        name: The name of the group.
        embed_author_name: The embed_author_name value.
    """
    logger.debug(f"Setting embed_author_name for {name} to {embed_author_name}")
    reader.set_tag((), f"{name}_embed_author_name", embed_author_name)  # type: ignore  # noqa: PGH003


def set_embed_author_url(reader: Reader, name: str, embed_author_url: str) -> None:
    """Set the embed_author_url tag for the group.

    Args:
        reader: The reader to use to set the tag.
        name: The name of the group.
        embed_author_url: The embed_author_url value.
    """
    logger.debug(f"Setting embed_author_url for {name} to {embed_author_url}")
    reader.set_tag((), f"{name}_embed_author_url", embed_author_url)  # type: ignore  # noqa: PGH003


def set_embed_author_icon_url(reader: Reader, name: str, embed_author_icon_url: str) -> None:
    """Set the embed_author_icon_url tag for the group.

    Args:
        reader: The reader to use to set the tag.
        name: The name of the group.
        embed_author_icon_url: The embed_author_icon_url value.
    """
    logger.debug(f"Setting embed_author_icon_url for {name} to {embed_author_icon_url}")
    reader.set_tag((), f"{name}_embed_author_icon_url", embed_author_icon_url)  # type: ignore  # noqa: PGH003


def set_embed_url(reader: Reader, name: str, embed_url: str) -> None:
    """Set the embed_url tag for the group.

    Args:
        reader: The reader to use to set the tag.
        name: The name of the group.
        embed_url: The embed_url value.
    """
    logger.debug(f"Setting embed_url for {name} to {embed_url}")
    reader.set_tag((), f"{name}_embed_url", embed_url)  # type: ignore  # noqa: PGH003


def set_embed_timestamp(reader: Reader, name: str, embed_timestamp: bool) -> None:
    """Set the embed_timestamp tag for the group.

    Args:
        reader: The reader to use to set the tag.
        name: The name of the group.
        embed_timestamp: The embed_timestamp value.
    """
    logger.debug(f"Setting embed_timestamp for {name} to {embed_timestamp}")
    reader.set_tag((), f"{name}_embed_timestamp", embed_timestamp)  # type: ignore  # noqa: PGH003


def set_embed_image(reader: Reader, name: str, embed_image: str) -> None:
    """Set the embed_image tag for the group.

    Args:
        reader: The reader to use to set the tag.
        name: The name of the group.
        embed_image: The embed_image value.
    """
    logger.debug(f"Setting embed_image for {name} to {embed_image}")
    reader.set_tag((), f"{name}_embed_image", embed_image)  # type: ignore  # noqa: PGH003


def set_embed_footer_text(reader: Reader, name: str, embed_footer_text: str) -> None:
    """Set the embed_footer_text tag for the group.

    Args:
        reader: The reader to use to set the tag.
        name: The name of the group.
        embed_footer_text: The embed_footer_text value.
    """
    logger.debug(f"Setting embed_footer_text for {name} to {embed_footer_text}")
    reader.set_tag((), f"{name}_embed_footer_text", embed_footer_text)  # type: ignore  # noqa: PGH003


def set_embed_footer_icon_url(reader: Reader, name: str, embed_footer_icon_url: str) -> None:
    """Set the embed_footer_icon_url tag for the group.

    Args:
        reader: The reader to use to set the tag.
        name: The name of the group.
        embed_footer_icon_url: The embed_footer_icon_url value.
    """
    logger.debug(f"Setting embed_footer_icon_url for {name} to {embed_footer_icon_url}")
    reader.set_tag((), f"{name}_embed_footer_icon_url", embed_footer_icon_url)  # type: ignore  # noqa: PGH003


def set_embed_show_title(reader: Reader, name: str, embed_show_title: bool) -> None:
    """Set the embed_show_title tag for the group.

    Args:
        reader: The reader to use to set the tag.
        name: The name of the group.
        embed_show_title: Whether or not to show the title.
    """
    logger.debug(f"Setting embed_show_title for {name} to {embed_show_title}")
    reader.set_tag((), f"{name}_embed_show_title", embed_show_title)  # type: ignore  # noqa: PGH003


def set_embed_show_author(reader: Reader, name: str, embed_show_author: bool) -> None:
    """Set the embed_show_author tag for the group.

    Args:
        reader: The reader to use to set the tag.
        name: The name of the group.
        embed_show_author: Whether or not to show the author.
    """
    logger.debug(f"Setting embed_show_author for {name} to {embed_show_author}")
    reader.set_tag((), f"{name}_embed_show_author", embed_show_author)  # type: ignore  # noqa: PGH003
