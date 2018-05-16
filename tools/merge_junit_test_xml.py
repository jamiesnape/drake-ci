#!/usr/bin/env python

"""
Merge multiple Bazel test.xml files from within a directory tree into a single
JUnit XML file.
"""

from __future__ import print_function

import argparse
import os
import sys
import lxml.etree as ET


def main():
    parser = argparse.ArgumentParser(
        description='Merge multiple Bazel test.xml files from within a '
                    'directory tree into a single JUnit XML file.')
    parser.add_argument('input', help='input directory, e.g., bazel-testlogs')
    parser.add_argument('output', help='output file, e.g., junit.xml')
    args = parser.parse_args()
    if not os.path.isdir(args.input):
        parser.error('{} is not a directory'.format(args.input))
    testsuites = ET.Element('testsuites')
    testsuites_errors = 0
    testsuites_failures = 0
    testsuites_skipped = 0
    testsuites_tests = 0
    testsuites_time = 0.0
    for directory, _, filenames in os.walk(args.input, followlinks=True):
        for filename in filenames:
            if filename == 'test.xml':
                path = os.path.join(directory, filename)
                try:
                    root = ET.parse(path).getroot()
                    if root.tag == 'testsuites':
                        for testsuite in root.iter('testsuite'):
                            testsuite.set(
                                'name', testsuite.get('name').replace(
                                    '.', '_'))
                            testsuite_errors = 0
                            testsuite_failures = 0
                            testsuite_skipped = 0
                            testsuite_tests = 0
                            testsuite_time = 0.0
                            for testcase in testsuite.iter('testcase'):
                                testcase.set('name', testcase.get(
                                    'name').replace('.', '_'))
                                if not testcase.get('classname'):
                                    testcase.set(
                                        'classname', testsuite.get('name'))
                                if testcase.get('status') == 'notrun' and \
                                        not testcase.find('skipped'):
                                    testcase.append(ET.Element('skipped'))
                                time = float(testcase.get('time', 0.0))
                                testcase.set('time', str(time))
                                testsuite_time += time
                                ET.strip_elements(
                                    testsuite, 'system-err', 'system-out')
                                ET.strip_attributes(
                                    testcase, 'disabled', 'duration', 'status')
                                for element in testcase.iter(
                                        'error', 'failure', 'skipped'):
                                    element.clear()
                                    if element.tag == 'error':
                                        testsuite_errors += 1
                                    elif element.tag == 'failure':
                                        testsuite_failures += 1
                                    elif element.tag == 'skipped':
                                        testsuite_skipped += 1
                                testsuite_tests += 1
                            errors = testsuite.get('errors')
                            if errors and int(errors) != testsuite_errors:
                                print(('{}: error: expected {} but found {} '
                                       'errors in testsuite in file '
                                       '{}').format(os.path.basename(__file__),
                                                    errors,
                                                    testsuite_errors, path))
                                sys.exit(2)
                            testsuite.set('errors', str(testsuite_errors))
                            failures = testsuite.get('failures')
                            if failures and int(
                                    failures) != testsuite_failures:
                                print(('{}: error: expected {} but found {} '
                                       'failures in testsuite in file '
                                       '{}').format(os.path.basename(__file__),
                                                    failures,
                                                    testsuite_failures, path))
                                sys.exit(3)
                            testsuite.set('failures', str(testsuite_failures))
                            skipped = testsuite.get(
                                'skipped', testsuite.get('disabled'))
                            if skipped and int(skipped) != testsuite_skipped:
                                print(('{}: error: expected {} but found {} '
                                       'skipped in testsuite in file '
                                       '{}').format(os.path.basename(__file__),
                                                    skipped, testsuite_skipped,
                                                    path))
                                sys.exit(4)
                            tests = testsuite.get('tests')
                            if tests and int(tests) != testsuite_tests:
                                print(('{}: error: expected {} but found {} '
                                       'tests in testsuite in file '
                                       '{}').format(os.path.basename(__file__),
                                                    tests, testsuite_tests,
                                                    path))
                                sys.exit(5)
                            testsuite.set('tests', str(testsuite_tests))
                            time = testsuite.get('time')
                            if time:
                                testsuite_time = float(time)
                            testsuite.set('time', str(testsuite_time))
                            testsuites_errors += testsuite_errors
                            testsuites_failures += testsuite_failures
                            testsuites_skipped += testsuite_skipped
                            testsuites_tests += testsuite_tests
                            testsuites_time += testsuite_time
                        testsuites.extend(root)
                except ET.XMLSyntaxError:
                    pass
    if len(testsuites) == 0:
        print('{}: error: no testsuites were found'.format(
            os.path.basename(__file__)))
        sys.exit(1)
    testsuites.set('errors', str(testsuites_errors))
    testsuites.set('failures', str(testsuites_failures))
    testsuites.set('skipped', str(testsuites_skipped))
    testsuites.set('tests', str(testsuites_tests))
    testsuites.set('time', str(testsuites_time))
    tree = ET.ElementTree(testsuites)
    tree.write(args.output, encoding='UTF-8', xml_declaration=True)


if __name__ == '__main__':
    main()
