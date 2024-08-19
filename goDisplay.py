import tkinter as tk
from tkinter import messagebox
from typing import List, Dict
from GoBoard import GoBoard

class GoDisplay:

    def __init__(self, root, board_size):
        self.root = root
        self.board_size = board_size

        # Main Frame to hold the board and the captured stones section
        self.main_frame = tk.Frame(root)
        self.main_frame.pack(expand=True, fill='both')

        self.make_board(board_size)
        self.make_captured_stone_board(board_size)
        self.make_game_summary()

        # Draw the initial grid on the board
        self.draw_grid()

    def make_game_summary(self):
        self.game_summary = tk.Frame(self.board_frame)
        self.game_summary.pack(side='bottom', expand=True, fill='both')

    def make_captured_stone_board(self, board_size):
        # Frame for captured stones
        self.captured_frame = tk.Frame(self.main_frame)
        self.captured_frame.pack(side='right', expand=True, fill='both')

        # Canvas for black captured stones
        tk.Label(self.captured_frame, text="Black Captured", font=("Arial", 14)).pack()
        self.black_canvas = tk.Canvas(self.captured_frame, width=300, height=board_size * 30, bg='white')
        self.black_canvas.pack(pady=10)

        # Canvas for white captured stones
        tk.Label(self.captured_frame, text="White Captured", font=("Arial", 14)).pack()
        self.white_canvas = tk.Canvas(self.captured_frame, width=300, height=board_size * 30, bg='white')
        self.white_canvas.pack(pady=10)

    def make_board(self, board_size):
        # Frame for the Go board
        self.board_frame = tk.Frame(self.main_frame)
        self.board_frame.pack(side='left', expand=True, fill='both')

        # Canvas for the Go board
        self.canvas = tk.Canvas(self.board_frame, width=board_size * 60, height=board_size * 60, bg='white')
        self.canvas.pack(expand=True, fill='both')

    def draw_grid(self):
        for i in range(self.board_size):
            self.canvas.create_line(30, 30 + i * 60, 30 + (self.board_size - 1) * 60, 30 + i * 60, fill='black')
            self.canvas.create_line(30 + i * 60, 30, 30 + i * 60, 30 + (self.board_size - 1) * 60, fill='black')

    def draw_captured_stones(self, black_captured, white_captured):
        # Clear the canvas for new drawing
        self.black_canvas.delete("all")
        self.white_canvas.delete("all")

        stones_per_line = 7  # Number of stones per line
        stone_size = 30  # Size of each stone (width and height)
        padding = 10  # Padding between stones
        start_x = 10  # Initial x-coordinate
        start_y = 10  # Initial y-coordinate

        # Draw black captured stones
        for i in range(black_captured):
            row = i // stones_per_line  # Determine the row
            col = i % stones_per_line  # Determine the column
            x0 = start_x + col * (stone_size + padding)
            y0 = start_y + row * (stone_size + padding)
            x1 = x0 + stone_size
            y1 = y0 + stone_size
            self.black_canvas.create_oval(x0, y0, x1, y1, fill='black')

        # Draw white captured stones
        for i in range(white_captured):
            row = i // stones_per_line  # Determine the row
            col = i % stones_per_line  # Determine the column
            x0 = start_x + col * (stone_size + padding)
            y0 = start_y + row * (stone_size + padding)
            x1 = x0 + stone_size
            y1 = y0 + stone_size
            self.white_canvas.create_oval(x0, y0, x1, y1, fill='white', outline='black')

    def display_board(self, board: GoBoard):
        self.canvas.delete("all")
        self.draw_grid()
        for x in range(self.board_size):
            for y in range(self.board_size):
                stone = board.board[x][y]
                if stone:
                    self.draw_stone(x, y, stone)

        self.draw_captured_stones(board.captured['BLACK'], board.captured['WHITE'])

    def draw_stone(self, x: int, y: int, color: str):
        x1, y1 = 30 + x * 60 - 20, 30 + y * 60 - 20
        x2, y2 = x1 + 40, y1 + 40
        self.canvas.create_oval(x1, y1, x2, y2, fill=color.lower(), outline='black')

    def display_results(self, results: List[Dict[str, int]]):
        # Clear previous content in game_summary frame
        for widget in self.game_summary.winfo_children():
            widget.destroy()

        # Create a label to display the results
        # results_str = "\n".join([f"Game {i+1}: BLACK {result['BLACK']}, WHITE {result['WHITE']}" for i, result in enumerate(results)])
        results_str = "\n".join([f"Game {i+1}: {'BLACK' if result['BLACK'] > result['WHITE'] else 'WHITE'}" for i, result in enumerate(results)])
        # messagebox.showinfo("Game Results", results_str)
        tk.Label(self.game_summary, text=results_str, font=("Arial", 14)).pack()