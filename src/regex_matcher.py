
from abc import ABC, abstractmethod
from enum import Enum, auto

import re

class Matcher(ABC):
    @abstractmethod
    def matches(self, line):
        ...

    @staticmethod
    def wrap_matcher(matcher):
        """
        Wrap string or pattern inputs in a RegexWrapper.
        """
        if isinstance(matcher, Matcher):
            return matcher
        elif isinstance(matcher, str) or isinstance(matcher, re.Pattern):
            return RegexWrapper(matcher)
        else:
            raise ValueError(f'Invalid matcher {matcher}')


class AlwaysMatcher(Matcher):
    def matches(self, line):
        return True
    def __str__(self):
        return 'AlwaysMatcher'


class NeverMatcher(Matcher):
    def matches(self, line):
        return False
    def __str__(self):
        return 'NeverMatcher'


class RegexWrapper(Matcher):

    def __init__(self, pattern):
        if isinstance(pattern, str):
            self.pattern = re.compile(pattern)
        elif isinstance(pattern, re.Pattern):
            self.pattern = pattern
        else:
            raise ValueError('Argument to RegexWrapper must be string or regex pattern object.')

    def matches(self, line):
        return bool(self.pattern.match(line))

    def __str__(self):
        return f'[{self.pattern}]'


class MultiRegexOperator(Enum):
    OR = 'OR'
    AND = 'AND'


class MultiRegex(Matcher):
    """
    Container class for combining multiple regexes and evaluating them independently.
    """

    def __init__(self, operator, matchers):
        self.matchers = list(map(self.wrap_matcher, matchers))
        if operator not in [MultiRegexOperator.OR, MultiRegexOperator.AND]:
            raise ValueError(f'Invalid operator {operator} for MultiRegex')
        self.operator = operator

    @staticmethod
    def or_matcher(*matchers):
        return MultiRegex(MultiRegexOperator.OR, *matchers)

    @staticmethod
    def and_matcher(*matchers):
        return MultiRegex(MultiRegexOperator.AND, *matchers)

    def matches(self, line):
        if self.operator == MultiRegexOperator.OR:
            return any(matcher.matches(line) for matcher in self.matchers)
        if self.operator == MultiRegexOperator.AND:
            return all(matcher.matches(line) for matcher in self.matchers)

    def __str__(self):
        return f' {self.operator.value} '.join(map(str, self.matchers))

