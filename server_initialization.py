#!/usr/bin/env python3
# -*- coding: utf8 -*-

import argparse
import logging
import os
import subprocess
import sys
from colorama import Fore, Style

is_silent = False

def add_content_to_file(file, content):
    with open(file, 'a') as file:
        file.write(content + '\n')

def is_path_existing(path):
    if os.path.exists(path):
        log(f"\033[92m...ok.\033[0m")
        return True
    log(f"...File does not exist.")
    return False

def log(output):
    if is_silent:
        logging.info(output)
        return
    print(f"{output}")

def determine_hostname(hostnames_file):
    counter = 1
    os_release_command = "lsb_release -a | grep Description | sed 's/ /_/g'| awk '{print $2}'"
    os_release = subprocess.check_output(os_release_command, shell=True, universal_newlines=True).strip()
    hostname = f"{os_release}_{counter}"
    if search_term_in_file(hostnames_file, hostname):
        counter = counter + 1
        hostname = f"{os_release}_{counter}"
        search_term_in_file(hostnames_file, hostname)
    return hostname

def determine_ip(ip_adresses_file):
    ip = "192.168.178.1"
    with open(ip_adresses_file, 'a+') as file:
        if not file.read(1):
            add_content_to_file(ip_adresses_file, ip)
        lines = file.readlines()
        ip = lines[-1]
        file.close()
    if is_ping_successful(ip):
        ip = increment_ip(ip)
        add_content_to_file(ip_adresses_file, ip)
        is_ping_successful(ip)
    return ip

def get_requirements(args):
    if not args.automatic and not args.silent:
        log('Reading path to requirements from console...')
        requirements = input('Please enter the full path to a file that contains the requirements: ')
        return requirements
    requirements = get_directory_containing_file("requirements.txt")
    return requirements

def get_hostname(args):
    if not args.automatic and not args.silent:
        log('Reading hostname from console...')
        hostname = input('Please enter hostname: ')
        return hostname
    hosts_list = get_directory_containing_file("hostnames")
    hostname = determine_hostname(hosts_list)
    return hostname

def get_ip(args):
    if not args.automatic and not args.silent:
        log('Reading IP from console...')
        ip = input('Please enter IP: ')
        return ip
    ip_adresses_file = get_directory_containing_file("ip_adresses")
    ip = determine_ip(ip_adresses_file)
    return ip

def increment_ip(ip):
    ip_parts = ip.split('.')
    last_octet = int(ip_parts[-1])
    last_octet += 1
    ip_parts[-1] = str(last_octet)
    return '.'.join(ip_parts)

def install_requirements(requirements):
    log('Creating a virtual environment...')
    run_command([f"python3 -m venv venv"])
    log('Installing packages...')
    run_command([f"pip install -r {requirements}"])

def is_ping_successful(ip):
    try:
        with open(os.devnull, 'w') as null_output:
            subprocess.run(f"ping -c 1 -W 10 {ip}", shell=True, stdout=null_output, stderr=null_output, check=True)
        return True
    except subprocess.CalledProcessError:
        return False
    except Exception as e:
        return False

def configure_log():
    logfile = "server_initialization.log"
    logformat = '%(asctime)s - %(levelname)s - %(message)s'
    logging.basicConfig(filename=logfile, level=logging.INFO, format=logformat)
    sys.stdout = open(logfile, 'a')
    sys.stderr = open(logfile, 'a')
    global is_silent
    is_silent = True

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
        log(f"\033[92m...ok.\033[0m")
    except subprocess.CalledProcessError as e:
        log(f"\033[91m...not ok: {e.stderr.strip()}\033[0m")

def getting_paths(file):
    shared_dir_command = "df -h | grep Desktop | awk '{print $6}'"
    current_dir_command = "pwd"
    tmp_dir = "/tmp"
    shared_dir = subprocess.check_output(shared_dir_command, shell=True, universal_newlines=True).strip()
    current_dir = subprocess.check_output(current_dir_command, shell=True, universal_newlines=True).strip()
    directories = [shared_dir, current_dir, tmp_dir]
    paths = [str(directory) + f"/{file}" for directory in directories]
    return paths 

def get_directory_containing_file(file):
    paths = getting_paths(file)
    for path in paths:
        log(f'Searching for file {path}...')
        if is_path_existing(path):
            return path
    log(f"\033[91m...not ok: NO LIST WAS FOUND. PROCEEDING WITH LUCK.\033[0m")
    return path[1]

def search_term_in_file(file, search_term):
    try:
        with open(file, 'r') as file:
            content = file.read()
            if search_term in content:
                return True
            return False
    except Exception as e:
        print(f"Error checking for term in file: {e}")
        return False

def set_hostname(hostname):
    log(f"{Fore.LIGHTBLUE_EX}Setting hostname to {hostname}.")
    run_command([f"hostnamectl set-hostname {hostname}"])

def set_ip(ip):
    log(f"{Fore.LIGHTBLUE_EX}Setting IP to {ip}.")
    run_command([f"ip addr add {ip}/24 dev eth1"])

def main():
    args = parse_arguments()
    if args.silent:
        configure_log()  
    requirements = get_requirements(args)
    install_requirements(requirements)
    ip = get_ip(args)
    set_ip(ip)
    hostname = get_hostname(args)
    set_hostname(hostname)

if __name__=='__main__':
    main()
