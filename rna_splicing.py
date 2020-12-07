from styledstring import Styledstring
from butils import read_FASTA, dna_to_protein

def make_pre_mrna(dna: str) -> str:
    complement = {
        'T': 'A',
        'C': 'G',
        'A': 'U',
        'G': 'C'
    }
    pre_mrna = ''
    for b in dna:
        pre_mrna += complement[b]
    return pre_mrna

def cut_pre_mrna(pre_mrna: str, *introns: str) -> list:
    pass

def splice_dna(dna: str, *introns: str) -> str:
    """ Removes all regions of dna matching a given intron
    """
    for intron in introns:
        dna = dna.replace(intron, '')
    return dna

def color_introns(dna: str, *introns: str) -> str:
    for intron in introns:
        intron = Styledstring(intron, fg='red')
        dna = dna.replace(intron, intron.styled)
    return dna


if __name__ == "__main__":
    data = read_FASTA('tests/test_splicing_wintrons.txt')
    dna = data['Rosalind_10']
    introns = [data['Rosalind_12'], data['Rosalind_15']]
    print(color_introns(dna, *introns))
    spliced = splice_dna(dna, *introns)
    protein, _ = dna_to_protein(spliced)
    print(protein)
