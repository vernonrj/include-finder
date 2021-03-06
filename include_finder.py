#!/usr/bin/env python2
"""
Finds all includes for c-like languages
"""
from __future__ import print_function
import os
import sys
from getopt import gnu_getopt, GetoptError

import graph
import includer

# TODO: handle filename aliasing better
# TODO: handle case-insensitive #includes

def inc_finder(path, root_file, reverse=False):
    """
    find all files included recursively by root_file
    """
    root_file = os.path.basename(root_file)
    # create a graph of includes to work with
    tree = build_include_tree(path)
    if reverse:
        tree = tree.reverse()
    # list of files included
    files = set()
    # files that haven't been checked yet.
    # when this is empty, we're done
    untouched = set([root_file])
    while untouched:
        new_files = set(untouched)
        untouched = set()
        # find all includes in untouched files
        for each in new_files:
            untouched.update(tree.node_edges(each))
        # remove seen files from untouched
        untouched.difference_update(files)
        # now add the unique files we found to the list of included files
        files.update(untouched)
    # return files as a sorted list
    files = list(files)
    files.sort()
    return files


def build_include_tree(path, reverse=False):
    """build a graph of includes on path"""
    # Create a dictionary of files and their includes
    files = populate_includes(path)
    # now build a graph using files and their includes
    tree = graph.Graph(files.keys())
    for each in tree.keys():
        # get the Include structure for current file
        # create it if an include structure doesn't exist for it
        node = files.get(each, None)
        if not node:
            node = includer.Include.from_file(each)
            tree.add_node(node)
        # connect files to their includes
        # add files to the graph if they aren't there already
        incs = node.includes
        for inc in incs:
            if inc not in tree:
                tree.add_node(inc)
            tree.connect(each, inc)
    if reverse:
        tree = tree.reverse()
    return tree


def populate_includes(path):
    """
    populate a dict of includes for each source or header
    file on the path
    """
    sources = dict()
    # valid file extensions for what we're looking for
    valid = ('.c', '.h', '.cpp', '.hpp')
    for dirpath, _, files in os.walk(path):
        file_list = [os.path.join(dirpath, x) for x in files]
        file_list = [x for x in file_list if x.endswith(valid)]
        # build include structure for each file found
        for each in file_list:
            sources[os.path.basename(each)] = includer.Include.from_file(each)
    return sources


# Below is used for running as a standalone python script


def usage():
    """print usage to STDOUT"""
    print("Usage: %s [OPTION]... FILE" % sys.argv[0])
    print("show an include tree for a file")
    print("")
    print("  -h, --help                 display this help and exit")
    print("  -r, --reverse              show files included by FILE")
    print("  -i, --includes=FILE        return chain from file to include")
    print("  -n, --norecurse            don't recursively find includes")
    print("      --json                 print include tree in JSON format")


TO_FILE = None
REVERSE = False
RECURSIVE = True
PRINT_JSON = False


if __name__ == '__main__':
    try:
        OPTS, ARGS = gnu_getopt(sys.argv[1:], "hi:jrn",
                ["help", "includes", "json", "reverse", "norecurse"])
    except GetoptError as err:
        print(str(err))
        usage()
        sys.exit(2)
    for OPT, ARG in OPTS:
        if OPT in ('-h', '--help'):
            usage()
            sys.exit()
        elif OPT in ('-i', '--includes'):
            TO_FILE = ARG
        elif OPT in ('-r', '--reverse'):
            REVERSE = True
        elif OPT == '--json':
            PRINT_JSON = True
        elif OPT in ('-n', '--norecurse'):
            RECURSIVE = False
        else:
            assert False, "unhandled option"
    if PRINT_JSON:
        import json
        TREE = build_include_tree('.', REVERSE)
        print(json.dumps(dict(TREE),
                         sort_keys=True,
                         indent=2))
        sys.exit(0)
    elif not ARGS:
        usage()
        raise Exception("no file given")
    elif TO_FILE or not RECURSIVE:
        TREE = build_include_tree('.', REVERSE)
        if TO_FILE:
            FILES = TREE.path_to(ARGS[0], TO_FILE)
        else:
            FILES = TREE.node_edges(ARGS[0])
            FILES.sort()
        for FILE in FILES:
            print(FILE)
    else:
        INCS = inc_finder('.', ARGS[0], REVERSE)
        for FILE in INCS:
            print(FILE)


# EOF
