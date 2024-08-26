import random
from typing import Tuple, Optional, Dict

class MinimaxAlphaBeta:
    def __init__(self, board, color: str):
        self.board = board
        self.color = color
        self.memo: Dict[str, float] = {}  # Memoization dictionary

    def minimax(self, depth: int) -> Tuple[Optional[Tuple[int, int]], float]:
        """
        Perform Minimax search with Alpha-Beta pruning to find the best move and its value.
        """
        best_move = None
        alpha = -float('inf')
        beta = float('inf')

        for move in self.board.get_legal_moves(self.color):
            board_copy = self.board.copy()
            board_copy.play_move(*move, self.color)
            move_value = self._minimax_search(board_copy, self.board.opponent_color(self.color), depth - 1, alpha, beta, False)
            if move_value > alpha:
                alpha = move_value
                best_move = move

        return best_move, alpha

    def _minimax_search(self, board: 'GoBoard', color: str, depth: int, alpha: float, beta: float, maximizing: bool) -> float:
        board_key = self._board_to_key(board.board)

        # Check memoization
        if (board_key, color, depth) in self.memo:
            return self.memo[(board_key, color, depth)]

        if depth == 0:
            value = board.evaluate_board_using_heuristic(color)
            self.memo[(board_key, color, depth)] = value
            return value

        moves = board.get_legal_moves(color)
        if not moves:
            value = board.evaluate_board_using_heuristic(color)
            self.memo[(board_key, color, depth)] = value
            return value

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
        else:
            best_value_for_black = -float('inf')
            best_value = float('inf')
            for move in moves:
                board_copy = board.copy()
                board_copy.play_move(*move, color)
                value = self._minimax_search(board_copy, board.opponent_color(color), depth - 1, alpha, beta, True)
                best_value = min(best_value, value)
                best_value_for_black = min(best_value_for_black, value)
                beta = min(beta, value)
                if beta <= alpha:
                    break  # Alpha cut-off
            # self.memo[(board_key, color, depth)] = best_value
            self.memo[(board_key, color, depth)] = best_value_for_black
            return best_value

    def _board_to_key(self, board: 'GoBoard') -> str:
        """
        Convert the board state to a unique key for memoization.
        """
        return str(board)
