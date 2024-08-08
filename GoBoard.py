from typing import Dict, Set, Tuple, List


class GoBoard:
    def __init__(self, size: int):
        self.size = size
        self.board = [[None for _ in range(size)] for _ in range(size)]
        self.captured = {'BLACK': 0, 'WHITE': 0}
        self.history = []  # To keep track of moves for undoing

    def is_on_board(self, x: int, y: int) -> bool:
        return 0 <= x < self.size and 0 <= y < self.size

    def get_neighbors(self, x: int, y: int) -> List[Tuple[int, int]]:
        neighbors = [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]
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

        # Save the current board state for undo purposes
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
            # Undo the move if it results in a self-capture
            self.board = board_copy
            self.captured = captured_before
            return False

        self.history.append((x, y, color, board_copy, captured_before))
        return True

    def undo_move(self):
        if not self.history:
            return
        x, y, color, board_copy, captured_before = self.history.pop()
        self.board = board_copy
        self.captured = captured_before
        self.board[x][y] = None

    def count_score(self) -> Dict[str, int]:
        def is_surrounded(x: int, y: int, color: str) -> bool:
            """Check if an empty point is surrounded by the specified color."""
            group = self.get_group(x, y, self.board)
            return not self.has_liberties(group, self.board) and all(self.board[nx][ny] == color for nx, ny in group)

        def count_territory(color: str) -> int:
            """Count the number of empty points surrounded by the specified color."""
            visited = set()
            territory_count = 0

            for x in range(self.size):
                for y in range(self.size):
                    if self.board[x][y] is None and (x, y) not in visited:
                        # Start a BFS/DFS to determine the surrounded area
                        group = set()
                        stack = [(x, y)]
                        while stack:
                            cx, cy = stack.pop()
                            if (cx, cy) not in group:
                                group.add((cx, cy))
                                for nx, ny in self.get_neighbors(cx, cy):
                                    if (nx, ny) not in group and self.board[nx][ny] is None:
                                        stack.append((nx, ny))
                                    elif self.board[nx][ny] is not None:
                                        # If any neighbor is a different color, this point is not surrounded
                                        if self.board[nx][ny] != color:
                                            break
                                else:
                                    continue
                                break
                        else:
                            # The entire group is surrounded by the same color
                            territory_count += len(group)
                            visited.update(group)

            return territory_count

        black_score = count_territory('BLACK') + self.captured['BLACK']
        white_score = count_territory('WHITE') + self.captured['WHITE']

        return {'BLACK': black_score, 'WHITE': white_score}

    def reset(self):
        self.board = [[None for _ in range(self.size)] for _ in range(self.size)]
        self.captured = {'BLACK': 0, 'WHITE': 0}
        self.history = []  # Clear history on reset
