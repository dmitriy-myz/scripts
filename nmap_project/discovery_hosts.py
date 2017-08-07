import nmap
import json
from subprocess import call
import sys

with open('config.json', 'r') as f:
    config = json.load(f)

hosts = config['hosts']
hosts_list = ' '.join(hosts)

ignore_hosts = ','.join(config['ignore_hosts'])

nm = nmap.PortScanner()

discovery = True
ports = 443
if discovery:
    args = '-n -sn -PE -PA22,80,443,30022,1194,1195,1701,5969 --exclude %s' % ignore_hosts
else:
    args = '-Pn -p %s --exclude %s' % (ports, ignore_hosts)


def discover_port():
    nm.scan(hosts_list, ports, arguments = args)
    for host in nm.all_hosts():
        for proto in nm[host].all_protocols():
            lport = nm[host][proto].keys()
            lport.sort()
            for port in lport:
                if nm[host][proto][port]['state'] not in ['closed', 'filtered']:
                    host_n_port = '%s:%s' %(host, port)
                    alert_msg += host_n_port + '\n'
                    #alert_msg += '%s %s:%s state: %s\n' % (proto,host,port,nm[host][proto][port]['state']) #(host, port, nm[host][proto][port]['state'])
    print msg

def discover_hosts():
    nm.scan(hosts_list, arguments=args)
    #print nm.command_line() 
    #print nm.all_hosts()

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
        diffs =  "Hosts list changed!\nNew hosts: %s \nRemoved hosts: %s" %(new_hosts, removed_hosts)

        with open('hosts.json', 'w') as f:
            json.dump(up_hosts, f, indent=4, sort_keys=True)

        call(['git', 'add', 'hosts.json'])
        call(['git', 'commit', '-m', diffs])
        call(['python', 'alert.py', 'email@test.com', 'production hosts info changes', diffs])
