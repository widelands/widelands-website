#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""This script runs pyformat over the code base.
"""

import argparse
import os
import re
import sys
from subprocess import call

def parse_args():
    p = argparse.ArgumentParser(
        description='Run pyformat over the code base.'
        ' Recurses over all relevant files.')
    return p.parse_args()


def find_files(startpath, extensions):
    for (dirpath, _, filenames) in os.walk(startpath):
        for filename in filenames:
            if os.path.splitext(filename)[-1].lower() in extensions:
                yield os.path.join(dirpath, filename)


def main():
    parse_args()

    if not os.path.isdir('pybb') or not os.path.isdir('_ops'):
        print('CWD is not the root of the repository.')
        return 1

    sys.stdout.write('\nFormatting Python code ')
    for filename in find_files('.', ['.py']):
        sys.stdout.write('.')
        sys.stdout.flush()
        call(['pyformat', '-i', filename])
    print(' done.')

    print ('Formatting finished.')
    return 0

if __name__ == '__main__':
    sys.exit(main())
