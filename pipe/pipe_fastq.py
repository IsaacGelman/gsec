import sys
import os
import glob

def hello(fastq):
    print("first char " + fastq[0])
    print("INPUT: " + fastq)
    print("END INPUT")
    os.system(fastq + " >> out.txt")
    print("HELLO")

data = sys.stdin.read()
hello(data)