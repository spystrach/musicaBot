#!/usr/bin/env python
# -*- coding: utf-8 -*-
## ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ##
##																				   ##
##  ----  ----  ----    MAJ VIA SSH DU BOT TELEGRAM MUSICABOT    ----  ----  ----  ##
##																				   ##
## ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ##

## programme pour mettre à jour via SSH le bot. Relance le conteneur si le programme est
## en retard par rapport au dossier distant https://github.com/spystrach/musicaBot

## ~~~~~~~~~~~~~~~~~~~~~~~~~~        PARAMETRES         ~~~~~~~~~~~~~~~~~~~~~~~~~~ ##

# modules complémentaires
import os
import sys
from paramiko import SSHClient, RejectPolicy
from getpass import getpass
from re import compile as reCompile

# le nom d'utilisateur du serveur et le chemin de musicaBot sont spécifié dans le .env
BASEPATH = os.path.realpath(os.path.dirname(sys.argv[0]))
REGEX_USERNAME = reCompile("username=[a-zA-Z0-9]{2,30}")
REGEX_BASEPATH = reCompile("folder=~[a-zA-Z0-9/]+")


## ~~~~~~~~~~~~~~~~~~~~~~~~~~         FONCTIONS         ~~~~~~~~~~~~~~~~~~~~~~~~~~ ##

# affiche les sorties d'un programme, stoppe s'il y a une erreur
def verify_no_errs(out, err):
    if err != b"":
        print(f"[!] {err.decode('UTF-8')}")
        sys.exit()
    if out != b"":
        print(f"{out.decode('UTF-8')}")

# renvois le dictionnaire DNS de l'ordinateur
def get_etc_hostnames():
    # ouvre le fichier des hôtes enregistrés
    with open('/etc/hosts', 'r') as f:
        hostlines = f.readlines()
    # on ne garde que les lignes interessantes
    hostlines = [line.strip() for line in hostlines if not line.startswith('#') and line.strip() != '']
    dictHosts = {}
    for line in hostlines:
        # l'adresse ip
        hostAddress = line.split('#')[0].split()[0]
        # pour chaque nom on crée une clef renvoyant à l'adresse ip
        for names in line.split('#')[0].split()[1:]:
            dictHosts[names] = hostAddress

    return dictHosts

# demande l'adresse ip du serveur
def ask_ip_adress(dns_dict):
    ipAddress = None
    # demande si on veut passer par le réseau local ou par internet
    while True:
        local = input("passer par internet (O/N) ? : ")
        if local.lower() == "o":
            ipAddress = dns_dict["maison"]
            break
        elif local.lower() == "n":
            ipAddress = dns_dict["raspberry4"]
            break
    # vérifie que l'adresse ip est bien trouvée
    if ipAddress:
        return ipAddress
    else:
        print("[!] adresse ip non trouvée dans le DNS")
        sys.exit()


## ~~~~~~~~~~~~~~~~~~~~~~~~~~    FONCTION PRINCIPALE    ~~~~~~~~~~~~~~~~~~~~~~~~~~ ##

# fonction principale
if __name__ == "__main__":
    # récupère les constantes du .env
    with open(os.path.join(BASEPATH, ".env"), "r") as f:
        txt = f.read()
    username_server = REGEX_USERNAME.findall(txt)[0][9:]
    basepath_server = f"/home/{username_server}/{REGEX_BASEPATH.findall(txt)[0][9:]}"
    del txt
    print(f"dossier du serveur : {basepath_server}")

    # récupère les DNS et l'adresse ip
    dns = get_etc_hostnames()
    ip_address = ask_ip_adress(dns)
    print(f"adresse ip : {ip_address}")

    # initialisation du client SSH
    ssh_client = SSHClient()
    # ajout des signatures des serveur ssh connues, rejete si la signature est inconnue
    ssh_client.load_host_keys(os.path.expanduser("~/.ssh/known_hosts"))
    ssh_client.set_missing_host_key_policy(RejectPolicy())

    # demande du mot de passe du raspberry
    while True:
        temp_pass = getpass("mot de passe raspberry :")
        # test du mot de passe
        try:
            ssh_client.connect(
                hostname=ip_address,
                username=username_server,
                password=temp_pass,
            )
            break
        except Exception as e:
            print(f"[!] {e}")


    with ssh_client:
        # met à jour le git local par rapport au dossier distant
        _, a, b = ssh_client.exec_command(f"git -C {basepath_server} remote update")
        # regarde si le dossier local est en retard
        _, stdout, stderr = ssh_client.exec_command(f"git -C {basepath_server} status -uno")
        out, err = stdout.read(), stderr.read()
        verify_no_errs(out, err)

        # si le git est en retard, on le met à jour
        output = out.decode("UTF-8")
        if "retard" in output or "behind" in output or "git pull" in output:
            _, stdout, stderr = ssh_client.exec_command(f"git -C {basepath_server} pull")
            out, err = stdout.read(), stderr.read()
            verify_no_errs(out, err)
            # reconstuit le docker
            _, stdout, stderr = ssh_client.exec_command(f"sh {os.path.join(basepath_server, 'restartMusicaBot.sh')}")
            out, err = stdout.read(), stderr.read()
            verify_no_errs(out, err)
        else:
            print("[!] le dossier est déja à jour")

# fin
