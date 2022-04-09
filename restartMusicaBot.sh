#!/bin/sh
# RECHARGE LE BOT

# navigue dans le bon dossier
cd && cd "/home/$(whoami)/Documents/musicaBot" || exit

# stopppe le conteneur
docker stop musica_bot_1

# supprime le conteneur
docker rm musica_bot_1

# supprime l'image
docker image rm musica_bot

# reconstruit l'image
docker build -t musica_bot .

# lance le nouveau conteneur
docker run -d --name musica_bot_1 musica_bot

# fin
cd || exit
