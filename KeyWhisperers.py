"""

                - MUEI - CSAI -

Description:
    Vigenere attack script using Kasiski method

Authors:
    - Daniel Vicente Ramos (daniel.vicente.ramos@udc.es)
    - Daniel Silva Iglesias (daniel.silva.iglesias@udc.es)

"""

import collections
import hashlib
import sys
import time
from collections import defaultdict
from math import sqrt

import numpy as np
from numpy.fft import fft, ifft

# 'Ñ' included
SPN_FQS = np.array([
    0.11525, 0.02215, 0.04019, 0.05010, 0.12181, 0.00692, 0.01768, 0.00703, 0.06247,
    0.00493, 0.00011, 0.04967, 0.03157, 0.06712, 0.08683, 0.02510, 0.00877, 0.06871,
    0.07977, 0.04632, 0.02927, 0.01138, 0.00017, 0.00215, 0.01008, 0.00467, 0.00125
])

ENG_FQS = np.array([
    0.08167, 0.01492, 0.02782, 0.04253, 0.12702, 0.02228, 0.02015, 0.06094, 0.06966,
    0.00153, 0.00772, 0.04025, 0.02406, 0.06749, 0.07507, 0.01929, 0.00095, 0.05987,
    0.06327, 0.09056, 0.02758, 0.00978, 0.02361, 0.00150, 0.01974, 0.00074
])

FRN_FQS = np.array([
    0.07636, 0.00901, 0.03260, 0.03369, 0.14715, 0.01066, 0.00866, 0.00737, 0.07529,
    0.00613, 0.00074, 0.05456, 0.02968, 0.07095, 0.05796, 0.02521, 0.01362, 0.06693,
    0.07948, 0.07244, 0.06311, 0.01838, 0.00049, 0.00427, 0.00128, 0.00326
])

PARTITION_LENGTH = 10


def create_cipher_map(alphabet):
    """ Maps characters to indexes and indexes to characters. """
    return {char: idx for idx, char in enumerate(alphabet)}, {idx: char for idx, char in enumerate(alphabet)}


def repeated_seq_pos(text, seq_len):
    """ Identifies repeated sequences of a given length in the text. """
    seq_pos = defaultdict(list)
    for i in range(len(text) - seq_len + 1):
        seq = text[i:i + seq_len]
        seq_pos[seq].append(i)

    return {seq: pos for seq, pos in seq_pos.items() if len(pos) > 1}


def calculate_fqs(text, char_to_index, d_length, i_length):
    """ Calculates the frequency of each character. """
    indices = np.fromiter((char_to_index.get(char) for char in text if char in char_to_index), dtype=int)
    fqs = np.bincount(indices, minlength=d_length)
    return fqs / i_length


def find_best_shift(fqs, lang_fqs):
    """ Use FFT to find the best shift efficiently with cross-correlation. """
    correlation = ifft(fft(fqs) * np.conj(fft(lang_fqs))).real
    return np.argmax(correlation)


def get_key(ciphertext, lang_fqs, char_to_index, alphabet, d_length, k_length):
    """ Finds the decryption key for the Vigenère cipher. """
    key = []
    segments = [ciphertext[i::k_length] for i in range(k_length)]
    fqs_list = [calculate_fqs(seg, char_to_index, d_length, len(seg)) for seg in segments]

    for fqs in fqs_list:
        shift = find_best_shift(fqs, lang_fqs)
        key.append(alphabet[shift])

    return ''.join(key)


def get_spacings(positions):
    """ Calculates the differences between positions. """
    return [positions[i + 1] - positions[i] for i in range(len(positions) - 1)]


def get_factors(number):
    """ Return the set of factors of the given number. """
    factors = set()
    for i in range(1, int(sqrt(number)) + 1):
        if number % i == 0:
            factors.add(i)
            factors.add(number // i)
    return list(factors)  # Return a list to simplify further processing


def candidate_key_lengths(factor_lists, max_key_len):
    """ Determine the most probable key lengths based on factor frequencies. """
    all_factors = [factor for sublist in factor_lists for factor in sublist if factor <= max_key_len]
    factor_freq = collections.Counter(all_factors)
    return sorted(factor_freq, key=factor_freq.get, reverse=True)


def find_key_length(ciphertext, seq_len, max_key_len):
    """ Estimate the most probable key length using the Kasiski Examination method. """
    rsp = repeated_seq_pos(ciphertext, seq_len)
    factor_lists = []
    for positions in rsp.values():
        spacings = get_spacings(positions)
        for space in spacings:
            factors = get_factors(space)
            factor_lists.append(factors)
    if not factor_lists:
        return None
    return candidate_key_lengths(factor_lists, max_key_len)


def vigenere_decrypt(ciphertext, key, char_to_index, index_to_char, d_length, k_length):
    """ Decrypts text using the Vigenère cipher. """
    key_indices = [char_to_index[k] for k in key]

    decrypted_text = [
        index_to_char[(char_to_index[char] - key_indices[i % k_length]) % d_length] if char in char_to_index else char
        for i, char in enumerate(ciphertext)
    ]

    return ''.join(decrypted_text)


def get_hash(text):
    """ Returns SHA-256 hash of text. """
    return hashlib.new('sha256', text.encode('utf-8')).hexdigest()


def compare_distributions(fqs, lang_fps):
    """ Compares two frequency distributions. """
    if fqs.size != lang_fps.size:
        return -1
    return np.linalg.norm(fqs - lang_fps)


def compute_fqs(text, alphabet):
    """ Computes normalized letter frequencies. """
    char_to_index = {ch: idx for idx, ch in enumerate(alphabet)}
    fqs = np.zeros(len(alphabet))

    for char in text:
        if char in char_to_index:
            fqs[char_to_index[char]] += 1

    total = fqs.sum()
    if total > 0:
        fqs /= total

    return fqs


def cosine_similarity(fqs1, fqs2):
    """ Calculates the cosine similarity between two distributions. """
    return np.dot(fqs1, fqs2) / (np.linalg.norm(fqs1) * np.linalg.norm(fqs2))


def get_lang(text, alphabet, lang_fqs):
    """ Determines the most likely language by comparing frequency distributions. """
    text_fqs = compute_fqs(text, alphabet)
    max_similarity = 0
    best_lang = None

    for lang, fqs in lang_fqs.items():
        similarity = cosine_similarity(text_fqs, fqs)
        if similarity > max_similarity:
            max_similarity = similarity
            best_lang = lang

    return best_lang, lang_fqs[best_lang]


def main():
    global PARTITION_LENGTH

    #start_time = time.time()

    n_args = len(sys.argv) - 1

    if n_args < 3 or n_args > 3:
        print("Usage: python KeyWhisperers.py [input_file] [dictionary] [hash]\n"
              "Example: python KeyWhisperers.py test/JdP_001_input test/JdP_001_dictionary test/JdP_001_hash")
        return

    lang_fqs = {
        'ENG': ENG_FQS,
        'FRN': FRN_FQS
    }

    with open(file=sys.argv[1], mode='r', encoding='utf-8') as f:
        i_file = f.readline().upper()
    i_length = len(i_file)

    with open(file=sys.argv[2], mode='r', encoding='utf-8') as f:
        d_file = f.readline().upper()
    d_length = len(d_file)

    with open(file=sys.argv[3], mode='r', encoding='utf-8') as f:
        h_file = f.readline()

    char_to_index, index_to_char = create_cipher_map(d_file)

    if "Ñ" in d_file or "Ñ" in i_file:
        best_lang = 'SPN'
        best_fqs = SPN_FQS
        alphabet = "ABCDEFGHIJKLMNÑOPQRSTUVWXYZ"
    else:
        best_lang, best_fqs = get_lang(i_file, d_file, lang_fqs)
        alphabet = d_file

    current_partition = 1
    max_key_length = PARTITION_LENGTH
    keys = []
    while current_partition <= i_length:
        key_lengths = find_key_length(i_file, current_partition, max_key_length)
        if key_lengths is None:
            break

        for k_length in key_lengths:
            key = get_key(i_file, best_fqs, char_to_index, alphabet, d_length, k_length)
            if key in keys:
                break
            keys.append(key)
            decrypted_text = vigenere_decrypt(i_file, key, char_to_index, index_to_char, d_length, k_length)
            if get_hash(decrypted_text) == h_file:
                # print("------------------------------------------------------------------")
                print(f"Key: {key}.")
                # print(f"Execution time: {time.time() - start_time}")
                # print(f"Language estimated: {lang}")
                # print(f"Alphabet: {alphabet}")
                # print(f"Encrypted Text: {i_file[:50]}...")
                # print(f"Decrypted Text: {decrypted_text[:50]}...")
                # print("------------------------------------------------------------------")
                return
        current_partition += PARTITION_LENGTH
        max_key_length += PARTITION_LENGTH

    print("Key cannot be found or key is equal to text.")


if __name__ == "__main__":
    main()
