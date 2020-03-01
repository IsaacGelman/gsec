import os
import glob

if 'count' not in os.listdir():
    os.system("g++ -O3 countkmers.cpp -o count")
os.system("chmod +x count")


def kmer_count(seqtype):
    out_path = "processing/temp_out/"

    listing = glob.glob(os.getcwd() + "/model_building/data/" + seqtype + "/*/*")
    counts_filenames = [filename.split('/')[-1].split('.')[0] for filename in listing]

    srp_list = glob.glob(os.getcwd() + "/processing/fastq/" + seqtype + "/*")
    for srp_path in srp_list:
        srr_path_list = glob.glob(srp_path + "/*")
        srp = srp_path.split('/')[-1]

        os.makedirs("./model_building/data/" + seqtype + "/" + srp, exist_ok=True)

        for path in srr_path_list[:15]:
            # skip if already counted
            filename = path.split("/")[-1].split('.')[0]
            print("filename:\n\t", filename)
            if filename in counts_filenames:
                print(path + "\n\talready counted")
                continue
            # skip if not fastq
            if path.split('.')[-1] != 'fastq':
                print(path + "\n\tnot fastq")
                continue

            path = path.split("CAIS++/")[-1]

            # Count 1-mers and create file, then append 2-6mers
            os.system("./ count 1 " + path + " > model_building/data/" + seqtype + "/" + srp + "/" + filename + ".txt")
            os.system("./ count 2 " + path + " >> model_building/data/" + seqtype + "/" + srp + "/" + filename + ".txt")
            os.system("./ count 3 " + path + " >> model_building/data/" + seqtype + "/" + srp + "/" + filename + ".txt")
            os.system("./ count 4 " + path + " >> model_building/data/" + seqtype + "/" + srp + "/" + filename + ".txt")
            os.system("./ count 5 " + path + " >> model_building/data/" + seqtype + "/" + srp + "/" + filename + ".txt")
            os.system("./ count 6 " + path + " >> model_building/data/" + seqtype + "/" + srp + "/" + filename + ".txt")
