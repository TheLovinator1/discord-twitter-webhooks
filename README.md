# Discord-twitter-webhooks

<p align="center">
  <img src="https://raw.githubusercontent.com/TheLovinator1/discord-twitter-webhooks/master/Bot.png"/>
</p>

<p align="center"><sup> Theme is https://github.com/KillYoy/DiscordNight <sup></p>

![Docker Pulls](https://img.shields.io/docker/pulls/thelovinator/discord-twitter-webhooks)

`discord-twitter-webhooks` is an automated tool that checks [Twitter](https://twitter.com) for new tweets and sends them to a [Discord](https://discord.com/) webhook.

This bot is configured with a config file (.env) or environment variables and is written in Python.

## Installation

You have two choices, [install directly on your computer](#Install-directly-on-your-computer) or using [Docker](#docker-compose-with-env-file).

### Install directly on your computer

- Install the latest version of needed software:
  - [git](https://git-scm.com/)
    - Default installation is fine.
  - [Python](https://www.python.org/)
    - You should use the latest version.
    - You want to add Python to your PATH.
  - [Poetry](https://python-poetry.org/docs/master/#installation)
    - Windows: You have to add `\AppData\Roaming\Python\Scripts` to your PATH for Poetry to work.
- Download the project from GitHub with git or download the [ZIP](https://github.com/TheLovinator1/discord-twitter-webhooks/archive/refs/heads/master.zip).
  - If you want to update the bot, you can run `git pull` in the project folder or download the ZIP again.
- Rename .env.example to .env and open it in a text editor (e.g., VSCode, Notepad++, Notepad).
  - If you can't see the file extension:
    - Windows 10: Click the View Tab in File Explorer and click the box next to File name extensions.
    - Windows 11: Click View -> Show -> File name extensions.
- Open a terminal in the repository folder.
  - Windows 10: <kbd>Shift</kbd> + <kbd>right-click</kbd> in the folder and select `Open PowerShell window here`
  - Windows 11: <kbd>Shift</kbd> + <kbd>right-click</kbd> in the folder and Show more options and `Open PowerShell window here`
- Install requirements:
  - `poetry install`
    - (You may have to restart your terminal if it can't find the `poetry` command. Also double check that it's in your PATH.)
- Start the bot:
  - `poetry run bot`
    - You can stop the bot with <kbd>Ctrl</kbd> + <kbd>c</kbd>.

Note: You will need to run `poetry install` again if [poetry.lock](poetry.lock) has been modified.

### Docker

Docker Hub: [thelovinator/discord-twitter-webhooks](https://hub.docker.com/r/thelovinator/discord-twitter-webhooks)

- Rename .env.example to .env and open it in a text editor (e.g., VSCode, Notepad++, Notepad).
  - If you can't see the file extension:
    - Windows 10: Click the View Tab in File Explorer and click the box next to File name extensions.
    - Windows 11: Click View -> Show -> File name extensions.
- Open a terminal in the extras folder.
  - Windows 10: <kbd>Shift</kbd> + <kbd>right-click</kbd> in the folder and select `Open PowerShell window here`
  - Windows 11: <kbd>Shift</kbd> + <kbd>right-click</kbd> in the folder and Show more options and `Open PowerShell window here`
- Run the Docker Compose file:
  - `docker-compose up`
    - You can stop the bot with <kbd>Ctrl</kbd> + <kbd>c</kbd>.
    - If you want to run the bot in the background, you can run `docker-compose up -d`.

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
