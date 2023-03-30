import sys

from dotenv import load_dotenv

from discord_twitter_webhooks import get_settings
from discord_twitter_webhooks.logger import setup_logger

# Setup the logger
setup_logger()

# Parse the .env file and then load all the variables found as environment variables.
# TODO: Split .env into multiple files?
load_dotenv(verbose=True)

# https://developer.twitter.com/en/portal/projects-and-apps
bearer_token: str = get_settings.get_bearer_token()

# Get webhook and rule from the environment.
webhooks, rules = get_settings.get_hook_and_rule()
if len(rules) == 0:
    sys.exit("No rules found, you should edit the .env or environment variables to add rules.")

# If we should send errors to Discord.
error_webhook: str = get_settings.get_error_webhook()

# If we should use a custom display name. This is the name that shows up on the left side of the username.
embed_author_name: str = get_settings.get_embed_author_name()

# If we should use a custom author url. This is the url that the display name and username links to.
embed_author_url: str = get_settings.get_embed_author_url()

# If we should use a custom author icon. This is the image on the left side of the display name and username.
embed_author_icon: str = get_settings.get_embed_author_icon()

# If we should use a custom image. This will the image in the embed.
embed_image: str = get_settings.get_embed_image()

# If we should use a custom thumbnail. This is the image on the right side of the embed.
embed_thumbnail: str = get_settings.get_embed_thumbnail()

# If we should use a custom footer text.
embed_footer_text: str = get_settings.get_embed_footer_text()

# If we should use a custom footer icon.
embed_footer_icon: str = get_settings.get_embed_footer_icon()

# Show a timestamp on the bottom of the embed. This will show when the tweet was sent/created.
show_timestamp: bool = get_settings.get_embed_timestamp()

# Our embed color. This is the color of the left side of the embed. This can be a hex color or "random"
embed_color: str = get_settings.get_embed_color()

# If we should show a webhook title. This shows the tweet authors display name and username.
show_title: bool = get_settings.get_show_title()

# If we should show a webhook author. This shows the tweet authors display name, username and profile picture.
show_author: bool = get_settings.get_show_author()

# If the tweet should be sent as a text instead of an embed.
no_embed: bool = get_settings.get_no_embed()

# Add [text](tweet_url) to the tweet text. This will make the text a link.
make_text_link: bool = get_settings.should_make_text_link()

# If we should disable the link preview by adding < > around the link.
make_text_link_twitter_preview: bool = get_settings.get_make_text_link_preview()

# If we should use a custom URL for the link instead of the tweet URL.
make_text_link_custom_url: str = get_settings.get_make_text_link_url()

# If we should only send the link to the tweet.
only_link: bool = get_settings.get_setting_value(env_var="ONLY_LINK", default_value=False)

# If we should disable the link preview by adding < > around the link.
only_link_preview: bool = get_settings.get_setting_value(env_var="ONLY_LINK_PREVIEW", default_value=True)

# Append username to text.
append_username: bool = get_settings.get_setting_value(env_var="APPEND_USERNAME", default_value=False)

# Append link to the end of the tweet text.
append_image_links: bool = get_settings.get_setting_value(env_var="APPEND_IMAGE_LINKS", default_value=False)

# If we should upload images to Discord. Alternative to append_image_links.
upload_images: bool = get_settings.get_setting_value(env_var="UPLOAD_IMAGES", default_value=False)

# Convert t.co links to their original links
remove_tco_links: bool = get_settings.get_convert_tco_links()

# Unescape text like &amp; to &
unescape_text: bool = get_settings.get_unescape_text()

# Replace usernames with a link to the user
replace_username: bool = get_settings.get_replace_username()

# Replace hashtags with a link to the hashtag
replace_hashtag: bool = get_settings.get_replace_hashtags()

# Remove Discord link previews
discord_link_previews: bool = get_settings.get_discord_link_previews()

# Replace subreddits with a link to the subreddit
replace_subreddit: bool = get_settings.get_replace_subreddit()

# Replace Reddit usernames with a link to the user
replace_reddit_username: bool = get_settings.get_replace_reddit_username()

# Remove UTM parameters from links (utm_source, utm_medium, utm_campaign, utm_term, utm_content)
remove_utm_parameters: bool = get_settings.get_remove_utm_parameters()

# Remove copyright symbols (®, ™ and ©)
remove_copyright_symbols: bool = get_settings.get_remove_copyright_symbols()
