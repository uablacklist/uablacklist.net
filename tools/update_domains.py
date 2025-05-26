# -*- coding: utf-8 -*-
# Parses a pdf with urls and adds/updates domains.json

import json
import re
import argparse
import subprocess
import re

parser = argparse.ArgumentParser(description='Parses a file with urls and adds/updates domains.json.')
parser.add_argument('--in', dest='in_file', type=str, default='in.txt', help='path to incoming data file')
parser.add_argument('--aliases', type=str, default='../gen/scripts/aliases.json', help='path to aliases json file')
parser.add_argument('--domains', type=str, default='../gen/scripts/domains.json', help='path to domains.json to update')
parser.add_argument('--term', type=str, default=None, help='restriction term, format: "dd.mm.yyyy"')
parser.add_argument('--reason', type=str, help='restriction reason')

DOMAIN_REGEX = '[0-9а-яa-z-]+(?:\.[0-9а-яa-z-]+)+'
PATH_REGEX = '(?:/[a-z0-9_]+)*'

def pdf_to_text(filename):
    # Call pdftotext and capture the output
    result = subprocess.run(['pdftotext', '-colspacing', '0.3', '-layout', filename, '-'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        print("[ERROR] error converting PDF to text:", result.stderr.decode('utf-8'))
        return None
    return result.stdout.decode('utf-8')

def remove_unwanted_sections(text):
    # Define the pattern to remove text from form feed until "юридичної особи)"
    form_feed_pattern = re.compile(r'\f.*?(юридичної особи\)|професійна діяльність)', re.DOTALL)
    
    # Substitute the unwanted sections with an empty string
    cleaned_text = re.sub(form_feed_pattern, '', text)
    
    return cleaned_text

def split_text_into_chunks(text):
    # Define the regex pattern to split the text
    pattern = re.compile(r'\n\d+\.', re.DOTALL)
    
    # Find all chunks
    chunks = pattern.split(text)
    
    return chunks

def extract_company_name(chunk):
    # Split the chunk into lines
    lines = chunk.split('\n')
    
    # Join all the lines in the second column, stripping extra whitespace
    second_column_text = []
    for line in lines:
        columns = re.split(r'\s{2,}|^\s+', line)
        if len(columns) > 1:
            second_column_text.append(columns[1].strip())
    
    joined_text = ' '.join(second_column_text).replace('- ', '-')
    
    
    # Extract text until the first "(" symbol
    company_name = joined_text.split('(')[0].strip()
    
    return company_name

def parse_incoming_data(chunk, aliases, args):
    company = extract_company_name(chunk)
    urls = re.findall('(' + DOMAIN_REGEX + PATH_REGEX + ')', chunk)

    domains = {}
    for url in urls:
        parts = re.match('(' + DOMAIN_REGEX + ')(' + PATH_REGEX + ')', url)
        domain = parts.group(1)
        path = parts.group(2)
        if domains.get(domain):
            domain_data = domains[domain]
        else:
            domain_data = { 'company': company, 'term': args.term, 'reason': args.reason }
            if aliases.get(company):
                domain_data['alias'] = aliases[company]
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
            print('[WARNING] domain had infinite term, but changed to finite')
            print(domain, data)
        merged_domains[domain] = data

    return merged_domains

def run(args):
    with open(args.aliases) as f:
        aliases = json.load(f)
        
    # Convert PDF to text
    text = pdf_to_text(args.in_file)
    if text is None:
        return
    
    # Remove unwanted sections from the text
    cleaned_text = remove_unwanted_sections(text)
    
    # Split the text into chunks
    chunks = split_text_into_chunks(cleaned_text)
    
    # Extract and print company names from each chunk
    for _, chunk in enumerate(chunks):
        new_domains = parse_incoming_data(chunk, aliases, args)
        with open(args.domains) as f:
            current_domains = json.load(f)
            merged_domains = merge_domains(current_domains, new_domains)
        with open(args.domains, 'w') as f:
            json.dump(merged_domains, f, ensure_ascii=False, indent=4)
    
run(parser.parse_args())
