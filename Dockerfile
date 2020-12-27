FROM archlinux

# Update Arch and install gcc, python and pip and remove cache
RUN pacman -Syu --noconfirm && pacman --noconfirm -S gcc python python-pip git && yes | pacman -Scc

# Copy requirements for the bot and install them
COPY requirements.txt /tmp/
RUN pip install --disable-pip-version-check --no-cache-dir --yes --requirement  /tmp/requirements.txt

# Create user
RUN useradd --create-home botuser
WORKDIR /home/botuser
USER botuser

# Copy bot and run
COPY main.py .
CMD ["python", "./main.py"]
