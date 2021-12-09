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
    start_time: datetime
    end_time: datetime
    match_patterns: List[str]
    exclude_patterns: List[str]

    def __post_init__(self):
        if self.match_patterns is None:
            self.match_patterns = []
        if self.exclude_patterns is None:
            self.exclude_patterns = []
        if self.directory is not None:
            self.directory = pathlib.Path(self.directory).expanduser().resolve()

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

        start_time = None
        if parser.has_section('start_time'):
            start_time = parse(list(parser['start_time'])[0])

        end_time = None
        if parser.has_section('end_time'):
            end_time = parse(list(parser['end_time'])[0])

        match_patterns = []
        if parser.has_section('match_pattern'):
            match_patterns = list(parser['match_pattern'])

        exclude_patterns = []
        if parser.has_section('exclude_pattern'):
            exclude_patterns = list(parser['exclude_pattern'])

        return ParserConfig(directory, start_time, end_time, match_patterns, exclude_patterns)

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
        start_time = config2.start_time or config1.start_time
        end_time = config2.end_time or config1.end_time

        match_patterns = config1.match_patterns + config2.match_patterns
        exclude_patterns = config1.exclude_patterns + config2.exclude_patterns

        return ParserConfig(directory, start_time, end_time, match_patterns, exclude_patterns)
