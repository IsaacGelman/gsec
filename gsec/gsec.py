# gsec.py: Processes commands from the and calls appropriate 
# functions, or example gsec train to train a new model.
#
# Authors: Isaac Gelman, Nicolas Perez, Natalie Abreu, Shannon Brownlee,
# Tomas Angelini, Laura Cao, Shreya Havaldar
#
# This software is Copyright (C) 2020 The University of Southern
# California. All Rights Reserved.
#
# Permission to use, copy, modify, and distribute this software and
# its documentation for educational, research and non-profit purposes,
# without fee, and without a written agreement is hereby granted,
# provided that the above copyright notice, this paragraph and the
# following three paragraphs appear in all copies.
#
# Permission to make commercial use of this software may be obtained
# by contacting:
#
# USC Stevens Center for Innovation
# University of Southern California
# 1150 S. Olive Street, Suite 2300
# Los Angeles, CA 90115, USA
#
# This software program and documentation are copyrighted by The
# University of Southern California. The software program and
# documentation are supplied "as is", without any accompanying
# services from USC. USC does not warrant that the operation of the
# program will be uninterrupted or error-free. The end-user
# understands that the program was developed for research purposes and
# is advised not to rely exclusively on the program for any reason.
#
# IN NO EVENT SHALL THE UNIVERSITY OF SOUTHERN CALIFORNIA BE LIABLE TO
# ANY PARTY FOR DIRECT, INDIRECT, SPECIAL, INCIDENTAL, OR
# CONSEQUENTIAL DAMAGES, INCLUDING LOST PROFITS, ARISING OUT OF THE
# USE OF THIS SOFTWARE AND ITS DOCUMENTATION, EVEN IF THE UNIVERSITY
# OF SOUTHERN CALIFORNIA HAS BEEN ADVISED OF THE POSSIBILITY OF SUCH
# DAMAGE. THE UNIVERSITY OF SOUTHERN CALIFORNIA SPECIFICALLY DISCLAIMS
# ANY WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE. THE SOFTWARE PROVIDED

#!/usr/bin/env python3

import argparse
from .gsec_train import train
from .gsec_apply import apply_

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('command',
                        help='Options: gsec train, gsec predict, ...') 
    parser.add_argument('--pos-strat', dest='pos_strat', required=True,
                        help='strategy for positive set')
    parser.add_argument('--pos-org', dest='pos_org', required=True,
                        help='organism for positive set')
    parser.add_argument('--neg-strat', dest='neg_strat', required=True,
                        help='strategy for negative set')
    parser.add_argument('--neg-org', dest='neg_org', required=True,
                        help='organism for negative set')
    parser.add_argument('-k', '--k-value', dest='max_k', required=False,
                        type=int, help='maximum size of k-mers')
    parser.add_argument('-l', '--limit-reads', dest='limit_reads', required=False, 
                        type=int, help='number of reads to use')
    parser.add_argument('-n', '--num-samples', dest="num_samples", required=False,
                        type=int, help='number of samples to count from each set')
    parser.add_argument('-f', '--fastq', dest="fastq", required=False,
                        help='file to apply model to')
    args = parser.parse_args()
    
    if args.command=="train":
        if args.pos_strat and args.pos_org and args.neg_strat \
         and args.neg_org and args.max_k and args.limit_reads \
         and args.num_samples:
            train(args.pos_strat, args.pos_org, args.neg_strat,
                  args.neg_org, args.max_k, args.limit_reads,
                  args.num_samples)
        else:
            parser.error("command gsec train requires:\n\t pos-strat," +
                         " pos-org, neg-strat, neg-org, k-value, num-samples")
    elif args.command=="apply":
        if args.pos_strat and args.pos_org and args.neg_strat \
         and args.neg_org and args.fastq:
            apply_(args.pos_strat, args.pos_org, args.neg_strat,
                    args.neg_org, args.fastq)
        else:
            parser.error("arguments not correct")
    else:
        parser.error("Available commands:\n\ttrain\n\tapply")


    return 0


if __name__ == '__main__':
    main()
