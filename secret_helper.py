# this code isn't in the text (at least not in the part where it's first referenced)
# it was discovered in the book's github repo

from unittest import TestSuite, TextTestRunner

import hashlib

BASE58_ALPHABET = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'

def run(test):
	suite = TestSuite()
	suite.addTest(test)
	TextTestRunner().run(suite)


def hash256(s):
	'''two rounds of sha256'''
	return hashlib.sha256(hashlib.sha256(s).digest()).digest()


def encode_base58(s: bytes):
	n_zero_bytes = 0
	for b in s: 
		if b == 0:
			n_zero_bytes += 1
		else:
			break
	prefix = '1' * n_zero_bytes

	num = int.from_bytes(s, 'big')
	result = ''
	while num > 0:
		num, mod = divmod(num, 58)
		result = BASE58_ALPHABET[mod] + result

	return prefix + result


def encode_base58_checksum(b: bytes):
	return encode_base58(b + hash256(b)[:4])


def hash160(s: bytes):
	'''sha256 followed by ripemd160'''
	return hashlib.new('ripemd160', hashlib.sha256(s).digest()).digest()

def little_endian_to_int(b: bytes) -> int:
    """Interpret a byte string as a little-endian integer."""
    return int.from_bytes(b, byteorder='little')
    
def int_to_little_endian(i: int) -> bytes:
    """Convert an integer to a little-endian byte string."""
    n_bytes_needed = (i.bit_length() + 7) // 8
    return i.to_bytes(n_bytes_needed, byteorder='little')

