#!/usr/bin/env python
import sys
import os
import re
import json
import datetime
from socket import gethostname
import argparse
import logging
import time
import signal
import numpy as np

from influxdb import InfluxDBClient


# replace this with your nginx log format string
nginx_log_format = '''$remote_addr [$time_local] "$request" $status $request_length $bytes_sent "$host" "$http_referer" "$http_user_agent" $request_time'''


metric_name = 'nginx_access'
hostname = gethostname()

nginx_time_format = '%d/%b/%Y:%H:%M:%S'
nginx_spec_values = {
  '$upstream_addr': r'(?P<upstream_addr>\S+)',
  '$upstream_status': r'((?P<upstream_status>\d{3})|-)',
  '$remote_addr': r'(?P<remote_addr>\S+)',
  '$http_x_forwarded_for': r'(((?P<http_x_forwarded_for>\S+)(, (?P<http_x_forwarded_for1>\S+))*)|-)',
  '$proxy_add_x_forwarded_for': r'(?P<proxy_add_x_forwarded_for>[0-9a-f:.]+)(, (?P<proxy_add_x_forwarded_for1>\S+))*',

  '$time_local': r'(?P<time>\d{2}/\w+/\d{4}:\d{2}:\d{2}:\d{2}) [+\-]?\d{4}',
  '$upstream_response_time': r'((?P<upstream_response_time>\d+\.\d+)|-)',
  '$request_uri': r'(?P<request_uri>\S+)',
  '$request_time': r'(?P<request_time>\d+\.\d+)',
  '$request_method': r'(?P<request_method>\w+)',
  '$request': r'(((?P<request_method>\w+) (?P<request_uri>\S+) HTTP/(?P<http_version>\d+\.\d+))|-)',
  '$status': r'((?P<status>\d{3})|-)',
  '$bytes_sent': r'((?P<bytes_sent>\d+)|-)',
  '$request_length': r'((?P<request_length>\d+)|-)',
  '$http_referer': r'((?P<http_referer>\S+)|-)?',
  '$http_user_agent': r'(?P<user_agent>[\\\\A-Za-z0-9.();:+*&=?#^`$%~!@,/\-_\[\] \']+)',
  '$http_host': r'((?P<http_host>\S+)|-)',
  '$host': r'((?P<host>\S+)|-)',
  '$geoip_country_code': r'((?P<geoip_country_code>\w+)|-)',
  '$remote_user': r'((?P<remote_user>\w+)|-)',
  '$body_bytes_sent': r'((?P<body_bytes_sent>\d+)|-)',
  '$upstream_cache_status': r'(?P<upstream_cache_status>(MISS|BYPASS|EXPIRED|STALE|UPDATING|REVALIDATED|HIT|-))'

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


def parse_log(f, filename):
    request_time = 0.0
    n_requests = 0
    statuses = {}
    times = {}
    unparsed_lines = 0
    start_time = {}
    string_end_time = {}
    end_time = {}
    processed_time = {}

    for line in f:
        parsed = nginx_log_pattern.match(line)
        if parsed is None:
            logger.info('can not parse line: %s', line)
            unparsed_lines += 1
            pass
        else:
            host = parsed.group('host')
            # if host not in statuses:
            if host not in start_time:
                start_time[host] = datetime.datetime.strptime(parsed.group('time'), nginx_time_format)
                statuses[host] = {}
                times[host] = []
            status = parsed.group('status')
            if status not in statuses[host]:
                statuses[host][status] = {'time': 0.0, 'count': 0, 'bytes_send': 0, 'bytes_received':  0}
            statuses[host][status]['time'] += float(parsed.group('request_time'))
            times[host].append(float(parsed.group('request_time')))
            statuses[host][status]['count'] += 1
            statuses[host][status]['bytes_send'] += int(parsed.group('bytes_sent'))
            statuses[host][status]['bytes_received'] += int(parsed.group('request_length'))
            string_end_time[host] = parsed.group('time')
            #logger.debug(parsed.groupdict())

    for host in start_time.keys():
        end_time[host] = datetime.datetime.strptime(string_end_time[host], nginx_time_format)
        logger.info('start time for server %s in log: %s', host, start_time)
        logger.info('finish time for host %s in log: %s', host, end_time)
        processed_time[host] = end_time[host] - start_time[host]
        timerange = processed_time[host].seconds
        print_result(statuses[host], timerange, host, times[host])
        logger.info('unparsed lines: %s' ,unparsed_lines)

def print_result(statuses, timerange, nginx_host, times):
        global client
        influx_point = []
        for status in statuses.keys():
            if timerange > 0:
                rps = statuses[status]['count']/float(timerange)
            else:
                rps = 0
            rps = round(rps, 2)
            bytes_send = statuses[status]['bytes_send']
            bytes_received = statuses[status]['bytes_received']
            avg_time = statuses[status]['time']/statuses[status]['count']
            #print('{0},server={1},status={2},host={3} rps={4}'.format(metric_name, hostname, status, nginx_host, rps))
            #print('{0},server={1},status={2},host={3} avg_time={4}'.format(metric_name, hostname, status, nginx_host, avg_time))
            influx_point.append(
                {
                    "measurement": metric_name,
                    "tags": {
                        "status": status,
                        "instance": hostname,
                        "host": nginx_host,
                        "dc":  dcname
                    },
                    "time": datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
                    "fields": {
                        "rps": int(rps),
                        "avg_time": round(avg_time, 3),
                        "bytes_send": bytes_send,
                        "bytes_received": bytes_received,
                    }
                }
            )
        nptimes = np.array(times)
        median = np.percentile(nptimes, 50)
        pt85 = np.percentile(nptimes, 85)
        pt90 = np.percentile(nptimes, 90)
        pt95 = np.percentile(nptimes, 95)
        pt99 = np.percentile(nptimes, 99)
        influx_point.append(
            {
                "measurement": metric_name,
                "tags": {
                    "instance": hostname,
                    "host": nginx_host,
                    "dc":  dcname
                },
                "time": datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
                "fields": {
                    "median": round(median, 3),
                    "pt85": round(pt85, 3),
                    "pt90": round(pt90, 3),
                    "pt95": round(pt95, 3),
                    "pt99": round(pt99, 3),

                }
            }
        )
        try:
            client.write_points(influx_point)
        except Exception as e:
            print(str(e))
            sys.stdout.flush()
            client = InfluxDBClient(host, port, user, password, dbname)
        logger.info(statuses)

def parse_arg():
    parser = argparse.ArgumentParser(description='Process nginx log files and output result in influx format.')
    parser.add_argument('file', type=str, help='log files to process')
    parser.add_argument('--loglevel', '-l', type=str, help='log level', default = 'warning')
    parser.add_argument('--influxhost', '-host', type=str, help='influxdb host')
    parser.add_argument('--influxport', '-P', type=str, help='influxdb port', default = 8086)
    parser.add_argument('--influxuser', '-u', type=str, help='influxdb user', default = None)
    parser.add_argument('--influxpass', '-p', type=str, help='influxdb password', default = None)
    parser.add_argument('--influxdb', '-d', type=str, help='influxdb database', default = 'nginx')
    parser.add_argument('--dcname', '-D', type=str, help='current DC', default = None)

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
    with open(in_file) as f:
        parse_log(f, os.path.basename(in_file))

args = parse_arg()
init_logger()

nginx_log_re = '^{}$'.format(convert_to_re(nginx_log_format))
nginx_log_pattern = re.compile(nginx_log_re)

logger.info(nginx_log_re)

host = args.influxhost or os.getenv('INFLUX_HOST')
port = args.influxport or os.getenv('INFLUX_PORT')
user = args.influxuser or os.getenv('INFLUX_USER')
password = args.influxpass or os.getenv('INFLUX_PASSWORD')
dbname = args.influxdb or os.getenv('INFLUX_DB')
dcname = args.dcname or os.getenv('DC')

client = InfluxDBClient(host, port, user, password, dbname)

signal.signal(signal.SIGTERM, lambda *_: sys.exit(0))
signal.signal(signal.SIGINT, lambda *_: sys.exit(0))

in_file = args.file
while True:
    if os.path.isfile(in_file):
        with open(in_file, 'w') as f:
            f.truncate(0)
        time.sleep(15)
        process_log(in_file)
    else:
        print("file does not exists")
        sys.stdout.flush()
        time.sleep(60)

