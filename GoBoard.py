from typing import Dict, Set, Tuple, List, Optional
from copy import deepcopy

class GoBoard:
    def __init__(self, size: int):
        self.size = size
        self.board = [[None for _ in range(size)] for _ in range(size)]
        self.captured = {'BLACK': 0, 'WHITE': 0}
        self.history = []  # Track moves for undo
        self.previous_boards = []  # Track board states for Ko rule

    def is_on_board(self, x: int, y: int) -> bool:
        return 0 <= x < self.size and 0 <= y < self.size

    def get_neighbors(self, x: int, y: int) -> List[Tuple[int, int]]:
        neighbors = [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]
        return [(nx, ny) for nx, ny in neighbors if self.is_on_board(nx, ny)]

    def get_group(self, x: int, y: int, board: Optional[List[List[Optional[str]]]] = None) -> Set[Tuple[int, int]]:
        board = board or self.board
        color = board[x][y]
        group = set()
        stack = [(x, y)]
        while stack:
            cx, cy = stack.pop()
            if (cx, cy) not in group:
                group.add((cx, cy))
                for nx, ny in self.get_neighbors(cx, cy):
                    if board[nx][ny] == color and (nx, ny) not in group:
                        stack.append((nx, ny))
        return group

    def has_liberties(self, group: Set[Tuple[int, int]], board: Optional[List[List[Optional[str]]]] = None) -> bool:
        board = board or self.board
        for x, y in group:
            for nx, ny in self.get_neighbors(x, y):
                if board[nx][ny] is None:
                    return True
        return False

    def remove_group(self, group: Set[Tuple[int, int]], color: str):
        for x, y in group:
            self.board[x][y] = None
        self.captured[color] += len(group)

    def play_move(self, x: int, y: int, color: str) -> bool:
        if not self.is_on_board(x, y) or self.board[x][y] is not None:
            return False

        board_copy = [row.copy() for row in self.board]
        captured_before = self.captured.copy()

        self.board[x][y] = color
        captured_any = False
        for nx, ny in self.get_neighbors(x, y):
            neighbor_color = self.board[nx][ny]
            if neighbor_color is not None and neighbor_color != color:
                neighbor_group = self.get_group(nx, ny)
                if not self.has_liberties(neighbor_group):
                    self.remove_group(neighbor_group, neighbor_color)
                    captured_any = True

        if not captured_any and not self.has_liberties(self.get_group(x, y)):
            self.board = board_copy
            self.captured = captured_before
            return False

        # Ko rule: Save the board state for checking in subsequent moves
        if self.is_ko_violation():
            self.board = board_copy
            self.captured = captured_before
            return False
        else:
            self.previous_boards.append([row.copy() for row in self.board])

        self.history.append((x, y, color, board_copy, captured_before))
        return True

    def is_ko_violation(self) -> bool:
        return any(board == self.board for board in self.previous_boards)

    def undo_move(self):
        if not self.history:
            return
        x, y, color, board_copy, captured_before = self.history.pop()
        self.board = board_copy
        self.captured = captured_before
        self.board[x][y] = None
        if self.previous_boards:
            self.previous_boards.pop()

    def is_surrounded(self, group: Set[Tuple[int, int]], color: str) -> bool:
        for x, y in group:
            for nx, ny in self.get_neighbors(x, y):
                if self.board[nx][ny] is None:
                    return False
                elif self.board[nx][ny] != color:
                    return False
        return True

    def count_score(self) -> Dict[str, int]:
        def count_area(color: str) -> int:
            visited = set()
            score = 0
            for x in range(self.size):
                for y in range(self.size):
                    if self.board[x][y] is None and (x, y) not in visited:
                        group = self.get_group(x, y, self.board)
                        if self.is_surrounded(group, color):
                            score += len(group)
                        visited.update(group)
            return score

        black_score = count_area('BLACK') + self.captured['WHITE']
        white_score = count_area('WHITE') + self.captured['BLACK']
        return {'BLACK': black_score, 'WHITE': white_score}
