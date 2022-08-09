"""Delete old rules and add new rules.

delete_old_rules - Delete old rules from Twitter.
new_rule - Add new rules to Twitter.
"""
import sys

import tweepy

from discord_twitter_webhooks import settings
from discord_twitter_webhooks.send_webhook import send_normal_webhook


def delete_old_rules(stream) -> None:
    """Check if we have any old rules and delete them if we do.

    Args:
        stream: The tweepy stream object
    """

    # Check Twitter app for rules that already have been created.
    old_rules = stream.get_rules()
    settings.logger.debug(f"Old rules: {old_rules}")

    # Get rules and add to list, so we can delete them later.
    rules_to_delete = []
    if old_rules.data and len(old_rules.data) > 0:
        for old_rule in old_rules.data:
            settings.logger.debug(f"Added {old_rule.value} - {old_rule.id} for deletion")
            rules_to_delete.append(old_rule.id)

    # TODO: Only remove rule if the user list has changed?
    # If the app already has rules, delete them first before adding our own
    if rules_to_delete:
        settings.logger.debug(f"Deleting rules: {rules_to_delete}")
        stream.delete_rules(rules_to_delete)
    else:
        settings.logger.debug("App had no rules to delete")


def new_rule(rule, rule_tag, stream) -> str:
    """Add rule to Twitter. If error, exit.

    Args:
        rule: The rule to add.
        rule_tag: The tag label. This is a free-form text you can use to identify the rules.
        stream: The tweepy stream object.
    """
    settings.logger.debug(f"Adding rule: {rule!r} for stream: {stream!r}")
    if rule:
        print(f"Rule: {rule}")
        rule_to_add = tweepy.StreamRule(value=rule, tag=rule_tag)
        rule_response = stream.add_rules(add=rule_to_add)

        if rule_response.errors:
            for error in rule_response.errors:
                error_msg = (f"Error adding rule: {error['value']!r}"
                             f"{error['title']!r} - Error details: {error['details'][0]!r}")
                settings.logger.error(error_msg)
                if settings.send_errors == "True":
                    send_normal_webhook(error_msg, settings.error_webhook)
            sys.exit(1)

        rule_data = rule_response.data
        settings.logger.debug(f"Rule data: {rule_data}")

        return rule_data[0].id
