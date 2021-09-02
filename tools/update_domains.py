# -*- coding: utf-8 -*-
# Parses a file with urls and adds/updates domains.json
# File structure:
# [company]
# [reason]
# [term, leave empty line if infinite]
# [alias, leave empty line if no alias]
#
# "raw",
# list
# 'of';
# domains"

from urllib.parse import urlparse
from datetime import datetime
import json
import re
import argparse

parser = argparse.ArgumentParser(description='Parses a file with urls and adds/updates domains.json.')
parser.add_argument('--in', dest='in_file', type=str, default='in.txt', help='path to incoming data file')
parser.add_argument('--domains', type=str, default='../gen/scripts/domains.json', help='path to domains.json to update')

DOMAIN_REGEX = '[0-9а-яa-z-]+(?:\.[0-9а-яa-z-]+)+'
PATH_REGEX = '(?:/[a-z0-9_]+)*'

def parse_incoming_data(in_file):
    company = None
    term = None
    reason = None
    urls = None
    alias = None
    with open(in_file) as f:
        data = f.read()
        lines = data.split('\n')
        company = lines[0]
        reason = lines[1]
        term = lines[2] or None
        alias = lines[3] or None
        raw_urls = " ".join(lines[5:])
        urls = re.findall('(' + DOMAIN_REGEX + PATH_REGEX + ')', raw_urls)

    domains = {}
    for url in urls:
        parts = re.match('(' + DOMAIN_REGEX + ')(' + PATH_REGEX + ')', url)
        domain = parts.group(1)
        path = parts.group(2)
        if domains.get(domain):
            domain_data = domains[domain]
        else:
            domain_data = { 'company': company, 'term': term, 'reason': reason }
            if alias:
                domain_data['alias'] = alias
            domains[domain] = domain_data
        if path:
            if not domain_data.get('urls'):
                domain_data['urls'] = set()
            domain_data['urls'].add('http://{}{}'.format(domain, path))

    for domain, data in domains.items():
        if data.get('urls'):
            data['urls'] = list(data['urls'])

    return domains

def merge_domains(current_domains, new_domains):
    merged_domains = {}
    merged_domains.update(current_domains)
    for domain, data in new_domains.items():
        if merged_domains.get(domain) and merged_domains[domain]['term'] is None and data['term'] is not None:
            print('[WARNING] domain had infinite term, but changed to finite, ignoring the change completely')
            print(domain, data)
        else:
            merged_domains[domain] = data

    return merged_domains

def run(args):
    new_domains = parse_incoming_data(args.in_file)
    with open(args.domains) as f:
        current_domains = json.load(f)
        merged_domains = merge_domains(current_domains, new_domains)
    with open(args.domains, 'w') as f:
        json.dump(merged_domains, f, ensure_ascii=False, indent=4)
    
run(parser.parse_args())
