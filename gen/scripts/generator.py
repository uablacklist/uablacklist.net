# -*- coding: utf-8 -*-
import glob, os
import urllib.request
from urllib.parse import urlparse, urlencode
from jinja2 import Template
import pytz
from datetime import datetime
import json
import subprocess
import ipaddress
import netaddr
import re
import argparse
import logging
from transliterate import translit, get_available_language_codes

parser = argparse.ArgumentParser(description='Generates files for uablacklist.net.')
parser.add_argument('out', metavar='output', type=str, help='output directory')


def net_info(domain):
    # covert internationalized domains (IDN) to ASCII
    encoded = domain.encode('idna')
    ips = subprocess.check_output(['dig', encoded, 'A', '+short']).decode('utf-8').split('\n')
    ips = [ip for ip in ips if re.match('\d+.\d+.\d+.\d+', ip)]
    return ips

individuals = {}

def gen_subnets():
    print('Generate subnets')
    all_subnets = {}
    with open('asns.json') as f:
        data = json.load(f)
        for alias, info in data.items():
            subnets = set()
            print(alias)
            for asn in info['asns']:
                print(asn)
                try:
                    request = urllib.request.Request(
                        'https://www.ididb.ru/ip-json/',
                        data=urlencode({
                            'dmn': asn,
                            'tp': 'autnum_rating',
                            'src': '8000'
                        }).encode()
                    )
                    result = json.load(urllib.request.urlopen(request))
                    subnets.update([netaddr.IPNetwork(r['rt']) for r in result['route']])
                except Exception as e:
                    logging.exception(e)
                    pass
            merged_subnets = list(map(str, netaddr.cidr_merge(subnets)))
            all_subnets[alias] = merged_subnets
            print('Result:', ', '.join(merged_subnets), '\n\n')
    return all_subnets


def gen_domains():
    global individuals
    print('\n\nGenerate domains list info')
    print('Prepare domains')
    with open('domains.json') as f:
        data = json.load(f)
        for domain, info in data.items():
            print(domain)
            if 'alias' in info:
                alias = info['alias']
            elif 'company' in info:
                alias = translit(info['company'], 'uk', reversed=True)
                alias = alias.replace('«', '"').replace('»', '"')
                alias = alias.replace('’', "'")
            else:
                alias = domain
            individuals[domain] = {
                'alias': alias,
                'term': info['term'],
                'urls': info['urls'] if 'urls' in info else ['http://{}/'.format(domain)],
                'ips': net_info(domain)
            }

# Gen mikrotik firewall rules
def gen_mikrotik(subnets):
    def gen_chunk(alias, subnets, max_size=4000):
        out = ['# %s' % alias]
        for subnet in subnets:
            if len('\n'.join(out + [subnet]) + '\n') > max_size:
                yield '\n'.join(out) + '\n'
                out = ['# %s' % alias]
            out.append(subnet)
        yield '\n'.join(out) + '\n'

    # There can be a case when amount of subnets decreased, that's why we remove all old files
    for f in glob.glob('%s/subnets_mikrotik_*.txt' % (out_dir)):
        os.remove(f)

    i = 0
    for alias in subnets:
        if not len(subnets[alias]):
            continue
        for chunk in gen_chunk(alias, subnets[alias]):
            with open('%s/subnets_mikrotik_%s.txt' % (out_dir, i), 'w') as outfile:
                outfile.write(chunk)
            i=i+1

def filter_invalid_ips(ips):
    return [ip for ip in ips if ip != '127.0.0.1']

def run():
    gen_domains()
    subnets = gen_subnets()
    ips = set()
    domains = list(individuals.keys())
    domains.sort()
    out = ''
    for domain in domains:
        print('Prepare %s' % domain)
        info = individuals[domain]
        info['urls'] = list(info['urls'])
        domain_ips = filter_invalid_ips(info['ips'])
        ips.update(domain_ips)
        if not subnets.get(info['alias']):
            subnets[info['alias']] = set()
        # Add domain IPs to subnets list
        for ip in domain_ips:
            is_in = False
            for subnet in list(subnets[info['alias']])[:]:
                if ipaddress.ip_address(ip) in ipaddress.ip_network(subnet):
                    is_in = True
                    break
            if not is_in:
                print('add additional ip %s' % ip)
                subnets[info['alias']].add(str(ipaddress.ip_network(ip)))
    blocked_ips = 0
    for key, array in subnets.items():
        for subnet in array:
            blocked_ips = blocked_ips + ipaddress.ip_network(subnet).num_addresses
    ips = list(ips)
    ips.sort(key=lambda ip: ipaddress.ip_address(ip))
    plain_subnets = set()
    [plain_subnets.update(networks) for networks in subnets.values()]
    plain_subnets = list(plain_subnets)
    plain_subnets.sort(key=lambda s: ipaddress.ip_network(s))

    # Generate index.html
    with open(out_dir + '/index.tpl.html') as f:
        template = Template(f.read())
        now = datetime.now(pytz.timezone('Europe/Kiev'))
        with open('l18n.json') as l:
            l18n = json.load(l)
            for lang in l18n['strings']:
                file = template.render(
                    str=l18n['strings'][lang],
                    lang=lang,
                    last_update=now.strftime('%Y-%m-%d %H:%M:%S'),
                    domains=domains,
                    info=individuals,
                    ips=blocked_ips,
                    switch_lang_link=l18n['settings']['switch'][lang]['link'],
                    switch_lang_title=l18n['settings']['switch'][lang]['title'],
                    lang_link=l18n['settings']['links'][lang]
                )
                with open(out_dir + l18n['settings']['html_out_folder'][lang] + '/index.html', 'w') as o:
                    o.write(file)

    # Generate APIs
    with open(out_dir + '/all.json', 'w') as outfile:
        json.dump(individuals, outfile)
    with open(out_dir + '/ips.json', 'w') as outfile:
        json.dump(ips, outfile)
    with open(out_dir + '/domains.json', 'w') as outfile:
        json.dump(list(domains), outfile)
    with open(out_dir + '/ips.txt', 'w') as outfile:
        outfile.write('\n'.join(ips))
    with open(out_dir + '/domains.txt', 'w') as outfile:
        outfile.write('\n'.join(domains))
    with open(out_dir + '/subnets.json', 'w') as outfile:
        json.dump(plain_subnets, outfile)
    with open(out_dir + '/subnets.txt', 'w') as outfile:
        outfile.write('\n'.join(plain_subnets))
    gen_mikrotik(subnets)

args = parser.parse_args()
out_dir = args.out
run()
