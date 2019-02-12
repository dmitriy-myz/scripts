#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pythonwhois
import datetime
import sys
import os

import socket
import ssl

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
    data, server_list = pythonwhois.net.get_whois_raw(domain, with_server_list=True)
    parsed = pythonwhois.parse.parse_raw_whois(data, normalized=True, never_query_handles=False, handle_server=server_list[-1])
    expiration_date = parsed['expiration_date'][0]
    return (expiration_date - datetime.datetime.now()).days

if __name__ == '__main__':
    if len(sys.argv) == 1:
        print("Usage: {} <discovery|status|nodeStatus> [serviceID]".format(sys.argv[0]))
        sys.exit(1)
    action = sys.argv[1].lower()
    domain = sys.argv[2]
    if action == 'domain':
        remaining_days = domain_expiry_days(domain)
        msg = "domain {} expired in {} days".format(domain, remaining_days)
    elif action == 'ssl':
        remaining_days = ssl_expiry_days(domain)
        msg = "ssl on {} expired in {} days".format(domain, remaining_days)
    if remaining_days < 14 or True:
        print(msg)
        recipient = 'a5b1ca@gmail.com'
        notify.send_mail(recipient, 'domain checkert alert', msg)



