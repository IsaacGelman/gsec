import sys
import os
import glob


def sra_to_fastq(seqtype):
    # remember files that have already been converted to fastq
    listing = glob.glob(os.getcwd() + "/processing/fastq/" + seqtype + "/*/*")
    completed_fastq_names = [fastq_path.split('/')[-1].split('.')[0] for fastq_path in listing]

    srp_list = glob.glob(os.getcwd() + "/preprocessing/pysradb_downloads/" + seqtype + "/*")

    for srp_path in srp_list:
        srr_path_list = glob.glob(srp_path + "/*")

        srp = srp_path.split('/')[-1]

        os.makedirs("./processing/fastq/" + seqtype + "/" + srp, exist_ok=True)
        for srr_path in srr_path_list:
            sra_path_list = glob.glob(srr_path + "/*")
            srr = srr_path.split('/')[-1]

            for path in sra_path_list:
                # skip if already counted
                filename = path.split("/")[-1].split('.')[0]
                print("filename:", filename)
                if filename in completed_fastq_names:
                    print(path + "\n\talready completed")
                    continue
                # skip if not sra
                if path.split('.')[-1] != 'sra':
                    print(path + "\n\tnot sra")
                    continue
                os.system("parallel-fastq-dump --threads 4 --outdir processing / fastq / {seqtype} / {srp} --tmpdir\
                 tmpdir -s preprocessing/pysradb_downloads/\
                          " + seqtype + "/" + srp + "/" + srr + "/" + filename + ".sra")
