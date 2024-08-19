import math
from typing import Optional, Tuple, Dict
from concurrent.futures import ThreadPoolExecutor
from GoBoard import GoBoard
from Expectimax import Expectimax

class MCTSNode:
    def __init__(self, board, color: str, move: Optional[Tuple[int, int]] = None, parent: Optional['MCTSNode'] = None):
        self.board = board
        self.color = color
        self.move = move
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
        return max(self.children.values(), key=lambda child: child.uct_score(exploration_weight))

    def uct_score(self, exploration_weight: float) -> float:
        if self.visits == 0:
            return float('inf')
        parent_visits = self.parent.visits if self.parent else 1
        return (self.value / self.visits) + exploration_weight * math.sqrt(math.log(parent_visits) / self.visits)


class MCTS:
    def __init__(self, board: GoBoard, color: str, iterations: int, exploration_weight: float, expectimax_depth: int):
        self.board = board
        self.color = color
        self.iterations = iterations
        self.exploration_weight = exploration_weight
        self.expectimax_depth = expectimax_depth

    def mcts_search(self) -> Optional[Tuple[int, int]]:
        root = MCTSNode(self.board, self.color)

        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(self._run_simulation, root) for _ in range(self.iterations)]
            for future in futures:
                node, reward = future.result()
                self._backpropagate(node, reward)

        best_node = root.best_child(0)
        return best_node.move if best_node else None

    def _run_simulation(self, root: MCTSNode):
        node = self._select(root)
        reward = self._simulate(node)
        return node, reward

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
        expectimax_agent = Expectimax(node.board, node.color)
        _, value = expectimax_agent.expectimax(self.expectimax_depth)
        return value

    def _backpropagate(self, node: MCTSNode, reward: float):
        while node is not None:
            node.visits += 1
            node.value += reward
            node = node.parent
