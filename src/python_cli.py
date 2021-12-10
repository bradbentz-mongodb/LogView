#!/usr/bin/env python3
# Python 3.7 or greater

from dateutil.parser import parse

import argparse
import datetime
import pathlib
import os
import log_parser
import time

from parser_config import ParserConfig


def dir_path(string):
    if os.path.isdir(string):
        return string
    else:
        raise Exception(f'Invalid directory {string}')


def file_path(string):
    if os.path.isfile(string):
        return string
    else:
        raise Exception(f'Invalid file {string}')


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
    nargs='?',
)
parser.add_argument('--exclude-files', type=str, action='extend', help='exclude files', nargs='*')
parser.add_argument('--start-time', type=input_date, help='show logs after this time (inclusive)')
parser.add_argument('--end-time', type=input_date, help='show logs before this time (exclusive)')
parser.add_argument(
    '--match-pattern', type=str, action='extend', help='show logs matching the specified pattern', nargs='*'
)
parser.add_argument(
    '--exclude-pattern', type=str, action='extend', help='hide logs matching the specified pattern', nargs='*'
)
parser.add_argument('--min_log_line_length', type=int, help='show logs with number of lines greater than this integer')
parser.add_argument('--dry-run', action='store_true', help='dry run')
parser.add_argument('-c', '--config', type=file_path, help='configuration file')
parser.add_argument('-v', '--verbose', action='store_true', help='verbose')


def main(args):
    start_time = time.time()
    args_parser_config = ParserConfig(
        args.directory, args.exclude_files, args.start_time, args.end_time, args.match_pattern, args.exclude_pattern, args.min_log_line_length
    )
    file_parser_config = ParserConfig.from_file(args.config) if args.config else None
    parser_config = ParserConfig.merge(file_parser_config, args_parser_config)

    if args.verbose:
        print(f'Parsing logs in directory {parser_config.directory}')
        print(
            f'Using following regexes\n\tcase sensitive match: {parser_config.match_pattern}\n\tcase insensitive match: {parser_config.case_insensitive_match_pattern}\n\tcase sensitive exclude: {parser_config.exclude_pattern}\n\tcase insensitive exclude {parser_config.case_insensitive_exclude_pattern}'
        )
        print(parser_config)

    if args.dry_run:
        return

    log_parser.main(parser_config)
    print(f"--- {time.time() - start_time} seconds ---")


if __name__ == '__main__':
    try:
        args = parser.parse_args()
        main(args)
    except Exception as e:
        raise
        print(e)
