import re
from dateutil.parser import parse
import heapq
import os

timestamp_pattern = '\\d{4}\\-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}\\.\\d{3}\\+\\d{4}'
extracted_lines = []


def include_log_item(log_item, parser_config):
    if log_item is None:
        return False
    return log_item.matches_regex(
        parser_config.match_pattern,
        parser_config.case_insensitive_match_pattern,
        parser_config.exclude_pattern,
        parser_config.case_insensitive_exclude_pattern,
    ) and log_item.between_timestamps(parser_config.start_time, parser_config.end_time)


class LogItem:
    def __init__(self, filename, timestamp, log_line):
        self.filename = filename
        self.timestamp = timestamp
        self.log_lines = [log_line]

    def append_log_line(self, log_line):
        self.log_lines.append(log_line)

    def matches_regex(
        self, inclusion_regex, case_insensitive_inclusion_regex, exclusion_regex, case_insensitive_exclusion_regex
    ):
        if inclusion_regex:
            if not any(re.match(inclusion_regex, line) for line in self.log_lines):
                return False
        if case_insensitive_inclusion_regex:
            if not any(re.match(case_insensitive_inclusion_regex, line, re.IGNORECASE) for line in self.log_lines):
                return False
        if exclusion_regex:
            if any(re.match(exclusion_regex, line) for line in self.log_lines):
                return False
        if case_insensitive_exclusion_regex:
            if any(re.match(case_insensitive_exclusion_regex, line, re.IGNORECASE) for line in self.log_lines):
                return False
        return True

    def between_timestamps(self, start_time, end_time):
        if start_time and self.timestamp < start_time:
            return False
        if end_time and self.timestamp > end_time:
            return False
        return True

    def __str__(self):
        timestamp_string = self.timestamp.isoformat()
        log_lines = '\n'.join(self.log_lines)
        return f"[filename:{self.filename}]\n timestamp:{timestamp_string}\n\tlog_lines:{log_lines}\n\t\tlog_line_length:{len(self.log_lines)}\n\n"


def keyfunc(log_item):
    return log_item.timestamp


def extract_timestamp(line):
    timestamp_string = re.search(timestamp_pattern, line)
    if timestamp_string is not None:
        # gets first occurrence of timestamp
        # TODO: handle edge case where log line doesn't actually have a timestamp but there is a timestamp in the log message
        return parse(timestamp_string.group(0))
    return None


def main(parser_config):

    directory_path = parser_config.directory

    for filename in os.listdir(directory_path):
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
