# Discord-twitter-webhooks

<p align="center">
  <img src="https://raw.githubusercontent.com/TheLovinator1/discord-twitter-webhooks/master/Bot.png"/>
</p>

<p align="center"><sup> Theme is https://github.com/KillYoy/DiscordNight <sup></p>

![Docker Pulls](https://img.shields.io/docker/pulls/thelovinator/discord-twitter-webhooks)

`discord-twitter-webhooks` is an automated tool that checks [Twitter](https://twitter.com) for new tweets and sends them to a [Discord](https://discord.com/) webhook.

This bot is configured with a config file (.env) or environment variables and is written in Python.

## Installation

- Install latest version of [git](https://git-scm.com/), [Python](https://www.python.org/) and [Poetry](https://python-poetry.org/docs/#installation).
- Download the project from GitHub and change the directory into it.
- Open a terminal in the repository folder.
- Install requirements:
  - `poetry install`
- Rename .env.example to .env and fill it with things from [Twitter](https://developer.twitter.com) and [TweeterID](https://tweeterid.com). If you don't want to use the .env-file you can add variables to your environment.
- Start the bot:
  - `poetry run bot`

You will have to run `poetry install` again if [poetry.lock](poetry.lock) updates.

## Tests

There are not enough tests yet. But we have a few.

Add environment variable TEST_WEBHOOK to your environment or the .env before running tests.

- TEST_WEBHOOK=https://discordapp.com/api/webhooks/582694/a3hmHAXItB_lzSYBx0-CeVeUDqac1vT

Run tests with `poetry run pytest`

## Need help?

- Email: [tlovinator@gmail.com](mailto:tlovinator@gmail.com)
- Discord: TheLovinator#9276
- Steam: [TheLovinator](https://steamcommunity.com/id/TheLovinator/)
- Send an issue: [discord-twitter-webhooks/issues](https://github.com/TheLovinator1/discord-twitter-webhooks/issues)
- GitHub Discussions: [discord-twitter-webhooks/discussions](https://github.com/TheLovinator1/discord-twitter-webhooks/discussions)
