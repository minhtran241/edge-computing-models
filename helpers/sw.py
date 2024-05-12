from typing import Tuple, List


def _smith_waterman_algo(
    seq1, seq2, match_score=2, mismatch_score=-1, gap_penalty=-1
) -> Tuple[int, str, str]:
    """
    Perform pairwise sequence alignment using the Smith-Waterman algorithm.

    Args:
        seq1 (str): The first sequence to align.
        seq2 (str): The second sequence to align.
        match_score (int): The score to add for a match.
        mismatch_score (int): The score to add for a mismatch.
        gap_penalty (int): The score to subtract for a gap.

    Returns:
        int: The maximum alignment score.
        str: The first aligned sequence.
        str: The second aligned sequence.
    """
    # Initialize the score matrix
    score_matrix = [[0] * (len(seq2) + 1) for _ in range(len(seq1) + 1)]

    # Initialize variables to store the maximum score and its position
    max_score = 0
    max_i, max_j = 0, 0

    # Fill in the score matrix
    for i in range(1, len(seq1) + 1):
        for j in range(1, len(seq2) + 1):
            # Calculate the score for the current position
            match = score_matrix[i - 1][j - 1] + (
                match_score if seq1[i - 1] == seq2[j - 1] else mismatch_score
            )
            delete = score_matrix[i - 1][j] + gap_penalty
            insert = score_matrix[i][j - 1] + gap_penalty
            score_matrix[i][j] = max(0, match, delete, insert)

            # Update the maximum score and its position
            if score_matrix[i][j] > max_score:
                max_score = score_matrix[i][j]
                max_i, max_j = i, j

    # Traceback to find the aligned sequences
    aligned_seq1 = ""
    aligned_seq2 = ""
    i, j = max_i, max_j
    while score_matrix[i][j] != 0:
        if score_matrix[i][j] == score_matrix[i - 1][j - 1] + (
            match_score if seq1[i - 1] == seq2[j - 1] else mismatch_score
        ):
            aligned_seq1 = seq1[i - 1] + aligned_seq1
            aligned_seq2 = seq2[j - 1] + aligned_seq2
            i -= 1
            j -= 1
        elif score_matrix[i][j] == score_matrix[i - 1][j] + gap_penalty:
            aligned_seq1 = seq1[i - 1] + aligned_seq1
            aligned_seq2 = "-" + aligned_seq2
            i -= 1
        else:
            aligned_seq1 = "-" + aligned_seq1
            aligned_seq2 = seq2[j - 1] + aligned_seq2
            j -= 1

    return max_score, aligned_seq1, aligned_seq2


def get_records(filename: str) -> List[str]:
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


def records_to_txt(
    dir: str, dbfilename: str = "database.txt", queryfilename: str = "query.txt"
) -> str:
    """
    Convert the records from a FASTA file to a text format.

    Args:
        dir (str): The directory containing the FASTA files (database and query sequences)

    Returns:
        str: The records in text format.
    """
    dbfile = f"{dir}/{dbfilename}"
    db_seq = get_records(dbfile)[0]
    queryfile = f"{dir}/{queryfilename}"
    query_seq = get_records(queryfile)[0]
    result = db_seq + "\n" + query_seq
    return result


def smith_waterman(text: str) -> Tuple[int, str, str]:
    """
    Perform pairwise sequence alignment using the Smith-Waterman algorithm.

    Args:
        text (str): The text containing the sequences to align.

    Returns:
        Tuple[int, str, str]: The maximum alignment score, the first aligned sequence, and the second aligned sequence.
    """
    # seq1 and seq2 are separated by a newline character
    records = text.split("\n")
    # records[0] is db sequence, records[1] is query sequence
    return _smith_waterman_algo(records[0], records[1])
