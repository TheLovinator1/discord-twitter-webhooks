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

## Rules

More information about the rules can be found [here](https://developer.twitter.com/en/docs/twitter-api/tweets/filtered-stream/integrate/build-a-rule).

### Boolean operators and grouping

If you want to string together multiple operators, you can use the
following:

| Operator           | Description                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| ------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| AND logic          | Successive operators **with a space between them** will result in boolean "AND" logic, meaning that Tweets will match only if both conditions are met. For example, `RULE="snow day #NoSchool"` will match Tweets containing the terms snow and day and the hashtag #NoSchool.                                                                                                                                                                 |
| OR logic           | Successive operators with OR between them will result in OR logic, meaning that Tweets will match if either condition is met. For example, specifying `RULE="grumpy OR cat OR #meme"` will match any Tweets containing at least the terms grumpy or cat, or the hashtag #meme.                                                                                                                                                                 |
| NOT logic/negation | Prepend a dash (-) to a keyword (or any operator) to negate it. For example, `RULE="cat #meme -grumpy"` will match Tweets containing the hashtag #meme and the term cat, but only if they do not contain the term grumpy. One common rule clause is -is:retweet, which will not match on Retweets, thus matching only on original Tweets, Quote Tweets, and replies. All operators can be negated, but negated operators cannot be used alone. |
| Grouping           | You can use parentheses to group operators together. For example, `RULE="(grumpy cat) OR (#meme has:images)"` will return either Tweets containing the terms grumpy and cat, or Tweets with images containing the hashtag #meme. Note that ANDs are applied first, then ORs are applied.                                                                                                                                                       |

Note: Do not negate a set of operators grouped together in a set of
parentheses. Instead, negate each individual operator.
For example, instead of using `RULE="skiing -(snow OR day OR #NoSchool)"`, we suggest that you use `RULE="skiing -snow -day -#NoSchool"`.

### Get everything from a user

If you want to get tweets, replies, retweets and quotes from @Steam, @Xbox and @PlayStation.

- You can use the following rule:
  - `RULE="from:Steam OR from:Xbox OR from:PlayStation"`
  - See [#remove-retweets-replies-and-quotes](#remove-retweets-replies-and-quotes) if you only want tweets.

### Remove/Only retweets

- Remove retweets by adding -is:retweet to the rule:
  - `RULE="(from:Steam OR from:Xbox OR from:PlayStation) -is:retweet"`
    - Change -is:retweet to is:retweet to only get retweets.
    - Note that we added parentheses to group the operators together otherwise the -is:retweet would only be for Playstation.
- If you want to get retweets (and tweets, replies, quotes) from Steam but not Xbox or PlayStation, you can use the following rule:
  - `RULE="(from:Steam) OR (-is:retweet (from:Xbox OR from:PlayStation))"`

### Remove/Only replies

- Remove replies by adding -is:reply to the rule.
  - `RULE="(from:Steam OR from:Xbox OR from:PlayStation) -is:reply"`
    - Change -is:reply to is:reply to only get replies.
    - Note that we added parentheses to group the operators together otherwise the -is:reply would only be for Playstation.
- If you want to get replies (and tweets, retweets, quotes) from Steam but not Xbox or PlayStation, you can use the following rule:
  - `RULE="(from:Steam) OR (-is:reply (from:Xbox OR from:PlayStation))"`

### Remove/Only quote tweets

- Remove quote tweets by adding -is:quote to the rule:
  - `RULE="(from:Steam OR from:Xbox OR from:PlayStation) -is:quote"`
    - Change -is:quote to is:quote to only get quotes
    - Note that we added parentheses to group the operators together otherwise the -is:quote would only be for Playstation.
- If you want to get quote tweets (and tweets, retweets, replies) from Steam but not Xbox or PlayStation, you can use the following rule:
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
    - If we used double quotes in the rule we have to use single quotes around the rule.
- If we only want to get tweets from @Xbox that are about Halo you can use the following rule:
  - `RULE="Halo from:Xbox"`

## Operators

If you have Academic Research access you can use more advanced operators. Those can be found [here](https://developer.twitter.com/en/docs/twitter-api/tweets/filtered-stream/integrate/build-a-rule#list).

### Operators - Standalone

| Operator             | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     | Example                                                      |
| -------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------ |
| keyword              | Matches a keyword within the body of a Tweet. This is a tokenized match, meaning that your keyword string will be matched against the tokenized text of the Tweet body. Tokenization splits words based on punctuation, symbols, and Unicode basic plane separator characters. For example, a Tweet with the text “I like coca-cola” would be split into the following tokens: I, like, coca, cola. These tokens would then be compared to the keyword string used in your rule. To match strings containing punctuation (for example coca-cola), symbol, or separator characters, you must wrap your keyword in double-quotes. | `RULE='pepsi OR cola OR "coca cola"'`                        |
| emoji                | Matches an emoji within the body of a Tweet. Similar to a keyword, emojis are a tokenized match, meaning that your emoji will be matched against the tokenized text of the Tweet body. Note that if an emoji has a variant, you must wrap it in double quotes to add to a rule.                                                                                                                                                                                                                                                                                                                                                 | `RULE="(😃 OR 😡) 😬"`                                       |
| "exact phrase match" | Matches the exact phrase within the body of a Tweet.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | `RULE='("Twitter API" OR #v2) -"filtered stream"'`           |
| #                    | Matches any Tweet containing a recognized hashtag, if the hashtag is a recognized entity in a Tweet. This operator performs an exact match, NOT a tokenized match, meaning the rule #thanku will match posts with the exact hashtag #thanku, but not those with the hashtag #thankunext.                                                                                                                                                                                                                                                                                                                                        | `RULE="#thankunext #fanart OR @arianagrande"`                |
| @                    | Matches any Tweet that mentions the given username, if the username is a recognized entity (including the @ character).                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         | `RULE="(@twitterdev OR @twitterapi) -@twitter"`              |
| from:                | Matches any Tweet from a specific user. The value can be either the username (excluding the @ character) or the user’s numeric user ID.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         | `RULE="from:twitterdev OR from:twitterapi -from:twitter"`    |
| to:                  | Matches any Tweet that is in reply to a particular user. The value can be either the username (excluding the @ character) or the user’s numeric user ID.                                                                                                                                                                                                                                                                                                                                                                                                                                                                        | `RULE="to:twitterdev OR to:twitterapi -to:twitter"`          |
| url:                 | Performs a tokenized match on any validly-formatted URL of a Tweet. Works with both short URLs (https://t.co/c0A36SWil4) and real URLs (https://developer.twitter.com/en/docs/labs). URL needs to be quoted.                                                                                                                                                                                                                                                                                                                                                                                                                    | `RULE='from:TwitterDev url:"https://developer.twitter.com"'` |
| retweets_of:         | Matches Tweets that are Retweets of the specified user. The value can be either the username (excluding the @ character) or the user’s numeric user ID.                                                                                                                                                                                                                                                                                                                                                                                                                                                                         | `RULE="retweets_of:twitterdev OR retweets_of:twitterapi"`    |

### Operators - Conjunction required

| Operator     | Description                                                                                                                                                                                                                                                                                          | Example                                         |
| ------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------- |
| is:retweet   | Matches on Retweets that match the rest of the specified rule. This operator looks only for true Retweets (for example, those generated using the Retweet button). Quote Tweets will not be matched by this operator.                                                                                | `RULE="data @twitterdev is:retweet"`            |
| is:quote     | Returns all Quote Tweets, also known as Tweets with comments.                                                                                                                                                                                                                                        | `RULE='"sentiment analysis" is:quote'`          |
| is:verified  | Deliver only Tweets whose authors are verified by Twitter.                                                                                                                                                                                                                                           | `RULE="#nowplaying is:verified"`                |
| has:hashtags | Matches Tweets that contain at least one hashtag.                                                                                                                                                                                                                                                    | `RULE="from:twitterdev has:hashtags"`           |
| has:links    | This operator matches Tweets which contain links and media in the Tweet body.                                                                                                                                                                                                                        | `RULE="from:twitterdev announcement has:links"` |
| has:mentions | Matches Tweets that mention another Twitter user.                                                                                                                                                                                                                                                    | `RULE="#nowplaying has:mentions"`               |
| has:media    | Matches Tweets that contain a media object, such as a photo, GIF, or video, as determined by Twitter. This will not match on media created with Periscope, or Tweets with links to other media hosting sites.                                                                                        | `RULE="(kittens OR puppies) has:media"`         |
| has:images   | Matches Tweets that contain a recognized URL to an image.                                                                                                                                                                                                                                            | `RULE="#meme has:images"`                       |
| has:videos   | Matches Tweets that contain native Twitter videos, uploaded directly to Twitter. This will not match on videos created with Periscope, or Tweets with links to other video hosting sites.                                                                                                            | `RULE="#icebucketchallenge has:videos"`         |
| sample:      | Returns a random percent sample of Tweets that match a rule rather than the entire set of Tweets. The percent value must be represented by an integer between 1 and 100 (for example, sample:10 will return a random 10% sample).                                                                    | `RULE="#nowplaying @spotify sample:15"`         |
| lang:        | Matches Tweets that have been classified by Twitter as being of a particular language (if, and only if, the tweet has been classified). It is important to note that each Tweet is currently only classified as being of one language, so AND’ing together multiple languages will yield no results. | `RULE="recommend #paris lang:en"`               |

## Need help?

- Email: [tlovinator@gmail.com](mailto:tlovinator@gmail.com)
- Discord: TheLovinator#9276
- Steam: [TheLovinator](https://steamcommunity.com/id/TheLovinator/)
- Send an issue: [discord-twitter-webhooks/issues](https://github.com/TheLovinator1/discord-twitter-webhooks/issues)
- GitHub Discussions: [discord-twitter-webhooks/discussions](https://github.com/TheLovinator1/discord-twitter-webhooks/discussions)
