# python script to automate nmap scanning
```bash

python3 -m pip install python-nmap

cp config.json.example config.json

vim config.json

```


add to crontab:

`python3 scan_hosts.py --scan_type=discovery`
`python3 scan_hosts.py --scan_type=short`
`python3 scan_hosts.py --scan_type=full`
