#!/usr/bin/env python

# 
a = '''$remote_addr - $host - $server_protocol - $remote_user [$time_local] "$request_method" "$request_uri" $status $bytes_sent "$upstream_addr" "$upstream_response_time" "$http_referer" "$http_user_agent" "$geoip_country_code"'''

nginx_spec_values = {
  '$upstream_addr': '(?:%{IPORHOST:upstream_addr:drop}(\:%{NUMBER:upstream_port:drop})?|-)',
  '$upstream_status': '%{NUMBER:upstream_response:tag}',
  '$remote_addr': '%{IPORHOST:balancer_ip:drop}',
  '$http_x_forwarded_for': '%{IPORHOST:source_ip:drop}[^\[]',
  '$proxy_add_x_forwarded_for': '%{IPORHOST:source_ip:drop}[^\[]',
  '$time_local': '%{HTTPDATE:timestamp:drop}',
  '$upstream_response_time': '%{NUMBER:upstream_response_time:drop}',
  '$request_uri': '%{NOTSPACE:uri:drop}',
  '$request_time': '%{NUMBER:request_time:float}',
  '$request_method': '%{WORD:method:drop}',
  '$request': '(?:%{WORD:method:drop} %{NOTSPACE:uri:drop}(?: HTTP/%{NUMBER:version:drop})?|-)',
  '$status': '%{NUMBER:response:tag}',
  '$bytes_sent': '(?:%{NUMBER:bytes:drop}|-)',
  '$http_referer': '(?:%{URI:referer:drop}|-)',
  '$http_user_agent': '%{DATA:agent:drop}',
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
    re = escape_re(in_llp)
    values = nginx_spec_values.keys()
    values.sort(reverse=True)
    for pg_llp_value in values:
        re = re.replace('{}'.format(pg_llp_value), nginx_spec_values[pg_llp_value])
        print pg_llp_value
    return '{}'.format(re)

print convert_to_re(a)
