# Edd
# Copyright (C) 2011 Jure Žiberna
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.
# If not, see http://www.gnu.org/licenses/gpl-3.0.html

DESCRIPTION = "Edd (C) 2011 Jure Žiberna"

import os
import re
import subprocess
import shlex
import argparse

from edd.lict import lict

# path to configuration file, default editor
CONF_PATH = os.environ['HOME'] + '/.config/edd'
EDITOR = os.environ['EDITOR'] if 'EDITOR' in os.environ else 'vi'

def parse_conf(conf_path=CONF_PATH):
    # read configuration from file, return empty settings on failure
    try:
        conf_raw = open(conf_path).read()
    except IOError:
        print("Configuration file %s doesn't exist." % conf_path)
        return lict(), lict() # files, tools
    # remove comments
    conf_raw = re.sub(r" *#.*?(\n|$)", "", conf_raw)
    # trim spaces and tabs
    conf_raw = re.sub(r"(?<=\n)( |\t)*|( |\t)*(?=\n)", "", conf_raw)
    # remove empty lines (start|middle|end)
    conf_raw = re.sub(r"^\n+|(?<=\n)\n+|\n+$", "", conf_raw)
    
    # split by lines
    conf_lines = conf_raw.split("\n")
    # prepare a dictionary for temporary storage
    conf = {
        'TOOLS':[],
        'PATHS':[],
        'FILES':[]
    }
    # set option variable
    opt_name = None
    
    # parse into dict
    for conf_line in conf_lines:
        # check for an [option header]
        opt_match = re.search("(?<=\[).*?(?=\])", conf_line)
        if opt_match: # add new option
            opt_name = opt_match.group(0)
            if opt_name not in conf: opt_name = False
        elif opt_name: # add to current option
            conf[opt_name].append(conf_line)
    
    tools = lict()
    for tool in conf['TOOLS']:
        var, sep, tool = tool.partition('=')
        if not tool:
            tool = var
        tools[var] = tool
    
    paths = lict()
    for path in conf['PATHS']:
        var, sep, path = path.partition('=')
        if not path:
            path = var
        paths[var] = {'path':path}
    
    files = lict()
    for file in conf['FILES']:
        var, sep, file = file.partition('=')
        if not file:
            file = var
        file, sep, tool = file.partition(' with ')
        if '$' in file:
            file = parse_vars(file, paths)
            file = parse_vars(file, files)
        if '$' in tool:
            tool = parse_vars(tool, tools)
        files[var] = {'path': file}
        if tool:
            files[var]['tool'] = tool
    
    return files, tools

# parse variables of format $var
def parse_vars(string, vars):
    for var in vars.reverse():
        if '$%s' % var in string:
            string = string.replace('$%s' % var, vars[var]['path'])
    return string

# parse command-line arguments
def parse_args():
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument('file', metavar='FILE', default='', nargs='?', help='file to edit')
    parser.add_argument('tool', metavar='TOOL', default='', nargs='?', help='tool to use')
    parser.add_argument('--conf', metavar='CONFIG_PATH', default=None, nargs='?', help='path to configuration file')
    args = parser.parse_args()
    return args.file, args.tool, args.conf

# optioner: a function that accepts index and returns formatted option
# selector: same as optioner but returns selected value based on an answer
def ask(question, options=[], optioner=None, selector=None, default=None):
    if default:
        question += ' (default=%s)' % default
    for num in range(0, len(options)):
        option = '%i)' % (num + 1)
        if optioner:
            option += ' %s' % optioner(options, num)
        else:
            option += ' %s' % options[num]
        print('   %s' % option)
    try:
        answer = input('> %s: ' % question)
        if not answer and default:
            answer = default
        if answer:
            answer = int(answer) - 1
        if selector:
            answer = selector(options, answer)
    except KeyboardInterrupt:
        answer = None
    except ValueError:
        if not answer:
            answer = default
    except IndexError:
        if selector:
            if answer < len(options) * (-1):
                answer = selector(options, 0)
            else:
                answer = selector(options, -1)
    finally:
        return answer

def from_files(file, files):
    command = None
    if not files:
        if not file:
            # ask for a path
            path = ask('Type a file path')
        else:
            path = file
    elif file not in files:
        if not file or file == 'ask':
            # ask for a choice or a path
            optioner = lambda opts, num: opts(num) if opts(num) == opts[opts(num)]['path'] else '%s (%s)' % (opts(num), opts[opts(num)]['path'])
            selector = lambda opts, num: opts[opts(num)]['path']
            path = ask('Choose a file or type a path', files, optioner, selector, '1')
        else:
            path = file
    else:
        path = files[file]['path']
        if 'tool' in files[file]:
            command = files[file]['tool']
    return path, command

def from_tools(tool, tools):
    if not tools:
        if not tool:
            # ask for a command
            command = ask('Type a command', default=EDITOR)
        else:
            command = tool
    elif not tool:
        command = tools[tools(0)]
    elif tool not in tools:
        if tool == 'ask':
            # ask for a choice or command
            optioner = lambda opts, num: opts(num) if opts(num) == opts[opts(num)] else '%s (%s)' % (opts(num), opts[opts(num)])
            selector = lambda opts, num: opts[opts(num)]
            command = ask('Choose a file or type a command', tools, optioner, selector, '1')
        else:
            command = tool
    else:
        command = tools[tool]
    return command

def main(conf_path=CONF_PATH):
    # command-line arguments
    file, tool, conf_path_arg = parse_args()
    if conf_path_arg:
        conf_path = conf_path_arg
    # read configuration
    files, tools = parse_conf(conf_path)
    
    path, command = from_files(file, files)
    
    if not path:
        print('')
        return True
    
    if tool or not command:
        command = from_tools(tool, tools)
    
    if not command:        
        print('') # force newline
        return True
    
    # generate raw command, split into arguments
    cmd_raw = '%s %s' % (command, path)
    cmd_args = shlex.split(cmd_raw)
    # call the command, print error if it fails
    try:
        retcode = subprocess.check_call(cmd_args)
        print('> Edited %s with %s.' % (path, command))
        return True
    except OSError as error:
        print('> Error running %s:' % cmd_raw)
        print(error.strerror)
        return False

if __name__ == '__main__':
    import cProfile
    cProfile.run('main()')
