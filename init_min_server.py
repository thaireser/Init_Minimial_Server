#!/usr/bin/env python3
# -*- coding: utf8 -*-

#BIBLIOTHEKENIMPORT
import argparse
import ipaddress
import logging
import subprocess
import sys
from colorama import Fore, Style

#VARIABLEN
start_ip = f"192.168.56.101"
silence_mode = False
output = "undef"

#PARAMETER
def main():
    parser = argparse.ArgumentParser(description='Dieses Skript initialisiert minimale Server. Bitte vor Verwendung Dokumentation lesen.')
    #Definition der Befehlszeilenoptionen
    parser.add_argument('-s', '--silent', action='store_true', help="Führt das Skript im stillen Modus aus. Log wird in das aktuelle Verzeichnis geschrieben.")
    parser.add_argument('-a', '--automatic', action='store_true', help='Sucht automatisch nach einer passenden IP und einem Hostnamen.')
    #Parsen der Befehlszeilenargumente
    args = parser.parse_args()

    if args.silent:
        # Konfiguration des Logging-Moduls
        log_format = '%(asctime)s - %(levelname)s - %(message)s'
        logging.basicConfig(filename='logfile.log', level=logging.INFO, format=log_format)
        # Umleitung von stdout und stderr
        #sys.stdout = open('logfile.log', 'a')
        #sys.stderr = open('logfile.log', 'a')
        global silence_mode
        silence_mode = True

    if args.automatic:
        search_ip_list()
        search_hostname_list()
    else:
        read_ip()
        read_hostname()

    set_ip()
    set_hostname()
    get_packages()

def read_ip():
    create_output('Reading IP from console...')

def read_hostname():
    create_output('Reading hostname from console...')

def search_ip_list():
    create_output('Searching for a list of ip_adresses in current directory...')
    create_output('Searching for a list of ip_adresses in /tmp ...')

def search_hostname_list():
    create_output('Searching for a list of hostnames in current directory...')
    create_output('Searching for a list of hostnames in /tmp ...')

def set_hostname():
    create_output('Setting hostname.')

def set_ip():
    create_output('Setting ip.')

def get_packages():
    create_output('Searching for a list of requirements in current directory...')
    create_output('Searching for a list of requirements in /tmp ...')
    create_output('Packages will be installed.')

def create_output(output):
    if silence_mode:
        logging.info(output)
    else:
        print(output)
        print("\033[92m" + "...ok" + "\033[0m")
        print("\033[91m" + "...not ok" + "\033[0m")

main()
