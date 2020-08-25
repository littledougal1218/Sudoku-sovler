import sys
import string 
import math
from readsudoku import *

def Solve(board):
	moves = []
	assignments = 0

	while assignments < 10000:
		if board.IsComplete():
			print("Finish!")
			break

		entry = board.MostConstrainedEntry()
		if not moves and assignments > 0:
			if len(entry.possibilities) == 0:
				print("Cannot be done.")
				assignments = 10000
				break

		if len(entry.possibilities) == 0:
			if entry.value == 0:
				badMove = moves.pop()
				board.Restore(badMove)
				if len(entry.possibilities) == 0:
					board.Reset(badMove)
				continue

		leastConstrainingValue = board.LeastConstrainingValue(entry)
		if not leastConstrainingValue or leastConstrainingValue == 0:
			badMove = moves.pop()
			board.Restore(badMove)
			if len(entry.possibilities) == 0:
				board.Reset(badMove)
			continue

		board.Update(entry.j, entry.i, leastConstrainingValue)
		moves.append(entry)
		assignments += 1

	return assignments

def main():
	if len(sys.argv) == 2:							
		filename = sys.argv[1]
	else:
		print("Wrong inputs!")

	board = ConstructBoard(filename, 9)
	print("Starting board:")
	print(board)
	assignments = Solve(board)
	print("Final board:")
	print(board)
	print("Total assignments made: {}".format(assignments))


main()