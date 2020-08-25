import copy

class Entry:
	def __init__(self, value, i, j):
		self.i = i 
		self.j = j 
		self.assigned = []
		if value != 0:
			self.value = value
			self.possibilities = []
			self.assigned.append(value)
		else:
			self.value = 0
			self.possibilities = list(range(1, 10))

	def __contains__(self, value):
		return value in self.possibilities

	def __eq__(self, other):
		return (self.i == other.i) and (self.j == other.j)

	def __ne__(self, other):
		return not self == other

	def __repr__(self):
		return str(self.value)	

	def Reset(self, possibilities):
		self.possibilities = list(possibilities)
		self.assigned = []
	
	def Remove(self, value):
		if value in self.possibilities:
			self.possibilities.remove(value)

	def Update(self, value):
		if value != 0:	
			self.value = value
			self.possibilities = []
			self.assigned.append(value)

	def AddPossibility(self, value):
		if value not in self.possibilities:
			if value not in self.assigned:
				self.possibilities.append(value)
				self.possibilities = sorted(self.possibilities)

	def Restore(self, possibilities):
		self.value = 0
		self.possibilities = [p for p in possibilities if p not in self.assigned]


class Board:
	def __init__(self, other=None):
		if other:
			self.spaces = other.spaces
		else:
			self.spaces = [[Entry(0, i, j) for i in range(9)] for j in range(9)]

	def Rows(self):
		return self.spaces

	def Columns(self):
		return [list(x) for x in zip(*self.spaces)]

	def Boxes(self):
		boxStarts = [(0,0), (0,3), (0, 6), (3, 0), (3, 3), (3, 6), (6, 0), (6, 3), (6, 6)]
		boxes = []
		for start in boxStarts:
			box = []
			for x in range(start[0], start[0]+3):
				for y in range(start[1], start[1]+3):
					box.append(self.spaces[x][y])
			boxes.append(box)
		return boxes

	def FindRow(self, i, j):
		return self.spaces[i]

	def FindColumn(self, i, j):
		return [list(x) for x in zip(*self.spaces)][j]

	def FindBox(self, i, j):
		boxStarts = [(0,0), (0,3), (0, 6), (3, 0), (3, 3), (3, 6), (6, 0), (6, 3), (6, 6)]
		box = []
		for start in boxStarts:
			if (i >= start[0] and i <= start[0]+2):
				if (j >= start[1] and j <= start[1]+2):			
					for x in range(start[0], start[0]+3):
						for y in range(start[1], start[1]+3):
							box.append(self.spaces[x][y])
					return box

	def FindEntry(self, i, j):
		return self.spaces[i][j]

	def FindNeighbours(self, entry):
		box = self.FindBox(entry.j, entry.i)
		row = self.FindRow(entry.j, entry.i)
		col = self.FindColumn(entry.j, entry.i)
		return row + col + box

	def Remove(self, i, j, value):
		self.spaces[i][j].Remove(value)

	def Restore(self, entry):
		self.RestoreConstraints(entry)

	def Update(self, i, j, value):
		self.spaces[i][j].Update(value)
		self.PropogateConstraints(self.spaces[i][j])

	def Reset(self, entry):
		constraints = self.FindNeighbours(entry)
		possibilities = list(range(1, 10))
		if entry.value in possibilities:
			possibilities.remove(entry.value)

		for c in constraints:
			if c.value != 0:
				if c != entry and c.value in possibilities:
					possibilities.remove(c.value)

		entry.Reset(possibilities)
 
	def LeastConstrainingValue(self, entry):
		constraints = self.FindNeighbours(entry)

		maxTotal = 100
		maxValue = None

		for p in entry.possibilities:
			if not self.ForwardCheck(entry, p):
				entry.Remove(p)
				continue
				
			total = 0
			for c in constraints:
				if p in c.possibilities and c != entry:
					total += 1

			if total < maxTotal:
				maxTotal = total
				maxValue = p

		return maxValue

	def MostConstrainedEntry(self):
		most = self.spaces[0][0]
		for i in range(0, 9):
			for j in range(0, 9):
				entry = self.spaces[i][j]
				if not entry.possibilities and entry.value == 0:
					return entry
				if not most.possibilities or (len(entry.possibilities) > 0 and len(entry.possibilities) < len(most.possibilities)):
					most = entry

		mostConstrained = [most]
		for i in range(0, 9):
			for j in range(0, 9):
				entry = self.spaces[i][j]
				if entry not in mostConstrained:
					if (len(entry.possibilities) > 0 and len(entry.possibilities) == len(most.possibilities)):
						mostConstrained.append(entry)

		if len(mostConstrained) <= 1:
			return most
		else:
			best = mostConstrained[0]
			leastNeighbours = 0
			for e in mostConstrained:
				constraints = self.FindNeighbours(e)

				unassignedNeighbours = 0
				for c in constraints:	
					if c != e and c.value == 0:
						unassignedNeighbours += 1

				if unassignedNeighbours >= leastNeighbours:
					leastNeighbours = unassignedNeighbours
					best = e
			return best
			
	def PropogateConstraints(self, entry):
		constraints = self.FindNeighbours(entry)

		for e in constraints:
			e.Remove(entry.value)

	def RestoreConstraints(self, entry):
		possibilities = list(range(1, 10))
		possibilities.remove(entry.value)
		constraints = self.FindNeighbours(entry)

		for square in constraints:
			if square == entry:
				continue
			if square.value != 0
				if square.value in possibilities:
					possibilities.remove(square.value)
			elif square.value == 0 and entry.value not in square.possibilities and entry.value not in square.assigned:
				nconstraints = self.FindNeighbours(square)
				inNeighbour = False
				for c in nconstraints:
					if c != entry and c.value == entry.value:
						inNeighbour = True
				if not inNeighbour:
					square.AddPossibility(entry.value)
		entry.Restore(possibilities)

	def IsComplete(self):
		for row in self.Rows():
			l = [i.value for i in row]
			if not AllDiff(l):
				return False
		for col in self.Columns():
			l = [i.value for i in col]
			if not AllDiff(l):
				return False
		for box in self.Boxes():
			l = [i.value for i in box]
			if not AllDiff(l):
				return False
		return True

	def IsValid(self):
		for row in self.Rows():
			l = [i.value for i in row]
			if not ValidRBC(l):
				return False
			for s in row:
				if s.value == 0:
					if len(s.possibilities) == 0:
						return False
		for col in self.Columns():
			l = [i.value for i in col]
			if not ValidRBC(l):
				return False
			for s in col:
				if s.value == 0:
					if len(s.possibilities) == 0:
						return False
		for box in self.Boxes():
			l = [i.value for i in box]
			if not ValidRBC(l):
				return False
			for s in box:
				if s.value == 0:
					if len(s.possibilities) == 0:
						return False
		return True

	def ForwardCheck(self, entry, value):
		testBoard = copy.deepcopy(self)
		testEntry = copy.deepcopy(entry)
		testBoard.Update(testEntry.j, testEntry.i, value)

		if not testBoard.IsValid():
			return False

		return True

	def __repr__(self):
		string = ""
		for i in range(0, 9):
			string += str(self.spaces[i]) + '\n'
		return string 

def ConstructBoard(filename, size):
	board = Board()
	data = open(filename).read().split('\n')
	for i in range(0, size):
		row = data[i].split()
		for j in range(0, size):
			entry = board.spaces[i][j]
			board.Update(i, j, int(row[j]))
	return board

def AllDiff(l):
	found = set()
	return not any(i in found or found.add(i) for i in l) and set(l) == set(range(1, 10))

def ValidRBC(l):
	found = list()
	for number in l:
		if number != 0:
			if number not in found:
				found.append(number)
			elif number in found:
				return False
	return True