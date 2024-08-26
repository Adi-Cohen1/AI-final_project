import random
from copy import deepcopy

from GoBoard import GoBoard



class Agent:
    def __init__(self, color):
        self.color = color

    def getAction(self, board: GoBoard):
        raise NotImplementedError


class RandomAgent(Agent):
    def __init__(self, color):
        super().__init__(color)

    def getAction(self, board):
        legal_moves = board.get_legal_moves(self.color)
        return random.choice(legal_moves) if legal_moves else None

class GreedyAgent(Agent):
    def __init__(self,color):
        super().__init__(color)


    def getAction(self, board):
        legal_moves = board.get_legal_moves(self.color)
        best_score = float('-inf')
        best_actions = []

        for action in legal_moves:
            x, y = action
            # Simulate the move
            board_copy = deepcopy(board)
            if board_copy.play_move(x, y, self.color):
                # Evaluate the board using the heuristic
                score = board_copy.evaluate_board_using_heuristic(self.color)
                if score > best_score:
                    best_score = score
                    best_actions = [action]
                elif score == best_score:
                    best_actions.append(action)

        if best_actions:
            return random.choice(best_actions)
        else:
            return None