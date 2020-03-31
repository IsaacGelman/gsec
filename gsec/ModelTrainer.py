import os
ROOT = os.path.dirname(os.path.realpath(__file__))

class ModelTrainer():

	def __init__(self,
		pos_org, 
		neg_org,
		pos_strat,
		neg_strat,
		k,
		limit,
		n)

	self.pos_org = pos_org
	self.pos_strat = pos_strat
	self.neg_strat = neg_strat
	self.k = k
	self.limit = limit

	def count(srr, out):
    """
    srr (str): srr id for read
    out (str): directory to save files
    """

    # shell commands to run
    filename = os.path.join(out, '{}.txt'.format(srr))
    count_path = os.path.join(ROOT, 'utils', "stream_kmers")
    fastq = "fastq-dump --skip-technical --split-spot -Z {}".format(srr)
    count = "{} {} {} > {}".format(count_path,
                                     str(self.k),
                                     str(self.limit),
                                     str(filename))
    full = fastq + " | " + count
    subprocess.call(full, shell=True)


    def query(positive, temp_path):
    """
    set (bool): True for positive, False for negative 
    temp_path (string): path to save temp file
    """
    if positive:
    	strat, org = self.pos_strat, self.pos_org
    else:
    	strat, org = self.neg_strat, self.neg_org

    esearch = 'esearch -db sra -query "{}[strategy] AND {}[organism]"'.format(
        strat, org)
    efetch = 'efetch -db sra -format docsum -stop {}'.format(str(self.n))
    query = esearch + ' | ' + efetch + ' > ' + temp_path

    subprocess.call(query, shell=True)

    