import random
from copy import deepcopy
from GoBoard import GoBoard


class Agent:
    """
    Base class for an agent that plays the game of Go. This class provides a common interface 
    for various types of agents, such as random or greedy agents.
    """
    def __init__(self, color):
        """
        Initializes the agent with a specified color (either 'BLACK' or 'WHITE').

        Args:
            color (str): The color of the agent's stones.
        """
        self.color = color

    def getAction(self, board: GoBoard):
        """
        Abstract method to be implemented by subclasses. Determines the next action for the agent
        based on the current board state.

        Args:
            board (GoBoard): The current game board.

        Returns:
            Tuple[int, int]: The coordinates of the chosen move.
        """
        raise NotImplementedError


class RandomAgent(Agent):
    """
    An agent that selects a random legal move from the available legal moves on the board.
    """
    def __init__(self, color):
        """
        Initializes the RandomAgent with a specified color (either 'BLACK' or 'WHITE').

        Args:
            color (str): The color of the agent's stones.
        """
        super().__init__(color)

    def getAction(self, board):
        """
         Selects a random legal move from the list of legal moves available to the agent.

         Args:
             board (GoBoard): The current game board.

         Returns:
             Tuple[int, int] or None: The coordinates of the chosen move (row, col) or None if there are no legal moves.
         """
        legal_moves = board.get_legal_moves(self.color)
        return random.choice(legal_moves) if legal_moves else None


class GreedyAgent(Agent):
    """
    An agent that selects a move based on a heuristic function. The GreedyAgent evaluates all legal
    moves and picks the one that maximizes the heuristic score.
    """
    def __init__(self, color):
        """
        Initializes the GreedyAgent with a specified color and heuristic function.

        Args:
            color (str): The color of the agent's stones.
            heuristic_function (callable): A function used to evaluate board positions and select the best move.
                                           Default is GoBoard.null_heuristic, which can be replaced by other heuristic functions.
        """
        super().__init__(color)

    def getAction(self, board):
        """
        Selects the best legal move based on the provided heuristic function. The agent simulates
        each legal move, evaluates the board using the heuristic, and selects the move with the highest score.

        Args:
            board (GoBoard): The current game board.

        Returns:
            Tuple[int, int] or None: The coordinates of the best move (row, col) or None if no legal moves are available.
        """
        legal_moves = board.get_legal_moves(self.color)
        best_score = float('-inf')
        best_actions = []

        for action in legal_moves:
            x, y = action
            # Simulate the move
            board_copy = deepcopy(board)
            if board_copy.play_move(x, y, self.color):
                # Evaluate the board using the heuristic
                score = board_copy.evaluate_board_using_heuristic2(self.color)
                if score > best_score:
                    best_score = score
                    best_actions = [action]
                elif score == best_score:
                    best_actions.append(action)

        if best_actions:
            return random.choice(best_actions)
        else:
            return None