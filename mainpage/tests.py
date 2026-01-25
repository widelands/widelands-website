#!/usr/bin/python -tt

# Load and runs the test from the utest subdirectory
# your unittests should append ".." to their path to
# find the files relative to this directory

import unittest
from glob import glob
import os
import sys

prefix = ""
append_path = False
if __name__ != "__main__":
    prefix = __name__[:-5]
    append_path = True


def suite():
    # If we are not called directly, we have
    # to append this path to sys.path so our
    # subtests will find their files
    this_dir = os.path.dirname(__file__)
    if append_path:
        sys.path.append(this_dir)

    suite = unittest.TestSuite()
    l = unittest.TestLoader()

    dname = os.path.dirname(__file__)

    for f in glob(f"{dname}/utest/*.py"):
        if os.path.basename(f) == "__init__.py":
            continue

        modname = f"{prefix}utest.{os.path.basename(f)[:-3]}"

        # Load tests
        tests = l.loadTestsFromName(modname)
        suite.addTests(tests)

    if append_path:
        sys.path.remove(this_dir)

    return suite


def main():
    tsuite = suite()
    runner = unittest.TextTestRunner()
    runner.run(tsuite)
    return unittest.TestResult()


if __name__ == "__main__":
    main()
