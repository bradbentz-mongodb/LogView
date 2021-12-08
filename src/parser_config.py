from dataclasses import dataclass, field
from datetime import datetime

from typing import List


@dataclass
class ParserConfig:
    """
    Configuration class for a log parser.
    """

    directory: str
    start_time: datetime
    end_time: datetime
    match_patterns: List[str] = field(default_factory=lambda: [])
    exclude_patterns: List[str] = field(default_factory=lambda: [])

    @staticmethod
    def prepare_patterns(pattern_list):
        joined_patterns = '|'.join(pattern_list)
        return f'.*({joined_patterns}).*'

    @property
    def match_pattern(self):
        if self.match_patterns is None or len(self.match_patterns) == 0:
            return None
        return self.prepare_patterns(self.match_patterns)

    @property
    def exclude_pattern(self):
        if self.exclude_patterns is None or len(self.exclude_patterns) == 0:
            return None
        return self.prepare_patterns(self.exclude_patterns)
