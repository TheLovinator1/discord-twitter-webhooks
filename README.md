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

- Install [Docker](https://docs.docker.com/get-docker/).
- Grab the docker-compose.yml file from the repository.
    - You can download it directly
      from [here](https://raw.githubusercontent.com/TheLovinator1/discord-twitter-webhooks/master/docker-compose.yml).
- Modify the volume path to where you want the database to be stored.
    - The default is `./data:/app/data` which will create a folder called `data` in the same folder as the
      docker-compose.yml file.
    - You can also use an absolute path (e.g., `/home/user/discord-twitter-webhooks/data:/app/data`).

### Install directly on your computer

This is not recommended if you don't have an init system (e.g., systemd)

- Install the latest version of needed software:
    - [Python](https://www.python.org/)
        - You should use the latest version.
        - You want to add Python to your PATH.
        - Windows: Find `App execution aliases` and disable python.exe and python3.exe
    - [Poetry](https://python-poetry.org/docs/master/#installation)
        - Windows: You have to add `%appdata%\Python\Scripts` to your PATH for Poetry to work.
- Download the project from GitHub with Git or download
  the [ZIP](https://github.com/TheLovinator1/discord-twitter-webhooks/archive/refs/heads/master.zip).
    - If you want to update the bot, you can run `git pull` in the project folder or download the ZIP again.
- Rename .env.example to .env and open it in a text editor (e.g.,
  VSCode, Notepad++, Notepad) and fill it out.
    - Your settings will be stored in the .env file, not settings.py.
    - If you can't see the file extension:
        - Windows 10: Click the View Tab in File Explorer and click the box next to File name extensions.
        - Windows 11: Click View -> Show -> File name extensions.
- Open a terminal in the repository folder.
    - Windows 10: <kbd>Shift</kbd> + <kbd>right-click</kbd> in the folder and select `Open PowerShell window here`
    - Windows 11: <kbd>Shift</kbd> + <kbd>right-click</kbd> in the folder and Show more options
      and `Open PowerShell window here`
- Install requirements:
    - Type `poetry install` into the PowerShell window. Make sure you are
      in the repository folder where the [pyproject.toml](pyproject.toml) file is located.
        - (You may have to restart your terminal if it can't find the `poetry` command. Also double check it is in
          your PATH.)
- Start the bot:
    - Type `poetry run bot` into the PowerShell window.
        - You can stop the bot with <kbd>Ctrl</kbd> + <kbd>c</kbd>.

Note: You will need to run `poetry install` again if [poetry.lock](poetry.lock) has been modified.

## Need help?

- Email: [tlovinator@gmail.com](mailto:tlovinator@gmail.com)
- Discord: TheLovinator#9276
- Send an issue: [discord-twitter-webhooks/issues](https://github.com/TheLovinator1/discord-twitter-webhooks/issues)
