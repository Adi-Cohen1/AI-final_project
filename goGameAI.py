import random
from typing import Optional, Tuple
import tkinter as tk
from GoBoard import GoBoard
from goDisplay import GoDisplay
from MCTS import MCTS
from Expectimax import Expectimax
from Agents import RandomAgent,GreedyAgent

class GoGame:
    def __init__(self, size: int, num_games: int, display: GoDisplay, mcts_iterations: int = 1000,
                 exploration_weight: float = 1.0):
        self.size = size
        self.num_games = num_games
        self.display = display
        self.results = []
        self.current_game = 0
        self.current_color = 'BLACK'
        self.game_over = False
        self.finished = False
        self.board = None
        self.previous_boards = set()
        # self.mcts_iterations = mcts_iterations
        # self.exploration_weight = exploration_weight
        self.speed = 100
        self.first_turn = True
        # self.expectimax_agent = Expectimax(self.current_color)
        self.random_agent_white = RandomAgent('WHITE')
        self.greedy_agent_white = RandomAgent('WHITE')


    def is_game_over(self) -> bool:
        black_moves = any(self.board.is_legal_move(x, y, 'BLACK') for x in range(self.size) for y in range(self.size))
        white_moves = any(self.board.is_legal_move(x, y, 'WHITE') for x in range(self.size) for y in range(self.size))
        return not black_moves and not white_moves

    def play_game_step(self):
        if self.finished:
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

        if self.current_color == 'BLACK':
            # Monte Carlo strategy:
            move = self.monte_carlo_strategy()

            # Expectimax strategy:
            # move = self.expectimax_strategy()
        else:
            move = self.greedy_agent_white.getAction(self.board)

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
        mcts = MCTS(self.board, self.current_color, mcts_iterations=50, exploration_weight=0.1)
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

    def run(self):
        self.play_game_step()


if __name__ == "__main__":
    size = 5
    num_games = 10

    root = tk.Tk()
    root.title("Go Game")

    display = GoDisplay(root, size)

    game = GoGame(size, num_games, display)
    game.run()

    root.mainloop()
