#!/usr/bin/env python3
"""
Convert ConTeXt interface XML into snippet-cson

Call: ixml2cson.py <TEXROOT> <output filename>
"""
import os
import sys
import subprocess
from pathlib import Path
import xml.etree.ElementTree as ET
from cson import compile_cson

xmlns_cd = '{http://www.pragma-ade.com/commands}'
outputname = 'autosnippets-context.cson'

def find_context():
    'find ConTeXt tree'
    if 'TEXROOT' in os.environ:
        # e.g. ~/texmf/tex
        return Path(os.environ['TEXROOT'])
    # TODO: search for texmf/tex in PATH?
    cp = subprocess.run('which mtxrun', shell=True, capture_output=True)
    # e.g. ~/texmf/tex/texmf-linux-64/bin/mtxrun
    if cp.stdout.strip():
        context = Path(cp.stdout.decode('utf-8').strip())
        return context.parents[2]
    return None

if len(sys.argv) > 1:
    ipath = Path(sys.argv[1])
    if not ipath.is_dir():
        print('Parameter "%s" is not a directory.' % ipath)
        sys.exit(2)
    if len(sys.argv) > 2:
        outputname = sys.argv[2]
else:
    ipath = find_context()
    if not ipath:
        print('ConTeXt path not found.')
        sys.exit(1)

ipath = ipath / 'texmf-context/tex/context/interface/mkiv'
contents = list(ipath.glob('i-*.xml'))
if not len(contents):
    print('No ConTeXt interface files found in "%s"' % ipath)
    sys.exit(3)

commands = {}
for interface in contents:
    print(interface.name)
    try:
        tree = ET.parse(interface)
    except ET.ParseError as ex:
        print(ex)
    root = tree.getroot()
    for cmd in root.iter(xmlns_cd + 'command'):
        name = cmd.attrib['name']
        body = r'\\'+name
        args = cmd.find(xmlns_cd + 'arguments')
        noofargs = 0
        if args:
            for child in args:
                noofargs += 1
                if child.tag=='assignments':
                    body += '[${%d:options}]' % noofargs
                elif child.tag=='content':
                    body += '{${%d:content}}' % noofargs
                # TODO: sequence, instances, inheritance
        #body += '$%d' % (noofargs + 1)
        if name.startswith('start'):
            body += '\n\\\\%s\n' % name.replace('start', 'stop')
        desc = ''
        if 'category' in cmd.attrib:
            desc = 'category: %s' % (cmd.attrib['category'])
            if 'level' in cmd.attrib:
                desc += '; '
        if 'level' in cmd.attrib:
            desc += 'level: %s' % cmd.attrib['level']
        if 'file' in cmd.attrib:
            desc += '; defined in: %s' % cmd.attrib['file']
        desc += '; interface: %s' % interface.name
        commands['\\'+name] = {
            'description': desc,
            'descriptionMoreURL': 'https://wiki.contextgarden.net/Command/' + name,
            'prefix': name,
            'body': body
        }
with open(outputname, 'w') as csonf:
    csonf.write("'.text.tex.context': ",)
    #csonf.write(json.dumps(commands, sort_keys=True, indent=4))
    csonf.write(compile_cson(commands, indent=2))
