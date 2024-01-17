#!/usr/bin/env python3
# -*- coding: utf8 -*-

import argparse
import logging
import os
import re
import socket
import struct
import subprocess
import sys
from colorama import Fore, Style

silence_mode = False

def append_list(list_path, extension):
    with open(list_path, 'a') as file:
        file.write(extension + '\n')

def check_path_existence(itemlist_path):
    if os.path.exists(itemlist_path):
        create_output(f"\033[92m...ok.\033[0m")
        return 0
    create_output(f"...File does not exist.")
    return 1

def create_output(output):
    if silence_mode:
        logging.info(output)
        return
    print(f"{output}")

def determine_hostname(hosts_list):
    counter = 1
    os_release_command = "lsb_release -a | grep Description | sed 's/ /_/g'| awk '{print $2}'"
    os_release = subprocess.check_output(os_release_command, shell=True, universal_newlines=True).strip()
    proposed_hostname = f"{os_release}_{counter}"
    if search_term_in_file(hosts_list, proposed_hostname) == True:
        counter = counter + 1
        proposed_hostname = f"{os_release}_{counter}"
        search_term_in_file(hosts_list, proposed_hostname)
    return proposed_hostname

def determine_ip(ip_list):
    proposed_ip = "192.168.178.1"
    with open(ip_list, 'a+') as file:
        if not file.read(1):
            append_list(ip_list, proposed_ip)
        ip_list_lines = file.readlines()
        proposed_ip = ip_list_lines[-1]
        file.close()
    if is_ping_successful(proposed_ip) == True:
        proposed_ip = increment_ip(proposed_ip)
        append_list(ip_list, proposed_ip)
        is_ping_successful(proposed_ip)
    return proposed_ip

def get_requirements(args):
    if args.automatic == False and args.silent == False:
        create_output('Reading path to requirements from console...')
        requirements = input('Please enter the full path to a file that contains the requirements: ')
        return requirements
    requirements = search_lists("requirements", "requirements.txt")
    return requirements

def get_hostname(args):
    if args.automatic == False and args.silent == False:
        create_output('Reading hostname from console...')
        proposed_hostname = input('Please enter IP: ')
        return proposed_hostname
    hosts_list = search_lists(f"hostnames", "hostnames")
    proposed_hostname = determine_hostname(hosts_list)
    return proposed_hostname

def get_ip(args):
    if args.automatic == False and args.silent == False:
        create_output('Reading IP from console...')
        proposed_ip = input('Please enter IP: ')
        return proposed_ip
    ip_list = search_lists(f"ip_adresses", "ip_adresses")
    proposed_ip = determine_ip(ip_list)
    return proposed_ip

def increment_ip(ip):
    ip_parts = ip.split('.')
    last_octet = int(ip_parts[-1])
    last_octet += 1
    ip_parts[-1] = str(last_octet)
    return '.'.join(ip_parts)

def install_requirements(requirements):
    create_output('Creating a virtual environment...')
    run_command([f"python3 -m venv venv"])
    create_output('Installing packages...')
    run_command([f"pip install -r {requirements}"])

def is_ping_successful(proposed_ip):
    try:
        with open(os.devnull, 'w') as null_output:
            subprocess.run(f"ping -c 1 -W 10 {proposed_ip}", shell=True, stdout=null_output, stderr=null_output, check=True)
        return True
    except subprocess.CalledProcessError:
        return False
    except Exception as e:
        return False

def logger():
    logfile = "server_initialization.log"
    logformat = '%(asctime)s - %(levelname)s - %(message)s'
    logging.basicConfig(filename=logfile, level=logging.INFO, format=logformat)
    sys.stdout = open(logfile, 'a')
    sys.stderr = open(logfile, 'a')
    global silence_mode
    silence_mode = True

def parse_arguments():
    parser = argparse.ArgumentParser(description='This script initializes minimal servers for a very specific context. Please read the documentation before use.')
    # Command-line options
    parser.add_argument('-s', '--silent', action='store_true', help='Silent mode. Uses automatic IP and hostname configuration. Logs will be written to the current directory.')
    parser.add_argument('-a', '--automatic', action='store_true', help='Automatic IP and hostname configuration.')
    return parser.parse_args()

def run_command(command):
    try:
        result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                  universal_newlines=True)
        create_output(f"\033[92m...ok.\033[0m")
    except subprocess.CalledProcessError as e:
        create_output(f"\033[91m...not ok: {e.stderr.strip()}\033[0m")

def search_lists(item, itemlist):
    sharedfolder_command = "df -h | grep Desktop | awk '{print $6}'"
    sharedfolder = subprocess.check_output(sharedfolder_command, shell=True, universal_newlines=True).strip()
    sharedfolder_path = f"{sharedfolder}/{itemlist}"
    currentdir_path = f"{itemlist}"
    tmpdir_path = f"/tmp/{itemlist}"
    paths_to_check = [sharedfolder_path, currentdir_path, tmpdir_path]
    for path in paths_to_check:
        create_output(f'Searching for file {path}...')
        return_code = check_path_existence(path)
        if return_code == 0:
            return path
    create_output(f"\033[91m...not ok: NO LIST WAS FOUND. PROCEEDING WITH LUCK.\033[0m")

def search_term_in_file(file_path, search_term):
    try:
        with open(file_path, 'r') as file:
            content = file.read()
            if search_term in content:
                return True
            return False
    except Exception as e:
        print(f"Error checking for term in file: {e}")
        return False

def set_hostname(proposed_hostname):
    create_output(f"{Fore.LIGHTBLUE_EX}Setting hostname to {proposed_hostname}.")
    run_command([f"hostnamectl set-hostname {proposed_hostname}"])

def set_ip(proposed_ip):
    create_output(f"{Fore.LIGHTBLUE_EX}Setting IP to {proposed_ip}.")
    run_command([f"ip addr add {proposed_ip}/24 dev eth1"])

def main():
    args = parse_arguments()
    if args.silent:
        logger()  
    requirements = get_requirements(args)
    install_requirements(requirements)
    proposed_ip = get_ip(args)
    set_ip(proposed_ip)
    proposed_hostname = get_hostname(args)
    set_hostname(proposed_hostname)

if __name__=='__main__':
    main()