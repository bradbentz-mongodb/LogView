import re
from dateutil.parser import parse
import heapq
import os
import fnmatch
import datetime
import pytz

timestamp_pattern = '\\d{4}\\-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}\\.\\d{3}\\+\\d{4}'
extracted_lines = []
utc = pytz.UTC

def include_log_item(log_item, parser_config):
    if log_item is None:
        return False
    return log_item.matches_regex(
        parser_config.inclusion_matcher,
        parser_config.exclusion_matcher
    ) and log_item.between_timestamps(utc.localize(parser_config.start_time), utc.localize(parser_config.end_time)) and (len(log_item.log_lines) >= parser_config.min_log_line_length)


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class LogItem:
    def __init__(self, filename, timestamp, log_line):
        self.filename = filename
        self.timestamp = timestamp
        self.log_lines = [log_line]

    def append_log_line(self, log_line):
        self.log_lines.append(log_line)

    def matches_regex(self, inclusion_matcher, exclusion_matcher):
        """
        One line in each of the log lines must match the inclusion matcher and no lines can match the exclusion matcher.
        """
        if inclusion_matcher:
            if not any(inclusion_matcher.matches(line) for line in self.log_lines):
                    return False
        if exclusion_matcher:
            if any(exclusion_matcher.matches(line) for line in self.log_lines):
                    return False
        return True

    def between_timestamps(self, start_time, end_time):
        if start_time and self.timestamp < start_time:
            return False
        if end_time and self.timestamp >= end_time:
            return False
        return True

    def __str__(self):
        timestamp_string = self.timestamp.isoformat()
        log_lines = '\n'.join(self.log_lines)
        return f"{bcolors.OKBLUE}[{self.filename}]{bcolors.ENDC}\n{bcolors.OKGREEN}{timestamp_string}{bcolors.ENDC} {log_lines}\n"


def keyfunc(log_item):
    return log_item.timestamp

def extract_timestamp(line):
    timestamp_string = re.search(timestamp_pattern, line)
    if timestamp_string is not None:
        # gets first occurrence of timestamp
        # TODO: handle edge case where log line doesn't actually have a timestamp but there is a timestamp in the log message
        return parse(timestamp_string.group(0))
    return None

def get_files(directory_path, file_patterns):
    all_files = os.listdir(directory_path)
    exclude_files = set()
    for file_pattern in file_patterns:
        files = fnmatch.filter(all_files, file_pattern)
        print(files)
        print(file_pattern)
        exclude_files.update(files)
    include_files = set(all_files) - exclude_files
    return include_files

def main(parser_config):
    directory_path = parser_config.directory
    exclude_files = parser_config.exclude_files

    for filename in get_files(directory_path, parser_config.exclude_files):
        if filename.endswith('.log'):
            file_path = os.path.join(directory_path, filename)
            with open(file_path) as log_input:
                extracted_lines_by_file = []
                current_log_item = None
                for line in log_input:
                    line = line.strip()
                    timestamp = extract_timestamp(line)
                    if timestamp is not None:
                        if include_log_item(current_log_item, parser_config):
                            extracted_lines_by_file.append(current_log_item)
                        current_log_item = LogItem(filename, timestamp, line)
                    else:
                        # ignores initial log lines without associated timestamps
                        if current_log_item is not None:
                            current_log_item.append_log_line(line)
                if include_log_item(current_log_item, parser_config):
                    extracted_lines_by_file.append(current_log_item)
                extracted_lines.append(extracted_lines_by_file)

    merged = heapq.merge(*extracted_lines, key=keyfunc)

    with open('output.txt', 'w') as log_output:
        results = [str(log_item) for log_item in merged]
        log_output.writelines(results)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(e)
