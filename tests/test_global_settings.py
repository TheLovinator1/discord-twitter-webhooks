from pathlib import Path

from reader import Reader, make_reader

from discord_twitter_webhooks.dataclasses import GlobalSettings
from discord_twitter_webhooks.global_settings import get_global_settings


def test_get_global_settings(tmp_path: Path) -> None:
    """Test get_global_settings.

    Args:
        tmp_path: Use a temporary path. This is a pytest fixture.
    """
    our_reader: Reader = make_reader(str(tmp_path / "test.db"))

    global_settings_empty: GlobalSettings = set_global_settings(
        our_reader,
        "https://nitter.lovinator.space",
        "https://translate.lovinator.space",
        False,
    )
    assert not global_settings_empty.send_errors_to_discord_webhook

    our_reader.set_tag((), "global_nitter_instance", "https://nitter.net")  # type: ignore  # noqa: PGH003
    our_reader.set_tag((), "global_translator_instance", "https://translate.example.com")  # type: ignore  # noqa: PGH003, E501
    our_reader.set_tag((), "global_send_errors_to_discord", True)  # type: ignore  # noqa: PGH003
    our_reader.set_tag((), "global_send_errors_to_discord_webhook", "https://discord.com")  # type: ignore  # noqa: PGH003, E501

    global_settings: GlobalSettings = set_global_settings(
        our_reader,
        "https://nitter.net",
        "https://translate.example.com",
        True,
    )
    assert global_settings.send_errors_to_discord_webhook == "https://discord.com"

    # Check that there are no other tags.
    assert len(list(our_reader.get_tags(()))) == 4  # noqa: PLR2004


def set_global_settings(
    our_reader: Reader,
    nitter_instance: str,
    translator_instance: str,
    send_errors: bool,
) -> GlobalSettings:
    """Set the global settings.

    Args:
        our_reader: The reader that has the global settings.
        nitter_instance: The nitter instance to use.
        translator_instance: The translator instance to use.
        send_errors: Whether or not to send errors to Discord.

    Returns:
        The global settings.
    """
    result: GlobalSettings = get_global_settings(our_reader)
    assert result.nitter_instance == nitter_instance
    assert result.translator_instance == translator_instance
    assert result.send_errors_to_discord is send_errors
    return result
