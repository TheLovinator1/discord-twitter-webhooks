# Changelog

All notable changes to discord-twitter-webhooks will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2022-05-23

## Changed

- You need to use BEARER_TOKEN to authenticate instead of CONSUMER_KEY,
  CONSUMER_SECRET, ACCESS_TOKEN and ACCESS_TOKEN_SECRET
- You have to use RULE instead of USERS_TO_FOLLOW,
  USER_LIST_REPLIES_TO_OTHERS_TWEET, USER_LIST_REPLIES_TO_OUR_TWEET,
  USER_LIST_WE_RETWEET_SOMEONE_ELSES_TWEET, USER_LIST_SOMEONE_RETWEETS_OUR_TWEET

## [0.3.0] - 2022-02-19

### Added

- There is now a CHANGELOG.md file

## [0.2.0] - 2022-02-19

### Added

- Docker Hub image is now built automatically with GitHub Actions
- Add CONTRIBUTING.md
- ?utm_source is not removed from the tweet
- Added more tests and docstrings. Still not enough
- It now gets a image from the URL in the tweet if the tweet has none. It checks for the twitter:image tag and og:image tag.

### Changed

- The twitter_image_collage_maker is now called collage_maker_url
- Now exits when USERS_TO_FOLLOW is empty
- No longer warns when no .env file is found
- Comments are now rewritten to be more helpful
- Reduced the amount of files
- Imports are now relative
- License is now GPLv3
- Line length is now 80 characters instead of 119
- Rename OAuthHandler to OAuth1UserHandler
- Functions are now in its own files
- Updated comments in .env.example
- Test is now using environment variable instead of hardcoded webhook.

### Fixed

- Dockerfile should now be working again
- Username and hashtags replacement is disabled when inside word or url

### Removed

- DEBUG logging for the tests
- Clear-text logging of sensitive information is not removed
- Remove Docker builds badge from README.md
- Remove build: . from docker-compose.yml
- Version in docker-compose.yml is now removed, as it is not needed anymore.

## [0.1.0] - 2021-07-23

### Added

- Use Poetry to manage dependencies.
