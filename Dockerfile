
FROM python:3.11-slim

# Create a non-root user
RUN useradd --create-home botuser

# Switch to the non-root user
USER botuser

# Add /home/botuser/.local/bin to the PATH
ENV PATH=/home/botuser/.local/bin:$PATH

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the Python requirements
RUN pip install --no-cache-dir --disable-pip-version-check -r requirements.txt

# Copy source code
COPY discord_twitter_webhooks /app/discord_twitter_webhooks/

# Create the directory for the database
RUN mkdir -p /home/botuser/.local/share/discord_twitter_webhooks

# Create a volume for the database
VOLUME /home/botuser/.local/share/discord_twitter_webhooks

# Expose the port that Uvicorn will listen on
EXPOSE 8000

# Start Uvicorn
CMD [ "uvicorn", "discord_twitter_webhooks.main:app", "--host", "0.0.0.0", "--port", "8000" ]
