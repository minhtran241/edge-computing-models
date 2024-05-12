from typing import Tuple, List
import numpy as np


def _get_records(filename: str) -> List[str]:
    """
    Get the records from a FASTA file. Each record is a sequence of nucleotides.
    The first record is the database sequence. The subsequent records are query sequences.

    Args:
        filename (str): The name of the FASTA file.

    Returns:
        List[str]: A list of sequences.
    """
    result = []
    current_seq = []

    with open(filename, "r") as f:
        for line in f:
            line = line.strip()
            if line.startswith(">hsa:"):
                joined_seq = "".join(current_seq)
                result.append(joined_seq)
                current_seq.clear()
            else:
                current_seq.append(line)

    joined_seq = "".join(current_seq)
    result.append(joined_seq)
    result.pop(0)  # Remove the first element (empty string or header)

    return result


def _get_matrix(filename: str) -> Tuple[List[List[int]], List[str]]:
    """
    Get the substitution matrix from a text file.

    Args:
        filename (str): The name of the text file.

    Returns:
        Tuple[List[List[int]], List[str]]: The substitution matrix and the alphabet.
    """
    matrix = []
    with open(filename, "r") as f:
        for line in f:
            matrix.append([int(x) for x in line.split()])

    return matrix


def _get_alphabet(filename: str) -> str:
    """
    Get the alphabet from a text file.

    Args:
        filename (str): The name of the text file.

    Returns:
        str: The alphabet.
    """
    with open(filename, "r") as f:
        return "".join(f.read().splitlines())


def _calculate_score_data(
    alphabet: str,
    row: int,
    column: int,
    substitution_matrix: List[List[int]],
    scoring_matrix: np.ndarray,
    seq1: str,
    seq2: str,
) -> Tuple[int, int]:
    """
    Calculate the score and its origin for the current scoring matrix cell.

    Args:
        alphabet (str): The alphabet.
        row (int): The row index.
        column (int): The column index.
        substitution_matrix (List[List[int]]): The substitution matrix.
        scoring_matrix (np.ndarray): The scoring matrix.
        seq1 (str): The first sequence.
        seq2 (str): The second sequence.

    Returns:
        Tuple[int, int]: The score and its origin.
    """
    # calculate and return the best score and its origin for the current scoring matrix cell
    seq1_letter = seq1[column - 1]
    seq2_letter = seq2[row - 1]

    match_score = substitution_matrix[alphabet.index(seq1_letter)][
        alphabet.index(seq2_letter)
    ]

    diagonal_score = scoring_matrix[row - 1][column - 1] + match_score
    left_score = (
        scoring_matrix[row][column - 1]
        + substitution_matrix[alphabet.index(seq1_letter)][-1]
    )
    up_score = (
        scoring_matrix[row - 1][column]
        + substitution_matrix[alphabet.index(seq2_letter)][-1]
    )

    score = max(diagonal_score, up_score, left_score, 0)
    score_origin = 0

    # 8 = DIAGONAL, 2 = UP, 4 = LEFT
    if score == diagonal_score:
        score_origin = 8
    elif score == up_score:
        score_origin = 2
    else:
        score_origin = 4

    return (score, score_origin)


def _get_indices(
    backtracking_matrix: np.ndarray, row: int, column: int, seq1: str, seq2: str
) -> Tuple[List[int], List[int]]:
    """
    Get the indices for the best alignment for both sequences.

    Args:
        backtracking_matrix (np.ndarray): The backtracking matrix.
        row (int): The row index.
        column (int): The column index.
        seq1 (str): The first sequence.
        seq2 (str): The second sequence.

    Returns:
        Tuple[List[int], List[int]]: The indices for the best alignment for both sequences.
    """
    seq1_indices = []
    seq2_indices = []
    seq1_alignment = ""
    seq2_alignment = ""

    # iterate through backtracking matrix starting with cell which has the max score
    # iterate while collecting indices for the best alignment for both sequences
    while row > 0 and column > 0:
        score_origin = backtracking_matrix[row][column]

        if score_origin == 8:
            seq1_alignment += seq1[column - 1]
            seq2_alignment += seq2[row - 1]
            row = row - 1
            column = column - 1
            seq1_indices.append(column)
            seq2_indices.append(row)
        elif score_origin == 2:
            seq1_alignment += "-"
            seq2_alignment += seq2[row - 1]
            row = row - 1
        else:
            seq1_alignment += seq1[column - 1]
            seq2_alignment += "-"
            column = column - 1

    seq1_indices.sort()
    seq2_indices.sort()
    seq1_alignment = seq1_alignment[::-1]
    seq2_alignment = seq2_alignment[::-1]
    return (seq1_indices, seq2_indices)


def _water(
    alphabet: str, substitution_matrix: List[List[int]], seq1: str, seq2: str
) -> Tuple[int, List[int], List[int]]:
    """
    Perform the Smith-Waterman algorithm.

    Args:
        alphabet (str): The alphabet.
        substitution_matrix (List[List[int], str]): The substitution matrix and the alphabet.
        seq1 (str): The first sequence.
        seq2 (str): The second sequence.

    Returns:
        Tuple[int, List[int], List[int]]: The maximum alignment score, the indices for the first aligned sequence, and the indices for the second aligned sequence.
    """
    # gathering values
    p = len(alphabet)
    seq1_len = len(seq1)
    seq2_len = len(seq2)

    # initalise scoring matrix, backtracking matrix, and max score data
    scoring_matrix = np.zeros((seq2_len + 1, seq1_len + 1))
    max_score, max_score_row, max_score_column = 0, -1, -1
    backtracking_matrix = np.zeros((seq2_len + 1, seq1_len + 1))

    # iterate through scoring matrix to fill it in while filling backtracking matrix
    for row in range(1, seq2_len + 1):
        for column in range(1, seq1_len + 1):
            score_data = _calculate_score_data(
                alphabet, row, column, substitution_matrix, scoring_matrix, seq1, seq2
            )
            score, score_origin = score_data[0], score_data[1]
            if score > max_score:
                max_score = score
                max_score_row = row
                max_score_column = column

            scoring_matrix[row][column] = score
            backtracking_matrix[row][column] = score_origin

    indices = _get_indices(
        backtracking_matrix, max_score_row, max_score_column, seq1, seq2
    )
    return (int(max_score), indices[0], indices[1])


def collect_sw_data(
    dir: str,
    dbfilename: str = "database.txt",
    queryfilename: str = "query.txt",
    matrixfilename: str = "matrix.txt",
    alphabetfilename: str = "alphabet.txt",
) -> Tuple[str, List[List[int]], List[str]]:
    """
    Collect the data needed for pairwise sequence alignment.

    Args:
        dir (str): The directory containing the files.
        dbfilename (str): The name of the database file.
        queryfilename (str): The name of the query file.
        matrixfilename (str): The name of the matrix file.
        alphabetfilename (str): The name of the alphabet file.

    Returns:
        Tuple[str, str, List[List[int]], List[str]]: The database sequence, the query sequence, the substitution matrix, and the alphabet.
    """
    dbfile = f"{dir}/{dbfilename}"
    seq1 = _get_records(dbfile)[0]
    queryfile = f"{dir}/{queryfilename}"
    seq2 = _get_records(queryfile)[0]
    matrixfile = f"{dir}/{matrixfilename}"
    matrix = _get_matrix(matrixfile)
    alphabetfile = f"{dir}/{alphabetfilename}"
    alphabet = _get_alphabet(alphabetfile)
    return (seq1, seq2, matrix, alphabet)


def smith_waterman(
    sw_data: Tuple[str, str, List[List[int]], List[str]]
) -> Tuple[int, str, str]:
    """
    Perform pairwise sequence alignment using the Smith-Waterman algorithm.

    Args:
        sw_data (Tuple[str, str, List[List[int]], List[str]]): The database sequence, the query sequence, the substitution matrix, and the alphabet.

    Returns:
        Tuple[int, str, str]: The maximum alignment score, the first aligned sequence, and the second aligned sequence.
    """
    seq1, seq2, matrix, alphabet = sw_data
    return _water(alphabet, matrix, seq1, seq2)
