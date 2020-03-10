#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <exception>
#include <stdexcept>
#include <algorithm>
#include <sstream>

using std::string;
using std::cin;
using std::cout;
using std::endl;
using std::getline;
using std::stoi;
using std::begin;
using std::end;
using std::vector;


// "char" can represent a numerical value of -128 to 127, so it's ok
// to have numbers in the table below
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
//         A     C           G (look up from letters to see the encoding)
//                  T

// any way this can be faster than the "transform" below?
static void
encode_line(string &line) {
  for (auto && i : line)
    i = encoding[i];
}

// template here allows for different magnitudes of counts
struct kmer_counter {
  kmer_counter(const size_t the_k_value) {
    k = the_k_value;
    n_kmers = (1ul << 2*k);
    the_mask = n_kmers - 1;
  }
  size_t k;
  size_t n_kmers;
  size_t the_mask;
  template <typename T>
  void count_line(const string &line, vector<T> &counts) const;
};

template <typename T>
void
kmer_counter::count_line(const string &line, vector<T> &counts) const {

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

int main(int argc, char** argv) {
try {	
	int limit;
	if (argc == 2)
		limit = stoi(argv[1]);
	else
		limit = 5;
	string s;
	int num_lines = 0;
	int num_counted = 0;

    int k_value = 2;

	cout << "***** starting program ******" << endl;

    kmer_counter the_counter(k_value);
    std::vector<unsigned int> counts(the_counter.n_kmers);
    size_t lines_with_N = 0;

    string line;
    line.reserve(256);

    size_t line_count = 0;
	
	while (getline(cin,line) && num_counted < limit)
	{
		if (num_lines % 4 == 1)
		{
			cout << line << endl;
			++num_counted;

            if (line.find('N') == string::npos) {
                std::transform(begin(line), end(line), begin(line),
                        [](const char c) {return encoding[c];});
                the_counter.count_line(line, counts);
            }
            else ++lines_with_N;
            line_count++;
		}
		++num_lines;
	}

	string k_mer_sequence;
    k_mer_sequence.resize(k_value); // avoid re-allocating space
    for (size_t i = 0; i < the_counter.n_kmers; ++i) {
      decode_kmer_inplace(k_value, i, k_mer_sequence);
      cout << k_mer_sequence << '\t' << counts[i] << '\n';
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
  return 0; // success
}
