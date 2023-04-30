from dataclasses import dataclass


@dataclass
class Settings:
    webhooks: str | None = None
    include_retweets: bool | None = None
    include_replies: bool | None = None
    send_text: bool = False
    send_embed: bool = True
    embed_color: str = "#1DA1F2"
    embed_color_random: bool = False
    embed_author_name: str = ""
    embed_author_url: str = ""
    embed_author_icon_url: str = ""
    embed_url: str = ""
    embed_timestamp: bool = True
    embed_image: str = ""
    embed_footer_text: str = ""
    embed_footer_icon_url: str = ""
    embed_show_title: bool = False
    embed_show_author: bool = True
    send_only_link: bool = False
    send_only_link_preview: bool = True
    make_text_a_link: bool = False
    make_text_a_link_preview: bool = False
    make_text_a_link_url: str = ""
    upload_media: bool = False
    append_usernames: bool = False
    translate: bool = False
    translate_to: str = "en"
    translate_from: str = "auto"
    whitelist: str = ""
    whitelist_active: bool = False
    blacklist: str = ""
    blacklist_active: bool = False
    unescape_html: bool = True
    remove_utm: bool = True
    remove_copyright: bool = True
    username_link: bool = True
    username_link_destination: str = "Nitter"  # Can be "Nitter" or "Twitter"
    hashtag_link: bool = True
    hashtag_link_destination: str = "Nitter"  # Can be "Nitter" or "Twitter"


@dataclass
class GlobalSettings:
    nitter_instance: str = "https://nitter.lovinator.space"
    translator_instance: str = "https://translate.lovinator.space"
    send_errors_to_discord: bool = False
    send_errors_to_discord_webhook: str = ""
