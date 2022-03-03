import configparser

from functools import cached_property
import dataclasses
import re
from dataclasses import dataclass, field, asdict
from datetime import datetime
import pathlib

from regex_matcher import AlwaysMatcher, NeverMatcher, MultiRegex, RegexWrapper

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
    match_pattern: List[str]
    exclude_pattern: List[str]
    min_log_line_length: int

    def __post_init__(self):
        if self.match_pattern is None:
            self.match_pattern = []
        if self.exclude_pattern is None:
            self.exclude_pattern = []
        if self.directory is not None:
            self.directory = pathlib.Path(self.directory).expanduser().resolve()
        if self.exclude_files is None:
            self.exclude_files = []
        if self.min_log_line_length is None:
            self.min_log_line_length = 0

    @staticmethod
    def join_patterns_orwise(pattern_list):
        joined_patterns = '|'.join(pattern_list)
        return f'.*({joined_patterns}).*'

    @staticmethod
    def prepare_matcher(matcher_group):
        """
        Join a group of regexes orwise while handling case sensitivity.
        """
        case_sensitive_patterns = [pattern for pattern in matcher_group if not pattern.startswith('-i ')]
        case_insensitive_patterns = [pattern[3:] for pattern in matcher_group if pattern.startswith('-i ')]

        case_sensitive_regex = None
        case_insensitive_regex = None

        if len(case_sensitive_patterns) > 0:
            case_sensitive_pattern = ParserConfig.join_patterns_orwise(case_sensitive_patterns)
            case_sensitive_regex = re.compile(case_sensitive_pattern)
        if len(case_insensitive_patterns) > 0:
            case_insensitive_pattern = ParserConfig.join_patterns_orwise(case_insensitive_patterns)
            case_insensitive_regex = re.compile(case_insensitive_pattern, re.IGNORECASE)

        if case_sensitive_regex is not None and case_insensitive_regex is not None:
            return MultiRegex.or_matcher([case_sensitive_regex, case_insensitive_regex])
        elif case_sensitive_regex is not None:
            return RegexWrapper(case_sensitive_regex)
        elif case_insensitive_regex is not None:
            return RegexWrapper(case_insensitive_regex)
        else:
            return None

    @cached_property
    def inclusion_matcher(self):
        """
        Get inclusion matcher for a parser config.
        """
        # If no match patterns are specified, we want to match every line.
        if self.match_pattern == []:
            return AlwaysMatcher()

        # Case where one group of patterns is specified
        # Join the group or-wise and return the single regex
        return self.prepare_matcher(self.match_pattern)

        # Case where multiple groups of patterns are specified
        # Join the individual groups or-wise and join all groups and-wise.
        # TODO: Implement multiple match patterns

    @cached_property
    def exclusion_matcher(self):
        """
        Get exclusion matcher for a parser config.
        """
        # If no exclude patterns are specified, we want to exclude no lines.
        if self.exclude_pattern == []:
            return NeverMatcher()

        # Case where one group of patterns is specified
        return self.prepare_matcher(self.exclude_pattern)

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

        match_pattern = []
        if parser.has_section('match_pattern'):
            match_pattern = list(parser['match_pattern'])

        exclude_pattern = []
        if parser.has_section('exclude_pattern'):
            exclude_pattern = list(parser['exclude_pattern'])

        min_log_line_length = 0
        if parser.has_section('min_log_line_length'):
            min_log_line_length_list = list(parser['min_log_line_length'])
            if len(min_log_line_length_list) > 0:
                min_log_line_length = int(min_log_line_length_list[0])

        print(f'directory={directory}\nstart_time={start_time}\nend_time={end_time}\nmatch_pattern={match_pattern}\nexclude_pattern={exclude_pattern}\nmin_log_line_length={min_log_line_length}\nexclude_files={exclude_files}')
        return ParserConfig(directory, exclude_files, start_time, end_time, match_pattern, exclude_pattern, min_log_line_length)

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

        match_pattern = config1.match_pattern + config2.match_pattern
        exclude_pattern = config1.exclude_pattern + config2.exclude_pattern
        return ParserConfig(directory, exclude_files, start_time, end_time, match_pattern, exclude_pattern, min_log_line_length)

