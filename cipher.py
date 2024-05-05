import re
import numpy as np
import hashlib
from os import listdir
from os.path import isfile, join

char_to_index = {}
index_to_char = {}

TESTS_FOLDER = "test"


def create_cipher_map(alphabet):
    global char_to_index, index_to_char

    char_to_index = {char: idx for idx, char in enumerate(alphabet)}
    index_to_char = {idx: char for idx, char in enumerate(alphabet)}


def encrypt_vigenere(text, key, alphabet):
    global char_to_index, index_to_char
    kUp = key.upper()
    tUp = text.strip().upper()
    key_indices = np.array([char_to_index[char] for char in kUp if char in char_to_index])
    text_indices = np.array([char_to_index[char] for char in tUp if char in char_to_index])

    repeated_key = np.resize(key_indices, text_indices.size)
    encrypted_indices = (text_indices + repeated_key) % len(alphabet)
    encrypted_text = ''.join(index_to_char[idx] for idx in encrypted_indices)

    return encrypted_text


def decrypt_vigenere(ciphertext, key, alphabet):
    global char_to_index, index_to_char
    n = len(ciphertext)
    kUp = key.upper()
    tUp = ciphertext.strip().upper()
    key_indices = np.array([char_to_index[char] for char in kUp if char in char_to_index])
    cipher_indices = np.array([char_to_index[char] for char in tUp if char in char_to_index])

    repeated_key = np.resize(key_indices, n)
    decrypted_indices = (cipher_indices - repeated_key) % len(alphabet)
    decrypted_text = ''.join(index_to_char[idx] for idx in decrypted_indices)

    return decrypted_text


def hash_sha256(input_string):
    return hashlib.new('sha256', input_string.encode('utf-8')).hexdigest()


def main():
    global TESTS_FOLDER

    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

    create_cipher_map(alphabet)
    ciphertext = """
    MARK LIVES IN A SMALL TOWN SURROUNDED BY FORESTS AND LAKES HE ENJOYS HIKING THROUGH THE WOODS AND KAYAKING ON THE WATER 
    EVERY WEEKEND HIS DOG BUDDY JOINS HIM ON THESE ADVENTURES THEY SPEND HOURS EXPLORING THE NATURAL TRAILS AND WATCHING 
    WILDLIFE IT GIVES MARK A SENSE OF PEACE AND CONNECTS HIM TO NATURE BUDDY SEEMS TO LOVE THESE TRIPS JUST AS MUCH AS MARK 
    DOES TOGETHER THEY HAVE MADE COUNTLESS MEMORIES IN THE GREAT OUTDOORS
    """
    key = "SUNLIGHT"

    encrypted = encrypt_vigenere(ciphertext,
                                 key,
                                 alphabet)

    decrypted = decrypt_vigenere(encrypted, key, alphabet)

    h_text = hash_sha256(decrypted)

    all_files = [f for f in listdir(TESTS_FOLDER) if isfile(join(TESTS_FOLDER, f))]

    r = re.compile(".*_input")  # Input files
    num = len(list(filter(r.match, all_files)))+1

    if num < 10:
        num = "00" + str(num)
    elif num < 100:
        num = "0" + str(num)

    with open(f"{TESTS_FOLDER}/JdP_{num}_input", "w", buffering=2048) as f:
        f.write(encrypted)
    with open(f"{TESTS_FOLDER}/JdP_{num}_dictionary", "w", buffering=2048) as f:
        f.write(alphabet)
    with open(f"{TESTS_FOLDER}/JdP_{num}_hash", "w", buffering=2048) as f:
        f.write(h_text)
    print(f"Encrypted: {encrypted} \nDecrypted: {decrypted} \nHASH: {h_text}")


if __name__ == "__main__":
    main()
