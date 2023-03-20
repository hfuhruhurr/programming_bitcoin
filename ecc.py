from unittest import TestCase
from random import randint  ## NB: DO NOT USE FOR PRODUCTION...NOT RANDOM ENOUGH!!!
import hashlib 
import hmac 

from secret_helper import encode_base58_checksum, hash160

class FieldElement:

	def __init__(self, num, prime):
		if num >= prime or num < 0:
			error = f'The number {num} is not in the field range of [0..{prime - 1}]'
			raise ValueError(error)
		self.num = num
		self.prime = prime 

	def __repr__(self):
		return f'FieldElement_{self.prime}({self.num})'

	def __eq__(self, other):
		if other is None:
			return False
		return self.num == other.num and self.prime == other.prime

	def __ne__(self, other):
		# my solution
		# if other is None:
		# 	return True
		# return self.num != other.num or self.prime != other.prime

		# a better solution (since this should be the logical negation of ==)
		return (not self == other)

	def __add__(self, other):
		if self.prime != other.prime:
			error = f'Two different fields detected...no bueno.'
			raise TypeError(error)
		num = (self.num + other.num) % self.prime 
		return self.__class__(num, self.prime)  # need to return a FieldElement class, not an integer

	def __sub__(self, other):
		if self.prime != other.prime:
			error = f'Two different fields detected...no bueno.'
			raise TypeError(error)
		num = (self.num - other.num) % self.prime 
		return self.__class__(num, self.prime)  # need to return a FieldElement class, not an integer

	def __mul__(self, other):
		if self.prime != other.prime:
			error = f'Two different fields detected...no bueno.'
			raise TypeError(error)
		num = (self.num * other.num) % self.prime
		return self.__class__(num, self.prime)

	def __pow__(self, exponent):
		n = exponent % (self.prime - 1)  # force exponent in [0..prime-2]
		num = self.num**n % self.prime 
		return self.__class__(num, self.prime)

	def __truediv__(self, other):
		if self.prime != other.prime:
			error = f'Two different fields detected...no bueno.'
			raise TypeError(error)
		        # self.num and other.num are the actual values
        # self.prime is what we need to mod against
        # use fermat's little theorem:
        # self.num**(p-1) % p == 1
        # this means:
        # 1/n == pow(n, p-2, p)
		num = (self.num * pow(other.num, self.prime - 2, self.prime)) % self.prime  # This works.
		return self.__class__(num, self.prime)

	def __rmul__(self, scalar):
		num = (self.num * scalar) % self.prime 
		return self.__class__(num, self.prime)


class Point:
	def __init__(self, x, y, a, b):
		self.x = x  
		self.y = y 
		self.a = a 
		self.b = b  
		if self.x is None and self.y is None:  # this is how we define the 'point at infinity', aka the additive identity
			return  # won't pass the formula check below but it's a valid, albeit artificial, point on the curve
		if self.y**2 != self.x**3 + a * x + b:
			error = f'The point ({x}, {y}) is not on the curve, brah.'
			raise ValueError(error)


	def __eq__(self, other):
		same_point = self.x == other.x and self.y == other.y
		same_curve = self.a == other.a and self.b == other.b
		return same_point and same_curve

	def __ne__(self, other):
		return not (self == other)

	def __add__(self, other):
		if self.a != other.a or self.b != other.b:
			error = f'Point {self} is not on the same curve as Point {other}, chief.'
			raise TypeError(error)

		# Case 1: One of the points is the point at infinity.
		if self.x is None:   # self is the point at infinity so added this to other results in other (additive identity, bro)
			return other 

		if other.x is None:  # ibid
			return self 

		# Case 2: The two points lie in a vertical line (same x) but are distinct (different y).
		#         By definition, the sum is the point at infinity.
		if self.x == other.x and self.y != other.y:
			return self.__class__(None, None, self.a, self.b)  # remember to return a _class_, not just a number

		# Case 3: The two points lie in a vertical line (same x) but are not distinct.
		#         This can only happen when y = 0 --> vertical line tangent to curve
		#         NB: Instead of figuring out what 0 is for each type, just use 0 * self.x.
		if self == other and self.y == 0 * self.x:
			return self.__class__(None, None, self.a, self.b)
				
		# Case 4: The two points do not lie in a vertical line (different x).
		#         In this case, we need to find where the line connecting the two points intersects the curve.
		if self.x != other.x:
			slope = (other.y - self.y) / (other.x - self.x)
			x = slope**2 - self.x - other.x
			y = slope * (self.x - x) - self.y
			return self.__class__(x, y, self.a, self.b)
				
		# Case 5: The two points are the same.
		#         In this case, we need to find where the tangent line intersects the curve.
		if self == other:
			slope = (3 * self.x**2 + self.a)/(2 * self.y)
			x = slope**2 - 2 * self.x
			y = slope * (self.x - x) - self.y
			return self.__class__(x, y, self.a, self.b)


	def __rmul__(self, scalar):
		coef = scalar
		current = self 
		result = self.__class__(None, None, self.a, self.b)
		while coef:
			if coef & 1:
				result += current
			current += current
			coef >>= 1  # bit-shift to the right
		return result


	def __repr__(self):
		if self.x is None:
			return 'Point(infinity)'
		elif isinstance(self.x, FieldElement):
			return f'Point({self.x.num},{self.y.num})_{self.a.num}_{self.b.num} FieldElement({self.x.prime})'
		else:
			return f'Point({self.x},{self.y})_{self.a}_{self.b})'


class ECCTest(TestCase):
	def test_on_curve(self):
		prime = 223
		a = FieldElement(0, prime)
		b = FieldElement(7, prime)
		valid_puntas = ((192, 105), (17, 56), (1, 193))
		invalid_puntas = ((200, 199), (42,99))
		for x_raw, y_raw in valid_puntas:
			x = FieldElement(x_raw, prime)
			y = FieldElement(y_raw, prime)
			Point(x, y, a, b)
		for x_raw, y_raw in invalid_puntas:
			x = FieldElement(x_raw, prime)
			y = FieldElement(y_raw, prime)
			with self.assertRaises(ValueError):
				Point(x, y, a, b)


	def test_add(self):
		prime = 223
		a = FieldElement(0, prime)
		b = FieldElement(7, prime)

		pairs = [
			(170, 142, 60, 139),
			(47, 71, 17, 56),
			(143, 98, 76, 66)
		]

		for pair in pairs:
			x1 = FieldElement(pair[0], prime)
			y1 = FieldElement(pair[1], prime)
			x2 = FieldElement(pair[2], prime)
			y2 = FieldElement(pair[3], prime)
			p1 = Point(x1, y1, a, b)
			p2 = Point(x2, y2, a, b)


# some known constants for the secp256k1, Bitcoin's cryptographic elliptic curve
A = 0
B = 7
P = 2**256 - 2**32 - 977
N = 0xfffffffffffffffffffffffffffffffebaaedce6af48a03bbfd25e8cd0364141


class S256FieldElement(FieldElement):  # why omit the "Element" part, Jimmy???

	def __init__(self, num, prime=None):
		super().__init__(num, prime=P)

	def __repr__(self):
		return f'{self.num:x}'.zfill(64)

	def sqrt(self):
		return self**((P + 1) // 4)


class S256Point(Point):
	def __init__(self, x, y, a=None, b=None):
		a, b = S256FieldElement(A), S256FieldElement(B)
		if type(x) == int:
			super().__init__(S256FieldElement(x), S256FieldElement(y), a, b)
		else:
			super().__init__(x, y, a, b)  # we're not S256FieldElement-ifying x & y in case we init the pt @ inf.

	def __repr__(self):
		if self.x is None:
			return 'S256Point(infinity)'
		else:
			return f'S256Point({self.x}, {self.y})'

	def __rmul__(self, scalar):
		coef = scalar % N 
		return super().__rmul__(coef)
	
	def verify(self, sig_hash, sig):
		s_inv = pow(sig.s, N -2, N)  # curtesy Fermat's Little Theorem
		u = sig_hash * s_inv % N
		v = sig.r * s_inv % N 
		expected_r = u * G + v * self 
		return expected_r == sig.r 
	
	def sec(self, compressed=True):
		'''returns the serialized binary version of the SEC format, big-endian-style'''
		x_big_endian = self.x.num.to_bytes(32, 'big')
		if compressed:
			if self.y.num % 2 == 0:
				prefix_byte = b'\x02'
			else:
				prefix_byte = b'\x03'
			return prefix_byte + x_big_endian
		else:
			prefix_byte = b'\x04'
			y_big_endian = self.y.num.to_bytes(32, 'big')
			return prefix_byte + x_big_endian + y_big_endian
		
	@classmethod
	def parse(self, sec_bin):
		'''returns a Point object from a SEC binary (note: not hex)'''
		prefix = sec_bin[0] 
		x_coordinate = int.from_bytes(sec_bin[1:33], 'big')
		
		if prefix == 4:  # ie, we're given both the x and y (uncompressed format)
			y_coordinate = int.from_bytes(sec_bin[33:65], 'big')
			return S256Point(x=x_coordinate, y=y_coordinate)
		
		# if we've reached this point, y is not given, just the x and the parity
		# but we can solve for y since the equation is y^2 = x^3 + 7
		rhs = S256FieldElement(x_coordinate)**3 + S256FieldElement(B)  # rhs := Right Hand Side
		y_candidate = rhs.sqrt()

		if y_candidate % 2 == 0:                                    # if the candidate is even
			if prefix == 2:                                         # and we know the y should be even
				y_solution = y_candidate                            # then the solution is the candidate
			else:
				y_solution = S256FieldElement(P - y_candidate.num)  # ow, it's the other possible candidate
		else:
			if prefix == 3:
				y_solution = y_candidate
			else:
				y_solution = S256FieldElement(P - y_candidate.num)

		return S256Point(S256FieldElement(x_coordinate), y_solution)

	def hash160(self, compressed=True):
		return hash160(self.sec(compressed))
	
	def address(self, compressed=True, testnet=False):
		'''returns the address string'''
		h160 = self.hash160(compressed)
		if testnet:
			prefix = b'\x6f'
		else:
			prefix = b'\x00'
		return encode_base58_checksum(prefix + h160)
	

# now that S256Point() is defined, we can add one more known constant, the generator point
G = S256Point(0x79be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798, 0x483ada7726a3c4655da4fbfc0e1108a8fd17b448a68554199c47d08ffb10d4b8)


class Signature:

	def __init__(self, r, s):
		self.r = r
		self.s = s 

	def __repr__(self):
		return f'Signature({self.r},{self.s})'
	
	def der(self):
		der_prefix = 0x30
		r_marker = 0x02
		s_marker = 0x02

		r = self.r.to_bytes(32, 'big').lstrip(b'\x00')
		if r[0] & 0x80:  # bitwise AND op to look for the most sign. bit set to 1 --> negative #
			r = b'\x00' + r
		r_len = len(r)
		sig = bytes([r_marker, r_len]) + r

		s = self.s.to_bytes(32, 'big').lstrip(b'\x00')
		if s[0] & 0x80:
			s = b'\x00' + s
		s_len = len(s)
		sig += bytes([s_marker, s_len]) + s

		sig_len = len(sig)

		return bytes([der_prefix, sig_len]) + sig


class PrivateKey:

	def __init__(self, secret):
		self.secret = secret
		# self.point = secret * G  # this is the public key, introduced here for convenience
		self.public_key = secret * G  

	def hex(self):
		return f'{self.secret:x}'.zfill(64)
	
	def sign(self, z):
		# k = randint(0, N)  # not to be trusted in production
		k = self.deterministic_k(z)  # accepted way to get a unique k for each signature 
		r = (k * G).x.num 
		k_inv = pow(k, N - 2, N)
		s = (z + r * self.secret) * k_inv % N 
		if s > N/2:
			s = N - s 
		return Signature(r, s) 
	
	def deterministic_k(self, z):
		k = b'\x00' * 32
		v = b'\x01' * 32 
		if z > N:
			z -= N 
		z_bytes = z.to_bytes(32, 'big')
		secret_bytes = self.secret.to_bytes(32, 'big')
		s256 = hashlib.sha256 
		k = hmac.new(k, v + b'\x00' + secret_bytes + z_bytes, s256).digest()
		v = hmac.new(k, v, s256).digest()
		k = hmac.new(k, v + b'\x01' + secret_bytes + z_bytes, s256).digest()
		v = hmac.new(k, v, s256).digest()
		while True:
			v = hmac.new(k, v, s256).digest()
			candidate = int.from_bytes(v, 'big')
			if candidate >= 1 and candidate < N:
				return candidate
			k = hmac.new(k, v + b'\x00', s256).digest()
			v = hmac.new(k, v, s256).digest()

	def wif(self, compressed=True, testnet=False):
		secret_bytes = self.secret.to_bytes(32, 'big')

		if testnet:
			prefix = b'\xef'
		else:
			prefix = b'\x80'

		if compressed:
			suffix = b'\x01'
		else:
			suffix = b''

		return encode_base58_checksum(prefix + secret_bytes + suffix)