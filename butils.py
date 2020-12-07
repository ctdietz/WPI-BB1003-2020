from itertools import groupby
from typing import Optional, Tuple


def read_FASTA(filepath: str) -> dict:
    """ load a FASTA formatted file
    returns: dict with pair sig {'>haeder': 'sequence'}
    """
    def fasta_iter(filepath):
        """ generator function to parse through FASTA files
        Currently does not load FASTA doc header strings

        NOTE: if all would rather just use iterator,
              can move this func to main body and use.
              I figured the dict wrapper would be convenient.
        """
        fasta_file = open(filepath)
        
        # build iterator based on new sequence token '>'
        # handles cases where sequences may be on multiple lines
        fi = (c[1] for c in groupby(fasta_file, lambda line: line[0] == '>'))

        # do the iteratoring
        for fasta in fi:
            # drop the '>' 
            header = fasta.__next__()[1:].strip()
            # join all sequence lines to one, if necessary
            sequence = "".join(pair.strip() for pair in fi.__next__())
            yield (header, sequence)
    
    # expand the iterator to a dict
    data = {}
    for fasta in fasta_iter(filepath):
        header, sequence = fasta
        data[header] = sequence
    return data


DNA_CODON_DICT = {
    'TTT': 'F',     'CTT': 'L',     'ATT': 'I',     'GTT': 'V',
    'TTC': 'F',     'CTC': 'L',     'ATC': 'I',     'GTC': 'V',
    'TTA': 'L',     'CTA': 'L',     'ATA': 'I',     'GTA': 'V',
    'TTG': 'L',     'CTG': 'L',     'ATG': 'M',     'GTG': 'V',
    'TCT': 'S',     'CCT': 'P',     'ACT': 'T',     'GCT': 'A',
    'TCC': 'S',     'CCC': 'P',     'ACC': 'T',     'GCC': 'A',
    'TCA': 'S',     'CCA': 'P',     'ACA': 'T',     'GCA': 'A',
    'TCG': 'S',     'CCG': 'P',     'ACG': 'T',     'GCG': 'A',
    'TAT': 'Y',     'CAT': 'H',     'AAT': 'N',     'GAT': 'D',
    'TAC': 'Y',     'CAC': 'H',     'AAC': 'N',     'GAC': 'D',
    'TAA': '-',     'CAA': 'Q',     'AAA': 'K',     'GAA': 'E',
    'TAG': '-',     'CAG': 'Q',     'AAG': 'K',     'GAG': 'E',
    'TGT': 'C',     'CGT': 'R',     'AGT': 'S',     'GGT': 'G',
    'TGC': 'C',     'CGC': 'R',     'AGC': 'S',     'GGC': 'G',
    'TGA': '-',     'CGA': 'R',     'AGA': 'R',     'GGA': 'G',
    'TGG': 'W',     'CGG': 'R',     'AGG': 'R',     'GGG': 'G'
}

def codon_to_amino_acid(codon: str) -> Optional[str]:
    aa = None
    if codon in DNA_CODON_DICT:
        aa = DNA_CODON_DICT[codon]
    
    if aa == '-':
        return None
    else:
        return aa

def dna_to_protein(dna: str) -> Tuple[str, str]:
    """
    Args:
        dna (str): the dna sequence to translate

    Returns:
        Tuple[str, str]: the translated protein,
                         any remaining dna after a stop codon
    """
    protein = ''
    for i in range(0, len(dna), 3):
        codon = dna[i:i+3]
        aa = codon_to_amino_acid(codon)
        if aa is None:
            dna = dna[i+3:]
            break
        protein += aa
    return protein, dna


if __name__ == "__main__":
    fasta = read_FASTA('tests/test_splicing_wintrons_copy.txt')
    print(fasta)
    print(dna_to_protein(fasta['Rosalind_10']))
