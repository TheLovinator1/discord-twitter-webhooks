# Discord-twitter-webhooks

<p align="center">
  <img src="https://i.lovinator.space/discord-twitter-webhooks.png" title="Example Image" alt="This image shows a tweet from @Steam"/>
</p>

<p align="center">
<sup> 
Theme is https://github.com/KillYoy/DiscordNight
</sup>
</p>

`discord-twitter-webhooks` is an automated tool that checks [Twitter](https://twitter.com) for new tweets and sends them
to a [Discord](https://discord.com/) webhook.

This bot is configured with a config file (.env) or environment variables.

## Features

- Change Reddit username and subreddits to clickable links.
- Change Twitter username and hashtags to clickable links.
- Change t.co url to the actual url.
- If the tweet has more than one image, it will merge them into one
  image in the embed.
- Remove ®, ™ and © from the tweet text.
- Five rules can be configured, each with a different webhook.
- Customize the Discord embed.

## Installation

You have three choices, using [Docker](https://hub.docker.com/r/thelovinator/discord-twitter-webhooks),
[Heroku](https://dashboard.heroku.com/apps/discord-twitter-webhooks)
or [install directly on your computer](#Install-directly-on-your-computer).

### Docker

This is the recommended way to install the bot.

Docker Hub: [thelovinator/discord-twitter-webhooks](https://hub.docker.com/r/thelovinator/discord-twitter-webhooks)

- Rename .env.example to .env and open it in a text editor (e.g., VSCode, Notepad++, Notepad) and fill it out.
    - If you can't see the file extension:
        - Windows 10: Click the View Tab in File Explorer and click the box next to File name extensions.
        - Windows 11: Click View -> Show -> File name extensions.
- Open a terminal in the repository folder.
    - Windows 10: <kbd>Shift</kbd> + <kbd>right-click</kbd> in the folder and select `Open PowerShell window here`
    - Windows 11: <kbd>Shift</kbd> + <kbd>right-click</kbd> in the folder and Show more options
      and `Open PowerShell window here`
- Run the Docker Compose file:
    - `docker-compose up`
        - You can stop the bot with <kbd>Ctrl</kbd> + <kbd>c</kbd>.
        - If you want to run the bot in the background, you can run `docker-compose up -d`.
- You can update the container with `docker-compose pull`
    - You can automate this with [Watchtower](https://github.com/containrrr/watchtower)
      or [Diun](https://github.com/crazy-max/diun)

### Heroku

[![Link to deploy this program on Heroku](https://www.herokucdn.com/deploy/button.svg "Deploy")](https://heroku.com/deploy)

- Fill out the form.
    - You can find more information about each environment variable in the [.env.example](.env.example) file. If you
      have any questions, feel free to [contact me](#Need help?)
- If you want to have several webhooks and/or different rules, you can add WEBHOOK_URL2/RULE2, WEBHOOK_URL3/RULE3
  under Settings and then Config Vars. You can find more environment variable in the [.env.example](.env.example) file.
- To run the bot you have to go to Resources, Click the little pen icon besides the worker and activate it.
- Click More in the top right corner and select View logs to see the logs and if the bot is running or not.

### Install directly on your computer

This is not recommended if you don't have an init system (e.g., systemd)

- Install the latest version of needed software:
    - [Python](https://www.python.org/)
        - You should use the latest version.
        - You want to add Python to your PATH.
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

## Rules

More information about the rules can be found in
the [Twitter Documentation](https://developer.twitter.com/en/docs/twitter-api/tweets/filtered-stream/integrate/build-a-rule)
.
Operator (AND, OR, NOT) examples can be found [here](rule-operators.md).

### Get everything from a user

If you want to get tweets, replies, retweets and quotes from @Steam, @Xbox and @PlayStation.

- You can use the following rule:
    - `RULE="from:Steam OR from:Xbox OR from:PlayStation"`
    - See [#remove-retweets-replies-and-quotes](#remove-retweets-replies-and-quotes) if you only want tweets.

### Remove/Only retweets

- Remove retweets by adding -is:retweet to the rule:
    - `RULE="(from:Steam OR from:Xbox OR from:PlayStation) -is:retweet"`
        - Change -is:retweet to is:retweet to only get retweets.
        - Note that we added parentheses to group the operators together otherwise the -is:retweet would only be for
          Playstation.
- If you want to get retweets (and tweets, replies, quotes) from Steam but not Xbox or PlayStation, you can use the
  following rule:
    - `RULE="(from:Steam) OR (-is:retweet (from:Xbox OR from:PlayStation))"`

### Remove/Only replies

- Remove replies by adding -is:reply to the rule.
    - `RULE="(from:Steam OR from:Xbox OR from:PlayStation) -is:reply"`
        - Change -is:reply to is:reply to only get replies.
        - Note that we added parentheses to group the operators together otherwise the -is:reply would only be for
          Playstation.
- If you want to get replies (and tweets, retweets, quotes) from Steam but not Xbox or PlayStation, you can use the
  following rule:
    - `RULE="(from:Steam) OR (-is:reply (from:Xbox OR from:PlayStation))"`

### Remove/Only quote tweets

- Remove quote tweets by adding -is:quote to the rule:
    - `RULE="(from:Steam OR from:Xbox OR from:PlayStation) -is:quote"`
        - Change -is:quote to is:quote to only get quotes
        - Note that we added parentheses to group the operators together otherwise the -is:quote would only be for
          Playstation.
- If you want to get quote tweets (and tweets, retweets, replies) from Steam but not Xbox or PlayStation, you can use
  the following rule:
    - `RULE="(from:Steam) OR (-is:quote (from:Xbox OR from:PlayStation))"`

### Remove retweets, replies and quotes

- If you want to only get tweets from Steam, you can use the following rule:
    - `RULE="from:Steam -is:retweet -is:reply -is:quote"`
- If you have several users you have to use parentheses to group them together:
    - `RULE="(from:Steam OR from:Xbox OR from:PlayStation) -is:retweet -is:reply -is:quote"`

### Get tweets with a specific word

- If you want to get tweets with the words `pepsi`, `cola` or `coca cola`, you
  can use the following rule:
    - `RULE='pepsi OR cola OR "coca cola"'`
        - Note the double quotes around words with spaces.
        - We have to use single quotes around the rule if we used double quotes in the rule.
- If we only want to get tweets from @Xbox that are about Halo you can use the following rule:
    - `RULE="Halo from:Xbox"`
- Several words can be used in the rule:
    - `RULE='("Resident Evil" OR "Team Fortress" OR "Terraria" OR "Free Weekend") from:Steam'`

## Need help?

- Email: [tlovinator@gmail.com](mailto:tlovinator@gmail.com)
- Discord: TheLovinator#9276
- Send an issue: [discord-twitter-webhooks/issues](https://github.com/TheLovinator1/discord-twitter-webhooks/issues)
- GitHub
  Discussions: [discord-twitter-webhooks/discussions](https://github.com/TheLovinator1/discord-twitter-webhooks/discussions)
