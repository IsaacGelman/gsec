/*
  countkmers: A program to count kmers in FASTQ files, for a given
  value of k, and ignoring anything with an N

  Author: Andrew D Smith

  This software is Copyright (C) 2020 The University of Southern
  California. All Rights Reserved.

  Permission to use, copy, modify, and distribute this software and
  its documentation for educational, research and non-profit purposes,
  without fee, and without a written agreement is hereby granted,
  provided that the above copyright notice, this paragraph and the
  following three paragraphs appear in all copies.

  Permission to make commercial use of this software may be obtained
  by contacting:
  USC Stevens Center for Innovation
  University of Southern California
  1150 S. Olive Street, Suite 2300
  Los Angeles, CA 90115, USA

  This software program and documentation are copyrighted by The
  University of Southern California. The software program and
  documentation are supplied "as is", without any accompanying
  services from USC. USC does not warrant that the operation of the
  program will be uninterrupted or error-free. The end-user
  understands that the program was developed for research purposes and
  is advised not to rely exclusively on the program for any reason.

  IN NO EVENT SHALL THE UNIVERSITY OF SOUTHERN CALIFORNIA BE LIABLE TO
  ANY PARTY FOR DIRECT, INDIRECT, SPECIAL, INCIDENTAL, OR
  CONSEQUENTIAL DAMAGES, INCLUDING LOST PROFITS, ARISING OUT OF THE
  USE OF THIS SOFTWARE AND ITS DOCUMENTATION, EVEN IF THE UNIVERSITY
  OF SOUTHERN CALIFORNIA HAS BEEN ADVISED OF THE POSSIBILITY OF SUCH
  DAMAGE. THE UNIVERSITY OF SOUTHERN CALIFORNIA SPECIFICALLY DISCLAIMS
  ANY WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
  WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
  PURPOSE. THE SOFTWARE PROVIDED
*/

#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <exception>
#include <stdexcept>
#include <algorithm>
#include <csignal>
#include <math.h>

using std::string;
using std::vector;
using std::cin;
using std::cout;
using std::endl;
using std::begin;
using std::end;

// template here allows for different magnitudes of counts
struct kmer_counter {
  kmer_counter(const size_t the_k_value) {
    k = the_k_value;
    n_kmers = (1ul << 2*k);
    the_mask = n_kmers - 1;
    total_kmers = 0;
  }
  size_t k;
  size_t n_kmers;
  size_t the_mask;
  template <typename T, typename T2>
  void count_line(const string &line, vector<T> &counts, vector<T2> &freqs);
  size_t total_kmers;
};

template <typename T, typename T2>
void
kmer_counter::count_line(const string &line, vector<T> &counts, vector<T2> &freqs) {


  // start building up the kmer encoding
  string::const_iterator itr(begin(line));
  const string::const_iterator init_lim(itr + k - 1);
  size_t the_k_mer = 0;
  while (itr != init_lim) {
    the_k_mer <<= 2;
    the_k_mer |= *itr;
    ++itr;
  }

  // now get the full kmers and count them
  const auto lim(end(line));
  for (; itr != lim; ++itr) {
    the_k_mer <<= 2;
    the_k_mer |= *itr;
    ++counts[the_k_mer & the_mask];
    total_kmers++;
  }
}


char decoding[] = { 'A', 'C', 'G', 'T', 'N' };

static void
decode_kmer_inplace(const size_t k_value,
                    size_t the_k_mer,
                    string &k_mer_sequence) {
  // assumes the space for k_mer_sequence is exactly "k"
  auto idx = end(k_mer_sequence);
  const auto lim = begin(k_mer_sequence);

  while (idx != lim) {
    --idx;
    *idx = decoding[the_k_mer & 3ul];
    the_k_mer >>= 2;
  }
}

char encoding[] = {
	/*first*/                                              /*last*/
	/*  0*/ 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, /*  4*/
	/* 16*/ 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, /* 31*/
	/* 32*/ 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, /* 47*/
	/* 48*/ 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, /* 63*/
	/* 64*/ 4, 0, 4, 1, 4, 4, 4, 2, 4, 4, 4, 4, 4, 4, 4, 4, /* 79 (upper) */
	/* 80*/ 4, 4, 4, 4, 3, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, /* 95 (upper) */
	/* 96*/ 4, 0, 4, 1, 4, 4, 4, 2, 4, 4, 4, 4, 4, 4, 4, 4, /*111 (lower) */
	/*112*/ 4, 4, 4, 4, 3, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, /*127 (lower) */
};

bool check_converge(std::vector<double> &f, std::vector<double> &prev, bool print=false) {
  double diff = 0;
  for (int i = 0; i < 4; i++) {
    diff+= (f[i] - prev[i])*(f[i] - prev[i]);
  }
  if (print) cout << "diff: " << diff << " converged? " << (diff <= 2*pow(10,-5)) << endl;

  return diff <= 2*pow(10,-5);
}

int
main(int argc, const char * const argv[]) {

  try {

    if (argc != 3) {
      std::cerr << "usage: " << argv[0] << " <k-value> <limit>" << endl;
      return 1; // for bad command format
    }

    const size_t k_value(atoi(argv[1])); // need error checking here
    const size_t limit(atoi(argv[2])); // need error checking here

    kmer_counter the_counter(k_value);
    std::vector<unsigned int> counts(the_counter.n_kmers);
    size_t lines_with_N = 0;

    std::vector<double> freqs(the_counter.n_kmers);
    std::vector<double> prev_freqs(the_counter.n_kmers);

    string line;
    line.reserve(256);

    size_t line_count = 0;
    size_t reads_count = 0;

    bool converge = false;

    while (getline(cin, line) && reads_count < limit && !converge) {

      if (line_count % 4 == 1) // only do "sequence" lines
        if (line.find('N') == string::npos) {

          if(reads_count > 1) {
            converge = check_converge(freqs, prev_freqs);
          }

          for (unsigned int i = 0; i < 4; i++) {
            prev_freqs[i] = freqs[i];
          }

          

          std::transform(begin(line), end(line), begin(line),
                         [](const char c) {return encoding[c];});
          the_counter.count_line(line, counts, freqs);
	        ++reads_count;

          for (unsigned int i = 0; i < 4; i++) {
            freqs[i] = (double(counts[i]) / the_counter.total_kmers);
          }
        }
        else ++lines_with_N;
      line_count++;
    }

    string k_mer_sequence;
    k_mer_sequence.resize(k_value); // avoid re-allocating space

    cout << "total " << the_counter.total_kmers << endl;
    cout << "final reads count: " << reads_count << endl;
    string end = "???";
    if (!getline(cin, line)) {
      end = "reached end of file";
    }
    else if (reads_count >= limit) {
      end = "reached limit";
    }
    else if(converge) {
      end = "kmer frequencies converged";
    }
    cout << "ended because: " << end << endl;
    for (size_t i = 0; i < the_counter.n_kmers; ++i) {
      decode_kmer_inplace(k_value, i, k_mer_sequence);
      cout << k_mer_sequence << '\t' << counts[i] << '\n';
    }

    for (size_t i = 0; i < the_counter.n_kmers; ++i) {
      decode_kmer_inplace(k_value, i, k_mer_sequence);
      cout << k_mer_sequence << '\t' << freqs[i] << '\n';
    }

    // output the additional info
    std::cerr << "total_reads: "
              << line_count/4 + ((line_count % 4) > 0) << endl
              << "invalid_reads: " << lines_with_N << endl;
  }
  catch (const std::exception &e) {
    std::cerr << e.what() << std::endl;
    return 2; // exception thrown somewhere
  }
   
  exit(SIGUSR1); 
  return 0; // success
}
