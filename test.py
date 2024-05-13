import os
import ahocorasick
from typing import List, Tuple


def _get_keywords(filename: str) -> List[str]:
    """
    Read the keywords from the specified file.

    Args:
    - filename (str): The file containing the keywords.

    Returns:
    - list: List of keywords read from the file.
    """
    with open(filename, "r") as file:
        keywords = [line.strip() for line in file]
    return keywords


def collect_ac_data(
    dir: str, text_file: str = "text.txt", keyword_file: str = "keywords.txt"
) -> Tuple[str, List[str]]:
    """
    Read the text and keywords from the specified directory.

    Args:
    - dir (str): The directory containing the text and keywords.
    - text_file (str): The file containing the text.
    - keyword_file (str): The file containing the keywords.

    Returns:
    - tuple: Tuple containing the text and list of keywords.
    """
    text = os.path.join(dir, text_file)
    with open(text, "r") as file:
        text = file.read()
    keywords = os.path.join(dir, keyword_file)
    return text, _get_keywords(keywords)


def _build_automaton(keywords: List[str]) -> ahocorasick.Automaton:
    """
    Build Aho-Corasick automaton from a list of keywords.

    Args:
    - keywords (list): List of keywords to build the automaton.

    Returns:
    - AhoCorasick object: Aho-Corasick automaton.
    """
    A = ahocorasick.Automaton()
    for idx, key in enumerate(keywords):
        A.add_word(key, (idx, key))
    A.make_automaton()
    return A


def _acas_search(text: str, automaton: ahocorasick.Automaton):
    match_keywords = {}
    for end_index, (insert_order, original_value) in automaton.iter(text):
        start_index = end_index - len(original_value) + 1
        match_keywords.setdefault(str(original_value), [])
        match_keywords[str(original_value)].append((start_index, end_index))
    return match_keywords


def acohorasick_search(data: Tuple[str, List[str]]) -> List[str]:
    """
    Main function to run Aho-Corasick algorithm on input text.

    Args:
    - data (tuple): Tuple containing the input text and list of keywords.

    Returns:
    - list: List of matched keywords.
    """
    text, keywords = data
    automaton = _build_automaton(keywords)
    matched_keywords = _acas_search(text, automaton)
    print(f"Matched keywords: {matched_keywords}")
    return matched_keywords


data = collect_ac_data("data/acas")
result = acohorasick_search(data)
print(result)
