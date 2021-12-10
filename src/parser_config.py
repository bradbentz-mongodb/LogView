import configparser

import dataclasses
from dataclasses import dataclass, field, asdict
from datetime import datetime
import pathlib

from typing import List

from dateutil.parser import parse


@dataclass
class ParserConfig:
    """
    Configuration class for a log parser.
    """

    directory: pathlib.PosixPath
    exclude_files: List[str]
    start_time: datetime
    end_time: datetime
    match_patterns: List[str]
    exclude_patterns: List[str]
    min_log_line_length: int

    def __post_init__(self):
        if self.match_patterns is None:
            self.match_patterns = []
        if self.exclude_patterns is None:
            self.exclude_patterns = []
        if self.directory is not None:
            self.directory = pathlib.Path(self.directory).expanduser().resolve()
        if self.exclude_files is None:
            self.exclude_files = []
        if self.min_log_line_length is None:
            self.min_log_line_length = 0

    @staticmethod
    def prepare_patterns(pattern_list):
        joined_patterns = '|'.join(pattern_list)
        return f'.*({joined_patterns}).*'

    @property
    def match_pattern(self):
        case_sensitive_patterns = [pattern for pattern in self.match_patterns if not pattern.startswith('-i ')]
        if len(case_sensitive_patterns) == 0:
            return None
        return self.prepare_patterns(case_sensitive_patterns)

    @property
    def exclude_pattern(self):
        case_sensitive_patterns = [pattern for pattern in self.exclude_patterns if not pattern.startswith('-i ')]
        if len(case_sensitive_patterns) == 0:
            return None
        return self.prepare_patterns(case_sensitive_patterns)

    @property
    def case_insensitive_match_pattern(self):
        case_insensitive_patterns = [pattern[3:] for pattern in self.match_patterns if pattern.startswith('-i ')]
        if len(case_insensitive_patterns) == 0:
            return None
        return self.prepare_patterns(case_insensitive_patterns)

    @property
    def case_insensitive_exclude_pattern(self):
        case_insensitive_patterns = [pattern[3:] for pattern in self.exclude_patterns if pattern.startswith('-i ')]
        if len(case_insensitive_patterns) == 0:
            return None
        return self.prepare_patterns(case_insensitive_patterns)

    @staticmethod
    def from_file(config_file):
        """
        Create a ParserConfig from a file.
        """
        parser = configparser.ConfigParser(allow_no_value=True, delimiters=('\n',))
        parser.optionxform = str
        parser.read(config_file)

        directory = None
        if parser.has_section('directory'):
            directory = list(parser['directory'])[0]

        exclude_files = None
        if parser.has_section('exclude_files'):
            exclude_files = list(parser['exclude_files'])

        start_time = None
        if parser.has_section('start_time'):
            start_time_list = list(parser['start_time'])
            if len(start_time_list) > 0:
                start_time = parse(start_time_list[0])

        end_time = None
        if parser.has_section('end_time'):
            end_time_list = list(parser['end_time'])
            if len(end_time_list) > 0:
                end_time = parse(end_time_list[0])

        match_patterns = []
        if parser.has_section('match_pattern'):
            match_patterns = list(parser['match_pattern'])

        exclude_patterns = []
        if parser.has_section('exclude_pattern'):
            exclude_patterns = list(parser['exclude_pattern'])

        min_log_line_length = 0
        if parser.has_section('min_log_line_length'):
            min_log_line_length_list = list(parser['min_log_line_length'])
            if len(min_log_line_length_list) > 0:
                min_log_line_length = int(min_log_line_length_list[0])

        print(f'directory={directory}\nstart_time={start_time}\nend_time={end_time}\nmatch_patterns={match_patterns}\nexclude_patterns={exclude_patterns}\nmin_log_line_length={min_log_line_length}\nexclude_files={exclude_files}')
        return ParserConfig(directory, exclude_files, start_time, end_time, match_patterns, exclude_patterns, min_log_line_length)

    @staticmethod
    def merge(config1, config2):
        """
        Merge two ParserConfigs replacing all attributes in config1
        with any specified attributes in config2.
        """
        if config1 is None:
            return config2
        if config2 is None:
            return config1

        directory = config2.directory or config1.directory or '.'
        exclude_files = config2.exclude_files or config1.exclude_files
        start_time = config2.start_time or config1.start_time
        end_time = config2.end_time or config1.end_time
        min_log_line_length = config2.min_log_line_length or config1.min_log_line_length

        match_patterns = config1.match_patterns + config2.match_patterns
        exclude_patterns = config1.exclude_patterns + config2.exclude_patterns
        return ParserConfig(directory, exclude_files, start_time, end_time, match_patterns, exclude_patterns, min_log_line_length)

