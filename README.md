Discord-twitter-webhooks
=========

This program sends [tweets](https://twitter.com) to [Discord](https://discord.com/) via [webhooks](https://en.wikipedia.org/wiki/Webhook).

## Installation

* Install latest version of Python 3.
* Install pipenv
    * `pip install pipenv`
* Install requirements and make virtual enviroment
    * `pipenv install`
    * (Optional) `pipenv install --dev`
* Rename .env-example to .env and fill it with things from https://developer.twitter.com and https://tweeterid.com.
* Start the bot
    * `pipenv run python main.py`

## Autostart - Linux (systemd)
* Keep services running after logout
    * `loginctl enable-linger`
* Move service file to correct location (You may have to modify WorkingDirectory and/or ExecStart)
    * `cp discord-twitter-webhooks.service ~/.config/systemd/user/discord-twitter-webhooks.service`
* Start bot now and at boot
    * `systemctl --user enable --now discord-twitter-webhooks`


systemd examples:
* Start bot automatically at boot
    *  `systemctl --user enable discord-twitter-webhooks`
* Don't start automatically
    *  `systemctl --user disable discord-twitter-webhooks`
* Restart
    * `systemctl --user restart discord-twitter-webhooks`
* Stop
    * `systemctl --user stop discord-twitter-webhooks`
* Start
    * `systemctl --user start discord-twitter-webhooks`
* Check status
    * `systemctl --user status discord-twitter-webhooks`
* Reading the journal
    * `journalctl --user-unit discord-twitter-webhooks`

## Help
* Email: tlovinator@gmail.com
* Discord: TheLovinator#9276
* Steam: https://steamcommunity.com/id/TheLovinator/

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details
