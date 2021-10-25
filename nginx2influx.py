#!/usr/bin/env python
import sys
import os
import re
import json
import datetime
from socket import gethostname
import argparse
import logging
import glob


# replace this with your nginx log format string

nginx_log_format = '''$remote_addr - $remote_user [$time_local] "$request" $status $body_bytes_sent $upstream_response_time "$http_referer" "$http_user_agent" "$http_x_forwarded_for" "$host" "$request_length"'''

metric_name = 'nginx_access'
hostname = gethostname()

position_file = '/tmp/log_position.json'



nginx_time_format = '%d/%b/%Y:%H:%M:%S'
nginx_spec_values = {
  '$upstream_addr': '(?P<upstream_addr>\S+)',
  '$upstream_status': '((?P<upstream_status>\d{3})|-)',
  '$remote_addr': '(?P<remote_addr>\S+)',
  '$http_x_forwarded_for': '(((?P<http_x_forwarded_for>\S+)(, (?P<http_x_forwarded_for1>\S+))*)|-)',
  '$proxy_add_x_forwarded_for': '(?P<proxy_add_x_forwarded_for>[0-9a-f:.]+)(, (?P<proxy_add_x_forwarded_for1>\S+))*',

  '$time_local': '(?P<time>\d{2}/\w+/\d{4}:\d{2}:\d{2}:\d{2}) [+\-]?\d{4}',
  '$upstream_response_time': '((?P<upstream_response_time>\d+\.\d+)|-)',
  '$request_uri': '(?P<request_uri>\S+)',
  '$request_time': '(?P<request_time>\d+\.\d+)',
  '$request_method': '(?P<request_method>\w+)',
  '$request': '(((?P<request_method>\w+) (?P<request_uri>\S+) HTTP/(?P<http_version>\d+\.\d+))|-)',
  '$status': '((?P<status>\d{3})|-)',
  '$bytes_sent': '((?P<bytes_sent>\d+)|-)',
  '$http_referer': '((?P<http_referer>\S+)|-)?',
  '$http_user_agent': '(?P<user_agent>[\\\\A-Za-z0-9.();:+*&=?#^`$%~!@,/\-_\[\] \']+)',
  '$http_host': '((?P<http_host>\S+)|-)',
  '$host': '((?P<host>\S+)|-)',
  '$geoip_country_code': '((?P<geoip_country_code>\w+)|-)',
  '$remote_user': '((?P<remote_user>\w+)|-)',
  '$body_bytes_sent': '((?P<body_bytes_sent>\d+)|-)',
  '$upstream_cache_status': '(?P<upstream_cache_status>(MISS|BYPASS|EXPIRED|STALE|UPDATING|REVALIDATED|HIT|-))',
  '$request_length': '((?P<request_length>\d+)|-)',

}

def escape_re(string):
    for i in ['\\', '[', ']', '+']:
        string = string.replace(i, "\\{}".format(i))
    return string

def convert_to_re(in_format):
    re = escape_re(in_format)
    values = nginx_spec_values.keys()
    values = sorted(values,reverse=True)
    for nginx_value in values:
        logger.debug(nginx_value)
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

def parse_log(f, filename):
    request_time = 0.0
    n_requests = 0
    statuses = {}
    unparsed_lines = 0
    start_time = None
    for line in f:
        parsed = nginx_log_pattern.match(line)
        if parsed is None:
            logger.info('can not parse line: %s', line)
            unparsed_lines += 1
            pass
        else:
            if not start_time:
                start_time = datetime.datetime.strptime(parsed.group('time'), nginx_time_format)
            status = parsed.group('status')
            if status not in statuses:
                statuses[status] = {'time': 0.0, 'count': 0}
            statuses[status]['time'] += float(parsed.group('request_time'))
            statuses[status]['count'] += 1
            string_end_time = parsed.group('time')
            #logger.debug(parsed.groupdict())
    if start_time:
        end_time = datetime.datetime.strptime(string_end_time, nginx_time_format)
        logger.info('start time in log: %s', start_time)
        logger.info('finish time in log: %s', end_time)
        processed_time = end_time - start_time
        timerange = processed_time.seconds
        print_result(statuses, timerange, filename)
        logger.info('unparsed lines: %s' ,unparsed_lines)

def print_result(statuses, timerange, filename):
        for status in statuses.keys():
            if timerange > 0:
                rps = statuses[status]['count']/float(timerange)
            else:
                rps = 0
            rps = round(rps, 2)
            avg_time = statuses[status]['time']/statuses[status]['count']
            avg_time = round(avg_time,3)
            statuses[status]['rps'] = rps
            statuses[status]['avg_time'] = avg_time
            print('{0},server={1},status={2},log_name={3} rps={4}'.format(metric_name, hostname, status, filename, rps))
            print('{0},server={1},status={2},log_name={3} avg_time={4}'.format(metric_name, hostname, status, filename, avg_time))
        logger.info(statuses)


def parse_arg():
    parser = argparse.ArgumentParser(description='Process nginx log files and output result in influx format.')
    parser.add_argument('files', type=str, help='log files to process', nargs='+')
    parser.add_argument('--loglevel', '-l', type=str, help='log level', default = 'warning')
    args = parser.parse_args()
    return args


def init_logger():
    global logger
    logger = logging.getLogger(__name__)
    log_level = getattr(logging, args.loglevel.upper())
    logger.setLevel(log_level)
    formatter = logging.Formatter('%(asctime)s: %(levelname)s %(message)s', '%Y-%m-%d %H:%M:%S')
    channel = logging.StreamHandler(sys.stdout)
    channel.setLevel(log_level)
    channel.setFormatter(formatter)
    logger.addHandler(channel)

 
def process_log(in_file):
    logger.info('processing file: %s', in_file)
    last_position = load_offset(in_file)
    if os.path.getsize(in_file) < last_position:
        # file truncated?
        last_position = 0
        logger.info('possible file %s rotated, reset position to zero', in_file)
    with open(in_file) as f:
        f.seek(last_position)
        parse_log(f, os.path.basename(in_file))
        current_posttion = f.tell()
        save_offset(in_file, current_posttion)

args = parse_arg()

init_logger()

nginx_log_re = '^{}$'.format(convert_to_re(nginx_log_format))
nginx_log_pattern = re.compile(nginx_log_re)

logger.info(nginx_log_re)

files = args.files
in_files = []
for in_file in args.files:
    for _in_file in glob.glob(in_file):
        in_files.append(_in_file)


for in_file in in_files:
    process_log(in_file)
