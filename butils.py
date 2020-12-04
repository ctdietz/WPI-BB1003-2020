from itertools import groupby


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


if __name__ == "__main__":
    fasta = read_FASTA('tests/test_fasta.txt')
    print(fasta)
