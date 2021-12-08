#!/usr/bin/env python3
# Python 3.7 or greater

from dateutil.parser import parse

import argparse
import datetime
import pathlib
import os
import log_parser

from parser_config import ParserConfig


def dir_path(string):
    if os.path.isdir(string):
        return string
    else:
        raise Exception(f'Invalid directory {string}')


def input_date(string):
    try:
        return parse(string)
    except ParserError:
        print(f'Could not parse timestamp {string}')
        raise


def prepare_patterns(pattern_list):
    joined_patterns = '|'.join(pattern_list)
    return f'.*({joined_patterns}).*'


parser = argparse.ArgumentParser(description='Unified log view')
parser.add_argument(
    'directory',
    metavar='directory',
    type=dir_path,
    help='directory containing log files to view',
    default='.',
    nargs='?',
)
parser.add_argument('--start-time', type=input_date, help='show logs after this time')
parser.add_argument('--end-time', type=input_date, help='show logs before this time')
parser.add_argument(
    '--match-pattern', type=str, action='extend', help='show logs matching the specified pattern', nargs='*'
)
parser.add_argument(
    '--exclude-pattern', type=str, action='extend', help='hide logs matching the specified pattern', nargs='*'
)
parser.add_argument('-c', '--config', type=argparse.FileType('r', encoding='UTF-8'), help='configuration file')


def main(args):
    directory_path = pathlib.Path(args.directory).resolve()

    log_string = f'Viewing logs in {directory_path}'

    if args.start_time:
        log_string += f' starting from {args.start_time}'
    if args.end_time:
        log_string += f' ending at {args.end_time}'

    print(log_string)

    if args.config:
        print(f'Reading from configuration file {args.config}')
        return

    parser_config = ParserConfig(
        directory_path, args.start_time, args.end_time, args.match_pattern, args.exclude_pattern
    )

    log_parser.main(parser_config)


if __name__ == '__main__':
    try:
        args = parser.parse_args()
        main(args)
    except Exception as e:
        raise
        print(e)
