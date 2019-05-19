import re


WHITESPACE_PATTERN = re.compile(r'\s+', re.MULTILINE)


def compact_whitespace(text):
    return WHITESPACE_PATTERN.sub(' ', text).strip()


def normalize_text(text):
    return compact_whitespace(text).strip()
