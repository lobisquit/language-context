#!/usr/bin/env python3
"""
Extract manually added information from language-context.cson
"""
import re
import sys
#import json
import cson
from pathlib import Path

#inputfile = Path('snippets/autosnippets-context.cson')
inputfile = Path('tools/language-context_orig.cson')
outputfile = Path('tools/context-infos.cson')

reContinue = re.compile(r"'\s*\+\s*'", flags=re.M|re.U)

COMMANDS = {}
data = None

# if outputfile.is_file():
#     print(f'output file "{outputfile}" exists, won’t overwrite.')
#     # TODO: read in, add information
#     sys.exit(1)

print(f'reading {inputfile}')

with open(inputfile, 'r') as input:
    text = '\n'.join(input.readlines())
    # cson parser can’t handle continued strings
    m = reContinue.search(text)
    while m:
        text = text.replace(m.group(0), '')
        m = reContinue.search(text)
    data = cson.loads(text)

for cmd in data['.text.tex.context']:
    try:
        desc = data['.text.tex.context'][cmd]['description']
    except KeyError:
        desc = ''
    try:
        url = data['.text.tex.context'][cmd]['descriptionMoreURL']
    except KeyError:
        url = 'https://wiki.contextgarden.net/Command/' + cmd.replace('\\', '')
    COMMANDS[cmd] = {
        'description': desc,
        'body': data['.text.tex.context'][cmd]['body'],
        'url': url
    }
    #if desc:
    #    print(cmd, ':\t', desc)

with open(outputfile, 'w') as output:
    cson.dump(COMMANDS, output, ensure_ascii=False, indent=2)

# outputfile = outputfile.with_suffix('.json')
# with open(outputfile, 'w') as output:
#     json.dump(COMMANDS, output, ensure_ascii=False, indent=2)

print(f'output written to {outputfile}')
