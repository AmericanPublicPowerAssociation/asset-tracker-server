import re


WHITESPACE_PATTERN = re.compile(r'\s+', re.MULTILINE)


def compact_whitespace(string):
    return WHITESPACE_PATTERN.sub(' ', string).strip()
