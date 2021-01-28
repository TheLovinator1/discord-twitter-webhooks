# Discord-twitter-webhooks

<p align="center">
  <img src="https://raw.githubusercontent.com/TheLovinator1/discord-twitter-webhooks/master/Bot.png" />
</p>

<p align="center"><sup> Theme is https://github.com/KillYoy/DiscordNight <sup></p>

`discord-twitter-webhooks` is automated tool that checks [Twitter](https://twitter.com) for new tweets and sends them to a [Discord](https://discord.com/) webhook.

This bot is configured with a config file or environment variables and is written in Python 3.

## Installation

*(click to expand the sections below for full setup instructions)*

<details>
<summary><b>Get discord-twitter-webhooks with <code>docker-compose</code></b></summary><br/><br/>

docker-compose.yml:

```yaml
version: "3"
services:
  discord-twitter-webhooks:
    image: thelovinator/discord-twitter-webhooks
    env_file:
      - .env
    container_name: discord-twitter-webhooks
    environment:
      - WEBHOOK_URL=${WEBHOOK_URL}
      - CONSUMER_KEY=${CONSUMER_KEY}
      - CONSUMER_SECRET=${CONSUMER_SECRET}
      - ACCESS_TOKEN=${ACCESS_TOKEN}
      - ACCESS_TOKEN_SECRET=${ACCESS_TOKEN_SECRET}
      - USERS_TO_FOLLOW=${USERS_TO_FOLLOW}
      - LOG_LEVEL=${LOG_LEVEL}
      - TWITTER_IMAGE_COLLAGE_API=${TWITTER_IMAGE_COLLAGE_API}
    restart: unless-stopped
```

This bot on [Docker Hub](https://hub.docker.com/repository/docker/thelovinator/discord-reminder-bot).

## Environment variables

No space should be between the equal sign in your .env.

Right click channel you want the tweets in -> Integrations -> Webhooks -> New Webhook -> Copy Webhook URL

* WEBHOOK\_URL=https://discordapp.com/api/webhooks/582694/a3hmHAXItB_lzSYBx0-CeVeUDqac1vT

Go to [Twitter](https://developer.twitter.com/en/portal/apps/new) and create an app. If you don't get one try to fill out as much as possible. After it is created go to Keys and tokens. CONSUMER_KEY = API key, CONSUMER_SECRET = API key secret:

* CONSUMER\_KEY=ASFkopkoasfPOFkopaf
* CONSUMER\_SECRET=ASFkopkoasfPOFkopafASFkopkoasfPOFkopafASFkopkoasfPOFkopaf
* ACCESS\_TOKEN=1294501204821094-kKPOASPKOFpkoaskfpo
* ACCESS\_TOKEN\_SECRET=ASKOpokfpkoaspofOPFPO2908iAKOPSFKPO

List of Twitter users to follow, comma separated list with no spaces.

* USERS\_TO\_FOLLOW=12549841489201410,18205090125,852185020125098

How much logging that should be sent to the terminal. Can be CRITICAL, ERROR, WARNING, INFO or DEBUG

* LOG\_LEVEL=INFO

Server that runs [twitter-image-collage-maker](https://github.com/TheLovinator1/twitter-image-collage-maker). See [Privacy](#privacy) for more information.

* TWITTER\_IMAGE\_COLLAGE\_API=https://twitter.lovinator.space/add

</details>
<details>
<summary><b>Get discord-twitter-webhooks with <code>docker cli</code></b></summary><br/><br/>

```console
docker run -d \
  --name=discord-twitter-webhooks \
  -e WEBHOOK_URL=https://discord.com/api/webhooks/151256151521/Drw1jBO9Xyo1hAVsvaNdI1d077dOsfsafAV-nxIDvH-XJeSIeAVavasvkM0Vu \
  -e CONSUMER_KEY=akaopspokfpofasfsaf \
  -e CONSUMER_SECRET=fsa0fskaopfsoapfkofskaopfskopafskopaf \
  -e ACCESS_TOKEN=1521521515-JeASFAd0cGtASifvSSaSFmIr4kopAw8V0oyiH6jN \
  -e ACCESS_TOKEN_SECRET=VlHAS12FYqkQdASFd5XvyunwPaS12F8zPMTZ6IZASF1No \
  -e USERS_TO_FOLLOW=1114707756,36803580 \
  -e LOG_LEVEL=INFO \
  -e TWITTER_IMAGE_COLLAGE_API=https://twitter.lovinator.space/add \
  --restart unless-stopped \
  thelovinator/discord-twitter-webhooks
```

This bot on [Docker Hub](https://hub.docker.com/repository/docker/thelovinator/discord-reminder-bot).

## Environment variables

No space should be between the equal sign in your .env.

Right click channel you want the tweets in -> Integrations -> Webhooks -> New Webhook -> Copy Webhook URL

* WEBHOOK\_URL=https://discordapp.com/api/webhooks/582694/a3hmHAXItB_lzSYBx0-CeVeUDqac1vT
  
Go to [Twitter](https://developer.twitter.com/en/portal/apps/new) and create an app. If you don't get one try to fill out as much as possible. After it is created go to Keys and tokens. CONSUMER_KEY = API key, CONSUMER_SECRET = API key secret:

* CONSUMER\_KEY=ASFkopkoasfPOFkopaf
* CONSUMER\_SECRET=ASFkopkoasfPOFkopafASFkopkoasfPOFkopafASFkopkoasfPOFkopaf
* ACCESS\_TOKEN=1294501204821094-kKPOASPKOFpkoaskfpo
* ACCESS\_TOKEN_SECRET=ASKOpokfpkoaspofOPFPO2908iAKOPSFKPO

List of Twitter users to follow, comma separated list with no spaces.

* USERS\_TO\_FOLLOW=12549841489201410,18205090125,852185020125098

How much logging that should be sent to the terminal. Can be CRITICAL, ERROR, WARNING, INFO or DEBUG

* LOG\_LEVEL=INFO

Server that runs [twitter-image-collage-maker](https://github.com/TheLovinator1/twitter-image-collage-maker). See [Privacy](#privacy) for more information.

* TWITTER_IMAGE_COLLAGE_API=https://twitter.lovinator.space/add

</details>
<details>
<summary><b>Get discord-twitter-webhooks with <code>Python</code> with <code>pipenv</code></b></summary>

* Install latest version of [git](https://git-scm.com/) and [Python 3.9](https://www.python.org/).
* Install pipenv
  * `pip install pipenv`
* Install requirements and make virtual environment
  * `pipenv install`
* Rename .env.example to .env and fill it with things from [Twitter](https://developer.twitter.com) and [TweeterID](https://tweeterid.com). If you don't want to use the .env-file you can add variables to your environment.
* Start the bot
  * `pipenv run python main.py`

## Environment variables

No space should be between the equal sign in your .env.

Right click channel you want the tweets in -> Integrations -> Webhooks -> New Webhook -> Copy Webhook URL

* WEBHOOK\_URL=https://discordapp.com/api/webhooks/582694/a3hmHAXItB_lzSYBx0-CeVeUDqac1vT

Go to [Twitter](https://developer.twitter.com/en/portal/apps/new) and create an app. If you don't get one try to fill out as much as possible. After it is created go to Keys and tokens. CONSUMER_KEY = API key, CONSUMER_SECRET = API key secret:

* CONSUMER\_KEY=ASFkopkoasfPOFkopaf
* CONSUMER\_SECRET=ASFkopkoasfPOFkopafASFkopkoasfPOFkopafASFkopkoasfPOFkopaf
* ACCESS\_TOKEN=1294501204821094-kKPOASPKOFpkoaskfpo
* ACCESS\_TOKEN\_SECRET=ASKOpokfpkoaspofOPFPO2908iAKOPSFKPO

List of Twitter users to follow, comma separated list with no spaces.

* USERS\_TO\_FOLLOW=12549841489201410,18205090125,852185020125098

How much logging that should be sent to the terminal. Can be CRITICAL, ERROR, WARNING, INFO or DEBUG

* LOG\_LEVEL=INFO

Server that runs [twitter-image-collage-maker](https://github.com/TheLovinator1/twitter-image-collage-maker). See [Privacy](#privacy) for more information.

* TWITTER\_IMAGE\_COLLAGE\_API=https://twitter.lovinator.space/add

</details>

<details>
<summary><b>Get discord-twitter-webhooks with <code>Python</code> with <code>pip</code></b></summary>

* Install latest version of [git](https://git-scm.com/) and [Python 3.9](https://www.python.org/)
* Download project from GitHub and change directory into it
* (Optional) Create virtual environment:
  * `python -m venv .venv`
    * Activate virtual environment:
      * Windows:  `.\.venv\Scripts\activate`
      * Not windows:  `source .venv/bin/activate`
* Install requirements
  * `pip install -r requirements.txt`
* Rename .env.example to .env and fill it with things from [Twitter](https://developer.twitter.com) and [TweeterID](https://tweeterid.com). If you don't want to use the .env-file you can add variables to your environment.
* Start the bot (inside the activated virtual environment if you made one):
  * `python main.py`

## Environment variables

No space should be between the equal sign in your .env.

Right click channel you want the tweets in -> Integrations -> Webhooks -> New Webhook -> Copy Webhook URL

* WEBHOOK\_URL=https://discordapp.com/api/webhooks/582694/a3hmHAXItB_lzSYBx0-CeVeUDqac1vT
  
Go to [Twitter](https://developer.twitter.com/en/portal/apps/new) and create an app. If you don't get one try to fill out as much as possible. After it is created go to Keys and tokens. CONSUMER_KEY = API key, CONSUMER_SECRET = API key secret:

* CONSUMER\_KEY=ASFkopkoasfPOFkopaf
* CONSUMER\_SECRET=ASFkopkoasfPOFkopafASFkopkoasfPOFkopafASFkopkoasfPOFkopaf
* ACCESS\_TOKEN=1294501204821094-kKPOASPKOFpkoaskfpo
* ACCESS\_TOKEN\_SECRET=ASKOpokfpkoaspofOPFPO2908iAKOPSFKPO

List of Twitter users to follow, comma separated list with no spaces.

* USERS\_TO\_FOLLOW=12549841489201410,18205090125,852185020125098

How much logging that should be sent to the terminal. Can be CRITICAL, ERROR, WARNING, INFO or DEBUG

* LOG\_LEVEL=INFO

Server that runs [twitter-image-collage-maker](https://github.com/TheLovinator1/twitter-image-collage-maker). See [Privacy](#privacy) for more information.

* TWITTER\_IMAGE\_COLLAGE\_API=https://twitter.lovinator.space/add

</details>

<details>
<summary><b>Automatic start-up on Linux with <code>systemd user services</code></b></summary>

All the user services will be placed in ~/.config/systemd/user/.

User instance of systemd does not inherit any of the environment variables set in places like .bashrc so I recommend you use the .env file.

You may have to modify WorkingDirectory and/or ExecStart. The example have it cloned directly in home.

```ini
~/.config/systemd/user/discord-twitter-webhooks.service

[Unit]
Description=discord-twitter-webhooks
Wants=network-online.target
After=network-online.target

[Service]
Type=simple
WorkingDirectory=%h/discord-twitter-webhooks
ExecStart=/usr/bin/pipenv run python %h/discord-twitter-webhooks/main.py
Restart=always

[Install]
WantedBy=default.target
```

* Start the bot. (You can also use stop and restart instead of start)
  * `systemctl --user start discord-twitter-webhooks`

* Start bot automatically at boot. You may need to run `loginctl enable-linger`
  * `systemctl --user enable discord-twitter-webhooks`

* Check status
  * `systemctl --user status discord-twitter-webhooks`
  
* Reading the journal
  * `journalctl --user-unit discord-twitter-webhooks`

</details>

## Privacy

If the tweet has more than 1 image this bot sends the tweet ID to [twitter.lovinator.space](https://twitter.lovinator.space/) that combines them into one image that we can use in the embed.
The only information stored is the tweet ID and combined image. No other information will be saved (e.g. IP address)
You can run [your own version](https://github.com/TheLovinator1/twitter-image-collage-maker) instead of using the default one.

## Need help?

* Email: [tlovinator@gmail.com](mailto:tlovinator@gmail.com)
* Discord: TheLovinator#9276
* Steam: [TheLovinator](https://steamcommunity.com/id/TheLovinator/)
* Send an issue: [discord-twitter-webhooks/issues](https://github.com/TheLovinator1/discord-twitter-webhooks/issues)
* GitHub Discussions: [discord-twitter-webhooks/discussions](https://github.com/TheLovinator1/discord-twitter-webhooks/discussions)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
