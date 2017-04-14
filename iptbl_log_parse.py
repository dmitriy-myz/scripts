#!/usr/bin/env python

import re                                                                                                         
import fileinput
import csv
import sys
from datetime import date, datetime
#sys.setdefaultencoding('utf8')

in_log = sys.argv[1]

out_csv = sys.argv[2]

#Dec  2 05:49:08 packet-log kernel: [553740.952912] BLOCKED TCP: IN=eth0 OUT= MAC=ca:3c:3c:00:e8:7f:00:25:90:d4:25:5e:08:00 SRC=42.102.67.137 DST=192.168.0.222 LEN=60 TOS=0x08 PREC=0x20 TTL=41 ID=3562 DF PROTO=TCP SPT=9058 DPT=23 WINDOW=5808 RES=0x00 SYN URGP=0

pattern = re.compile('IN=(?P<interface>\S*) OUT=(?P<out>\S*) MAC=(?P<mac>\S+) SRC=(?P<source>\S+) DST=(?P<destination>\S+) LEN=(?P<len>\d+)? TOS=(?P<tos>\S+) PREC=(?P<prec>\S+) TTL=(?P<ttl>\d+) ID=(?P<id>\d+)( (?P<flags>\S+))* PROTO=(?P<protocol>\S+) SPT=(?P<source_port>\d+) DPT=(?P<dest_port>\d+)( WINDOW=(?P<window>\d+) RES=(?P<res>\S+) (?P<flags2>\S+))*')
date_pattern = re.compile('^(?P<MONTH_NAME>[a-zA-Z]{3}) {1,2}(?P<DAY>[0-9]{1,2}) (?P<HOURS>[0-9]{2}):(?P<MINUTES>[0-9]{2}):(?P<SECONDS>[0-9]{2})')


MONTH_LOOKUP = {
    "Jan" : "01",
    "Feb" : "02",
    "Mar" : "03",
    "Apr" : "04",
    "May" : "05",
    "Jun" : "06",
    "Jul" : "07",
    "Aug" : "08",
    "Sep" : "09",
    "Oct" : "10",
    "Nov" : "11",
    "Dec" : "12",
}

now = datetime.now()
CURRENT_YEAR = now.year

def make_date_str(logline,date_format):
    """ Convert a log date time information format to inernal timegrep forma

    Function allowing to convert log file date format to internal timegrep date time format
    @param logline log file line containing normally a date time entry
    @param date_format date format to parse the log file date time
    @return string return log file date time as internal timegrep date time format ( YYYYMMDD HH:MM:SS )
    """

    m = re.match(date_format,logline)
    if m is None:
        return ''

    match_array = m.groupdict()
    d_year = match_array['YEAR'] if 'YEAR' in match_array else CURRENT_YEAR
    d_month = match_array['MONTH'] if 'MONTH' in match_array  else MONTH_LOOKUP[match_array['MONTH_NAME']]
    d_day = match_array['DAY'].zfill(2)
    d_hour = match_array['HOURS']
    d_min = match_array['MINUTES']
    d_sec = match_array['SECONDS'] if 'SECONDS' in match_array else '00'
    linedate = "{0}-{1}-{2} {3}:{4}:{5}".format(d_year, d_month, d_day, d_hour, d_min, d_sec)

    return linedate

csv_file = open(out_csv, 'wt')
writer =  csv.writer(csv_file, delimiter ='\t')
writer.writerow( ('date', 'interface', 'source', 'destination', 'length', 'ttl', 'flags', 'protocol', 'source_port', 'dest_port', 'flags2') )

for line in open(in_log).readlines():
#   if pattern.match(line):
    linedate = make_date_str(line, date_pattern)
    log = pattern.search(line).groupdict()
    writer.writerow( (linedate, log['interface'], log['source'], log['destination'], log['len'], log['ttl'], log['flags'], log['protocol'], log['source_port'], log['dest_port'], log['flags2']) )
    pass
