from typing import Tuple, Optional, Dict


class AlphaBeta:
    def __init__(self, board, color: str):
        self.board = board
        self.color = color
        self.memo: Dict[str, float] = {}  # Memoization dictionary

    def alphabeta(self, depth: int, alpha: float, beta: float, maximizing: bool) -> Tuple[Optional[Tuple[int, int]], float]:
        """
        Perform Alpha-Beta pruning to find the best move and its value.
        """
        best_move = None
        best_value = -float('inf') if maximizing else float('inf')

        for move in self.board.get_legal_moves(self.color):
            board_copy = self.board.copy()
            board_copy.play_move(*move, self.color)
            move_value = self._alphabeta_search(board_copy, self.board.opponent_color(self.color), depth - 1, alpha, beta, not maximizing)
            if maximizing:
                if move_value > best_value:
                    best_value = move_value
                    best_move = move
                alpha = max(alpha, best_value)
            else:
                if move_value < best_value:
                    best_value = move_value
                    best_move = move
                beta = min(beta, best_value)

            if beta <= alpha:
                break  # Beta cut-off

        return best_move, best_value

    def _alphabeta_search(self, board: 'GoBoard', color: str, depth: int, alpha: float, beta: float, maximizing: bool) -> float:
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
            value = board.evaluate_board(color)
            self.memo[(board_key, color, depth)] = value
            return value

        if maximizing:
            best_value = -float('inf')
            for move in moves:
                board_copy = board.copy()
                board_copy.play_move(*move, color)
                value = self._alphabeta_search(board_copy, board.opponent_color(color), depth - 1, alpha, beta, False)
                best_value = max(best_value, value)
                alpha = max(alpha, best_value)
                if beta <= alpha:
                    break  # Beta cut-off
            self.memo[(board_key, color, depth)] = best_value
            return best_value
        else:
            best_value = float('inf')
            for move in moves:
                board_copy = board.copy()
                board_copy.play_move(*move, color)
                value = self._alphabeta_search(board_copy, board.opponent_color(color), depth - 1, alpha, beta, True)
                best_value = min(best_value, value)
                beta = min(beta, best_value)
                if beta <= alpha:
                    break  # Alpha cut-off
            self.memo[(board_key, color, depth)] = best_value
            return best_value

    def _board_to_key(self, board: 'GoBoard') -> str:
        """
        Convert the board state to a unique key for memoization.
        """
        return str(board)  # A simple board serialization method
