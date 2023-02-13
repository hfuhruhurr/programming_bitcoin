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