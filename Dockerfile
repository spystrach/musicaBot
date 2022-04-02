# ne fonctionne pas avec bullseye sur raspberry pi
# FROM python:3.10-slim
FROM python:3.10-slim-buster

# non root-user
WORKDIR /home/musicabot/Documents
RUN ln -sf /bin/bash /bin/sh
RUN useradd -ms /bin/bash musicabot &&\
    chown -R musicabot /home/musicabot
USER interimbot

# modules python neccessaires
COPY requirements.txt ./
RUN pip install --no-cache-dir --disable-pip-version-check -r requirements.txt

# fichiers indispensables du bot
COPY .env ./
COPY musicaBot.py ./
COPY ./paroles/ ./paroles/
COPY ./tablatures/ ./tablatures/

# entrypoint
CMD [ "python", "./musicaBot.py" ]
