FROM archlinux
RUN pacman -Syu --noconfirm && pacman -S gcc python python-pip git --noconfirm
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
CMD python ./main.py
