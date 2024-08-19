from typing import Tuple, Optional, Dict


class Expectimax:
    def __init__(self, board, color: str):
        self.board = board
        self.color = color
        self.memo: Dict[str, float] = {}  # Memoization dictionary

    def expectimax(self, depth: int) -> Tuple[Optional[Tuple[int, int]], float]:
        """
        Perform Expectimax search to find the best move and its expected value.
        """
        best_move = None
        best_value = -float('inf')

        for move in self.board.get_legal_moves(self.color):
            board_copy = self.board.copy()
            board_copy.play_move(*move, self.color)
            move_value = self._expectimax_search(board_copy, self.board.opponent_color(self.color), depth - 1)
            if move_value > best_value:
                best_value = move_value
                best_move = move

        return best_move, best_value

    def _expectimax_search(self, board: 'GoBoard', color: str, depth: int) -> float:
        board_key = self._board_to_key(board)

        # Check memoization
        if (board_key, color, depth) in self.memo:
            return self.memo[(board_key, color, depth)]

        if depth == 0:
            value = self.board.evaluate_board(color)
            self.memo[(board_key, color, depth)] = value
            return value

        moves = board.get_legal_moves(color)
        if not moves:
            value =  self.board.evaluate_board(color)
            self.memo[(board_key, color, depth)] = value
            return value

        if color == self.color:
            best_value = -float('inf')
            for move in moves:
                board_copy = board.copy()
                board_copy.play_move(*move, color)
                value = self._expectimax_search(board_copy, self.board.opponent_color(color), depth - 1)
                best_value = max(best_value, value)
            self.memo[(board_key, color, depth)] = best_value
            return best_value
        else:
            total_value = 0
            for move in moves:
                board_copy = board.copy()
                board_copy.play_move(*move, color)
                total_value += self._expectimax_search(board_copy, self.board.opponent_color(color), depth - 1)
            average_value = total_value / len(moves) if moves else 0
            self.memo[(board_key, color, depth)] = average_value
            return average_value


    def _board_to_key(self, board: 'GoBoard') -> str:
        """
        Convert the board state to a unique key for memoization.
        """
        # Implement a unique board state representation
        # This is a placeholder and should be replaced with a proper method to serialize the board state
        return str(board)