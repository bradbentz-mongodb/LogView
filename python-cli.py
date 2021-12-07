#!/usr/bin/env python3
# Python 3.7 or greater

import argparse
import datetime
import pathlib
import os
import log_parser


def dir_path(string):
    if os.path.isdir(string):
        return string
    else:
        raise Exception(f'Invalid directory {string}')


def input_date(string):
    try:
        return datetime.datetime.fromisoformat(string)
    except ValueError:
        print(f'Could not parse timestamp {string}, try matching the format 2021-12-01T00:00:00+00:00')
        raise


parser = argparse.ArgumentParser(description='Unified log view')
parser.add_argument('directory', metavar='directory', type=dir_path, help='directory containing log files to view')
parser.add_argument('--start-time', type=input_date, help='show logs after this time')
parser.add_argument('--end-time', type=input_date, help='show logs before this time')


def main(args):
    directory_path = pathlib.Path(args.directory).resolve()
    log_parser.main(directory_path, args.start_time, args.end_time)

if __name__ == '__main__':
    try:
        args = parser.parse_args()
        main(args)
    except Exception as e:
        print(e)