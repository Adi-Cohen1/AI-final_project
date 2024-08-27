import tkinter as tk
from PIL import Image, ImageTk
from typing import List, Dict
from GoBoard import GoBoard

class GoDisplay:

    def __init__(self, root, board_size):
        self.root = root
        self.board_size = board_size
        self.num_wins_by_games = {"BLACK": 0, "WHITE": 0, "TIE":0}
        # Main Frame to hold the board and the captured stones section
        self.main_frame = tk.Frame(root)
        self.main_frame.pack(expand=True, fill='both')

        # Load images
        self.board_image = Image.open("wooden_board.jpg")  # Replace with your image path
        self.board_image = self.board_image.resize((board_size * 60, board_size * 60))
        self.board_photo = ImageTk.PhotoImage(self.board_image)

        self.black_stone_image = Image.open("black_piece.png")  # Replace with your image path
        self.black_stone_photo = ImageTk.PhotoImage(self.black_stone_image.resize((40, 40)))

        self.white_stone_image = Image.open("white_piece.png")  # Replace with your image path
        self.white_stone_photo = ImageTk.PhotoImage(self.white_stone_image.resize((40, 40)))

        self.make_board(board_size)
        self.make_captured_stone_board(board_size)
        self.make_game_summary()

        # Draw the initial grid on the board
        self.draw_grid()

    def make_game_summary(self):
        self.game_summary = tk.Frame(self.board_frame, bg="white")
        self.game_summary.pack(side='bottom', expand=True, fill='both')

    def make_captured_stone_board(self, board_size):
        # Frame for captured stones
        self.captured_frame = tk.Frame(self.main_frame, bg='navajo white')#
        self.captured_frame.pack(side='right', expand=True, fill='both')

        # Canvas for black captured stones
        tk.Label(self.captured_frame, text="Black Captured", font=("Arial", 14), bg="navajo white").pack()#
        self.black_canvas = tk.Canvas(self.captured_frame, width=300, height=board_size * 40, bg='white')
        self.black_canvas.pack(pady=10, expand=True, fill='both')

        # Canvas for white captured stones
        tk.Label(self.captured_frame, text="White Captured", font=("Arial", 14), bg="navajo white").pack()
        self.white_canvas = tk.Canvas(self.captured_frame, width=300, height=board_size * 40, bg='white')
        self.white_canvas.pack(pady=10, expand=True, fill='both')


    def make_board(self, board_size):
        # Frame for the Go board
        self.board_frame = tk.Frame(self.main_frame)
        self.board_frame.pack(side='left', expand=True, fill='both')

        # Canvas for the Go board
        self.canvas = tk.Canvas(self.board_frame, width=board_size * 60, height=board_size * 60, bg='white')
        self.canvas.pack(expand=False, fill='both')

        # Draw the wooden board image as the background
        self.canvas.create_image(0, 0, anchor='nw', image=self.board_photo)

    def draw_grid(self):

        line_width = 3  # Adjust this value to make the lines thicker
        for i in range(self.board_size):
            self.canvas.create_line(30, 30 + i * 60, 30 + (self.board_size - 1) * 60, 30 + i * 60, fill='black',
                                    width=line_width)
            self.canvas.create_line(30 + i * 60, 30, 30 + i * 60, 30 + (self.board_size - 1) * 60, fill='black',
                                    width=line_width)

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
            self.black_canvas.create_image(x0, y0, anchor='nw', image=self.black_stone_photo)

        # Draw white captured stones
        for i in range(white_captured):
            row = i // stones_per_line  # Determine the row
            col = i % stones_per_line  # Determine the column
            x0 = start_x + col * (stone_size + padding)
            y0 = start_y + row * (stone_size + padding)
            x1 = x0 + stone_size
            y1 = y0 + stone_size
            self.white_canvas.create_image(x0, y0, anchor='nw', image=self.white_stone_photo)

    def display_board(self, board: GoBoard):
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor='nw', image=self.board_photo)
        self.draw_grid()
        for x in range(self.board_size):
            for y in range(self.board_size):
                stone = board.board[x][y]
                if stone:
                    self.draw_stone(x, y, stone)

        self.draw_captured_stones(board.captured['BLACK'], board.captured['WHITE'])
        for widget in self.game_summary.winfo_children():
            widget.destroy()
        results_str = self.get_score_summary()
        tk.Label(self.game_summary, text=results_str, font=("Arial",14), bg="white").pack(expand=True)

    def draw_stone(self, x: int, y: int, color: str):
        x1, y1 = 30 + x * 60 - 20, 30 + y * 60 - 20
        if color.lower() == 'black':
            self.canvas.create_image(x1, y1, anchor='nw', image=self.black_stone_photo)
        elif color.lower() == 'white':
            self.canvas.create_image(x1, y1, anchor='nw', image=self.white_stone_photo)

    def get_winner_name(self, result):
        if result['BLACK'] > result['WHITE']:
            return "BLACK"
        elif result['BLACK'] < result['WHITE']:
            return "WHITE"
        else:
            return "TIE"

    def get_score_summary(self):
        black_score = str(self.num_wins_by_games["BLACK"])
        white_score = str(self.num_wins_by_games["WHITE"])
        tie_score = str(self.num_wins_by_games["TIE"])
        return "BLACK: " + black_score + "\nWHITE: " + white_score + "\nTIE: " + tie_score

    def display_results(self, results: List[Dict[str, int]]):
        # Clear previous content in game_summary frame
        for widget in self.game_summary.winfo_children():
            widget.destroy()

        # Create a label to display the results
        # results_str = "\n".join([f"Game {i+1}: BLACK {result['BLACK']}, WHITE {result['WHITE']}" for i, result in enumerate(results)])
        # results_str = "\n".join([f"Game {i+1}: {self.get_winner_name(result)}" for i, result in enumerate(results)])
        curr_winner = self.get_winner_name(results[-1])
        self.num_wins_by_games[curr_winner] += 1
        results_str = self.get_score_summary()

        # messagebox.showinfo("Game Results", results_str)
        tk.Label(self.game_summary, text=results_str, font=("Arial",14), bg="white").pack(expand=True)