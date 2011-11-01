# ConfEdit
# Copyright (C) 2011 Kantist
#
#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#     
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#     GNU General Public License for more details.
#     
#     You should have received a copy of the GNU General Public License
#     along with this program.
#     If not, see http://www.gnu.org/licenses/gpl-3.0.html

import os
import re
import subprocess
import shlex
import argparse

CONF_PATH = os.environ['HOME'] + '/.config/confedit'

def parse_file(conf_path=CONF_PATH):
    # read configuration from file, return empty settings on failure
    try:
        conf_raw = open(conf_path).read()
    except IOError:
        print("Configuration file %s doesn't exist." % conf_path)
        return {}, {}, {} # tools, paths, files
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
    
    tools = {}
    order = 1
    for tool in conf['TOOLS']:
        var, sep, tool = tool.partition('=')
        if not tool:
            tool = var
        tools[var] = (tool, order)
        order += 1
    
    paths = {}
    for path in conf['PATHS']:
        var, sep, path = path.partition('=')
        if not path: continue
        paths[var] = path
    
    files = {}
    for file in conf['FILES']:
        var, sep, file = file.partition('=')
        if not file:
            file = var
        file, sep, tool = file.partition(' with ')
        if '$' in file:
            file = parse_vars(file, paths)
        if '$' in tool:
            tool = parse_vars(tool, tools)
        if not tool:
            files[var] = (file,)
        else:
            files[var] = (file, tool)
    
    return tools, paths, files

# parse variables of format $var in a string
def parse_vars(string, vars):
    for var in vars:
        if '$%s' % var in string:
            string = string.replace('$%s' % var, vars[var])
    return string

# parse command-line arguments
def parse_args():
    parser = argparse.ArgumentParser(description='ConfEdit')
    parser.add_argument('file', metavar='FILE', help='file to edit')
    parser.add_argument('tool', metavar='TOOL', default=None, nargs='?', help='tool to use')
    parser.add_argument('--conf', metavar='CONFIG_PATH', default=None, nargs='?', help='path to configuration file')
    args = parser.parse_args()
    return args.file, args.tool, args.conf

def main(conf_path=CONF_PATH):
    # command-line arguments
    file, tool, conf_path_arg = parse_args()
    if conf_path_arg: conf_path = conf_path_arg
    # configuration
    tools, paths, files = parse_file(conf_path)
    # tool variables ordered as in configuration
    tool_vars_order = sorted(tools, key=lambda var: tools[var][1])
    # tool commands ordered as in configuration
    tools_order = [tools[var][0] for var in tool_vars_order]
    # set some default editors if no editor is defined
    if len(tools_order) == 0:
        tools_order = ['vi', 'vim', 'emacs', 'nano'] # vi is almost omnipresent
    
    if file in files:
        file = files[file][0]
    if not tool:
        tool = tools_order[0] 
    elif tool.lower() == 'ask':
        for pos in range(0, len(tools)):
            print('   %i) %s' % (pos + 1, tools_order[pos]))
        choice = input('> Choose tool or type a command (default=1): ')
        try:
            choice = int(choice)
            tool = tools_order[choice-1]
        except ValueError:
            tool = tools_order[0] if not choice else choice
        except IndexError:
            tool = tools_order[0] if choice < 0 else tools_order[-1]
    elif tool in tools:
            tool = tools[tool][0]
    
    # generate raw command, split into arguments
    cmd_raw = '%s %s' % (tool, file)
    cmd_args = shlex.split(cmd_raw)
    # call the command, print error if it fails
    try:
        retcode = subprocess.check_call(cmd_args)
        print('> Edited %s with %s.' % (file, tool))
        return True
    except OSError as error:
        print('> Error running %s:' % cmd_raw)
        print(error.strerror)
        return False


if __name__ == '__main__':
    main()
