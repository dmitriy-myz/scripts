import nmap
import json
from subprocess import call
import sys
import argparse


def alert(msg):
    call(['bash', 'send_msg.sh', msg])


def get_args():
    parser = argparse.ArgumentParser(description="nmap scanner script")
    parser.add_argument('--scan_type', dest='scan_type', required=True, help='Scan type: short|full|discovery')
    return parser.parse_args()


def main():
    args = get_args()

    with open('config.json', 'r') as f:
        config = json.load(f)

    with open('hosts.json', 'r') as f:
        up_hosts = json.load(f)
        up_hosts = sorted(up_hosts)

    hosts_list = ' '.join(config['hosts'])
    up_hosts_list = ' '.join(up_hosts)

    allowed_ports = config['allowed_ports']
    allowed_host_n_ports = config['allowed_host_n_ports']
    ports_quick_list = config['port_quick_list']
    ports_quick_list = [str(x) for x in ports_quick_list]
    ignore_hosts = ','.join(config['ignore_hosts'])

    if args.scan_type == "discovery":
        nm_args = '-n -sn -PE -PA22,80,443,30022,1194,1195,1701,5969 --exclude %s' % ignore_hosts
        msg = discover_hosts(hosts_list, nm_args)
    elif args.scan_type == "discovery_by_port":
        ports = "443"
        nm_args = '-Pn --exclude %s' % ignore_hosts
        msg = discover_port(hosts_list, ports, nm_args)
    elif args.scan_type == "short":
        nm_args = '-Pn -sT --exclude %s' % ignore_hosts
        ports = ','.join(ports_quick_list)
        msg = scan_hosts(up_hosts_list, ports, nm_args, allowed_ports, allowed_host_n_ports)
    elif args.scan_type == "full":
        nm_args = '-Pn -sT --exclude %s' % ignore_hosts
        ports = '1-65535'
        msg = scan_hosts(up_hosts_list, ports, nm_args, allowed_ports, allowed_host_n_ports)
    if(msg):
        print(msg)
        alert(msg)

def scan_hosts(hosts_list, ports, nm_args, allowed_ports, allowed_host_n_ports):
    nm = nmap.PortScanner()
    nm.scan(hosts_list, ports, arguments=nm_args)

    alert_msg = ''
    for host in nm.all_hosts():
        for proto in nm[host].all_protocols():
            lport = nm[host][proto].keys()
            lport = sorted(lport)
            disallowed_ports = [item for item in lport if item not in allowed_ports]
            for port in disallowed_ports:
                if nm[host][proto][port]['state'] not in ['closed', 'filtered']:
                    host_n_port = '%s:%s' % (host, port)
                    if host_n_port not in allowed_host_n_ports:
                        alert_msg += '%s:%s\tstate : %s\n' % (host, port, nm[host][proto][port]['state'])

    return alert_msg


def discover_port(hosts_list, ports, nm_args):
    nm = nmap.PortScanner()
    msg = ''
    nm.scan(hosts_list, ports, arguments=nm_args)
    for host in nm.all_hosts():
        for proto in nm[host].all_protocols():
            lport = sorted(nm[host][proto].keys())
            for port in lport:
                if nm[host][proto][port]['state'] not in ['closed', 'filtered']:
                    host_n_port = '%s:%s' % (host, port)
                    msg += host_n_port + '\n'
                    # alert_msg += '%s %s:%s state: %s\n' % (proto,host,port,nm[host][proto][port]['state']) #(host, port, nm[host][proto][port]['state'])
    return msg


def discover_hosts(hosts_list, nm_args):
    nm = nmap.PortScanner()
    nm.scan(hosts_list, arguments=nm_args)
    # print nm.command_line()
    # print nm.all_hosts()

    up_hosts = []
    for host in nm.all_hosts():
        if nm[host]['status']['state'] == 'up':
            up_hosts.append(host)
    up_hosts.sort()

    with open('hosts.json', 'r') as f:
        try:
            old_up_hosts = json.load(f)
        except:
            old_up_hosts = []
        old_up_hosts.sort()

    if old_up_hosts != up_hosts:
        new_hosts = [item for item in up_hosts if item not in old_up_hosts]
        new_hosts = ', '.join(new_hosts)
        removed_hosts = [item for item in old_up_hosts if item not in up_hosts]
        removed_hosts = ', '.join(removed_hosts)
        diffs = "Hosts list changed!\nNew hosts: %s \nRemoved hosts: %s" % (new_hosts, removed_hosts)

        with open('hosts.json', 'w') as f:
            json.dump(up_hosts, f, indent=4, sort_keys=True)

        # call(['git', 'add', 'hosts.json'])
        # call(['git', 'commit', '-m', diffs])
        # call(['python', 'alert.py', 'email@test.com', 'production hosts info changes', diffs])
        return diffs

main()
