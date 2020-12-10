codonTable = {
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
    'TAA': 'Stop',  'CAA': 'Q',     'AAA': 'K',     'GAA': 'E',
    'TAG': 'Stop',  'CAG': 'Q',     'AAG': 'K',     'GAG': 'E',
    'TGT': 'C',     'CGT': 'R',     'AGT': 'S',     'GGT': 'G',
    'TGC': 'C',     'CGC': 'R',     'AGC': 'S',     'GGC': 'G',
    'TGA': 'Stop',  'CGA': 'R',     'AGA': 'R',     'GGA': 'G',
    'TGG': 'W',     'CGG': 'R',     'AGG': 'R',     'GGG': 'G'
}


def codonMapping(codon):
    protein = None
    if len(codon) == 3 and codon in codonTable:
        protein = codonTable[codon]
        #print("We get a match! The match is: " + codon + " so we convert into " + protein)
    return protein


def translateReverse(dna):
    empty = ""
    lookup = {'A':'T', 'T':'A', 'G':'C', 'C':'G'}
    return empty.join([lookup[c] for c in reversed(dna)])


def stringPossibility(arg):
    result = []
    index = []
    count = 0
    print("*We start adding once we find an M because that is our start* \n")
    argLength = len(arg)
    for i in range(argLength):
        #for each element in argLengths range
        protein = codonMapping(arg[i:i+3])
        #we translate the codon
        if protein and protein == 'M':
            #add the i to the array
            index.append(i)

    for i in index:
        #each element in the index
        stopFind = False
        stringify = '' #proteins string

        for j in range(i, argLength, 3):
            #each j, translate
            protein = codonMapping(arg[j:j+3])

            if not protein:
                #do nothing
                break

            if protein == 'Stop':
                #we find stop here
                count = count + 1
                print(str(count) + " possibility is: ")
                print("-------------------------------------")
                print("The string state being: " + stringify)
                print("We have found a stop here, so we are done. Proceed to next until there are no more cases.\n")
                stopFind = True
                break
            #add protein to string
            stringify = stringify + protein

        if stopFind:
            #if we find stop then we add the string to the result
            result.append(stringify)

    return result


if __name__ == "__main__":
    endLine = "\n"

    dataEntry = "AGCCATGTAGCTAACTCAGGTTACATGGGGATGACCCCGCGACTTGGATTAGAGTCTCTTTTGGAATAAGCCTGAATGATCCGAGTAGCATCTCAG"
    print("-------------------------------------------------------------------------")
    print("                     Open Reading Frame Calculator                       ")
    print("-------------------------------------------------------------------------")
    print("Welcome BB1003 Students!\n The following program is intended to give all distinct protein\n strings that can be translated from Open Reading Frames (In any order).\n")
    #dataEntry = input("Enter the DNA String: ")
    print(" ***Thank you for entering*** \n")
    print("---We will start with the normal entry (no reversal)--- \n")
    possibilityA = stringPossibility(dataEntry) #regular

    print("---Now, we will do the reversal of the DNA--- \n")
    possibilityB = stringPossibility(translateReverse(dataEntry))  # possible string is reversal

    print("----If we have any duplicate scenarios, they will be processed as one.---- \n")
    print("***At this point, we have no more to process so we are done*** \n")

    print (endLine.join(set(possibilityA + possibilityB)))