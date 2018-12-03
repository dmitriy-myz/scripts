#!/usr/bin/env python

# 
a = '''$remote_addr - $host - $server_protocol - $remote_user [$time_local] "$request_method" "$request_uri" $status $bytes_sent "$upstream_addr" "$upstream_response_time" "$http_referer" "$http_user_agent" "$geoip_country_code"'''


nginx_spec_values = {
  '$upstream_addr': '(?:%{IPORHOST:upstream_addr:drop}(\:%{NUMBER:upstream_port:drop})?|-)',
  '$upstream_status': '%{NUMBER:upstream_response:tag}',
  '$remote_addr': '(?<remote_addr>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})',
  '$http_x_forwarded_for': '%{IPORHOST:source_ip:drop}[^\[]',
  '$proxy_add_x_forwarded_for': '(?<x-forwarded-for>([^,]+)(, [^,]+)*)',
  '$time_local': '(?<time>[^\\\]+)',
  '$upstream_response_time': '((?<upstream_response_time>\d+\.\d+(, \d+\.\d+)*)|-)',
  '$request_uri': '%{NOTSPACE:uri:drop}',
  '$request_time': '(?<request_time>\d+\.\d+)',
  '$request_method': '%{WORD:method:drop}',
  '$request': '(?<method>\w+) (?<uri>\S+) HTTP/(?<http_version>\d\.\d)',
  '$status': '(?<status>\d{3})',
  '$bytes_sent': '((?<bytes_sent>\d+)|-)',
  '$http_referer': '((?<referer>\S+)|-)',
  '$http_user_agent': '(?<user_agent>.+)',
  '$request_id': '(?<ctxt_reqid>[0-9a-f]{32})',
  '$http_host': '(?:%{IPORHOST:host_addr:drop}(\:%{NUMBER:host_port:drop})?|-)',
  '$host': '(?:%{IPORHOST:host_addr:drop}(\:%{NUMBER:host_port:drop})?|-)',
  '$geoip_country_code': '%{WORD:country:drop}',
  '$remote_user': '(?:%{WORD:user:drop}|-)'

}

def escape_re(string):
    for i in ['\\', '[', ']', '+']:
        string = string.replace(i, "\\{}".format(i))
    return string

def convert_to_grok(in_format):
    re = escape_re(in_format)
    values = nginx_spec_values.keys()
    values.sort(reverse=True)
    for pg_llp_value in values:
        re = re.replace('{}'.format(pg_llp_value), nginx_spec_values[pg_llp_value])
        print pg_llp_value
    return '{}'.format(re)

print convert_to_grok(a)
