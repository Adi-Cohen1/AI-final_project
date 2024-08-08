import random
from typing import List, Tuple, Dict


class Expectimax:
    def __init__(self, board, color: str):
        self.board = board
        self.color = color

    def expectimax(self, depth: int) -> Tuple[Tuple[int, int], float]:
        """
        Perform Expectimax search to find the best move and its expected value.
        """

        def expectimax_search(board: 'GoBoard', color: str, depth: int) -> float:
            if depth == 0:
                return self.board.evaluate_board(board, color)

            moves = self.board.get_legal_moves(board, color)
            if not moves:
                return self.board.evaluate_board(board, color)

            if color == self.color:
                best_value = -float('inf')
                for move in moves:
                    board_copy = board.copy()
                    board_copy.play_move(*move, color)
                    value = expectimax_search(board_copy, self.board.opponent_color(color), depth - 1)
                    best_value = max(best_value, value)
                return best_value
            else:
                total_value = 0
                for move in moves:
                    board_copy = board.copy()
                    board_copy.play_move(*move, color)
                    total_value += expectimax_search(board_copy, self.board.opponent_color(color), depth - 1)
                return total_value / len(moves)

        best_move = None
        best_value = -float('inf')
        for move in self.get_legal_moves(self.board, self.color):
            board_copy = self.board.copy()
            board_copy.play_move(*move, self.color)
            move_value = expectimax_search(board_copy, self.board.opponent_color(self.color), depth - 1)
            if move_value > best_value:
                best_value = move_value
                best_move = move

        return best_move, best_value



