#!/usr/bin/env python
import sys
import os
import re
import json
import smtplib
from email.mime.text import MIMEText

in_file = sys.argv[1]
slow_query_threshold = 10000
position_file = '/tmp/pg_log_position.json'
receivers =  ['']
sender = 'root@localhost'

#2017-07-27 00:00:05.469 EST [83200] web@192.168.21.53 postgres
# '%m [%p] %q%u@%h %d '

llp = '%m [%p] %q%u@%h %d '

m_re = '(?P<date>\d{4}(\-\d{2}){2}) (?P<time>(\d{2}:?){3}\.\d+) (?P<timezone>\w+)'
p_re = '(?P<pid>\d+)'
q_re = ''
u_re = '(?P<user>\w+)'
h_re = '(?P<ip>\S+)'
d_re = '(?P<database>(\w+|\[unknown\]))'

log_type_re = '(?P<log_type>\w+): '
duration_re = ' duration: (?P<query_time>\d+\.\d+) ms'

new_records = ['LOG', 'ERROR', 'FATAL']
slow_logs = ''
error_logs = ''

def escape_re(string):
    for i in ['\\', '[', ']', '+']:
        string = string.replace(i, "\\{}".format(i))
    return string

def convert_to_re(in_llp):
    in_llp = escape_re(in_llp)
    re = in_llp.replace('%m', m_re).replace('%p', p_re).replace('%q', q_re).replace('%u', u_re).replace('%h', h_re).replace('%d', d_re)
    re += log_type_re
    return '^{}'.format(re)

def process_query(query, log_type, duration = 0):
    global slow_logs
    global error_logs
    if duration > slow_query_threshold:
        slow_logs += query
        slow_logs += '\n------------\n\n'

    if log_type in ['ERROR', 'FATAL']:
        error_logs += query
        error_logs += '\n------------\n\n'

def parse_log(f):
    query = ''
    slow = False
    current_log_type = 'LOG'

    for line in f.readlines():
        parsed = new_duration_log_line_pattern.search(line) or new_log_line_pattern.search(line) or new_non_session_log_line_pattern.search(line)
        if  parsed:
            log_type =  parsed.group('log_type')
            if log_type in new_records:
                if slow:
                    process_query(query, current_log_type, query_time)
                    slow = False
                else:
                    process_query(query, current_log_type)
                current_log_type = log_type
                query = line
                if 'query_time' in parsed.groupdict():
                    query_time = float(parsed.group('query_time'))
                    slow = True
            else:
                query += line
        else:
            query += line

def save_offset(file_name, position):
    try:
        with open(position_file) as fr:
            _positions = json.load(fr)
    except:
            _positions = {}
    _positions[file_name] = position
    with open(position_file, 'w') as fw:
        json.dump(_positions, fw, indent=4, sort_keys=True)

def load_offset(file_name):
    try:
        with open(position_file, 'r') as fr:
            _positions = json.load(fr)
            position = _positions[file_name]
    except:
        position = 0
    return position

def send_email(message, subject, sender, receivers):
    msg = MIMEText(message, 'plain')
    msg['Subject'] = subject
    msg['From']   = sender
    msg['To'] = receivers[0]
    smtpObj = smtplib.SMTP('localhost')
    smtpObj.sendmail(sender, receivers, msg.as_string())


non_session_llp = llp.split('%q')[0]

non_session_llp_re = convert_to_re(non_session_llp)
llp_re = convert_to_re(llp)
duration_llp_re = llp_re + duration_re

new_non_session_log_line_pattern  = re.compile(non_session_llp_re)
new_log_line_pattern = re.compile(llp_re)
new_duration_log_line_pattern = re.compile(duration_llp_re)

last_position = load_offset(in_file)
if os.path.getsize(in_file) < last_position:
    # file truncated?
    last_position = 0
    print "file truncation detected!"

with open(in_file) as f:
    f.seek(last_position)
    parse_log(f)
    save_offset(in_file, f.tell())

if len(error_logs) > 10:
    send_email(error_logs, 'error logs on db!', sender, receivers)
if len(slow_logs) > 10:
    send_email(slow_logs, 'slow logs on db!', sender, receivers)
