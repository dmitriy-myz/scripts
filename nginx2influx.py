#!/usr/bin/env python
import sys
import os
import re
import json

in_file = sys.argv[1]
position_file = 'log_position.json'

# 
#a = '''$remote_addr - $host - $server_protocol - $remote_user [$time_local] "$request_method" "$request_uri" $status $bytes_sent "$upstream_addr" "$upstream_response_time" "$http_referer" "$http_user_agent" "$geoip_country_code"'''
# log_format main1
a = '''$remote_addr\t[$time_local]\t$status\t$upstream_addr\t$upstream_status\t$http_host\t$request\t$http_referer\t$http_user_agent\t$http_x_forwarded_for\t$proxy_add_x_forwarded_for\t-\t$request_time-$upstream_response_time\t$geoip_country_code'''


nginx_spec_values = {
  '$upstream_addr': '(?P<upstream_addr>\S+)',
  '$upstream_status': '((?P<upstream_status>\d+)|-)',
  '$remote_addr': '(?P<remote_addr>\S+)',
  # TODO fix
  '$http_x_forwarded_for': '((?P<http_x_forwarded_for1>\S+)|-)',
  # TODO fix
  '$proxy_add_x_forwarded_for': '(?P<proxy_add_x_forwarded_for>\S+)',

  '$time_local': '(?P<date>\d{1,2}/\w+/\d{4}):(?P<time>\d{1,2}:\d{1,2}:\d{1,2}) (?P<timezone>[+\-]?\d+)',
  '$upstream_response_time': '(?P<upstream_response_time>\d+\.\d+)',
  '$request_uri': '(?P<request_uri>\S+)',
  '$request_time': '(?P<request_time>\d+\.\d+)',
  '$request_method': '(?P<request_method>\w+)',
  '$request': '(((?P<request_method>\w+) (?P<request_uri>\S+) HTTP/(?P<http_version>\d+\.\d+))|-)',
  '$status': '((?P<status>\d+)|-)',
  '$bytes_sent': '((?P<bytes_sent>\d+)|-)',
  '$http_referer': '((?P<http_referer>\S+)|-)',
  '$http_user_agent': '(?P<user_agent>[A-Za-z0-9.();,/\- ]+)',
  '$http_host': '((?P<http_host>\S+)|-)',
  '$host': '((?P<host>\S+)|-)',
  '$geoip_country_code': '((?P<geoip_country_code>\w+)|-)',
  '$remote_user': '((?P<remote_user>\w+)|-)'

}

def escape_re(string):
    for i in ['\\', '[', ']', '+']:
        string = string.replace(i, "\\{}".format(i))
    return string

def convert_to_re(in_format):
    re = escape_re(in_format)
    values = nginx_spec_values.keys()
    values.sort(reverse=True)
    for nginx_value in values:
        re = re.replace('{}'.format(nginx_value), nginx_spec_values[nginx_value])
    return '{}'.format(re)


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

def parse_log(f):
    for line in f.readlines():
        parsed = nginx_log_pattern.search(line)
        print parsed.groupdict()
    pass

nginx_log_string = a
nginx_log_re = '^{}$'.format(convert_to_re(nginx_log_string))

"""
print nginx_log_re
nginx_log_pattern = re.compile(nginx_log_re)
parsed = nginx_log_pattern.search(l)
print parsed.groupdict()
"""


last_position = load_offset(in_file)
if os.path.getsize(in_file) < last_position:
    # file truncated?
    last_position = 0
    print("file truncation detected!")


with open(in_file) as f:
    f.seek(last_position)
    parse_log(f)
    save_offset(in_file, f.tell())

