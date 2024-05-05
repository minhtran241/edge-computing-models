import re


def get_device_id(environ):
    return environ.get("HTTP_DEVICE_ID", None)


def count_word_occurrences(input_string: str, word: str) -> int:
    return sum(1 for _ in re.finditer(r"\b%s\b" % re.escape(word), input_string))
