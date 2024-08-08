import tkinter as tk
from tkinter import messagebox
from typing import List, Dict
from GoBoard import GoBoard

class GoDisplay:
    def __init__(self, root, board_size):
        self.root = root
        self.board_size = board_size
        self.canvas = tk.Canvas(root, width=board_size * 30, height=board_size * 30)
        self.canvas.pack()
        self.draw_grid()

    def draw_grid(self):
        for i in range(self.board_size):
            self.canvas.create_line(15, 15 + i * 30, 15 + (self.board_size - 1) * 30, 15 + i * 30)
            self.canvas.create_line(15 + i * 30, 15, 15 + i * 30, 15 + (self.board_size - 1) * 30)

    def place_stone(self, x, y, color):
        if color == 'BLACK':
            self.canvas.create_oval(15 + x * 30 - 10, 15 + y * 30 - 10, 15 + x * 30 + 10, 15 + y * 30 + 10, fill='black', tags="stone")
        elif color == 'WHITE':
            self.canvas.create_oval(15 + x * 30 - 10, 15 + y * 30 - 10, 15 + x * 30 + 10, 15 + y * 30 + 10, fill='white', tags="stone")

    def display_board(self, board: GoBoard):
        self.canvas.delete("stone")
        for x in range(self.board_size):
            for y in range(self.board_size):
                if board.board[x][y] == 'BLACK':
                    self.place_stone(x, y, 'BLACK')
                elif board.board[x][y] == 'WHITE':
                    self.place_stone(x, y, 'WHITE')

    def display_results(self, results: List[Dict[str, int]]):
        result_message = "\n".join([f'Game {i+1}: BLACK {result["BLACK"]}, WHITE {result["WHITE"]}' for i, result in enumerate(results)])
        messagebox.showinfo("Game Results", result_message)
