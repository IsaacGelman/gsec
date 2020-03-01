import os
import glob
import sys

os.system("chmod +x Anaconda3-5.2.0-Linux-x86_64.sh")
os.system("bash ./Anaconda3-5.2.0-Linux-x86_64.sh -b -f -p /usr/local")

sys.path.append('/usr/local/lib/python3.6/site-packages/')
# Add channels for later installs
os.system("conda config --add channels bioconda")
os.system("conda config --add channels conda-forge")
os.system("conda install -y parallel-fastq-dump")
