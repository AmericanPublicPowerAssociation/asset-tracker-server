import re


WHITESPACE_PATTERN = re.compile(r'\s+', re.MULTILINE)


def normalize_text(text):
    # Adapted from invisibleroads-macros
    return compact_whitespace(text).strip()


def compact_whitespace(text):
    # Adapted from invisibleroads-macros
    return WHITESPACE_PATTERN.sub(' ', text).strip()
