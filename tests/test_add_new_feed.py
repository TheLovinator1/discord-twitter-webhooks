from pathlib import Path

import pytest
from reader import Reader, make_reader

from discord_twitter_webhooks.add_new_feed import create_group


def test_add_new_feed(tmp_path: str) -> None:  # noqa: C901, PLR0915, PLR0912
    """Test add_new_feed."""
    db_path = Path(tmp_path, "test.db")
    reader: Reader = make_reader(str(db_path))

    # Create a randomized name for the group.
    group_name: str = f"test_{str(db_path).replace('/', '_')}"

    new_feed: str = create_group(
        name=group_name,
        webhook_value="https://twitter.com/elonmusk",
        usernames_value="elonmusk",
        include_retweets=True,
        include_replies=True,
        reader=reader,
    )
    assert new_feed
    assert (
        new_feed
        == f"Added new group '{group_name}' with usernames 'elonmusk'.\n\nWebhook:"
        " 'https://twitter.com/elonmusk'\nInclude retweets: 'True'\nInclude replies: 'True'"
    )

    # Check that the group was added in the database.
    global_tags = reader.get_tags(())
    assert global_tags

    # Check that the group was added in the database.
    for tags in global_tags:
        if tags[0] == f"{group_name}_webhooks":
            assert tags[1] == "https://twitter.com/elonmusk"
        elif tags[0] == f"{group_name}_usernames":
            assert tags[1] == "elonmusk"
        elif tags[0] == f"{group_name}_include_retweets":
            assert tags[1] is True
        elif tags[0] == f"{group_name}_include_replies":
            assert tags[1] is True
        elif tags[0] == f"{group_name}_append_usernames":
            assert tags[1] is False
        elif tags[0] == f"{group_name}_blacklist":
            assert not tags[1]
        elif tags[0] == f"{group_name}_blacklist_active":
            assert tags[1] is False
        elif tags[0] == f"{group_name}_whitelist":
            assert not tags[1]
        elif tags[0] == f"{group_name}_whitelist_active":
            assert tags[1] is False
        elif tags[0] == f"{group_name}_embed_author_icon_url":
            assert not tags[1]
        elif tags[0] == f"{group_name}_embed_author_name":
            assert not tags[1]
        elif tags[0] == f"{group_name}_embed_author_url":
            assert not tags[1]
        elif tags[0] == f"{group_name}_embed_color":
            assert tags[1] == "#1DA1F2"
        elif tags[0] == f"{group_name}_embed_color_random":
            assert tags[1] is False
        elif tags[0] == f"{group_name}_embed_footer_icon_url":
            assert not tags[1]
        elif tags[0] == f"{group_name}_embed_footer_text":
            assert not tags[1]
        elif tags[0] == f"{group_name}_embed_image":
            assert not tags[1]
        elif tags[0] == f"{group_name}_embed_show_author":
            assert tags[1] is True
        elif tags[0] == f"{group_name}_embed_show_title":
            assert not tags[1]
        elif tags[0] == f"{group_name}_embed_timestamp":
            assert tags[1] is True
        elif tags[0] == f"{group_name}_embed_url":
            assert not tags[1]
        elif tags[0] == f"{group_name}_hashtag_link":
            assert tags[1] is True
        elif tags[0] == f"{group_name}_hashtag_link_destination":
            assert tags[1] == "Nitter"
        elif tags[0] == f"{group_name}_make_text_a_link":
            assert tags[1] is False
        elif tags[0] == f"{group_name}_make_text_a_link_preview":
            assert tags[1] is False
        elif tags[0] == f"{group_name}_make_text_a_link_url":
            assert not tags[1]
        elif tags[0] == f"{group_name}_remove_copyright":
            assert tags[1] is True
        elif tags[0] == f"{group_name}_remove_utm":
            assert tags[1] is True
        elif tags[0] == f"{group_name}_send_embed":
            assert tags[1] is True
        elif tags[0] == f"{group_name}_send_only_link":
            assert tags[1] is False
        elif tags[0] == f"{group_name}_send_only_link_preview":
            assert tags[1] is True
        elif tags[0] == f"{group_name}_send_text":
            assert tags[1] is False
        elif tags[0] == f"{group_name}_translate":
            assert tags[1] is False
        elif tags[0] == f"{group_name}_translate_from":
            assert tags[1] == "auto"
        elif tags[0] == f"{group_name}_translate_to":
            assert tags[1] == "en"
        elif tags[0] == f"{group_name}_unescape_html":
            assert tags[1] is True
        elif tags[0] == f"{group_name}_upload_media":
            assert tags[1] is False
        elif tags[0] == f"{group_name}_username_link":
            assert tags[1] is True
        elif tags[0] == f"{group_name}_username_link_destination":
            assert tags[1] == "Nitter"
        else:
            tag_without_group_name: str = tags[0].replace(f"{group_name}", "")
            pytest.fail(f"Unexpected tag: {tag_without_group_name}")
