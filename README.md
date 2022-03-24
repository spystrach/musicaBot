# MUSICABOT

![PyPI - Python Version](https://img.shields.io/pypi/pyversions/python-telegram-bot)

![](photo_musicaBot.svg)

un bot telegram qui envoit les paroles et tablatures de nos chansons ! :musical_score: :musical_note: :notes:

## protocole d'installation

Copier le dossier sur le serveur et créer un fichier **.env** qui va contenir le token d'identitification du bot. Il faut ensuite lancer le conteneur docker :
```sh
# récupération du projet sur le serveur
gh repo clone spystrach/musicaBot && cd musicaBot
# ajoute le token
echo "token={TOKEN}" > .env
# construit l'image et lance le docker
sh restartMusicaBot.sh
```

## protocole de développement

Pour tester et améliorer le bot, il faut télécharger ce dossier en local, créer un environnement virtuel python et lancer le programme :
```sh
# récupération du projet
gh repo clone spystrach/musicaBot && cd musicaBot
# ajoute le token
echo "token={TOKEN}" > .env
# environnement virtuel de développement
python3 -m venv venv && source venv/bin/activate
# dépendances
pip3 install -r requirements_dev.txt
# lancer le programme
python3 musicaBot.py
```

## protocole de mise à jour

Le script *musicaBot_update.py* sert à mettre à jour le bot sur le serveur à partir du dossier distant. Il néccessite un **accès ssh fonctionnel** avec un empreinte ssh enregistrée et une installation locale pour le développement. Il faut ensuite ajouter le nom de l'utilisateur du serveur et le chemin vers le dossier musicaBot :
```sh
# ajoute le nom d'utilisateur et le dossier de musicaBot du serveur
echo "username={USERNAME}" >> .env
echo "folder=~/{PATH}/{TO}/{MUSICABOT}" >> .env
# met à jour le bot
python3 musicaBot_update.py
```

Il faut aussi modifier le chemin ligne 4 de *restartMusicaBot.sh*

## à faire

- [x] : token d'identitification non hardcodé
- [x] : integrer un Dockerfile au projet
- [x] : mieux gérer les mises à jours coté serveur
- [ ] : ajouter des tests
- [ ] : ajouter des musiques :notes: !
