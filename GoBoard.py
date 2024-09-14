import random
from typing import Dict, Set, Tuple, List, Optional
from copy import deepcopy, copy


class GoBoard:
    def __init__(self, size: int, previous_boards):
        """
        Initializes a GoBoard instance with a given size and a list of previous board states.

        Args:
        size (int): The size of the Go board (e.g., 9x9, 19x19).
        previous_boards (list): A list of previous board configurations to detect repetitions (ko).

        Attributes:
        board (list): A 2D list representing the current state of the Go board, where each position can be None, 'BLACK', or 'WHITE'.
        captured (dict): Tracks the number of stones captured by 'BLACK' and 'WHITE' players.
        previous_boards (list): Stores previous board states to help detect ko.
        last_captured (dict): Keeps track of the most recent capture made by each player.
        """
        self.size = size
        self.board = [[None for _ in range(size)] for _ in range(size)]
        self.captured = {'BLACK': 0, 'WHITE': 0}
        self.previous_boards = previous_boards
        self.last_captured = {'BLACK': None, 'WHITE': None}

    def is_on_board(self, x: int, y: int) -> bool:
        """
        Checks if the given coordinates are within the boundaries of the board.

        Args:
        x (int): The x-coordinate.
        y (int): The y-coordinate.

        Returns:
        bool: True if the coordinates are on the board, False otherwise.
        """
        return 0 <= x < self.size and 0 <= y < self.size

    def get_neighbors(self, x: int, y: int) -> List[Tuple[int, int]]:
        """
        Retrieves the list of valid neighboring coordinates for a given position on the board.

        Args:
        x (int): The x-coordinate of the stone.
        y (int): The y-coordinate of the stone.

        Returns:
        List[Tuple[int, int]]: A list of valid neighboring coordinates.
        """
        neighbors = [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]
        return [(nx, ny) for nx, ny in neighbors if self.is_on_board(nx, ny)]

    def get_group(self, x: int, y: int, board: Optional[List[List[Optional[str]]]] = None) -> Set[Tuple[int, int]]:
        """
        Finds all stones connected to the given stone (i.e., the group of connected stones).

        Args:
        x (int): The x-coordinate of the starting stone.
        y (int): The y-coordinate of the starting stone.
        board (Optional[List[List[Optional[str]]]]): Optionally pass a different board to check the group on.
        If not provided, the current board is used.

        Returns:
        Set[Tuple[int, int]]: A set of coordinates representing the stones in the same group.
        """
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
        """
        Checks if a group of stones has at least one liberty (empty adjacent position).

        Args:
        group (Set[Tuple[int, int]]): A set of coordinates representing a group of connected stones.
        board (Optional[List[List[Optional[str]]]]): Optionally pass a different board to check on. If not provided, the current board is used.

        Returns:
        bool: True if the group has at least one liberty, False otherwise.
        """
        board = board or self.board
        for x, y in group:
            for nx, ny in self.get_neighbors(x, y):
                if board[nx][ny] is None:
                    return True
        return False

    def remove_group(self, group: Set[Tuple[int, int]], color: str):
        """
        Removes a group of stones from the board and updates the captured stones count for the opposing player.

        Args:
        group (Set[Tuple[int, int]]): A set of coordinates representing a group of connected stones to be removed.
        color (str): The color of the stones being removed (either 'BLACK' or 'WHITE').
        """
        for x, y in group:
            self.board[x][y] = None
        self.captured[color] += len(group)

    def play_move(self, x: int, y: int, color: str) -> bool:
        """
        Attempt to play a move for the given color at position (x, y).

        Args:
            x (int): The x-coordinate of the move.
            y (int): The y-coordinate of the move.
            color (str): The color of the stone to place ('BLACK' or 'WHITE').

        Returns:
            bool: True if the move is valid and successfully played, False otherwise.

        This function first checks if the move is valid (on the board and not already occupied).
        Then it simulates placing the stone and checks for any neighboring stones of the opposite color
        to see if any group can be captured (no liberties). If no captures occur, it checks if the group
        formed by the placed stone has any liberties. If the group has no liberties, the move is reverted.
        """
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

        return True

    def play_actual_move(self, x: int, y: int, color: str) -> bool:
        """
        Similar to play_move, this function attempts to place a stone and apply capture logic.

        Args:
            x (int): The x-coordinate of the move.
            y (int): The y-coordinate of the move.
            color (str): The color of the stone ('BLACK' or 'WHITE').

        Returns:
            bool: True if the move is valid, False otherwise.

        This function also tracks the last captured group for future Ko-rule checks.
        """
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
                    self.last_captured[color] = neighbor_group

        if not captured_any and not self.has_liberties(self.get_group(x, y)):
            self.board = board_copy
            self.captured = captured_before
            return False

        return True

    def is_surrounded(self, group: Set[Tuple[int, int]], color: str) -> bool:
        """
        Check if all empty spaces in the given group are fully surrounded by the specified color.

        Args:
            group (Set[Tuple[int, int]]): The group of empty spaces to check.
            color (str): The color that should be surrounding the empty group.

        Returns:
            bool: True if all empty spaces in the group are surrounded by stones of the given color, False otherwise.
        """
        for x, y in group:
            for nx, ny in self.get_neighbors(x, y):
                if self.board[nx][ny] == None:
                    return False  # Found an adjacent empty space
                elif self.board[nx][ny] != color:
                    return False  # Found an adjacent stone that is not the specified color
        return True  # All adjacent stones are of the specified color and no empty spaces are adjacent

    def is_legal_move(self, x: int, y: int, color: str) -> bool:
        """
        Check if placing a stone of the given color at the specified coordinates is a legal move.

        Args:
            x (int): The x-coordinate of the move.
            y (int): The y-coordinate of the move.
            color (str): The color of the stone to be placed.

        Returns:
            bool: True if the move is legal, False otherwise.
        """
        if self.board[x][y] is not None:
            return False

        board_copy = self.copy()
        board_copy.board[x][y] = color
        # Ko rule: check if this move reverts the board to a previous state
        if tuple(map(tuple, board_copy.board)) in self.previous_boards:
            return False

        # Check if move results in a capture or if it has liberties
        for nx, ny in self.get_neighbors(x, y):
            neighbor_color = board_copy.board[nx][ny]
            if neighbor_color is not None and neighbor_color != color:
                neighbor_group = self.get_group(nx, ny, board_copy.board)
                # check:
                if neighbor_group == self.last_captured[color]:
                    return False
                if not self.has_liberties(neighbor_group, board_copy.board):
                    board_copy.remove_group(neighbor_group, neighbor_color)
                    if tuple(map(tuple, board_copy.board)) in self.previous_boards:
                        return False
                    return True

        player_group = self.get_group(x, y, board_copy.board)
        if not self.has_liberties(player_group, board_copy.board):
            return False

        return True

    def get_legal_moves(self, color: str) -> List[Tuple[int, int]]:
        """
        Return a list of all legal moves for the given color.

        Args:
            color (str): The color of the stones for which to find legal moves.

        Returns:
            List[Tuple[int, int]]: A list of coordinates where legal moves can be made.
        """
        return [
            (x, y)
            for x in range(self.size)
            for y in range(self.size)
            if self.board[x][y] is None and self.is_legal_move(x, y, color)
        ]

    def random_move(self, color: str) -> Optional[Tuple[int, int]]:
        """
        Select a random legal move for the given color.

        Args:
            color (str): The color of the player making the move.

        Returns:
            Optional[Tuple[int, int]]: Coordinates of a random legal move, or None if no legal moves are available.
        """
        legal_moves = self.get_legal_moves(color)
        return random.choice(legal_moves) if legal_moves else None

    def is_terminal(self, color):
        """
         Determine if the game is in a terminal state, meaning no legal moves are left for the given player.

         Args:
             color (str): The color of the player.

         Returns:
             bool: True if there are no legal moves left for either player, False otherwise.
         """
        if len(self.get_legal_moves(color)) == 0:
            return True
        return False

    def evaluate_board(self, color: str) -> float:
        """
         Evaluate the current board state from the perspective of the given color.

         Args:
             color (str): The color for which the evaluation is being performed.

         Returns:
             float: The evaluation score, which is the difference between the scores of the player and the opponent.
         """
        opponent_color = self.opponent_color(color)
        return self.count_score()[color] - self.count_score()[opponent_color]

    def get_state(self):
        """
        Returns the current state of the board.

        Returns:
            list: The current board configuration.
        """
        return self.board

    def stone_count(self, color: str) -> int:
        """
        Count the number of stones of a specific color on the board.

        Args:
            color (str): The color of the stones to count ('BLACK' or 'WHITE').

        Returns:
            int: The number of stones of the specified color on the board.
        """
        return sum(row.count(color) for row in self.board)

    def controlled_territory(self, color: str) -> int:
        """
          Calculate the controlled territory for a given color by counting the number of empty spaces
          surrounded by the color's stones.

          Args:
              color (str): The color to evaluate ('BLACK' or 'WHITE').

          Returns:
              int: The score of the controlled territory for the given color.
          """
        visited = set()
        territory_score = 0

        def flood_fill(x: int, y: int) -> Set[Tuple[int, int]]:
            """
               Perform a flood fill to find all connected empty spaces.

               Args:
                   x (int): The x-coordinate of the starting point.
                   y (int): The y-coordinate of the starting point.

               Returns:
                   Set[Tuple[int, int]]: A set of coordinates representing the empty spaces.
               """
            stack = [(x, y)]
            group = set()
            while stack:
                cx, cy = stack.pop()
                if (cx, cy) in group or (cx, cy) in visited:
                    continue
                group.add((cx, cy))
                visited.add((cx, cy))
                if self.board[cx][cy] is None:  # Changed from '.' to None
                    for nx, ny in self.get_neighbors(cx, cy):
                        if (nx, ny) not in visited:
                            stack.append((nx, ny))
            return group

        for x in range(self.size):
            for y in range(self.size):
                if self.board[x][y] is None and (x, y) not in visited:  # Changed from '.' to None
                    empty_group = flood_fill(x, y)
                    if self.is_surrounded(empty_group, color):
                        territory_score += len(empty_group)

        return territory_score

    def get_captures(self, color: str) -> int:
        """
          Retrieve the number of opponent's stones that have been captured by the given color.

          Args:
              color (str): The color of the player whose captures are to be retrieved ('BLACK' or 'WHITE').

          Returns:
              int: The number of opponent's stones captured.
          """
        opponent = 'WHITE' if color == 'BLACK' else 'BLACK'
        return self.captured[opponent]  # Assuming captures is a dictionary tracking captured stones

    def potential_liberties(self, color: str) -> int:
        """
          Count the potential liberties (empty spaces adjacent to the stones) for a given color.

          Args:
              color (str): The color to evaluate ('BLACK' or 'WHITE').

          Returns:
              int: The number of potential liberties for the given color.
          """
        visited = set()
        liberty_count = 0

        def count_liberties(x: int, y: int):
            """
            Count the number of liberties for a group of stones.

            Args:
                x (int): The x-coordinate of the starting point.
                y (int): The y-coordinate of the starting point.
            """
            nonlocal liberty_count  # Declare that we are using the outer variable
            stack = [(x, y)]
            while stack:
                cx, cy = stack.pop()
                if (cx, cy) in visited:
                    continue
                visited.add((cx, cy))
                if self.board[cx][cy] == color:
                    for nx, ny in self.get_neighbors(cx, cy):
                        if self.board[nx][ny] is None:  # Changed from '.' to None
                            liberty_count += 1
                        elif self.board[nx][ny] != color:
                            continue
                        stack.append((nx, ny))

        for x in range(self.size):
            for y in range(self.size):
                if self.board[x][y] == color and (x, y) not in visited:
                    count_liberties(x, y)

        return liberty_count

    def corner_and_edge_control(self, color: str) -> int:
        """
        Evaluate the control over corners and edges for a given color.

        Args:
            color (str): The color to evaluate ('BLACK' or 'WHITE').

        Returns:
            int: The score based on control over corners and edges.
        """
        score = 0
        for x in range(self.size):
            for y in range(self.size):
                if self.board[x][y] == color:
                    if (x in [0, self.size - 1] and y in [0, self.size - 1]) or \
                            (x in [0, self.size - 1] or y in [0, self.size - 1]):
                        score += 1  # Additional points for controlling corners and edges
        return score

    def evaluate_board_using_heuristic(self, color: str) -> int:
        """
          Evaluate the board using a specific heuristic, combining stone count, controlled territory,
          captured stones, potential liberties, and corner/edge control.

          Args:
              color (str): The color to evaluate ('BLACK' or 'WHITE').

          Returns:
              int: The heuristic score for the given color.
          """
        score = 0
        score += self.stone_count(color) * 1  # Weighting can be adjusted
        score += self.controlled_territory(color) * 5
        score += self.get_captures(color) * 3
        score += self.potential_liberties(color) * 2
        score += self.corner_and_edge_control(color) * 4
        return score

    def evaluate_board_using_heuristic2(self, color: str) -> int:
        """
        Evaluate the board using an alternative heuristic, focusing on stone count, controlled territory,
        captured stones, and potential liberties.

        Args:
            color (str): The color to evaluate ('BLACK' or 'WHITE').

        Returns:
            int: The heuristic score for the given color.
        """
        score = 0
        score += self.stone_count(color) * 1  # Weighting can be adjusted
        score += self.controlled_territory(color) * 5
        score += self.get_captures(color) * 3
        score += self.potential_liberties(color) * 2
        return score

    def opponent_color(self, color: str) -> str:
        """
        Get the opponent's color based on the given color.

        Args:
            color (str): The color of the current player ('BLACK' or 'WHITE').

        Returns:
            str: The opponent's color.
        """
        return 'WHITE' if color == 'BLACK' else 'BLACK'

    def count_score(self) -> Dict[str, int]:
        """
        Count the score for both BLACK and WHITE players.
        The score is calculated as the number of empty spaces surrounded by the player's stones
        plus the number of opponent's stones captured.

        Returns:
            Dict[str, int]: A dictionary with scores for 'BLACK' and 'WHITE'.
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

    def null_heuristic(self, color: str) -> int:
        """
        A placeholder heuristic function that returns 0 for any input.

        Args:
            color (str): The color to evaluate ('BLACK' or 'WHITE').

        Returns:
            int: Always returns 0.
        """
        return 0

    def copy(self):
        """
         Create a deep copy of the current GoBoard instance.

         Returns:
             GoBoard: A new GoBoard instance with the same board configuration.
         """
        # Create a deep copy of the GoBoard instance
        new_board = GoBoard(self.size, self.previous_boards)
        new_board.board = deepcopy(self.board)
        return new_board
