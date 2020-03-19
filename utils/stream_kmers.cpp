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
#include <set>
#include <sstream>

using std::string;
using std::vector;
using std::cin;
using std::cout;
using std::endl;
using std::begin;
using std::end;
using std::set;

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

// reference code to iterator through vector matrix
  // for (auto it = f.begin(); it != f.end(); ++it) {
  //     for (auto jt = it->begin(); jt != it->end(); ++jt) {
  //       cout << *jt;
  //     }
  //   cout << endl;
  // } 

// checks if all frequencies have converged 
// convergence threshold currently set to 1e-10 
bool check_converge(std::vector<std::vector<double>> &f, std::vector<std::vector<double>> &prev) {
  double diff;

  for (unsigned int i = 0; i < f.size(); i++) {
    for (unsigned int j = 0; j < f[i].size(); j++) {
      diff = std::abs(f[i][j] - prev[i][j]);
      if (diff > 1*pow(10,-10)) {
        return false; 
      }
    }  
  }
  return true;
}

int main(int argc, const char * const argv[]) {

  try {

    if (argc != 3 && argc != 4) {
      std::cerr << "usage: " << argv[0] << " <max k-value> <limit> (optional)<k-value list as file>" << endl;
      return 1; // for bad command format
    }

    const size_t k_value(atoi(argv[1])); // need error checking here
    const size_t limit(atoi(argv[2])); // need error checking here

    std::set<int> k_vals;

    // creates set of k values the program will count kmers of
    // if specific set of k_values
    if (argc == 4) {
      std::ifstream ifile_kmers(argv[3]);
      string k_val_in;
      while (getline(ifile_kmers, k_val_in)) {
        std::stringstream ss;
        ss << k_val_in;
        int k_val;
        ss >> k_val;
        if (ss.fail()) {
          std::cerr << "k-value file should contain integer values of k" << endl;
          return 1; // bad input format
        }
        k_vals.insert(k_val);
      }
    }
    else {
      // if no file passed in, will run 1-k_value
      for (unsigned int i = 1; i <= k_value; ++i) {
        k_vals.insert(i);
      }
    }

    // stores list of pointers to each counter, one for each k value
    // also initializes vector matrices for counts + frequency tracking
    std::vector<kmer_counter*> the_counters;

    int index = 0;
    std::vector<std::vector<unsigned int>> counts(k_value);
    std::vector<std::vector<double>> freqs(k_value);
    std::vector<std::vector<double>> prev_freqs(k_value);

    for (std::set<int>::iterator it = k_vals.begin(); it != k_vals.end(); ++it) {
      the_counters.push_back(new kmer_counter(*it));

      counts[index].resize(the_counters[index]->n_kmers);
      freqs[index].resize(the_counters[index]->n_kmers);
      prev_freqs[index].resize(the_counters[index]->n_kmers);

      index++;
    }

    size_t lines_with_N = 0;


    string line;
    line.reserve(256);

    size_t line_count = 0;
    size_t reads_count = 0;

    bool converge = false;

    // begin reading fastq file
    while (getline(cin, line) && reads_count < limit && !converge) {

      if (line_count % 4 == 1) // only do "sequence" lines
        if (line.find('N') == string::npos) {

          // check convergence of frequencies
          if(reads_count > 1) {
            converge = check_converge(freqs, prev_freqs);
          }

          // update old frequencies
          for (unsigned int i = 0; i < freqs.size(); i++) {
            for (unsigned int j = 0; j < freqs[i].size(); j++) {
              prev_freqs[i][j] = freqs[i][j];
            }   
          }

          std::transform(begin(line), end(line), begin(line),
                         [](const char c) {return encoding[c];});
          
          // get counts for current line for each k value
          index = 0;
          for (std::vector<kmer_counter*>::iterator it = the_counters.begin(); it != the_counters.end(); ++it) {
            the_counters[index]->count_line(line, counts[index], freqs[index]);
            index++;
          }
          
	        ++reads_count;

          // update frequencies
          for (unsigned int i = 0; i < freqs.size(); i++) {
            for (unsigned int j = 0; j < freqs[i].size(); j++) {
              freqs[i][j] = (double(counts[i][j]) / the_counters[i]->total_kmers);
            }   
          }
        }
        else ++lines_with_N;
      line_count++;
    }

    // // output summary
    // cout << "final reads count: " << reads_count << endl;
    //   string end = "???";
    //   if (!getline(cin, line)) {
    //     end = "reached end of file";
    //   }
    //   else if (reads_count >= limit) {
    //     end = "reached limit";
    //   }
    //   else if(converge) {
    //     end = "kmer frequencies converged";
    // }
    // cout << "ended because: " << end << endl;
    
    // print total counts & frequencies
    index = 0;
    for (std::set<int>::iterator it = k_vals.begin(); it != k_vals.end(); ++it) {

      string k_mer_sequence;
      k_mer_sequence.resize(*it); // avoid re-allocating space

      // cout << "total " << (*it) << "-mers: " << the_counters[index]->total_kmers << endl;
      
      // for (size_t j = 0; j < the_counters[index]->n_kmers; ++j) {
      //   decode_kmer_inplace(index, j, k_mer_sequence);
      //   cout << k_mer_sequence << '\t' << counts[index][j] << '\n';
      // }

      // cout << endl;

      // cout << "frequencies: " << endl;
      for (size_t j = 0; j < the_counters[index]->n_kmers; ++j) {
        decode_kmer_inplace(index, j, k_mer_sequence);
        cout << k_mer_sequence << '\t' << freqs[index][j] << '\n';
      }
      // cout << endl;

      index++;
    }
    
    // output the additional info
    std::cerr << "total_reads: "
              << line_count/4 + ((line_count % 4) > 0) << endl
              << "invalid_reads: " << lines_with_N << endl;

    // clean up memory
    for (unsigned int i = 0; i < the_counters.size(); i++) {
      delete the_counters[i];
    } 
  }
  catch (const std::exception &e) {
    std::cerr << e.what() << std::endl;
    return 2; // exception thrown somewhere
  }
   
  exit(SIGUSR1); 
  return 0; // success
}
