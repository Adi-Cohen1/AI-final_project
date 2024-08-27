import random
from typing import Optional, Tuple
import tkinter as tk

import numpy as np

from GoBoard import GoBoard
from goDisplay import GoDisplay
from Agents import RandomAgent,GreedyAgent
import matplotlib.pyplot as plt


SPEED = 5000

class GoGame:
    def __init__(self, size: int, num_games: int, display: GoDisplay):
        self.size = size
        self.num_games = num_games
        self.display = display
        self.results = []
        self.current_game = 0
        self.current_color = 'BLACK'  # first player
        self.game_over = False
        self.finished = False  # Flag to ensure we stop after finishing all games
        self.board = None
        self.previous_boards = set()  # To keep track of board states for ko detection
        self.handicap_stones = []  # List to hold handicap stones
        self.random_agent_white = RandomAgent('WHITE')
        self.random_agent_black = GreedyAgent('BLACK')
        self.black_wins = 0
        self.white_wins = 0
        self.result_black = []
        self.result_white = []

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
            self.current_color = 'BLACK'  # BLACK is the first player, I think it's duplicate code
            self.display.display_board(self.board)
            self.display.root.after(SPEED, self.play_game_step)  # like callback function
            return
        move = RandomAgent(self.current_color).getAction(self.board)
        # move = self.board.random_move(self.current_color)
        if move is None:
            # If no move is possible, end the game
            if self.board:
                result = self.board.count_score()
                self.results.append(result)
                self.update_statistics(result)

                print(f'Game {self.current_game + 1}: BLACK {result["BLACK"]}, WHITE {result["WHITE"]}')
                self.display.display_results(self.results)

            self.current_game += 1
            if self.current_game >= self.num_games:
                self.end_game()
                self.finished = True  # Stop further game processing
            else:
                # Reset for the next game
                self.reset_game()
                # self.board = None
                # self.game_over = False
                # self.previous_boards.clear()  # Clear previous board states for ko rule
                # self.display.root.after(SPEED, self.play_game_step)
            return

        x, y = move
        if self.board.play_move(x, y, self.current_color):
            self.previous_boards.add(tuple(map(tuple, self.board.board)))  # Track board state
            self.current_color = 'WHITE' if self.current_color == 'BLACK' else 'BLACK'
            self.display.display_board(self.board)

        if self.is_game_over():
            self.game_over = True

        self.display.root.after(SPEED, self.play_game_step)

    def reset_game(self):
        self.board = None
        self.current_color = 'BLACK'
        self.game_over = False
        self.previous_boards.clear()
        self.display.root.after(SPEED, self.play_game_step)

    def update_statistics(self, result):
        self.result_black.append(self.board.captured['BLACK'])
        self.result_white.append(self.board.captured['WHITE'])

        if result["BLACK"] > result["WHITE"]:
            self.black_wins += 1
        else:
            self.white_wins += 1


    def end_game(self):
        if self.board and self.current_game < self.num_games:
            result = self.board.count_score()
            self.results.append(result)

            print(f'Game {self.current_game + 1} has ended: BLACK {result["BLACK"]}, WHITE {result["WHITE"]}')
            self.display.display_results(self.results)

        if self.current_game < self.num_games:
            self.current_game += 1
            # Reset for the next game
            self.reset_game()
            # self.board = None
            # self.current_color = 'BLACK'
            # self.game_over = False
            # self.previous_boards.clear()
            # self.display.root.after(SPEED, self.play_game_step)
        else:
            self.finished = True  # Ensure no more games are played
            self.visualize_statistics()

    def visualize_statistics(self):
        labels = ['Black Wins', 'White Wins']
        wins = [self.black_wins, self.white_wins]

        # Plotting the pie chart
        plt.figure(figsize=(8, 8))
        plt.pie(wins, labels=labels, colors=['black', 'green'], autopct='%1.1f%%', startangle=140)
        plt.title(f'Results After {self.num_games} Games')
        plt.show()

        # Data for the second plot (Captured Stones Over Time)
        plt.figure(figsize=(12, 6))
        plt.plot(range(len(self.result_black)), self.result_black, label='Black Captured', color='black')
        plt.plot(range(len(self.result_white)), self.result_white, label='White Captured', color='green')
        plt.xlabel('Game Number')
        plt.ylabel('Score')
        plt.title(f'Score Over {self.num_games} Games')
        plt.legend()
        plt.show()





    def run(self):
        self.play_game_step()

if __name__ == "__main__":
    size = 5  # Example size of the board
    num_games = 100  # Example number of games to play

    root = tk.Tk()
    root.title("Go Game")

    display = GoDisplay(root, size)

    game = GoGame(size, num_games, display)
    game.run()

    root.mainloop()
