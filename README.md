Discord-twitter-webhooks
=========

A bot for Discord that send tweets via webhooks

### Installation

You need Python 3 to run this bot. 

Ubuntu - Download and run
----
```sh
# Clone the repository
git clone https://github.com/TheLovinator1/discord-twitter-webhooks.git

# Change directory to the repository
cd discord-twitter-webhooks/

# Download the requirements
pip3 install -r requirements.txt

# Edit and fill out the information in the config file
nano config.ini

# It should look like this
[discord]
webhook_url = https://discordapp.com/api/webhooks/87629431744371866618/XWx4oZctMiliGhqA6xKSXWx4oZctMiliGhqA6xKSXWx4oZctMiliGhqA6xKS-ukRePERn-kekrWb0fYMbgQBEg9Tgn
webhook_error_url = https://discordapp.com/api/webhooks/87629431744371866618/XWx4oZctMiliGhqA6xKSXWx4oZctMiliGhqA6xKSXWx4oZctMiliGhqA6xKS-ukRePERn-kekrWb0fYMbgQBEg9Tgn

[twitter]
consumer_key = uXCoFuGelkHWWVkgtYDg
consumer_secret = akSWodGsnGSLnyioyeSyakSWodGsnGSLnyioyeSy
access_token = 7590329167-MYlEJVmbWMBGsEKgshRWMYlEJVmbWMBGsEKgshRW
access_token_secret = APspzJmSoDfWAqtHTPeNAPspzJmSoDfWAqtHTPeN
users_to_follow = 1114707756, 36803580

# Run the bot (Shut down the bot with ctrl + c)
python3 main.py
```
### Ubuntu - Autostart the bot with systemd (optional) 
```
# Make systemd service (Remember to change user)
sudo editor /etc/systemd/system/discord-twitter-webhooks.service

    [Unit]
    Description=discord-twitter-webhooks
    After=multi-user.target
    
    [Service]
    User=discord
    
    Type=simple
    ExecStart=/usr/bin/python3 /home/discord/discord-twitter-webhooks/main.py
    #KillMode=process
    Restart=always
    RestartSec=3
    WorkingDirectory=/home/discord/discord-twitter-webhooks
    
    [Install]
    WantedBy=multi-user.target

# Start the service
sudo systemctl start discord-twitter-webhooks.service

# Start with computer
sudo systemctl enable discord-twitter-webhooks.service

# Check if the bot is running
sudo service discord-twitter-webhooks status
```

License
----

[MIT](LICENSE)
