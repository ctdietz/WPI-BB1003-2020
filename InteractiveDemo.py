from termapp import TermApp, Text, MultilineText
from styledstring import Styledstring

from butils import read_FASTA, DNA_CODON_DICT
from rna_splicing import splice_dna
import random


def color_introns(dna, *introns) -> list:
    if not isinstance(dna, list):
        dna = [dna]
    for intron in introns:
        if intron in dna[-1]:
            res = dna[-1].split(intron)
            colored_intron = Styledstring(intron, fg='red')
            dna.extend([res[0], colored_intron, res[-1]])
    return dna


def gen_rand_dna(rows, linelen) -> list:
    dna = []
    for i in range(rows):
        line = []
        for j in range(linelen//3):
            line.append(random.choice(list(DNA_CODON_DICT.keys())))
        dna.append(''.join(line))
    return dna

splicing_data = read_FASTA('tests/test_splicing_wintrons_shorter.txt')
spl_dna = splicing_data['Rosalind_10']
introns = [splicing_data['Rosalind_12'], splicing_data['Rosalind_15']]
spliced = splice_dna(spl_dna, *introns)
# spl_protein, _ = dna_to_protein(spliced)

c_introns = color_introns(spl_dna, *introns)
demo = TermApp('Rosalind Problems Interactive Demo')

splicing_screen = demo.new_view(name="DNA Splicing", makedefault=True)

splicing_title_text = Styledstring('DNA Splicing', fg='blue', attrs=['bold', 'underline'])

splicing_title = Text(splicing_title_text, alignment='center', vposition=2)
introns_text = ['Introns to find: ']

for intron in introns:
    introns_text.extend([intron, ', '])
introns_text.pop(-1)

splicing_introns_text = Text(introns_text, alignment='center', vposition=4)
splicing_spliced = Text(c_introns, alignment='center', vposition=6)

rand_dna = gen_rand_dna(rows=8, linelen=120)
rand_dna_text = MultilineText(rand_dna, alignment='left', vposition=6)

splicing_screen.add_elements(splicing_title, splicing_spliced, splicing_introns_text)


def search_highlight_multiline(search):
    text = rand_dna
    for line in text:
        if search in line:
            search_colored = Styledstring(search, fg='red')
            line = line.replace(search, search.lower())
    rand_dna_text.update_value(text)   

demo.run(find_introns=search_highlight_multiline)  # the argument name is the command line arg