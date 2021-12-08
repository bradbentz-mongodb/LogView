import re
from dateutil.parser import parse
import heapq
import os

timestamp_pattern ='\\d{4}\\-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}\\.\\d{3}\\+\\d{4}'
extracted_lines = []
inclusion_regex = None
exclusion_regex = None
start_time = None
end_time = None

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
    def between_timestamps(self):
        if start_time and self.timestamp < start_time:
            return False
        if end_time and self.timestamp > end_time:
            return False
        return True
    def include_log_item(self):
        return self.matches_regex(inclusion_regex, exclusion_regex) and self.between_timestamps()
    def __str__(self):
        return f"[filename:{self.filename}]\n timestamp:{self.timestamp}\n\tlog_lines:{self.log_lines}\n\t\tlog_line_length:{len(self.log_lines)}\n\n"

def keyfunc(log_item):
    return log_item.timestamp

def extract_timestamp(line):
    timestamp_string = re.search(timestamp_pattern, line)
    if timestamp_string is not None:
        # gets first occurrence of timestamp
        # TODO: handle edge case where log line doesn't actually have a timestamp but there is a timestamp in the log message
        return parse(timestamp_string.group(0))
    return None

def main(directory_path, start_time=None, end_time=None, match_pattern=None, exclude_pattern=None):
    start_time = start_time
    end_time = end_time
    match_pattern = match_pattern
    exclude_pattern = exclude_pattern
    for filename in os.listdir(directory_path):
        if filename.endswith('.log'):
            with open(filename) as log_input:
                extracted_lines_by_file = []
                current_log_item = None
                for line in log_input:
                    line = line.strip()
                    timestamp = extract_timestamp(line)
                    if timestamp is not None:
                        if current_log_item is not None and current_log_item.include_log_item():
                            extracted_lines_by_file.append(current_log_item)
                        current_log_item = LogItem(filename, timestamp, line)
                    else:
                        # ignores initial log lines without associated timestamps
                        if current_log_item is not None:
                            current_log_item.append_log_line(line)
                if current_log_item is not None and current_log_item.include_log_item():
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
