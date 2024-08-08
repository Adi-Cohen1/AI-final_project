import random
from typing import Dict, Optional, Tuple
import tkinter as tk
from GoBoard import GoBoard
from goDisplay import GoDisplay


class GoGame:
    def __init__(self, size: int, num_games: int, display: GoDisplay):
        self.size = size
        self.num_games = num_games
        self.results = []
        self.display = display
        self.current_game = 0
        self.board = None
        self.current_color = 'BLACK'
        self.game_over = False
        self.finished = False  # Flag to ensure we stop after finishing all games

    def random_move(self, board: GoBoard, color: str) -> Optional[Tuple[int, int]]:
        empty_positions = [(x, y) for x in range(self.size) for y in range(self.size) if board.board[x][y] is None]
        if not empty_positions:
            return None
        return random.choice(empty_positions)

    def is_legal_move(self, board: GoBoard, x: int, y: int, color: str) -> bool:
        if board.board[x][y] is not None:
            return False

        board_copy = [row.copy() for row in board.board]
        board_copy[x][y] = color

        for nx, ny in board.get_neighbors(x, y):
            neighbor_color = board_copy[nx][ny]
            if neighbor_color is not None and neighbor_color != color:
                neighbor_group = board.get_group(nx, ny)
                if not board.has_liberties(neighbor_group):
                    return True

        player_group = board.get_group(x, y)
        if not board.has_liberties(player_group):
            return False

        return True

    def is_game_over(self) -> bool:
        black_legal_moves = any(
            self.is_legal_move(self.board, x, y, 'BLACK') for x in range(self.size) for y in range(self.size))
        white_legal_moves = any(
            self.is_legal_move(self.board, x, y, 'WHITE') for x in range(self.size) for y in range(self.size))
        return not black_legal_moves and not white_legal_moves

    def play_game_step(self):
        if self.finished:
            return

        if self.game_over:
            self.end_game()
            return

        if self.board is None:
            self.board = GoBoard(self.size)
            self.current_color = 'BLACK'
            self.display.display_board(self.board)
            self.display.root.after(100, self.play_game_step)
            return

        move = self.random_move(self.board, self.current_color)
        if move is None or not self.is_legal_move(self.board, move[0], move[1], self.current_color):
            if self.board:
                result = self.board.count_score()
                self.results.append(result)
                print(f'Game {self.current_game + 1}: BLACK {result["BLACK"]}, WHITE {result["WHITE"]}')
            self.current_game += 1
            if self.current_game >= self.num_games:
                self.end_game()
                self.finished = True  # Set flag to stop further game processing
            else:
                # Reset game state for the next game
                self.board = None
                self.game_over = False
                self.display.root.after(100, self.play_game_step)
            return

        x, y = move
        if self.board.play_move(x, y, self.current_color):
            self.current_color = 'WHITE' if self.current_color == 'BLACK' else 'BLACK'
            self.display.display_board(self.board)

        if self.is_game_over():
            self.game_over = True

        self.display.root.after(100, self.play_game_step)

    def end_game(self):

        if self.board and self.current_game < self.num_games:
            result = self.board.count_score()
            self.results.append(result)
            print(f'Game {self.current_game + 1} has ended: BLACK {result["BLACK"]}, WHITE {result["WHITE"]}')
            self.display.display_results(self.results)

        if self.current_game < self.num_games:
            self.current_game += 1
            # Reset for the next game
            self.board = None
            self.current_color = 'BLACK'
            self.game_over = False
            self.display.root.after(1000, self.play_game_step)

        else:
            self.finished = True  # Ensure no more games are played

    def run(self):
        self.play_game_step()


if __name__ == "__main__":
    size = 5  # Example size of the board
    num_games = 2  # Example number of games to play

    root = tk.Tk()
    root.title("Go Game")

    display = GoDisplay(root, size)

    game = GoGame(size, num_games, display)
    game.run()

    root.mainloop()
