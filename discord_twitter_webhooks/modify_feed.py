from reader import Reader

from discord_twitter_webhooks.set_settings.append_usernames import set_append_usernames
from discord_twitter_webhooks.set_settings.blacklist import (
    set_blacklist,
    set_blacklist_active,
)
from discord_twitter_webhooks.set_settings.embed import (
    set_embed_author_icon_url,
    set_embed_author_name,
    set_embed_author_url,
    set_embed_color,
    set_embed_color_random,
    set_embed_footer_icon_url,
    set_embed_footer_text,
    set_embed_image,
    set_embed_show_author,
    set_embed_show_title,
    set_embed_timestamp,
    set_embed_url,
    set_send_embed,
)
from discord_twitter_webhooks.set_settings.hashtag_link import (
    set_hashtag_link_destination,
)
from discord_twitter_webhooks.set_settings.include_retweets import set_include_retweets
from discord_twitter_webhooks.set_settings.includes_replies import set_include_replies
from discord_twitter_webhooks.set_settings.make_text_a_link import (
    set_make_text_a_link,
    set_make_text_a_link_preview,
    set_make_text_a_link_url,
)
from discord_twitter_webhooks.set_settings.remove_copyright_symbols import (
    set_remove_copyright_symbols,
)
from discord_twitter_webhooks.set_settings.remove_utm import set_remove_utm
from discord_twitter_webhooks.set_settings.send_only_link import (
    set_send_only_link,
    set_send_only_link_preview,
)
from discord_twitter_webhooks.set_settings.send_text import set_send_text
from discord_twitter_webhooks.set_settings.set_webhook_url import set_webhook_url
from discord_twitter_webhooks.set_settings.translate import (
    set_translate,
    set_translate_from,
    set_translate_to,
)
from discord_twitter_webhooks.set_settings.unescape_html import set_unescape_html
from discord_twitter_webhooks.set_settings.upload_media import set_upload_media
from discord_twitter_webhooks.set_settings.username_link import (
    set_username_link_destination,
)
from discord_twitter_webhooks.set_settings.usernames import set_usernames
from discord_twitter_webhooks.set_settings.whitelist import (
    set_whitelist,
    set_whitelist_active,
)


def modify_feed(  # noqa: PLR0913
    reader: Reader,
    name: str = "",
    webhooks: str = "",
    usernames: str = "",
    include_replies: bool = False,
    include_retweets: bool = False,
    send_text: bool = False,
    send_embed: bool = True,
    embed_color: str = "#1DA1F2",
    embed_color_random: bool = False,
    embed_author_name: str = "",
    embed_author_url: str = "",
    embed_author_icon_url: str = "",
    embed_url: str = "",
    embed_timestamp: bool = True,
    embed_image: str = "",
    embed_footer_text: str = "",
    embed_footer_icon_url: str = "",
    embed_show_title: bool = False,
    embed_show_author: bool = True,
    send_only_link: bool = False,
    send_only_link_preview: bool = True,
    make_text_a_link: bool = False,
    make_text_a_link_preview: bool = False,
    make_text_a_link_url: str = "",
    upload_media: bool = False,
    append_usernames: bool = False,
    translate: bool = False,
    translate_to: str = "en",
    translate_from: str = "auto",
    whitelist: str = "",
    whitelist_active: bool = False,
    blacklist: str = "",
    blacklist_active: bool = False,
    unescape_html: bool = True,
    remove_utm: bool = True,
    remove_copyright: bool = True,
    username_destination: str = "Nitter",  # Can be "Nitter" or "Twitter"
    hashtag_destination: str = "Nitter",  # Can be "Nitter" or "Twitter"
) -> None:
    """Modify a feed."""
    # Modify our feed
    set_usernames(reader, name, usernames)
    set_webhook_url(reader, name, webhooks)
    set_include_retweets(reader, name, include_retweets)
    set_include_replies(reader, name, include_replies)

    set_send_text(reader, name, send_text)

    set_send_embed(reader, name, send_embed)
    set_embed_color(reader, name, embed_color)
    set_embed_color_random(reader, name, embed_color_random)
    set_embed_author_name(reader, name, embed_author_name)
    set_embed_author_url(reader, name, embed_author_url)
    set_embed_author_icon_url(reader, name, embed_author_icon_url)
    set_embed_url(reader, name, embed_url)
    set_embed_timestamp(reader, name, embed_timestamp)
    set_embed_image(reader, name, embed_image)
    set_embed_footer_text(reader, name, embed_footer_text)
    set_embed_footer_icon_url(reader, name, embed_footer_icon_url)

    set_embed_show_title(reader, name, embed_show_title)
    set_embed_show_author(reader, name, embed_show_author)

    set_send_only_link(reader, name, send_only_link)
    set_send_only_link_preview(reader, name, send_only_link_preview)
    set_make_text_a_link(reader, name, make_text_a_link)
    set_make_text_a_link_preview(reader, name, make_text_a_link_preview)
    set_make_text_a_link_url(reader, name, make_text_a_link_url)

    set_upload_media(reader, name, upload_media)
    set_append_usernames(reader, name, append_usernames)

    set_translate(reader, name, translate)
    set_translate_to(reader, name, translate_to)
    set_translate_from(reader, name, translate_from)

    set_whitelist(reader, name, whitelist)
    set_whitelist_active(reader, name, whitelist_active)
    set_blacklist(reader, name, blacklist)
    set_blacklist_active(reader, name, blacklist_active)

    set_unescape_html(reader, name, unescape_html)
    set_remove_utm(reader, name, remove_utm)
    set_remove_copyright_symbols(reader, name, remove_copyright)

    set_username_link_destination(reader, name, username_destination)
    set_hashtag_link_destination(reader, name, hashtag_destination)
