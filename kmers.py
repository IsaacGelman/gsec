
# n = integer of kmers you want to go up to
# dna = the string of dna
def enumerate (num, dna):
    # create frequency table
    freq = {}

    # iterate through string num times
    for i in range (1,num+1):
        for n in range(0, len(dna)-i+1):
            kmer = dna[n:n+i]
            if kmer not in freq.keys():
                freq[kmer] = 0
            freq[kmer] += 1

    # return frequency table
    return freq

# test da code wooooooo
if __name__ == "__main__":
    result = enumerate(6, "atcgtcatctgactagcaatcga")
    print(result)
