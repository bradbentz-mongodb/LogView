import re
from dateutil.parser import parse
import heapq
import os

class LogItem:
    def __init__(self, filename, timestamp, log_line):
        self.filename = filename
        self.timestamp = timestamp
        self.log_lines = [log_line]
    def append_log_line(self, log_line):
        self.log_lines.append(log_line)
    def matches_regex(self, inclusion_regex=None, exclusion_regex=None):
        if inclusion_regex:
            if not any(re.match(inclusion_regex, line) for line in self.log_lines):
                return False
        if exclusion_regex:
            if any(re.match(exclusion_regex, line) for line in self.log_lines):
                return False
        return True
    def between_timestamps(self, start_timestamp, end_timestamp):
        if start_timestamp and self.timestamp < start_timestamp:
            return False
        if end_timestamp and self.timestamp > end_timestamp:
            return False
        return True
    def __str__(self):
        return f"filename:{self.filename}\n timestamp:{self.timestamp}\n\tlog_lines:{self.log_lines}\n\t\tlog_line_length:{len(self.log_lines)}\n\n"

def keyfunc(log_item):
    return log_item.timestamp

def main():
    pattern ='\\d{4}\\-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}\\.\\d{3}\\+\\d{4}'
    extracted_lines = []
    inclusion_regex = '.*(ERROR|WARN).*'
    exclusion_regex = '.*DEBUG.*'

    for filename in os.listdir():
        if filename.endswith('.log'):
            with open(filename) as log_input:
                extracted_lines_by_file = []
                current_log_item = None
                for line in log_input:
                    line = line.strip()
                    timestamp_string = re.search(pattern, line)
                    if timestamp_string is not None:
                        if current_log_item is not None and current_log_item.matches_regex(inclusion_regex, exclusion_regex):
                            extracted_lines_by_file.append(current_log_item)
                        timestamp = parse(timestamp_string.group(0))
                        current_log_item = LogItem(filename, timestamp, line)
                    else:
                        if current_log_item is not None:
                            current_log_item.append_log_line(line)
                if current_log_item is not None and current_log_item.matches_regex(inclusion_regex, exclusion_regex):
                    extracted_lines_by_file.append(current_log_item)
                extracted_lines.append(extracted_lines_by_file)

    merged = heapq.merge(*extracted_lines, key=keyfunc)

    with open('output.txt', 'w') as log_output:
        results = [str(log_item) for log_item in merged]
        log_output.writelines(results)

if __name__ == "__main__":
    main()
