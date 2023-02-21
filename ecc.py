from unittest import TestCase

class FieldElement:

	def __init__(self, num, prime):
		if num >= prime or num < 0:
			error = f'The number {num} is not in the field range of [0..{prime - 1}]'
			raise ValueError(error)
		self.num = num
		self.prime = prime 


	def __repr__(self):
		# return f'FieldElement_{self.prime}({self.num})'
		return f'{self.num}'


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


	def __truediv__(self, other):
		if self.prime != other.prime:
			error = f'Two different fields detected...no bueno.'
			raise TypeError(error)
		num = (self.num * other.num**(self.prime - 2)) % self.prime
		return self.__class__(num, self.prime)


	def __pow__(self, exponent):
		n = exponent % (self.prime - 1)  # force exponent in [0..prime-2]
		num = self.num**n % self.prime 
		return self.__class__(num, self.prime)


class Point:
	def __init__(self, x, y, a, b):
		self.a = a 
		self.b = b  
		self.x = x  
		self.y = y 
		if self.x is None and self.y is None:  # this is how we define the 'point at infinity', aka the additive identity
			return  # won't pass the formula check below but it's a valid, albeit artificial, point on the curve
		if self.y**2 != self.x**3 + a*x + b:
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

		# Case 1: One of the points is the point at infinity
		if self.a is None:   # self is the point at infinity so added this to other results in other (additive identity, bro)
			return other 

		if other.a is None:  # ibid
			return self 

		# Case 2: The two points lie in a vertical line
		if self.x == other.x and self.y != other.y:
			return self.__class__(None, None, self.a, self.b)  # remember to return a _class_, not just a number

		# Case 3: the points are not in a vertical line but are different
		if self.x != other.x:
			slope = (other.y - self.y)/(other.x - self.x)
			x3 = slope**2 - self.x - other.x
			y3 = slope*(self.x - x3) - self.y
			return self.__class__(x3, y3, self.a, self.b)
		
		# Case 4: the points are the same
		# if self == other and self.y == FieldElement(0, self.prime):  # THE CODE CHOKES ON THIS LINE
		if self == other and self.y == 0:
			return self.__class__(None, None, self.a, self.b)
		if self == other:
			# print(f'type(self) = {type(self)}')
			# print(f'type(self.y) = {type(self.y)}')
			# if self.y == FieldElement(0, self.prime):  # the sub-case where the tangent line is vertical --> slope is undefined and will choke trying to divide by 0
			# 	return self.__class__(None, None, self.a, self.b)  # by def'n, the point at infinity is the sum
			slope = (3*self.x**2 + self.a)/(2*self.y)
			x3 = slope**2 - 2*self.x
			y3 = slope*(self.x - x3) - self.y
			return self.__class__(x3, y3, self.a, self.b)


	def __repr__(self):
		return f'The point is ({self.x}, {self.y})_{self.a}_{self.b}'


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