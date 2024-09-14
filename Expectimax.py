import random
from typing import Tuple, Optional, Dict


class Expectimax:
    """
     Class implementing the Expectimax algorithm for the Go game. It evaluates possible moves for the current player
     and uses an Expectimax search tree to select the optimal move based on the expected value of future game states.
     """

    def __init__(self, board, color: str):
        """
           Initializes the Expectimax class with the current board state and player color.

           Args:
               board: The current GoBoard object representing the game state.
               color: The color of the player making the move ('BLACK' or 'WHITE').
           """
        self.board = board
        self.color = color
        self.memo: Dict[str, float] = {}  # Memoization dictionary



    def expectimax(self, depth: int) -> Tuple[Optional[Tuple[int, int]], float]:
        """
          Performs Expectimax search to find the best move for the current player.

          Args:
              depth: The depth of the search tree (number of plies to explore).

          Returns:
              A tuple containing the best move (row, col) and its expected value. If no moves are available, returns (None, -inf).
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
        """
        Recursively performs the Expectimax search for a given board state.

        Args:
            board: The GoBoard object representing the current state of the game.
            color: The color of the player whose move is being evaluated ('BLACK' or 'WHITE').
            depth: The depth of the search tree (number of remaining plies to explore).

        Returns:
            A float representing the expected value of the game state after performing the search.
        """
        board_key = self._board_to_key(board.board)

        # Check memoization
        if (board_key, color, depth) in self.memo:
            return self.memo[(board_key, color, depth)]

        if depth == 0:
            # value = board.evaluate_board(color)
            # value = board.evaluate_board_using_heuristic(color)
            value = board.evaluate_board_using_heuristic2(color)
            self.memo[(board_key, color, depth)] = value
            return value

        moves = board.get_legal_moves(color)
        if not moves:
            value = board.evaluate_board(color)
            self.memo[(board_key, color, depth)] = value
            return value

        if color == "BLACK":
            best_value = -float('inf')
            for move in moves:
                board_copy = board.copy()
                board_copy.play_move(*move, color)
                value = self._expectimax_search(board_copy, board.opponent_color(color), depth - 1)
                best_value = max(best_value, value)
            self.memo[(board_key, color, depth)] = best_value
            return best_value
        else:
            total_value = 0
            for move in moves:
                board_copy = board.copy()
                board_copy.play_move(*move, color)
                total_value += self._expectimax_search(board_copy, board.opponent_color(color), depth - 1)
            average_value = total_value / len(moves) if moves else 0
            self.memo[(board_key, color, depth)] = average_value
            return average_value


    def _board_to_key(self, board: 'GoBoard') -> str:
        """
         Converts the current board state into a unique string representation for memoization.

         Args:
             board: The current GoBoard object.

         Returns:
             A string representing the current board state that can be used as a key in the memoization dictionary.
         """
        return str(board)