import numpy as np
from typing import Tuple, Dict
from GoBoard import GoBoard

class QLearning:
    def __init__(self, size: int = 5, learning_rate: float = 0.3, discount_factor: float = 0.9, exploration_rate: float = 1.0, exploration_decay: float = 0.99, min_exploration_rate: float = 0.1):
        self.size = size
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.exploration_rate = exploration_rate
        self.exploration_decay = exploration_decay
        self.min_exploration_rate = min_exploration_rate
        self.q_table = {}

    def get_q_value(self, board, action: Tuple[int, int]) -> float:
        """Retrieve the Q-value for a given state, action, and color."""
        state = self.get_state(board)
        if (state, action) in self.q_table:
            return self.q_table[(state, action)]
        else:
            # Calculate heuristic evaluation for unseen board
            copy_board = board.copy()
            copy_board.play_move(*action, "BLACK")
            return copy_board.evaluate_board_using_heuristic2("BLACK") - copy_board.evaluate_board_using_heuristic2("WHITE")

    def set_q_value(self, state: Tuple[Tuple[str, ...]], action: Tuple[int, int], value: float):
        """Set the Q-value for a given state, action, and color."""
        self.q_table[(state, action)] = float(value)

    def choose_action(self, board: GoBoard, color: str) -> Tuple[int, int]:
        """Choose an action based on exploration or exploitation."""
        if np.random.rand() < self.exploration_rate:
            return board.random_move(color)  # Explore: random move
        else:
            legal_moves = board.get_legal_moves(color)
            if not legal_moves:
                return board.random_move(color)  # No legal moves: explore
            q_values = [self.get_q_value(board, move) for move in legal_moves]
            max_q = max(q_values, default=0.0)
            best_moves = [move for move, q in zip(legal_moves, q_values) if q == max_q]
            return best_moves[np.random.randint(len(best_moves))] if best_moves else board.random_move(color)  # Exploit: best move

    def update_q_values(self, board: GoBoard, color: str, action: Tuple[int, int], reward: float, next_board):
        """Update Q-values based on the reward received and the next state."""
        legal_moves_for_next_board = next_board.get_legal_moves(color)
        max_future_q = max([self.get_q_value(next_board, move) for move in legal_moves_for_next_board], default=0.0)
        current_q = self.get_q_value(board, action)
        new_q = (1 - self.learning_rate) * current_q + self.learning_rate * (reward + self.discount_factor * max_future_q)
        self.set_q_value(self.get_state(board), action, new_q)

    def decay_exploration_rate(self):
        """Decay the exploration rate over time."""
        self.exploration_rate = max(self.exploration_rate * self.exploration_decay, self.min_exploration_rate)

    def get_state(self, board: GoBoard) -> Tuple[Tuple[str, ...]]:
        """Convert the board state into a tuple for use in Q-learning."""
        return tuple(tuple(row) for row in board.board)

    def get_reward(self, board: GoBoard, color: str) -> float:
        """Calculate the reward for the current board state and color."""
        current_score = board.evaluate_board_using_heuristic(color)
        opponent_color = 'WHITE' if color == 'BLACK' else 'BLACK'
        opponent_score = board.evaluate_board_using_heuristic(opponent_color)

        score_difference = current_score - opponent_score
        normalization_factor = 10
        normalized_reward = score_difference / normalization_factor

        if board.is_terminal(color):
            result = board.count_score()
            if (color == 'BLACK' and result["BLACK"] > result["WHITE"]) or (color == 'WHITE' and result["WHITE"] > result["BLACK"]):
                return 1.0  # Win reward
            elif result["BLACK"] == result["WHITE"]:
                return 0.0  # Draw reward
            else:
                return -1.0  # Loss reward

        return normalized_reward

    def save(self, filename: str):
        """Save the Q-table to a file."""
        np.save(filename, self.q_table)
        print(f"{filename} saved successfully")

    def load(self, filename: str):
        """Load the Q-table from a file."""
        self.q_table = np.load(filename, allow_pickle=True).item()
        print(f"{filename} load successfully")