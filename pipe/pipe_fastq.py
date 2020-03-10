import sys
import os
import glob

def hello(fastq):
    print("INPUT: " + fastq)
    print("END INPUT")

    lines = fastq.split()
    for line in lines:
        if (len(line) != 0):
            if (line[0] == "A" or line[0] == "C" or line[0] == "G" or line[0] == "T"):
                # os.system("echo " + line)
                os.system("echo " + line + " >> out.txt")
    print("HELLO")

data = sys.stdin.read()
hello(data)