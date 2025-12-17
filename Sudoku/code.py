import numpy as np
import copy
import random

# Load sudokus
sudoku = np.load("data/hard_puzzle.npy")

# Load solutions for demonstration
solutions = np.load("data/hard_solution.npy")
print()

# Print the first 9x9 sudoku...
print("First sudoku:")
print(sudoku[1], "\n")

# ...and its solution
print("Solution of first sudoku:")
print(solutions[1])

class PartialSudokuState:
    def __init__(self, grid=None):
        self.n = 9
        if grid is not None:
            self.grid = np.array(grid, dtype=int)   # Ensure it's a numpy array
        else:
            self.grid = np.zeros((9, 9), dtype=int)
        
        # use 0 for empty, but inside CSP handling, treat 0 as unassigned
        self.possible_values = [
            [
                set(range(1, 10)) if self.grid[row, col] == 0 else set([self.grid[row, col]])
                for col in range(9)
            ]
            for row in range(9)
        ]
        self.propagate_all()

    def is_goal(self):
        return np.all(self.grid != 0)   # grid is complete, no zeros

    def is_invalid(self):
        return any(len(self.possible_values[row][col]) == 0
                   for row in range(9) for col in range(9))

    def get_singleton_cells(self):
        return [
            (row, col)
            for row in range(9) for col in range(9)
            if self.grid[row, col] == 0 and len(self.possible_values[row][col]) == 1
        ]

    def get_possible_values(self, row, col):
        return list(self.possible_values[row][col])

    def propagate_all(self):
        changed = True
        while changed:
            changed = False
            for row in range(9):
                for col in range(9):
                    if self.grid[row, col] != 0:
                        continue
                    # Remove candidates based on peers
                    old_len = len(self.possible_values[row][col])
                    self.possible_values[row][col] -= set(self.get_peers_values(row, col))
                    if len(self.possible_values[row][col]) != old_len:
                        changed = True

    def get_peers_values(self, row, col):
        peers = set()
        # Row
        peers |= set(self.grid[row, c] for c in range(9) if self.grid[row, c] != 0)
        # Column
        peers |= set(self.grid[r, col] for r in range(9) if self.grid[r, col] != 0)
        # Box
        start_row, start_col = 3 * (row // 3), 3 * (col // 3)
        for r in range(start_row, start_row + 3):
            for c in range(start_col, start_col + 3):
                if self.grid[r, c] != 0:
                    peers.add(self.grid[r, c])
        return peers

    def set_value(self, row, col, value):
        state = copy.deepcopy(self)
        state.grid[row, col] = value
        state.possible_values[row][col] = set([value])
        state.propagate_all()
        return state

def pick_next_cell(state):
    min_len = 10
    target = None
    for row in range(9):
        for col in range(9):
            if state.grid[row, col] == 0 and len(state.possible_values[row][col]) < min_len:
                min_len = len(state.possible_values[row][col])
                target = (row, col)
    return target

def order_values(state, row, col):
    values = state.get_possible_values(row, col)
    random.shuffle(values)
    return values

def depth_first_search(partial_state):
    if partial_state.is_goal():
        return partial_state
    cell = pick_next_cell(partial_state)
    if not cell:
        return None
    row, col = cell
    for value in order_values(partial_state, row, col):
        new_state = partial_state.set_value(row, col, value)
        if new_state.is_goal():
            return new_state
        if not new_state.is_invalid():
            result = depth_first_search(new_state)
            if result and result.is_goal():
                return result
    return None

sudoku_grid = sudoku[1]

partial_state = PartialSudokuState(sudoku_grid)
goal = depth_first_search(partial_state)
if goal:
    goal = goal.grid.astype(float)
else:
    goal = np.full((9, 9), -1, dtype=int)
print("My solution")
print(goal)
