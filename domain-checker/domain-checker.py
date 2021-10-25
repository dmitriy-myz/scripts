#!/usr/bin/env python
# -*- coding: utf-8 -*-

import whois
import datetime
import sys
import os

import socket
import ssl
import argparse

import send_mail as notify


def ssl_expiry_days(hostname):
    ssl_date_fmt = r'%b %d %H:%M:%S %Y %Z'

    context = ssl.create_default_context()
    conn = context.wrap_socket(
        socket.socket(socket.AF_INET),
        server_hostname=hostname,
    )
    conn.settimeout(4.0)

    conn.connect((hostname, 443))
    ssl_info = conn.getpeercert()
    not_after = datetime.datetime.strptime(ssl_info['notAfter'], ssl_date_fmt)
    return (not_after - datetime.datetime.now()).days

def domain_expiry_days(domain):
    data = whois.whois(domain)
    expiration_date = data.expiration_date
    return (expiration_date - datetime.datetime.now()).days


def parse_arg():
    parser = argparse.ArgumentParser(description='domain and ssl exipy checker.')
    parser.add_argument('domains', type=str, help='domains to process', nargs='+')
    parser.add_argument('--check', '-c', type=str, help='check ssl or domain')
    parser.add_argument('--recipient', '-r', type=str, help='recipient', nargs='+')
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    args = parse_arg()
    check = args.check
    domains = args.domains
    recipients = args.recipient
    for domain in domains:
        if check == 'domain':
            remaining_days = domain_expiry_days(domain)
            msg = "domain {} expired in {} days".format(domain, remaining_days)
        elif check == 'ssl':
            remaining_days = ssl_expiry_days(domain)
            msg = "ssl on {} expired in {} days".format(domain, remaining_days)
        if remaining_days < 14:
            print(msg)
            for recipient in recipients:
                print(recipient)
                notify.send_mail(recipient, 'domain checkert alert', msg)



