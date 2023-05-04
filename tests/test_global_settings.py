from pathlib import Path

from reader import Reader, make_reader

from discord_twitter_webhooks.dataclasses import GlobalSettings
from discord_twitter_webhooks.global_settings import save_global_settings


def test_save_global_settings(tmp_path: Path) -> None:
    """Test save_global_settings.

    Args:
        tmp_path: Use a temporary path. This is a pytest fixture.
    """
    our_reader: Reader = make_reader(str(tmp_path / "test.db"))

    global_settings_empty = GlobalSettings()
    global_settings_empty.nitter_instance = ""
    global_settings_empty.translator_instance = ""
    global_settings_empty.send_errors_to_discord = False
    global_settings_empty.error_webhook = ""

    save_global_settings(our_reader, global_settings_empty)

    assert not global_settings_empty.error_webhook
    assert not global_settings_empty.nitter_instance
    assert not global_settings_empty.translator_instance
    assert not global_settings_empty.send_errors_to_discord

    # Check that the tags are correct.
    assert not our_reader.get_tag((), "global_nitter_instance")
    assert not our_reader.get_tag((), "global_translator_instance")
    assert not our_reader.get_tag((), "global_send_errors_to_discord")  # type: ignore  # noqa: PGH003
    assert not our_reader.get_tag((), "global_error_webhook")  # type: ignore  # noqa: PGH003

    # Create a new global settings object that has values.
    global_settings = GlobalSettings()
    global_settings.nitter_instance = "https://nitter.net"
    global_settings.translator_instance = "https://translate.example.com"
    global_settings.send_errors_to_discord = True
    global_settings.error_webhook = "https://discord.com"

    save_global_settings(our_reader, global_settings)

    assert global_settings.error_webhook == "https://discord.com"
    assert global_settings.nitter_instance == "https://nitter.net"
    assert global_settings.translator_instance == "https://translate.example.com"
    assert global_settings.send_errors_to_discord

    # Check that there are no other tags.
    assert len(list(our_reader.get_tags(()))) == 4  # noqa: PLR2004

    # Check that the tags are correct.
    assert our_reader.get_tag((), "global_nitter_instance") == "https://nitter.net"  # type: ignore  # noqa: PGH003, E501
    assert our_reader.get_tag((), "global_translator_instance") == "https://translate.example.com"  # type: ignore  # noqa: PGH003, E501
    assert our_reader.get_tag((), "global_send_errors_to_discord")  # type: ignore  # noqa: PGH003
    assert our_reader.get_tag((), "global_error_webhook") == "https://discord.com"  # type: ignore  # noqa: PGH003
