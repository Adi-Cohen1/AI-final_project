import random
from typing import Dict, Set, Tuple, List, Optional
from copy import deepcopy, copy

oposite_color = {"BLACK": "WHITE", "WHITE": "BLACK"}
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
        # print(f"{oposite_color[color]} eat {len(group)} {color}S ")
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
        self.history.append((x, y, color, board_copy, captured_before))
        return True

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
        """
        Check if all empty spaces in the given group are fully surrounded by the specified color.
        """
        for x, y in group:
            for nx, ny in self.get_neighbors(x, y):
                if self.board[nx][ny] is None:
                    return False
                elif self.board[nx][ny] != color:
                    # If adjacent to any color other than the specified one,
                    # check that all neighboring empty groups are surrounded by that color
                    adjacent_group = self.get_group(nx, ny, self.board)
                    if any(self.board[xx][yy] != color for xx, yy in adjacent_group if self.board[xx][yy] is not None):
                        return False
        return True

    def is_legal_move(self, x: int, y: int, color: str) -> bool:
        if self.board[x][y] is not None:
            return False

        board_copy = [row.copy() for row in self.board]
        board_copy[x][y] = color

        # Check if move results in a capture or if it has liberties
        for nx, ny in self.get_neighbors(x, y):
            neighbor_color = board_copy[nx][ny]
            if neighbor_color is not None and neighbor_color != color:
                neighbor_group = self.get_group(nx, ny, board_copy)
                if not self.has_liberties(neighbor_group, board_copy):
                    return True

        player_group = self.get_group(x, y, board_copy)
        if not self.has_liberties(player_group, board_copy):
            return False

        return True

    def get_legal_moves(self, color: str) -> List[Tuple[int, int]]:
        """
        Return a list of legal moves for the given color.
        """
        return [
            (x, y)
            for x in range(self.size)
            for y in range(self.size)
            if self.board[x][y] is None and self.is_legal_move(x, y, color)
        ]

    def random_move(self, color: str) -> Optional[Tuple[int, int]]:
        legal_moves = self.get_legal_moves(color)
        return random.choice(legal_moves) if legal_moves else None

    def is_terminal(self, color):
        # Check if there are no legal moves left for either player
        if len(self.get_legal_moves(color)) == 0:
            # Assume both players passed in a row if no moves are available
            return True

        return False

    def evaluate_board(self, color: str) -> float:
        """
        Evaluate the board from the perspective of the given color.
        """
        opponent_color = self.opponent_color(color)
        return self.count_score()[color] - self.count_score()[opponent_color]

    def opponent_color(self, color: str) -> str:
        return 'WHITE' if color == 'BLACK' else 'BLACK'

    def count_score(self) -> Dict[str, int]:
        """
        Count the score for both BLACK and WHITE players.
        The score is calculated as the number of empty spaces surrounded by the player's stones
        plus the number of opponent's stones captured.
        """

        def count_area(color: str) -> int:
            """
            Count the number of empty spaces surrounded by the given color.
            """
            visited = set()
            score = 0

            def flood_fill(x: int, y: int) -> Set[Tuple[int, int]]:
                """
                Perform a flood fill to find all connected empty spaces.
                """
                stack = [(x, y)]
                group = set()
                while stack:
                    cx, cy = stack.pop()
                    if (cx, cy) in group or (cx, cy) in visited:
                        continue
                    group.add((cx, cy))
                    visited.add((cx, cy))
                    for nx, ny in self.get_neighbors(cx, cy):
                        if self.board[nx][ny] is None and (nx, ny) not in group:
                            stack.append((nx, ny))
                return group

            for x in range(self.size):
                for y in range(self.size):
                    if self.board[x][y] is None and (x, y) not in visited:
                        empty_group = flood_fill(x, y)
                        if self.is_surrounded(empty_group, color):
                            score += len(empty_group)

            return score

        black_score = count_area('BLACK') + self.captured['WHITE']
        white_score = count_area('WHITE') + self.captured['BLACK']
        return {'BLACK': black_score, 'WHITE': white_score}

    def copy(self):
        # Create a deep copy of the GoBoard instance
        new_board = GoBoard(self.size)
        new_board.board = deepcopy(self.board)
        return new_board