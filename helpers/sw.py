def sw_algo(seq1, seq2, match_score=2, mismatch_score=-1, gap_penalty=-1):
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


def get_records(filename: str):
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


def records_to_txt(filename: str) -> str:
    return "\n".join(get_records(filename))


def smith_waterman(text: str):
    # seq1 and seq2 are separated by a newline character
    records = text.split("\n")

    # records[0] is db sequence, records[1] is query sequence
    max_score, aligned_seq1, aligned_seq2 = sw_algo(records[0], records[1])
    return max_score, aligned_seq1, aligned_seq2
