#!/usr/bin/env python
# -*- coding: utf-8 -*-
## ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ##
##																				   ##
##  ----  ----  ----      BOT TELEGRAM TABLATURES & PAROLES      ----  ----  ----  ##
##																				   ##
## ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ##

## programme pour envoyer via Telegram des paroles et des tablatures de chansons

## ~~~~~~~~~~~~~~~~~~~~~~~~~~        PARAMETRES         ~~~~~~~~~~~~~~~~~~~~~~~~~~ ##

# modules complémentaires
import os
import sys
from re import compile as reCompile
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler

# les erreurs critiques
class Exit(Exception):
    pass

# compilation des regex pour les paroles et les tablatures
ID_PAROLES = "paroles_"
ID_TABLATURES = "tablature_"
REGEX_PAROLES = reCompile("^{}[a-zA-Z ]*$".format(ID_PAROLES))
REGEX_TABLATURES = reCompile("^{}[a-zA-Z ]*$".format(ID_TABLATURES))

# dossiers du projet
BASEPATH = os.path.realpath(os.path.dirname(sys.argv[0]))
FOLDER_PAROLES = "paroles"
FOLDER_TABLATURES = "tablatures"

# configuration du .env
REGEX_TOKEN = reCompile("token=[0-9]{8,10}:[a-zA-Z0-9_-]{35}")


## ~~~~~~~~~~~~~~~~~~~~~~~~~~    RECHERCHE DOSSIERS     ~~~~~~~~~~~~~~~~~~~~~~~~~~ ##

# navigue dans les dossiers
class obj_explorer:
    # initialisation de l'objet
    def __init__(self):
        global BASEPATH, FOLDER_PAROLES, FOLDER_TABLATURES
        self.pathParole = os.path.join(BASEPATH, FOLDER_PAROLES)
        self.pathTablature = os.path.join(BASEPATH, FOLDER_TABLATURES)

    # renvois la liste de toutes les paroles disponibles
    def get_list_paroles(self):
        list = []
        for k in os.listdir(os.path.join(self.pathParole)):
            if REGEX_PAROLES.search(k):
                list.append(k[len(ID_PAROLES):])
        return sorted(list)

    # renvois les paroles d'une chanson
    def get_paroles(self, chanson):
        with open(os.path.join(self.pathParole, "{}{}".format(ID_PAROLES, chanson)), "r") as f:
            text = f.read()
        return text

    # renvois la liste des tablatures disponibles
    def get_list_tablatures(self):
        list = []
        for k in os.listdir(self.pathTablature):
            if REGEX_TABLATURES.search(k):
                list.append(k[len(ID_TABLATURES):])
        return sorted(list)

    # renvois un le chemin complet vers la tablature
    def get_path_tablatures(self, chanson):
        return os.path.join(self.pathTablature, "{}{}".format(ID_TABLATURES, chanson))


## ~~~~~~~~~~~~~~~~~~~~~~~~~~       COMMANDES BOT       ~~~~~~~~~~~~~~~~~~~~~~~~~~ ##

# fonction lancée par la commande '/start'
def start(update, context):
    update.message.reply_text("Coucou !\nAppuis sur '/' pour voir les commandes disponibles")

# fonction lancée par la commande '/paroles'
def paroles(update, context):
    # récupération de tous les morceaux
    disponible = obj_explorer().get_list_paroles()
    # le clavier inline qu'on va remplir
    keyboard = []
    # on les groupes 2 par 2 pour le clavier inline
    for k in range(0, len(disponible)-1, 2):
        keyboard.append([ InlineKeyboardButton(disponible[k], callback_data="p_"+disponible[k]),
                          InlineKeyboardButton(disponible[k+1], callback_data="p_"+disponible[k+1]) ])
    # si on a un nombre impair de chanson, on rajoute la dernière
    if len(disponible)%2 == 1:
        keyboard.append([InlineKeyboardButton(disponible[-1], callback_data="p_"+disponible[-1])])

    # charge le clavier et l'envois
    update.message.reply_text("Paroles disponibles :", reply_markup=InlineKeyboardMarkup(keyboard))

# fonction lancée par la commande '/tablatures'
def tablatures(update, context):
        # récupération de tous les morceaux
        disponible = obj_explorer().get_list_tablatures()
        # le clavier inline qu'on va remplir
        keyboard = []
        # on les groupes 2 par 2 pour le clavier inline
        for k in range(0, len(disponible)-1, 2):
            keyboard.append([ InlineKeyboardButton(disponible[k], callback_data="t_"+disponible[k]),
                              InlineKeyboardButton(disponible[k+1], callback_data="t_"+disponible[k+1]) ])
        # si on a un nombre impair de chanson, on rajoute la dernière
        if len(disponible)%2 == 1:
            keyboard.append([InlineKeyboardButton(disponible[-1], callback_data="t_"+disponible[-1])])

        # charge le clavier et l'envois
        update.message.reply_text("Tablatures disponibles :", reply_markup=InlineKeyboardMarkup(keyboard))

# fonction lancée par un appuis le clavier inline
def button(update, context):
    query = update.callback_query
    # si la query commence par 'p', on renvois les paroles
    if query.data[:2] == "p_":
        text = obj_explorer().get_paroles(query.data[2:])
        # on renvois la réponse au client
        query.answer()
        query.edit_message_text(text=text)
    elif query.data[:2] == "t_":
        path = obj_explorer().get_path_tablatures(query.data[2:])
        # on renvois la réponse au client (obligatoire sinon bug sur certains clients)
        query.answer()
        query.edit_message_text(text="partition de {}".format(query.data[2:]))
        # envois de la partition
        context.bot.send_photo(chat_id=query.message.chat_id, photo=open(path, "rb"))

# affiche l'aide
def help(update, context):
    update.message.reply_text("""\
Commandes disponibles:
/paroles : affiche les paroles disponibles
/tablatures : affiche les tablatures disponibles
/help : affiche l'aide""")

# affiche les erreurs rencontrés par le programme
def error(update, context):
    print("Update '{}' \ncaused error '{}'".format(update, context.error))


## ~~~~~~~~~~~~~~~~~~~~~~~~~~    FONCTION PRINCIPALE    ~~~~~~~~~~~~~~~~~~~~~~~~~~ ##

# la fonction principale du bot
def main():
    # récupere le token d'identitification dans le .env
    if os.path.isfile(os.path.join(BASEPATH, ".env")):
        with open(os.path.join(BASEPATH, ".env"), "r") as f:
            try:
                # création du bot avec son token d'authentification (retire le 'token=' du début)
                bot = Updater(REGEX_TOKEN.findall(f.read())[0][6:], use_context=True)
            except Exception as e:
                raise e
    else:
        raise Exit("[!] le fichier .env contenant le token d'identitification n'existe pas")
    # ajout des gestionnaires de commande par ordre d'importance
    # la commande /start
    bot.dispatcher.add_handler(CommandHandler("start", start))
    # la commande /paroles
    bot.dispatcher.add_handler(CommandHandler("paroles", paroles))
    # la commande /tablatures
    bot.dispatcher.add_handler(CommandHandler("tablatures", tablatures))
    # le clavier inline
    bot.dispatcher.add_handler(CallbackQueryHandler(button))
    # la commande /help
    bot.dispatcher.add_handler(CommandHandler("help", help))
    # gestion des erreurs
    bot.dispatcher.add_error_handler(error)

    # lance le bot
    bot.start_polling()
    # continue le programme jusqu'à la réception d'un signal de fin (par ex: CTRL-C)
    bot.idle()

# lance la fonction principale
if __name__ == "__main__":
    main()


# fin
