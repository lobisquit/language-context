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
outputname = 'snippets/autosnippets-context.cson'

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

# common definitions
# COMMONS = {}
# commondefs = ipath.glob('i-common-*.xml')
# for interface in commondefs:
#     if interface.name == 'i-common-definitions.xml':
#         continue
#     try:
#         tree = ET.parse(interface)
#     except ET.ParseError as ex:
#         print(ex)
#     root = tree.getroot()
#     for define in root.iter(xmlns_cd + 'define'):
#         name = define.attrib['name']
#         COMMONS[name] = define

commands = {}
for interface in contents:
    if 'common' in interface.name:
        continue
    print(interface.name)
    try:
        tree = ET.parse(interface)
    except ET.ParseError as ex:
        print(ex)
    root = tree.getroot()
    for cmd in root.iter(xmlns_cd + 'command'):
        name = cmd.attrib['name']
        if 'variant' in cmd.attrib \
        and (cmd.attrib['variant'].startswith('instance') \
        or cmd.attrib['variant']=='assignment'):
            # instances need to get resolved
            # e.g. note => footnote, endnote
            continue
        if 'type' in cmd.attrib \
        and cmd.attrib['type']=='environment' \
        and not name.startswith('start'):
            name = 'start'+name
        body = name
        args = cmd.find(xmlns_cd + 'arguments')
        noofargs = 0
        if args:
            for child in args:
                noofargs += 1
                tag = child.tag.replace(xmlns_cd, '')
                if tag=='assignments':
                    body += '[${%d:options}]' % noofargs
                elif tag=='content':
                    body += '{${%d:content}}' % noofargs
                elif tag=='resolve':
                    resolvename = child.attrib['name']
                    if 'keyword-name' in resolvename:
                        body += '[${%d:name}]' % noofargs
                    elif 'keyword-reference' in resolvename:
                        body += '[${%d:reference}]' % noofargs
                    elif resolvename=='argument-true':
                        body += '{${%d:content if true}}' % noofargs
                    elif resolvename=='argument-false':
                        body += '{${%d:content if false}}' % noofargs
                    elif resolvename.startswith('argument-'):
                        rest = resolvename.replace('argument-','')
                        body += '{${%d:%s}}' % (noofargs, rest)
                    elif resolvename.startswith('keyword-') or resolvename.startswith('string-'):
                        rest = resolvename.replace('keyword-','').replace('string-','')
                        body += ' ${%d:%s}' % (noofargs, rest)
                    elif 'floatdata-list' in resolvename:
                        body += '[${%s:title={},reference=,}]' % noofargs
                    elif resolvename.startswith('assignment'):
                        body += '[${%d:options}]' % noofargs
                    else:
                        print("\t\tUnhandled resolve in %s: %s" % (name, resolvename))
                        body += '[${%d:%s}]' % (noofargs, resolvename)
                # TODO: sequence
        body += '$%d' % (noofargs + 1)
        if name.startswith('start'):
            body += '\n\\%s\n' % name.replace('start', 'stop')
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
            'body': '\\' + body
        }
with open(outputname, 'w') as csonf:
    csonf.write("'.text.tex.context': ",)
    #csonf.write(json.dumps(commands, sort_keys=True, indent=4))
    csonf.write(compile_cson(commands, indent=2))
