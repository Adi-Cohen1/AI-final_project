import math
from typing import Optional, Tuple, Dict

import Agents
from Expectimax import Expectimax
from Minimax import Minimax

from GoBoard import GoBoard

from Agents import RandomAgent, GreedyAgent


class MCTSNode:
    """
     A class representing a node in the Monte Carlo Tree Search (MCTS).

     Attributes:
     -----------
     board : GoBoard
         The game board associated with the node.
     color : str
         The color of the player ('BLACK' or 'WHITE') that made the move leading to this node.
     move : Optional[Tuple[int, int]]
         The move (row, col) that led to this node (None for the root node).
     parent : Optional['MCTSNode']
         The parent node in the MCTS tree.
     children : Dict[Tuple[int, int], 'MCTSNode']
         A dictionary mapping moves to child nodes.
     visits : int
         Number of times this node has been visited.
     value : float
         The total value accumulated from simulations starting from this node.
     """
    def __init__(self, board, color: str, move: Optional[Tuple[int, int]] = None, parent: Optional['MCTSNode'] = None):
        self.board = board
        self.color = color
        self.move = move  # This stores the move that led to this node
        self.parent = parent
        self.children: Dict[Tuple[int, int], 'MCTSNode'] = {}
        self.visits = 0
        self.value = 0

    def is_fully_expanded(self) -> bool:
        """
         Check if all possible legal moves have been expanded into children nodes.

         Returns:
         --------
         bool:
             True if all legal moves have corresponding child nodes, False otherwise.
         """
        legal_moves = self.board.get_legal_moves(self.color)
        return len(self.children) == len(legal_moves)

    def best_child(self, exploration_weight: float) -> Optional['MCTSNode']:
        """
          Select the best child node based on the Upper Confidence Bound for Trees (UCT) formula.

          Parameters:
          -----------
          exploration_weight : float
              The exploration weight used in the UCT formula to balance exploration and exploitation.

          Returns:
          --------
          Optional['MCTSNode']:
              The child node with the highest UCT score, or None if no children exist.
          """
        if not self.children:
            return None

        # self.children is a dict, so self.children.values() is an array of MCTSNodes
        return max(self.children.values(), key=lambda child: child.uct_score(exploration_weight))

    def uct_score(self, exploration_weight: float) -> float:
        """
        Calculate the UCT score for the node.

        Parameters:
        -----------
        exploration_weight : float
            The exploration weight for the UCT formula.

        Returns:
        --------
        float:
            The UCT score.
        """
        if self.visits == 0:
            return float('inf')
        parent_visits = self.parent.visits if self.parent else 1
        return (self.value / self.visits) + exploration_weight * math.sqrt(math.log(parent_visits) / self.visits)


class MCTS:
    """
    A class that implements Monte Carlo Tree Search (MCTS) for decision-making in a Go game.

    Attributes:
    -----------
    board : GoBoard
        The initial game board to start the MCTS from.
    color : str
        The color of the player ('BLACK' or 'WHITE') making the move.
    agent_white : object
        The agent responsible for making moves for the white player.
    mcts_iterations : int
        The number of MCTS iterations to perform.
    exploration_weight : float
        The exploration weight for balancing exploration and exploitation in the UCT formula.
    agent_black : object
        The agent responsible for making moves for the black player.
    """
    def __init__(self, board: GoBoard, color: str, agent_white, mcts_iterations: int, exploration_weight: float):
        self.board = board
        self.color = color
        self.iterations = mcts_iterations
        self.exploration_weight = exploration_weight
        self.agent_white = agent_white

    def mcts_search(self) -> Optional[Tuple[int, int]]:
        """
           Perform MCTS to search for the best move from the current board state.

           Returns:
           --------
           Optional[Tuple[int, int]]:
               The best move found by MCTS, or None if no move is found.
           """
        root = MCTSNode(self.board, self.color)

        for _ in range(self.iterations):
            node = self._select(root)
            reward = self._simulate(node)
            self._backpropagate(node, reward)

        best_node = root.best_child(0)
        return best_node.move if best_node else None

    def _select(self, node: MCTSNode) -> MCTSNode:
        """
          Select a node to expand based on the UCT scores of the children.

          Parameters:
          -----------
          node : MCTSNode
              The node from which selection starts.

          Returns:
          --------
          MCTSNode:
              The selected node.
          """
        while not node.board.is_terminal(node.color):
            if not node.is_fully_expanded():
                return self._expand(node)
            else:
                node = node.best_child(self.exploration_weight)
        return node

    def _expand(self, node: MCTSNode) -> MCTSNode:
        """
        Expand a node by creating a new child for an untried move.

        Parameters:
        -----------
        node : MCTSNode
            The node to expand.

        Returns:
        --------
        MCTSNode:
            The newly created child node.
        """
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
        """
        Simulate a random game from the given node.

        Parameters:
        -----------
        node : MCTSNode
            The node from which the simulation starts.

        Returns:
        --------
        float:
            The result of the simulation (e.g., win or loss evaluation).
        """
        board_copy = node.board.copy()
        current_color = node.color

        # Getting value to node using simulate random game (original MCTS):
        i = 0
        while not board_copy.is_terminal(current_color) and i < 50:
            if current_color == 'BLACK':
                move = board_copy.random_move(current_color)
            else:
                move = self.agent_white.getAction(board_copy)
            if move:
                board_copy.play_move(*move, current_color)
                current_color = 'WHITE' if current_color == 'BLACK' else 'BLACK'
                i += 1

        return board_copy.evaluate_board_using_heuristic("BLACK")


    def _backpropagate(self, node: MCTSNode, reward: float):
        """
           Backpropagate the reward from the simulation up the MCTS tree.

           Parameters:
           -----------
           node : MCTSNode
               The node from which backpropagation starts.
           reward : float
               The reward to propagate upwards.
           """
        while node is not None:
            node.visits += 1
            node.value += reward
            node = node.parent
