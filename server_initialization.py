#!/usr/bin/env python3
# -*- coding: utf8 -*-

import argparse
import distro
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
    return os.path.exists(path)

def log(output, color=None):
    if is_silent:
        logging.info(output)
        return
    if color is not None:
        color_code = getattr(Fore, color.upper(), Fore.RESET)
        print(f"{color_code}{output}{Style.RESET_ALL}")
        return
    print(f"{output}")

def determine_hostname(hostnames_file):
    counter = 1
    hostname = (f"{distro.linux_distribution()[0]}-{distro.linux_distribution()[1]}-{counter}").replace(" ", "-")
    while search_term_in_file(hostnames_file, hostname):
        counter += 1
        hostname = (f"{distro.linux_distribution()[0]}-{distro.linux_distribution()[1]}-{counter}").replace(" ", "-")
        #search_term_in_file(hostnames_file, hostname)
    add_content_to_file(hostnames_file, hostname)
    return hostname

def determine_ip(ip_adresses_file):
    with open(ip_adresses_file, 'r') as file:
        #STANDARD_START_IP
        ip = "192.168.178.1"
        lines = file.readlines()
        if not lines:
            add_content_to_file(ip_adresses_file, ip)
            lines = file.readlines()
        ip = lines[-1].strip()
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
    parser.add_argument('-s', '--silent', action='store_true', help='Silent mode. Uses automatic IP and hostname configuration. Logs will be written to the current directory.')
    parser.add_argument('-a', '--automatic', action='store_true', help='Automatic IP and hostname configuration.')
    return parser.parse_args()

def run_command(command):
    try:
        result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                  universal_newlines=True)
        log(f"...ok.", "GREEN")
    except subprocess.CalledProcessError as e:
        log(f"...not ok: {e.stderr.strip()}", "RED")

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
    log(f'Searching for file {file}...')
    for path in paths:
        if is_path_existing(path):
            log(f"...ok: {path} found.", "GREEN")
            return path
        log(f"...not found: {path}")
    log(f"...not ok: NO LIST WAS FOUND. PROCEEDING WITH LUCK." , "RED")
    log(f"Creating file {paths[1]}..." , "YELLOW")
    run_command(f"touch {paths[1]}")
    return paths[1]

def search_term_in_file(file, search_term):
    with open(file, 'r') as file:
        content = file.read()
        if search_term in content:
            return True
        return False

def set_hostname(hostname):
    log(f"SETTING HOSTNAME TO {hostname}..." , "YELLOW")
    run_command([f"hostnamectl set-hostname {hostname}"])

def set_ip(ip):
    log(f"SETTING IP TO {ip}... " , "YELLOW")
    log(f'Trying to run:ip addr add {ip}/24 dev eth1')
    run_command([f'ip addr add {ip}/24 dev eth1'])

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
