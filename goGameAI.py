import sys
import random
from typing import Optional, Tuple
import tkinter as tk
from GoBoard import GoBoard
from goDisplay import GoDisplay
from MCTS import MCTS
from Expectimax import Expectimax
from Minimax import Minimax
from MinimaxAlphaBeta import MinimaxAlphaBeta
from Agents import RandomAgent, GreedyAgent


class GoGame:

    def __init__(self, size: int, num_games: int, black_strategy, while_strategy, display, is_display):
        self.size = size
        self.num_games = num_games
        self.display = display
        if not is_display:
            self.display.root.withdraw()  # Hide the root window
        self.results = []
        self.current_game = 0
        self.current_color = 'BLACK'
        self.game_over = False
        self.finished = False
        self.board = None
        self.previous_boards = set()
        self.speed = 1
        self.first_turn = True
        self.black_strategy = black_strategy
        self.white_strategy = while_strategy
        self.random_agent_white = RandomAgent('WHITE')
        self.random_agent_black = RandomAgent('BLACK')
        self.greedy_agent_white = GreedyAgent('WHITE')
        self.greedy_agent_black = GreedyAgent('BLACK')

        # Define a dictionary of strategies for BLACK
        self.black_strategies = {
            "random": self.random_agent_black.getAction,
            "greedy": self.greedy_agent_black.getAction,
            "monte_carlo": lambda board: self.monte_carlo_strategy(),
            "expectimax": lambda board: self.expectimax_strategy(),
            "alpha_beta": lambda board: self.minimax_strategy(),
            "minimax": lambda board: self.alpha_beta_strategy(),
        }

        # Define a dictionary of strategies for WHITE
        self.white_strategies = {
            "random": self.random_agent_white.getAction,
            "greedy": self.greedy_agent_white.getAction,
        }


    def is_game_over(self) -> bool:
        black_moves = any(self.board.is_legal_move(x, y, 'BLACK') for x in range(self.size) for y in range(self.size))
        white_moves = any(self.board.is_legal_move(x, y, 'WHITE') for x in range(self.size) for y in range(self.size))
        return not black_moves and not white_moves

    def play_game_step(self):
        if self.finished:
            print("game over")
            return

        if self.game_over:
            self.end_game()
            return

        if self.board is None:
            self.board = GoBoard(self.size, self.previous_boards)
            self.current_color = 'BLACK'
            self.display.display_board(self.board)
            self.display.root.after(self.speed, self.play_game_step)
            return

        # Select the strategy based on the current color
        if self.current_color == 'BLACK':
            move = self.black_strategies[self.black_strategy](self.board)
        else:
            move = self.white_strategies[self.white_strategy](self.board)

        if move is None:
            if self.board:
                result = self.board.count_score()
                self.results.append(result)
                print(f'Game {self.current_game + 1}: BLACK {result["BLACK"]}, WHITE {result["WHITE"]}')
                self.display.display_results(self.results)

            self.current_game += 1
            if self.current_game >= self.num_games:
                self.end_game()
                self.finished = True
            else:
                self.reset_game()
            return

        x, y = move
        if self.board.play_actual_move(x, y, self.current_color): # todo play_actual_move
            self.previous_boards.add(tuple(map(tuple, self.board.board)))
            self.current_color = 'WHITE' if self.current_color == 'BLACK' else 'BLACK'
            self.display.display_board(self.board)

        if self.is_game_over():
            self.game_over = True

        self.display.root.after(self.speed, self.play_game_step)

    def monte_carlo_strategy(self):
        mcts = MCTS(self.board, self.current_color,self.greedy_agent_white, mcts_iterations=50, exploration_weight=1.5
                    )
        move = mcts.mcts_search()
        return move

    def expectimax_strategy(self):
        if self.first_turn:  # expectimax with depth=4 always return (3,0) for the first turn, so no need to check.
            move = (3, 0)
            self.first_turn = False
        else:
            expectimax_agent = Expectimax(self.board, self.current_color)
            move, value = expectimax_agent.expectimax(depth=4)
        return move

    def minimax_strategy(self):
        minimax_agent = Minimax(self.board, self.current_color)
        move, value = minimax_agent.minimax(depth=4)
        return move

    def alpha_beta_strategy(self):
        alpha_beta_agent = MinimaxAlphaBeta(self.board, self.current_color)
        move, value = alpha_beta_agent.minimax(depth=4)
        return move

    def reset_game(self):
        self.first_turn = True
        self.board = None
        self.current_color = 'BLACK'
        self.game_over = False
        self.previous_boards.clear()
        self.display.root.after(self.speed, self.play_game_step)

    def end_game(self):
        if self.board and self.current_game < self.num_games:
            result = self.board.count_score()
            self.results.append(result)
            print(f'Game {self.current_game + 1} has ended: BLACK {result["BLACK"]}, WHITE {result["WHITE"]}')
            self.display.display_results(self.results)

        if self.current_game < self.num_games:
            self.current_game += 1
            self.reset_game()
        else:
            self.finished = True
            print(self.display.num_wins_by_games)
            print("end game")

    def run(self):
        self.play_game_step()


if __name__ == "__main__":
    black_strategies = ["random", "greedy", "minimax", "alpha_beta", "expectimax", "monte_carlo"]
    white_strategies = ["random", "greedy"]
    if len(sys.argv) != 5 \
            or sys.argv[1] not in black_strategies \
            or sys.argv[2] not in white_strategies \
            or not sys.argv[3].isdigit()\
            or int(sys.argv[3]) < 1\
            or sys.argv[4] not in ["display", "not_display"]:
        print("put in the command line: goGameAI.py "
              "<BLACK-STRATEGY> <WHITE-STRATEGY> <NUMBER-OF-GAME> <DISPLAY-BOARD (display | not_display)>")
        print("BLACK-STRATEGY: ", str(black_strategies))
        print("WHITE-STRATEGY: ", str(white_strategies))
        exit()

    size = 5
    black_strategy = sys.argv[1]
    while_strategy = sys.argv[2]
    num_games = int(sys.argv[3])
    is_display = sys.argv[4] == "display"

    root = tk.Tk()
    root.title("Go Game")

    display = GoDisplay(root, size)

    game = GoGame(size, num_games, black_strategy, while_strategy, display, is_display)
    print("start game")
    game.run()

    root.mainloop()
