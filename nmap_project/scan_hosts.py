import nmap
import json
from subprocess import call
import sys

def alert(msg):
    call(['bash', 'send_msg.sh', msg])
#call(['python', 'alert.py', 'email@test.com', 'You have too many open ports', msg]) 

short_scan = False
if len(sys.argv) > 1:
    short_scan = (sys.argv[1] == 'short')

with open('config.json', 'r') as f:
    config = json.load(f)


with open('hosts.json', 'r') as f:
    hosts = json.load(f)
    hosts = sorted(hosts)

allowed_ports = config['allowed_ports']
allowed_host_n_ports = config['allowed_host_n_ports']
ports_quick_list = config['port_quick_list']
ports_quick_list = [ str(x) for x in ports_quick_list ]
ignore_hosts = ','.join(config['ignore_hosts'])

hosts_list = ' '.join(hosts)
#print hosts_list

if short_scan:
    ports = ','.join(ports_quick_list)
else:
    ports = '1-65535'


args = '-Pn -sT --exclude %s' % ignore_hosts

   
nm = nmap.PortScanner()
nm.scan(hosts_list, ports, arguments = args)
#print nm.command_line() 

"""
for host in nm.all_hosts():
    print('----------------------------------------------------')
    print('Host : %s (%s)' % (host, nm[host].hostname()))
    print('State : %s' % nm[host].state())
    for proto in nm[host].all_protocols():
        print('----------')
        print('Protocol : %s' % proto)

        lport = nm[host][proto].keys()
        lport.sort()
        for port in lport:
            print ('port : %s\tstate : %s' % (port, nm[host][proto][port]['state']))


print(nm.csv())
"""

alert_msg = ''
for host in nm.all_hosts():
    for proto in nm[host].all_protocols():
        lport = nm[host][proto].keys()
        lport.sort()
        disallowed_ports = [item for item in lport if item not in allowed_ports]
        for port in disallowed_ports:
            if nm[host][proto][port]['state'] not in ['closed', 'filtered']:
                host_n_port = '%s:%s' %(host, port)
                if host_n_port not in allowed_host_n_ports:
                    alert_msg += '%s:%s\tstate : %s\n' % (host, port, nm[host][proto][port]['state'])
    
if alert_msg:
    alert(alert_msg)
                   


