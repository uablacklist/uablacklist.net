# -*- coding: utf-8 -*-
# Removes expired domains from domains.json

from os import remove
from urllib.parse import urlparse
from datetime import datetime
import json
import re
import argparse
from datetime import datetime, timedelta

parser = argparse.ArgumentParser(description='Removes expired domains from domains.json.')
parser.add_argument('--domains', type=str, default='../gen/scripts/domains.json', help='path to domains.json to update')

def remove_expired(domains):
    updated_domains = {}
    for domain, data in domains.items():
        if data.get('term'):
            term = datetime.strptime(data['term'], '%d.%m.%Y')
            if term < datetime.now():
                continue
        updated_domains[domain] = data

    return updated_domains

def run(args):
    with open(args.domains) as f:
        current_domains = json.load(f)
        updated_domains = remove_expired(current_domains)
    with open(args.domains, 'w') as f:
        json.dump(updated_domains, f, ensure_ascii=False, indent=4)
    
run(parser.parse_args())
