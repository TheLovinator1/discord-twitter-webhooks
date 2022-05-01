# Discord-twitter-webhooks

<p align="center">
  <img src="https://raw.githubusercontent.com/TheLovinator1/discord-twitter-webhooks/master/Bot.png"/>
</p>

<p align="center"><sup> Theme is https://github.com/KillYoy/DiscordNight <sup></p>

`discord-twitter-webhooks` is an automated tool that checks [Twitter](https://twitter.com) for new tweets and sends them to a [Discord](https://discord.com/) webhook.

This bot is configured with a config file (.env) or environment variables.

## Features

- Change Reddit username and subreddits to clickable links
- Change Twitter username and hashtags to clickable links
- Change t.co url to the actual url
- If the tweet has more than one image, it will merge them into one
  image in the embed
- Remove ®, ™ and © from the tweet text

## Installation

You have two choices, [install directly on your computer](#Install-directly-on-your-computer) or using [Docker](https://hub.docker.com/r/thelovinator/discord-twitter-webhooks).

### Install directly on your computer

- Install the latest version of needed software:
  - [Python](https://www.python.org/)
    - You should use the latest version.
    - You want to add Python to your PATH.
  - [Poetry](https://python-poetry.org/docs/master/#installation)
    - Windows: You have to add `%appdata%\Python\Scripts` to your PATH for Poetry to work.
- Download the project from GitHub with git or download the [ZIP](https://github.com/TheLovinator1/discord-twitter-webhooks/archive/refs/heads/master.zip).
  - If you want to update the bot, you can run `git pull` in the project folder or download the ZIP again.
- Rename .env.example to .env and open it in a text editor (e.g.,
  VSCode, Notepad++, Notepad).
  - Your settings will be stored in the .env file, not settings.py.
  - If you can't see the file extension:
    - Windows 10: Click the View Tab in File Explorer and click the box next to File name extensions.
    - Windows 11: Click View -> Show -> File name extensions.
- Open a terminal in the repository folder.
  - Windows 10: <kbd>Shift</kbd> + <kbd>right-click</kbd> in the folder and select `Open PowerShell window here`
  - Windows 11: <kbd>Shift</kbd> + <kbd>right-click</kbd> in the folder and Show more options and `Open PowerShell window here`
- Install requirements:
  - Type `poetry install` into the PowerShell window. Make sure you are
    in the repository folder with the [pyproject.toml](pyproject.toml) file.
    - (You may have to restart your terminal if it can't find the `poetry` command. Also double check that it's in your PATH.)
- Start the bot:
  - Type `poetry run bot` into the PowerShell window.
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

Add environment variable TEST_WEBHOOK to your environment or the .env before running tests.

- TEST_WEBHOOK=https://discordapp.com/api/webhooks/582694/a3hmHAXItB_lzSYBx0-CeVeUDqac1vT

Run tests with `poetry run pytest`

## FAQ

- `453 - You currently have Essential access which includes access to Twitter API v2 enpoints only` when starting the bot
  - This bot was created before V2 of Twitter's API so you need to apply
    ([here](https://developer.twitter.com/en/portal/apps/new))
    for Elevated API access to get the V1 API keys. After you have applied
    you can go to Projects & Apps -> Create App under Standalone Apps
- `Poetry could not find a pyproject.toml file in the current directory.`
  - You are probably in the wrong directory. Go to root of the project
    where README.md, .env, and pyproject.toml are located.
- `python` or `poetry` is not recognized as an internal or external command
  - You need to install Python and Poetry if not installed or add them
    to your PATH.
    - When installing Python, you should check the box that says
      `Add Python 3.10 to PATH`
  - System Properties -> Environment Variables -> Double-click Path ->
    Add if missing:
    - `%localappdata%\Programs\Python\Python310\Scripts` (Change to your
      Python version)
    - `%localappdata%\Programs\Python\Python310\` (Change to your Python
      version)
    - `%appdata%\Python\Scripts`

## Need help?

- Email: [tlovinator@gmail.com](mailto:tlovinator@gmail.com)
- Discord: TheLovinator#9276
- Steam: [TheLovinator](https://steamcommunity.com/id/TheLovinator/)
- Send an issue: [discord-twitter-webhooks/issues](https://github.com/TheLovinator1/discord-twitter-webhooks/issues)
- GitHub Discussions: [discord-twitter-webhooks/discussions](https://github.com/TheLovinator1/discord-twitter-webhooks/discussions)
