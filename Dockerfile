# We need gcc, build-essential and git to install our requirements but we 
# don't need them when run the bot so we can selectively copy artifacts
# from this stage (compile-image) to second one (runtime-image), leaving 
# behind everything we don't need in the final build. 
FROM python:3.9-slim AS compile-image

# We don't want apt-get to interact with us,
# and we want the default answers to be used for all questions.
ARG DEBIAN_FRONTEND=noninteractive

# Don't generate byte code (.pyc-files). 
# These are only needed if we run the python-files several times.
# Docker doesn't keep the data between runs so this adds nothing.
ENV PYTHONDONTWRITEBYTECODE 1

# Force the stdout and stderr streams to be unbuffered. 
# Will allow log messages to be immediately dumped instead of being buffered. 
# This is useful when the bot crashes before writing messages stuck in the buffer.
ENV PYTHONUNBUFFERED 1

# Update packages and install needed packages to build our requirements.
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential gcc git curl

# Create user so we don't run as root.
RUN useradd --create-home botuser
RUN chown -R botuser:botuser /home/botuser && chmod -R 755 /home/botuser
USER botuser

# Install poetry
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -

# Add poetry to our path
ENV PATH="/home/botuser/.poetry/bin/:${PATH}"

COPY pyproject.toml poetry.lock README.md /home/botuser/

# Change directory to where we will run the bot.
WORKDIR /home/botuser

RUN poetry install --no-interaction --no-ansi --no-dev

COPY discord_twitter_webhooks/main.py discord_twitter_webhooks/settings.py /home/botuser/discord_twitter_webhooks/

# Run bot.
CMD [ "poetry", "run", "bot" ]
