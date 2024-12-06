# Author: Yanfeng Wang (yw4524@ic.ac.uk)
# File Name: python_align_seqs.py
# Description: reads DNA sequences from sequence.csv, finds the best alignment of two sequences, and writes the output
# Version: 0.0.1
# Date: Oct 2024 

"""
Description: reads DNA sequences from sequence.csv, finds the best alignment of two sequences, and writes the output
"""

import csv

# Function to read sequences from a CSV file
def read_sequences(filename):
    with open(filename, mode='r') as file:
        reader = csv.reader(file)
        # Read sequences into a dictionary using the first column as keys
        sequences = {rows[0]: rows[1] for rows in reader}
    
    # Ensure both 'seq1' and 'seq2' are present in the CSV
    if 'seq1' not in sequences or 'seq2' not in sequences:
        raise ValueError("CSV must contain 'seq1' and 'seq2' as keys.")
    
    return sequences['seq1'], sequences['seq2']

# Function to calculate the alignment score starting from a given point
def calculate_score(s1, s2, l1, l2, startpoint):
    matched = ""
    score = 0
    # Loop through each character in the second sequence
    for i in range(l2):
        # Ensure alignment is within the bounds of the first sequence
        if (i + startpoint) < l1: 
            if s1[i + startpoint] == s2[i]:  # Check if bases match
                matched += "*"
                score += 1  # Increment score for each match
            else:
                matched += "-"
        else:
            matched += "-"  
    return score, matched

# Function to find the best alignment of two sequences
def find_best_alignment(seq1, seq2):
    l1, l2 = len(seq1), len(seq2)
    # Assign the longer sequence to s1 and shorter to s2
    if l1 >= l2:
        s1, s2 = seq1, seq2
    else:
        s1, s2 = seq2, seq1
        l1, l2 = l2, l1

    best_align = ""
    best_score = -1

    # Loop through all possible start points of alignment
    for i in range(l1 - l2 + 1): 
        score, matched = calculate_score(s1, s2, l1, l2, i)
        if score > best_score:  # Update best score and alignment if found a higher score
            best_align = "." * i + s2  # Align with appropriate number of leading dots
            best_score = score

    return best_align, best_score, s1

# Function to write the best alignment and score to an output file
def write_output(output_file, best_align, s1, best_score):
    with open(output_file, 'w') as file:
        file.write(f"Best alignment:\n{best_align}\n{s1}\n")
        file.write(f"Best score: {best_score}\n")

# Main block to read sequences, find the best alignment, and save the results
if __name__ == "__main__":
    input_file = "sequence.csv"  # Input CSV file with sequences
    output_file = "best_alignment.txt"  # Output text file to save alignment results

    try:
        # Read sequences from the input file
        seq1, seq2 = read_sequences(input_file)

        # Find the best alignment and score for the sequences
        best_align, best_score, s1 = find_best_alignment(seq1, seq2)

        # Write the best alignment to the output file
        write_output(output_file, best_align, s1, best_score)

        print(f"Results saved to {output_file}")
    except FileNotFoundError:
        print(f"Error: The file {input_file} does not exist.")
    except ValueError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
