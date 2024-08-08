from typing import Dict, Set, Tuple, List

class GoBoard:
    def __init__(self, size: int):
        self.size = size
        self.board = [[None for _ in range(size)] for _ in range(size)]
        self.captured = {'BLACK': 0, 'WHITE': 0}

    def is_on_board(self, x: int, y: int) -> bool:
        return 0 <= x < self.size and 0 <= y < self.size

    def get_neighbors(self, x: int, y: int) -> List[Tuple[int, int]]:
        neighbors = [(x-1, y), (x+1, y), (x, y-1), (x, y+1)]
        return [(nx, ny) for nx, ny in neighbors if self.is_on_board(nx, ny)]

    def get_group(self, x: int, y: int, board_copy=None) -> Set[Tuple[int, int]]:
        if board_copy is None:
            board_copy = self.board
        color = board_copy[x][y]
        group = set()
        stack = [(x, y)]
        while stack:
            cx, cy = stack.pop()
            if (cx, cy) not in group:
                group.add((cx, cy))
                for nx, ny in self.get_neighbors(cx, cy):
                    if board_copy[nx][ny] == color:
                        stack.append((nx, ny))
        return group

    def has_liberties(self, group: Set[Tuple[int, int]], board_copy=None) -> bool:
        if board_copy is None:
            board_copy = self.board
        for x, y in group:
            for nx, ny in self.get_neighbors(x, y):
                if board_copy[nx][ny] is None:
                    return True
        return False

    def remove_group(self, group: Set[Tuple[int, int]], color: str):
        for x, y in group:
            self.board[x][y] = None
        self.captured[color] += len(group)

    def play_move(self, x: int, y: int, color: str) -> bool:
        if not self.is_on_board(x, y) or self.board[x][y] is not None:
            return False
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
            self.board[x][y] = None
            return False
        return True

    def count_score(self) -> Dict[str, int]:
        black_score = sum(row.count('BLACK') for row in self.board) + self.captured['BLACK']
        white_score = sum(row.count('WHITE') for row in self.board) + self.captured['WHITE']
        return {'BLACK': black_score, 'WHITE': white_score}

    def reset(self):
        self.board = [[None for _ in range(self.size)] for _ in range(self.size)]
        self.captured = {'BLACK': 0, 'WHITE': 0}
