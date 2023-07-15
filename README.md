# Discord-twitter-webhooks

<p align="center">
  <img src="https://i.lovinator.space/discord-twitter-webhooks.png" title="Example Image" alt="This image shows a tweet from @Steam"/>
</p>

<p align="center">
<sup>
Theme is https://github.com/KillYoy/DiscordNight
</sup>
</p>

`discord-twitter-webhooks` is an automated tool that sends tweets from Twitter to Discord using webhooks.

It is using RSS feeds from [Nitter](https://github.com/zedeus/nitter) to get the tweets.

## Installation

You have two choices, using [Docker](https://hub.docker.com/r/thelovinator/discord-twitter-webhooks)
or [install directly on your computer](#install-directly-on-your-computer).

### Run with Docker

This is the recommended way to install the bot.

Docker Hub: [thelovinator/discord-twitter-webhooks](https://hub.docker.com/r/thelovinator/discord-twitter-webhooks)

- Data is stored in /home/botuser/.local/share/discord_twitter_webhooks in the container.
- The container runs as the bot user with UID 1000 and GID 1000, this means your directory must be owned by UID 1000 and
  GID 1000.

### Install directly on your computer

This is not recommended if you don't have an init system (e.g., systemd)

- Install the latest version of needed software:
    - [Python](https://www.python.org/)
        - You should use the latest version.
        - You want to add Python to your PATH.
        - Windows: Find `App execution aliases` and disable python.exe and python3.exe
    - [Poetry](https://python-poetry.org/docs/master/#installation)
        - Windows: You have to add `%appdata%\Python\Scripts` to your PATH for Poetry to work.
            - Open System Properties
            - Click on Environment Variables...
            - Under User variables find Path and click Edit...
            - Add `%appdata%\Python\Scripts` to the list.
- Download the project from GitHub with Git or download
  the [ZIP](https://github.com/TheLovinator1/discord-twitter-webhooks/archive/refs/heads/master.zip).
    - If you want to update the bot, you can run `git pull` in the project folder or download the ZIP again.
- Open a terminal in the repository folder.
    - Windows 10: <kbd>Shift</kbd> + <kbd>right-click</kbd> in the folder and select `Open PowerShell window here`
    - Windows 11: <kbd>Shift</kbd> + <kbd>right-click</kbd> in the folder and Show more options
      and `Open PowerShell window here`
- Install requirements:
    - Type `poetry install` into the terminal.
- Start the bot:
    - Type `poetry run bot` into the PowerShell window.
        - You can stop the bot with <kbd>Ctrl</kbd> + <kbd>c</kbd>.

Note: You will need to run `poetry install` again if [poetry.lock](poetry.lock) has been modified.
