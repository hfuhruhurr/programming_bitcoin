from unittest import TestCase

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
		# num = (self.num * (other.num**(self.prime - 2) % self.prime)) % self.prime  # WTF does this not work???
		num = (self.num * pow(other.num, self.prime - 2, self.prime)) % self.prime
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