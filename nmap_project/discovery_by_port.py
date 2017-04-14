import nmap
import json
from subprocess import call
import sys
short_scan = False
ports = sys.argv[1] 

with open('config.json', 'r') as f:
    config = json.load(f)


with open('hosts.json', 'r') as f:
    hosts = json.load(f)
    hosts.sort()

allowed_ports = config['allowed_ports']
allowed_host_n_ports = config['allowed_host_n_ports']
ignore_hosts = ','.join(config['ignore_hosts'])

hosts_list = ' '.join(hosts)


args = '-Pn --exclude %s' % ignore_hosts

def alert(msg):
    pass
    print msg
    
nm = nmap.PortScanner()
nm.scan(hosts_list, ports, arguments = args)
#print nm.command_line() 

alert_msg = ''
for host in nm.all_hosts():
    for proto in nm[host].all_protocols():
        lport = nm[host][proto].keys()
        lport.sort()
        for port in lport:
            if nm[host][proto][port]['state'] not in ['closed', 'filtered']:
                host_n_port = '%s:%s' %(host, port)
                alert_msg += host_n_port + '\n'
                #alert_msg += '%s %s:%s state: %s\n' % (proto,host,port,nm[host][proto][port]['state']) #(host, port, nm[host][proto][port]['state'])
    
if alert_msg:
    alert(alert_msg)
                   


