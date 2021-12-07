#!/usr/bin/env python3
# Python 3.7 or greater

import argparse
import datetime
import pathlib
import os


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
    log_string = f'Viewing logs in {directory_path}'

    if args.start_time:
        log_string += f' starting from {args.start_time}'
    if args.end_time:
        log_string += f' ending at {args.end_time}'

    print(log_string)


if __name__ == '__main__':
    try:
        args = parser.parse_args()
        main(args)
    except Exception as e:
        print(e)
