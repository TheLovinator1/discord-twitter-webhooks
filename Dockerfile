FROM python:3.10-slim AS compile-image

RUN apt-get update
RUN apt-get install -y --no-install-recommends build-essential gcc

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN python -m pip install -r requirements.txt

FROM python:3.10-slim AS build-image
COPY --from=compile-image /opt/venv /opt/venv

COPY discord_twitter_webhooks/ discord_twitter_webhooks
CMD [ "/opt/venv/bin/python", "discord_twitter_webhooks/main.py" ]
