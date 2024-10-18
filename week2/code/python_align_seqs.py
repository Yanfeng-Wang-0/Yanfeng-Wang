import csv 

def read_sequences(filename):
    with open(filename, mode='r') as file:
        reader = csv.reader(file)
        sequences = {rows[0]: rows[1] for rows in reader}

def calculate_score(s1, s2, l1, l2, startpoint):
    matched = ""
    score = 0
    for i in range(l2):
        if (i + startpoint) < l1: 
            if s1[i + startpoint] == s2[i]:
                matched += "*"
                score += 1
            else:
                matched += "-"
    return score, matched 

# Main function to find the best alignment
def find_best_alignment(seq1, seq2):
    l1, l2 = len(seq1), len(seq2)
    if l1 >= l2:
        s1, s2 = seq1, seq2
    else:
        s1, s2 = seq2, seq1
        l1, l2 = l2, l1

    best_align = ""
    best_score = -1

    for i in range(l1 - l2 + 1): 
        score, matched = calculate_score(s1, s2, l1, l2, i)
        if score > best_score:
            best_align = "." * i + s2 
            best_score = score

    return best_align, best_score, s1

def write_output(output_file, best_align, s1, best_score):
    with open(output_file, 'w') as file:
        file.write(f"Best alignment:\n{best_align}\n{s1}\n")
        file.write(f"Best score: {best_score}\n")

if __name__ == "__main__":
    input_file = "sequence.csv" 
    output_file = "best_alignment.txt"

    try:
        seq1, seq2 = read_sequences(input_file)

        best_align, best_score, s1 = find_best_alignment(seq1, seq2)

        write_output(output_file, best_align, s1, best_score)

        print(f"Results saved to {output_file}")
    except ValueError as e:
        print(e)
