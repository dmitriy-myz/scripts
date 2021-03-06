## virtualbox-systemd

Systemd unit for Virtualbox vm's.  
Can start and stop vm's as a linux service

## Installing

1. copy `vbox_stop.sh` to `/etc/default/`
2. copy `vbox@.service` to `/etc/systemd/system/`
3. inspect `vbox@.service` for working directory, user and group (by default vm's running from user root)
4. run 
```bash
chmod +x /etc/default/vbox_stop.sh
systemctl daemon-reload
```

## Usage

Add new vm to autostart/autostop  
Run
```bash
vboxmanage list vms
```

get name or uuid from output  
Run 
```bash
systemctl enable vbox@"name"
systemctl status vbox@"name"
```

start:
```bash
systemtl start vbox@name
```

or
```bash
service vbox@name start
```

stop:
```bash
systemctl stop vbox@name
```

or
```bash
service vbox@name stop
```

## Limitation

1. Vm name should not contain whitespaces. If so, use UUID insteam vm name. Instruction for pretty name below
2. Vm should hanlde ACPI power buton signal to shutdown correctly
3. Vm should stop in 180 s after ACPI power button signal (or will be killed by systemd)


## Pretty name for vm with whitespaces

1. Edit `vbox.service`, set correct UUID, name, user, etc
2. Rename to you preferred name
3. Copy to `/etc/systemd/system/`
4. Run
```bash
systemctl daemon-reload
systemctl enable YOUR_SERVICE_NAME
```

