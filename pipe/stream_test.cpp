#include <iostream>
#include <string>

using std::string;
using std::cin;
using std::cout;
using std::endl;
using std::getline;
using std::stoi;

int main(int argc, char** argv)
{	
	int limit;
	if (argc == 2)
		limit = stoi(argv[1]);
	else
		limit = 5;
	string s;
	int num_lines = 0;
	int num_counted = 0;

	cout << "***** starting program ******" << endl;
	
	while (getline(cin,s) && num_counted < limit)
	{
		if (num_lines % 4 == 1)
		{
			cout << s << endl;
			++num_counted;
		}
		++num_lines;
	}

	return 0;
}
