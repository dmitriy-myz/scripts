# python script to automate nmap scanning
```bash

python3 -m pip install python-nmap

cp config.json.example config.json

vim config.json

```


add to crontab:
`python3 discovery_hosts.py`

`python3 scan_hosts.py`
