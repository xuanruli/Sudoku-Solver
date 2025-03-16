import collections
import copy

############################################################
# Imports
############################################################

############################################################
# Sudoku Solver
############################################################


def sudoku_cells():
    res = []
    for r in range(9):
        for c in range(9):
            res.append((r, c))
    return res


def sudoku_arcs():
    res = set()
    for r in range(9):
        for c in range(9):
            for k in range(9):
                if k != r:
                    res.add(((r, c), (k, c)))
                if k != c:
                    res.add(((r, c), (r, k)))
            # find starting index of its corresponding box
            rb, rc = (r // 3) * 3, (c // 3) * 3
            for i in range(rb, rb+3):
                for j in range(rc, rc+3):
                    if (i, j) != (r, c):
                        res.add(((r, c), (i, j)))
    return res


def read_board(path):
    list_board = []
    with open(path, "r") as file:
        for line in file:
            row = list(line.strip())
            list_board.append(row)

    board = {}
    for r in range(9):
        for c in range(9):
            if list_board[r][c] == "*":
                board[(r, c)] = {1, 2, 3, 4, 5, 6, 7, 8, 9}
            else:
                board[(r, c)] = {int(list_board[r][c])}
    return board


class Sudoku(object):

    CELLS = sudoku_cells()
    ARCS = sudoku_arcs()

    def __init__(self, board):
        self.board = board

    def get_values(self, cell):
        return self.board[cell]

    def remove_inconsistent_values(self, cell1, cell2):
        set1 = self.get_values(cell1)
        set2 = self.get_values(cell2)
        N = len(set1)
        for v in set1.copy():
            if not any(v != w for w in set2):
                set1.discard(v)
        return len(set1) < N

    def infer_ac3(self):
        """find the option format like {x}, remove x from
        corresponding arcs"""
        q = collections.deque(self.ARCS)
        while q:
            cell1, cell2 = q.popleft()
            if self.remove_inconsistent_values(cell1, cell2):
                neighbor = ({x for (c, x) in self.ARCS if c == cell1} |
                            {c for (c, x) in self.ARCS if x == cell1})
                for cellz in neighbor:
                    if cellz != cell2:
                        q.append((cellz, cell1))

    def infer_improved(self):
        while True:
            old_state = ({cell: frozenset(self.board[cell])
                          for cell in self.CELLS})

            self.infer_ac3()
            changed_only = self.find_only_option()

            new_state = ({cell: frozenset(self.board[cell])
                          for cell in self.CELLS})
            if (not changed_only) and (new_state == old_state):
                break

    def find_only_option(self):
        changed = False
        for r in range(9):
            cell_list = [(r, c) for c in range(9)]
            changed |= self.change_only_option(cell_list)
        for c in range(9):
            cell_list = [(r, c) for r in range(9)]
            changed |= self.change_only_option(cell_list)
        for br in range(3):
            for bc in range(3):
                box_list = []
                for i in range(3):
                    for j in range(3):
                        box_list.append((br*3 + i, bc*3 + j))
                changed |= self.change_only_option(box_list)
        return changed

    def change_only_option(self, cell_list):
        changed = False
        for i in range(1, 10):
            possible_option = []
            for cell in cell_list:
                if i in self.board[cell]:
                    possible_option.append(cell)

            if len(possible_option) == 1:
                cell = possible_option[0]
                if self.board[cell] != {i}:
                    self.board[cell] = {i}
                    changed = True
        return changed

    def infer_with_guessing(self):
        self.infer_improved()
        if self.any_empty():
            # for certain bad guess, ac3 will remove
            # some cell's all possible value
            return False

        if self.is_solved():
            return True
        cell = self.select_unfilled_cell()
        guess_list = self.board[cell].copy()
        for guess in guess_list:
            self.board[cell] = {guess}
            saved_board = copy.deepcopy(self.board)
            if self.infer_with_guessing():
                return True
            else:
                # recover to original if guess not work
                self.board = saved_board
        return False

    def is_solved(self):
        for cell in self.CELLS:
            if len(self.board[cell]) != 1:
                return False
        return True

    def select_unfilled_cell(self):
        candidates = [(cell, len(self.board[cell]))
                      for cell in self.CELLS
                      if len(self.board[cell]) > 1]
        cell, _ = min(candidates, key=lambda x: x[1])
        return cell

    def any_empty(self):
        for cell in self.CELLS:
            if len(self.board[cell]) == 0:
                return True
        return False



def main():

    board = read_board("sudoku_cases/hard1.txt")
    sudoku = Sudoku(board)

    print("Initial possible values for each cell:")
    for r in range(9):
        for c in range(9):
            print(f"({r},{c}): {sudoku.get_values((r, c))}")

    sudoku.infer_with_guessing()

    print("\nAfter AC-3:")
    for r in range(9):
        for c in range(9):
            print(f"({r},{c}): {sudoku.get_values((r, c))}")


if __name__ == "__main__":
    main()
