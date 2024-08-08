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
            self.canvas.create_line(15, 15 + i * 30, 15 + (self.board_size - 1) * 30, 15 + i * 30, fill='black')
            self.canvas.create_line(15 + i * 30, 15, 15 + i * 30, 15 + (self.board_size - 1) * 30, fill='black')

    def display_board(self, board: GoBoard):
        self.canvas.delete("all")
        self.draw_grid()
        for x in range(self.board_size):
            for y in range(self.board_size):
                stone = board.board[x][y]
                if stone:
                    self.draw_stone(x, y, stone)

    def draw_stone(self, x: int, y: int, color: str):
        x1, y1 = 15 + x * 30 - 13, 15 + y * 30 - 13
        x2, y2 = x1 + 26, y1 + 26
        self.canvas.create_oval(x1, y1, x2, y2, fill=color.lower(), outline='black')

    def display_results(self, results: List[Dict[str, int]]):
        results_str = "\n".join([f"Game {i+1}: BLACK {result['BLACK']}, WHITE {result['WHITE']}" for i, result in enumerate(results)])
        messagebox.showinfo("Game Results", results_str)
