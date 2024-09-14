import random
from typing import Tuple, Optional, Dict

import GoBoard

OPPONENT_COLOR = {"BLACK": "WHITE", "WHITE": "BLACK"}


class MinimaxAlphaBeta:
    """
    A class that implements the Minimax algorithm with Alpha-Beta pruning and memoization.
    This is used to optimize the decision-making process in games like Go by reducing
    the number of nodes evaluated in the game tree.
    """

    def __init__(self, board: GoBoard, color: str):
        """
        Initializes the MinimaxAlphaBeta object with the game board and the player's color.

        Args:
            board (GoBoard): The current state of the game board.
            color (str): The player's color ('BLACK' or 'WHITE').
        """
        self.board = board
        self.color = color
        self.memo: Dict[str, float] = {}  # Memoization dictionary

    def minimax(self, depth: int) -> Tuple[Optional[Tuple[int, int]], float]:
        """
        Perform the Minimax search with Alpha-Beta pruning to find the best move for the player.

        Args:
            depth (int): The depth to which the game tree should be searched.

        Returns:
            Tuple[Optional[Tuple[int, int]], float]: A tuple where the first element is the best move (row, col),
                                                     or None if no legal moves are available, and the second element
                                                     is the alpha value (best score found).
        """
        best_move = None
        alpha = -float('inf')
        beta = float('inf')

        for move in self.board.get_legal_moves(self.color):
            board_copy = self.board.copy()
            board_copy.play_move(*move, self.color)
            move_value = self._minimax_search(board_copy, self.board.opponent_color(self.color), depth - 1, alpha, beta,
                                              False)
            if move_value > alpha:
                alpha = move_value
                best_move = move

        return best_move, alpha

    def _minimax_search(self, board: 'GoBoard', color: str, depth: int, alpha: float, beta: float,
                        maximizing: bool) -> float:
        """
        A recursive helper function for the Minimax algorithm with Alpha-Beta pruning. It evaluates all possible
        game states up to the specified depth and returns the value of the best move.

        Args:
            board (GoBoard): The current state of the game board.
            color (str): The color of the current player ('BLACK' or 'WHITE').
            depth (int): The depth to which the game tree should be searched.
            alpha (float): The best score the maximizing player can guarantee.
            beta (float): The best score the minimizing player can guarantee.
            maximizing (bool): True if the current player is trying to maximize the score, False if minimizing.

        Returns:
            float: The value of the best move at the current depth.
        """
        board_key = self._board_to_key(board.board)

        # Return cached result if this board state has already been evaluated
        if (board_key, color, depth) in self.memo:
            return self.memo[(board_key, color, depth)]

        if depth == 0:
            value = board.evaluate_board_using_heuristic(color) - board.evaluate_board_using_heuristic(
                OPPONENT_COLOR[color])
            # value = board.evaluate_board_using_heuristic(color)
            # value = board.evaluate_board_using_heuristic_for_minimax(color)
            # value = board.evaluate_board(color)
            self.memo[(board_key, color, depth)] = value
            return value

        moves = board.get_legal_moves(color)
        if not moves:
            value = board.evaluate_board_using_heuristic(color) - board.evaluate_board_using_heuristic(
                OPPONENT_COLOR[color])
            # value = board.evaluate_board_using_heuristic(color)
            # value = board.evaluate_board_using_heuristic_for_minimax(color)
            # value = board.evaluate_board(color)
            self.memo[(board_key, color, depth)] = value
            return value
        # Maximizing player (trying to maximize score)
        if maximizing:
            best_value = -float('inf')
            for move in moves:
                board_copy = board.copy()
                board_copy.play_move(*move, color)
                value = self._minimax_search(board_copy, board.opponent_color(color), depth - 1, alpha, beta, False)
                best_value = max(best_value, value)
                alpha = max(alpha, value)
                if beta <= alpha:
                    break  # Beta cut-off
            self.memo[(board_key, color, depth)] = best_value
            return best_value
        # Minimizing player (trying to minimize score)
        else:
            best_value = float('inf')
            for move in moves:
                board_copy = board.copy()
                board_copy.play_move(*move, color)
                value = self._minimax_search(board_copy, board.opponent_color(color), depth - 1, alpha, beta, True)
                best_value = min(best_value, value)
                beta = min(beta, value)
                if beta <= alpha:
                    break  # Alpha cut-off
            self.memo[(board_key, color, depth)] = best_value
            return best_value

    def _board_to_key(self, board: 'GoBoard') -> str:
        """
         Convert the board state to a unique key for memoization.

         Args:
             board (GoBoard): The current state of the game board.

         Returns:
             str: A unique string representation of the board state.
         """
        return str(board)
