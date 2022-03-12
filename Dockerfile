FROM python:3-slim

RUN ln -sf /bin/bash /bin/sh
RUN useradd -ms /bin/bash musicabot
USER musicabot

WORKDIR /home/musicabot/Documents

COPY requirements.txt ./
COPY .env ./
COPY musicaBot.py ./
COPY ./paroles/ ./paroles/
COPY ./tablatures/ ./tablatures/

RUN pip install --no-cache-dir --disable-pip-version-check -r requirements.txt

CMD [ "python", "./musicaBot.py" ]
