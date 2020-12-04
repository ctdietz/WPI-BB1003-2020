
def is_reverse_palindrome(str):
    # Reverse DNA
    reverse_str = str[::-1]

    # Find DNA complement of reversed sequence
    inverse_str = ""
    for x in reverse_str:
        inverse_str += dnaComplement[x]

    # Return true if sequence is a reverse palindrome
    if inverse_str == str:
        return True

    return False


def find_reverse_palindromes(dna):
    palindromes = []

# Iterate over entire DNA sequence
    for i in range(len(dna)):
        current_str = ""

        # Examine sub-sequences of length 4 - 12 for each letter in the sequence
        for j in range (i, len(dna)):
            current_str += dna[j]
            # Increase sub-sequence until within range
            if len(current_str) < 4:
                continue
            # Move to next sub-sequence out of range
            if len(current_str) > 12:
                break
            # Determine if sub-sequence is a reverse palindrome if it is in range
            if is_reverse_palindrome(current_str):
                palindromes.append([i + 1, len(current_str)])

    # Print results in rosalind format (position, length)
    for entry in palindromes:
        print(entry[0], entry[1])


dna = "GCGCTCATTTCAATATACCCCGGTTGGCCTATGTGCGCACGCGCTCTCAAGTCTTCCTAAGGAGCGATTTAGTTATGATCGTCACAAACGAAAAGTAGTTGGTTGGGCTCCGCGGTGTATAAAATGAACCTTAGTGAGCCACTCACGCCACGGCGCCGACACATACTTTTATCACTCCGAAGGGGGACATTTGCATGTGAGACTTGATTGCACGAAAGTTATTCATCGCAGAAAACTTTTTTTAAGGTACGTCTGCACTGCACAGTACAGCCACTGGGGAGGAGGCTGCCCCCGTCTTGTGAAAACAACCTGTACCCTCGTTACGACGCAAAGGACTGCGTCTCATGAACATATTAACTGCTGGGGATGCATTATCTGGATCTCTTCAGTCCACAGTTTGCCATAGATTAGCTCTAGTCTCCAGAATATACGCTTCGAGATGTTTCGTTTGTTTGTTACCAGGGTACGCCCTGGAGCTTAACGTACGTTAAAAGAGTACTGCGCGACATTAACCAGGTCCGCACGACTAGTGTGTCGGCCGGGTTAACGGAAAAAATGACGCAGAGACCCAGACGGGTAAGGGGGGCCTCCGTTGTGGCTTCGCGACTTTATGGAGTTGGGAGCATACGTAGTTATATTATGTTAATAAGAGCGAAAACCAGAAGTAGGCGAAATGGTCCGACTAGTACAGGGGGTGCTTGCTCGTTCTCAATTACAGTCAACAATGGTACCGGTACTCATCGGACGATGAAACGCCCCGATCACTATCACGTTCTCTAAGTATTGTCACAGCTTTTGATCGGGCGTTACCGGCCTCAAAGTATGGTGTTCGCACTCGGCGACAGGGGGCTACAAGGACTCGTTCGTTTGCTTCCCTTCAAGCTAACGCGTAGAGACAAGACGACAGATGTGTTGTATGTTGTATTTTTGTTGAGATTACGTTGGATATCCATGACAAAAACCATATA"
dnaComplement = {
    "G": "C",
    "C": "G",
    "A": "T",
    "T": "A"
}

find_reverse_palindromes(dna)


def execute():
    dna = input("Please enter a DNA sequence in FASTA format: ")