import math
from typing import Optional, Tuple, Dict
from Expectimax import Expectimax
from Minimax import Minimax

from GoBoard import GoBoard

class MCTSNode:
    def __init__(self, board, color: str, move: Optional[Tuple[int, int]] = None, parent: Optional['MCTSNode'] = None):
        self.board = board
        self.color = color
        self.move = move  # This stores the move that led to this node
        self.parent = parent
        self.children: Dict[Tuple[int, int], 'MCTSNode'] = {}
        self.visits = 0
        self.value = 0

    def is_fully_expanded(self) -> bool:
        legal_moves = self.board.get_legal_moves(self.color)
        return len(self.children) == len(legal_moves)

    def best_child(self, exploration_weight: float) -> Optional['MCTSNode']:
        if not self.children:
            return None

        # self.children is a dict, so self.children.values() is an array of MCTSNodes
        return max(self.children.values(), key=lambda child: child.uct_score(exploration_weight))

    def uct_score(self, exploration_weight: float) -> float:
        if self.visits == 0:
            return float('inf')
        parent_visits = self.parent.visits if self.parent else 1
        return (self.value / self.visits) + exploration_weight * math.sqrt(math.log(parent_visits) / self.visits)


class MCTS:
    def __init__(self, board: GoBoard, color: str, mcts_iterations: int, exploration_weight: float):
        self.board = board
        self.color = color
        self.iterations = mcts_iterations
        self.exploration_weight = exploration_weight
        self.expectimax_depth = 3

    def mcts_search(self) -> Optional[Tuple[int, int]]:
        root = MCTSNode(self.board, self.color)

        for _ in range(self.iterations):
            node = self._select(root)
            reward = self._simulate(node)
            self._backpropagate(node, reward)

        best_node = root.best_child(0)
        return best_node.move if best_node else None

    def _select(self, node: MCTSNode) -> MCTSNode:
        while not node.board.is_terminal(node.color):
            if not node.is_fully_expanded():
                return self._expand(node)
            else:
                node = node.best_child(self.exploration_weight)
        return node

    def _expand(self, node: MCTSNode) -> MCTSNode:
        legal_moves = node.board.get_legal_moves(node.color)
        for move in legal_moves:
            if move not in node.children:
                new_board = node.board.copy()
                new_board.play_move(*move, node.color)
                child_color = 'WHITE' if node.color == 'BLACK' else 'BLACK'
                child_node = MCTSNode(new_board, child_color, move, node)
                node.children[move] = child_node
                return child_node
        return node.best_child(self.exploration_weight)

    def _simulate(self, node: MCTSNode) -> float:
        board_copy = node.board.copy()
        current_color = node.color

        # Getting value to node using simulate random game (original MCTS):
        i = 0
        while not board_copy.is_terminal(current_color) and i < 30:
            move = board_copy.random_move(current_color)
            if move:
                board_copy.play_move(*move, current_color)
                current_color = 'WHITE' if current_color == 'BLACK' else 'BLACK'
                i += 1

        # return self._evaluate_board(board_copy, node.color)
        # return board_copy.evaluate_board(node.color)
        return board_copy.evaluate_board_using_heuristic(node.color)

        # Getting value to node using Expectimax:
        # expectimax_agent = Expectimax(board_copy, current_color)
        # move, value = expectimax_agent.expectimax(depth=3)
        # return value

    def _evaluate_board(self, board: GoBoard, color: str) -> float:
        scores = board.count_score()
        return scores[color] - scores[board.opponent_color(color)]

    def _backpropagate(self, node: MCTSNode, reward: float):
        while node is not None:
            node.visits += 1
            node.value += reward
            node = node.parent
