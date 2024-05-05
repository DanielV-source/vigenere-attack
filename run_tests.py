import re
import sys
import time
from os import listdir
from os.path import isfile, join
import KeyWhisperers

TESTS_FOLDER = "test"

all_files = [f for f in listdir(TESTS_FOLDER) if isfile(join(TESTS_FOLDER, f))]

r = re.compile(".*_input")              # Input files
i_files = list(filter(r.match, all_files))

r = re.compile(".*_dictionary")         # Dictionary files
i_dicts = list(filter(r.match, all_files))

r = re.compile(".*_hash")               # Hash files
i_hashes = list(filter(r.match, all_files))

def test_kasiski():
    f_len = len(i_files)
    d_len = len(i_dicts)
    h_len = len(i_hashes)

    assert f_len == d_len == h_len, "Missing files! Make sure you have an input file, dictionary file and a hash file."

    original_argv = sys.argv
    results = []

    # Run tests
    for input_file, dictionary_file, hash_file in zip(i_files, i_dicts, i_hashes):
        sys.argv = ['KeyWhisperers.py', join(TESTS_FOLDER, input_file), join(TESTS_FOLDER, dictionary_file),
                    join(TESTS_FOLDER, hash_file)]
        try:
            start_time = time.time()
            KeyWhisperers.main()
            print(f"Time: {time.time() - start_time}")
            results.append(True)
        except Exception as e:
            print(f"{e}")
            results.append(False)

    sys.argv = original_argv

    assert all(results), "Some tests failed."

if __name__ == "__main__":
    test_kasiski()