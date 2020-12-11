from styledstring import Styledstring
from butils import read_FASTA, dna_to_protein


def splice_dna(dna: str, *introns: str) -> str:
    """ Removes all regions of dna matching a given intron
    """
    for intron in introns:
        dna = dna.replace(intron, '')
    return dna

def color_introns(dna: str, *introns: str) -> str:
    for intron in introns:
        intron_styled = Styledstring(intron, fg='red')
        dna = dna.replace(intron, intron_styled)
    return dna


if __name__ == "__main__":
    data = read_FASTA('tests/test_splicing_wintrons.txt')
    dna = data['Rosalind_10']
    introns = [data['Rosalind_12'], data['Rosalind_15']]
    print(color_introns(dna, *introns))
    spliced = splice_dna(dna, *introns)
    protein, _ = dna_to_protein(spliced)
    print(protein)
