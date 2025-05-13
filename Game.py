import tkinter as tk
from tkinter import simpledialog
import os
import random
import copy
from PIL import Image, ImageTk
from datetime import datetime

# --- Constants ---
PLAYER_NAME_FILE = "player_name.txt"
HIGH_SCORE_FILE = "high_scores.txt"
SAVED_GAMES_DIR = "saved_games"
PLAYER = "B"
AI = "W"
EMPTY = None
GRID_SIZE = 12
CELL_SIZE = 50
DEPTH_LIMIT = 3

if not os.path.exists(SAVED_GAMES_DIR):
    os.makedirs(SAVED_GAMES_DIR)

def save_player_name(name):
    with open(PLAYER_NAME_FILE, "w") as file:
        file.write(name)

def load_player_name():
    if os.path.exists(PLAYER_NAME_FILE):
        with open(PLAYER_NAME_FILE, "r") as file:
            return file.read().strip()
    return None

def save_game(board, current_turn, player_name, filename):
    filepath = os.path.join(SAVED_GAMES_DIR, f"{filename}.txt")
    with open(filepath, "w") as file:
        file.write(player_name + "\n")
        file.write(current_turn + "\n")
        for row in board:
            file.write(",".join([str(cell) if cell is not None else "None" for cell in row]) + "\n")
    return filepath

def load_game(filepath):
    if os.path.exists(filepath):
        with open(filepath, "r") as file:
            player_name = file.readline().strip()
            current_turn = file.readline().strip()
            board = []
            for _ in range(GRID_SIZE):
                row = file.readline().strip().split(",")
                board.append([PLAYER if cell == "B" else AI if cell == "W" else None for cell in row])
            return player_name, current_turn, board
    return None, None, None

def list_saved_games():
    return [f for f in os.listdir(SAVED_GAMES_DIR) if f.endswith(".txt")]

def valid_moves(board, player):
    moves = []
    for x in range(GRID_SIZE):
        for y in range(GRID_SIZE):
            if is_valid_move(board, player, x, y):
                moves.append((x, y))
    return moves

def is_valid_move(board, player, x, y):
    if board[x][y] is not None:
        return False

    opponent = AI if player == PLAYER else PLAYER
    directions = [(-1, -1), (-1, 0), (-1, 1),
                  (0, -1),         (0, 1),
                  (1, -1), (1, 0), (1, 1)]

    for dx, dy in directions:
        nx, ny = x + dx, y + dy
        found_opponent = False
        while 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE:
            if board[nx][ny] == opponent:
                found_opponent = True
            elif board[nx][ny] == player:
                if found_opponent:
                    return True
                else:
                    break
            else:
                break
            nx += dx
            ny += dy
    return False

def apply_move(board, player, x, y):
    opponent = AI if player == PLAYER else PLAYER
    directions = [(-1, -1), (-1, 0), (-1, 1),
                  (0, -1),         (0, 1),
                  (1, -1), (1, 0), (1, 1)]

    board[x][y] = player

    for dx, dy in directions:
        nx, ny = x + dx, y + dy
        path = []
        while 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE:
            if board[nx][ny] == opponent:
                path.append((nx, ny))
            elif board[nx][ny] == player:
                for px, py in path:
                    board[px][py] = player
                break
            else:
                break
            nx += dx
            ny += dy

def score(board):
    p = sum(row.count(PLAYER) for row in board)
    a = sum(row.count(AI) for row in board)
    return p - a

def minimax(board, depth, maximizingPlayer, alpha, beta):
    if depth == 0 or (not valid_moves(board, PLAYER) and not valid_moves(board, AI)):
        return score(board), None

    player = AI if maximizingPlayer else PLAYER
    moves = valid_moves(board, player)

    if not moves:
        return minimax(board, depth-1, not maximizingPlayer, alpha, beta)

    if maximizingPlayer:
        maxEval = float('-inf')
        best_move = None
        for move in moves:
            new_board = copy.deepcopy(board)
            apply_move(new_board, player, move[0], move[1])
            eval, _ = minimax(new_board, depth-1, False, alpha, beta)
            if eval > maxEval:
                maxEval = eval
                best_move = move
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        return maxEval, best_move
    else:
        minEval = float('inf')
        best_move = None
        for move in moves:
            new_board = copy.deepcopy(board)
            apply_move(new_board, player, move[0], move[1])
            eval, _ = minimax(new_board, depth-1, True, alpha, beta)
            if eval < minEval:
                minEval = eval
                best_move = move
            beta = min(beta, eval)
            if beta <= alpha:
                break
        return minEval, best_move

class ReversiGame:
    def __init__(self, player_name, current_turn=None, board=None):
        self.player_name = player_name
        self.current_turn = current_turn if current_turn else PLAYER
        self.board = board if board else [[EMPTY for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]

        if not board:
            mid = GRID_SIZE // 2
            self.board[mid-1][mid-1] = AI
            self.board[mid][mid] = AI
            self.board[mid-1][mid] = PLAYER
            self.board[mid][mid-1] = PLAYER

        self.game_window = tk.Toplevel(root)
        self.game_window.title("Reversi Game")
        self.game_window.state('zoomed')

        self.main_frame = tk.Frame(self.game_window)
        self.main_frame.pack(fill="both", expand=True)

        global CELL_SIZE
        CELL_SIZE = 60

        canvas_width = CELL_SIZE * GRID_SIZE
        canvas_height = CELL_SIZE * GRID_SIZE
        
        self.canvas = tk.Canvas(self.main_frame, bg="forest green", width=canvas_width, height=canvas_height)
        # --- Increased padx significantly ---
        self.canvas.pack(side="left", padx=60, pady=20, fill="both", expand=True)


        self.info_frame = tk.Frame(self.main_frame, bg="#e0f7fa", width=350)
        self.info_frame.pack(side="left", fill="both", expand=True)

        self.player_label = tk.Label(self.info_frame, text=f"{self.player_name} (Black)", font=("Arial", 18), bg="#e0f7fa", fg="black")
        self.player_label.pack(pady=10)

        self.ai_label = tk.Label(self.info_frame, text="AI Agent (White)", font=("Arial", 18), bg="#e0f7fa", fg="black")
        self.ai_label.pack(pady=10)

        self.status = tk.Label(self.info_frame, text="", font=("Arial", 16), bg="#e0f7fa", fg="black")
        self.status.pack(pady=15)

        self.save_name_entry = tk.Entry(self.info_frame, font=("Arial", 14))
        self.save_name_entry.pack(pady=10)

        self.save_button = tk.Button(self.info_frame, text="Save Game", font=("Arial", 14), bg="#00acc1", fg="white", command=self.save_game)
        self.save_button.pack(pady=10)

        self.result_label = tk.Label(self.info_frame, text="", font=("Arial", 16, "bold"), bg="#e0f7fa", fg="#004d40")
        self.result_label.pack(pady=20)

        self.rules_frame = tk.Frame(self.info_frame, bg="#e0f7fa", bd=2, relief=tk.GROOVE)
        self.rules_frame.pack(side="bottom", fill="x", padx=10, pady=10)

        rules_text = """
        Reversi Rules:
        \u2022 Players alternate turns placing discs.
        \u2022 A valid move captures opponent's discs.
        \u2022 Captured discs are flipped to your color.
        \u2022 To capture, your disc must bracket one or more opponent's discs in a straight line (horizontally,
          vertically, or diagonally).
        \u2022 The game ends when the board is full or no more valid moves exist.
        \u2022 The player with the most discs wins.
        """
        rules_label = tk.Label(self.rules_frame, text=rules_text, font=("Arial", 12), bg="#e0f7fa", justify=tk.LEFT)
        rules_label.pack(padx=5, pady=5)

        try:
            logo_img = Image.open("images.png").resize((150, 150), Image.Resampling.LANCZOS)
            logo_photo = ImageTk.PhotoImage(logo_img)
            self.logo_label = tk.Label(self.info_frame, image=logo_photo, bg="#e0f7fa")
            self.logo_label.image = logo_photo
            self.logo_label.pack(pady=15)
        except:
            pass

        self.canvas.bind("<Button-1>", self.click)

        self.draw_board()
        self.update_status()
            
    def save_game(self):
        filename = self.save_name_entry.get().strip()
        if filename:
            save_game(self.board, self.current_turn, self.player_name, filename)
            self.result_label.config(text=f"Game Saved: {filename}")
        else:
            self.result_label.config(text="Enter filename first!")
    def draw_board(self):
        self.canvas.delete("all")
        for i in range(GRID_SIZE):
            # Draw row numbers on the left
            x_text_left = 25  # More spacing from the left
            y_text_row = i * CELL_SIZE + CELL_SIZE // 2
            self.canvas.create_text(x_text_left, y_text_row, text=str(i + 1), font=("Arial", 10), fill="black", anchor="w")

            # Draw row numbers on the right
            x_text_right = GRID_SIZE * CELL_SIZE + 25 # More spacing from the right of the board
            y_text_row = i * CELL_SIZE + CELL_SIZE // 2
            self.canvas.create_text(x_text_right, y_text_row, text=str(i + 1), font=("Arial", 10), fill="black", anchor="e")

            for j in range(GRID_SIZE):
                x1 = j * CELL_SIZE
                y1 = i * CELL_SIZE
                x2 = x1 + CELL_SIZE
                y2 = y1 + CELL_SIZE
                self.canvas.create_rectangle(x1, y1, x2, y2, outline="black", fill="forest green")
                if self.board[i][j] == PLAYER:
                    self.canvas.create_oval(x1+5, y1+5, x2-5, y2-5, fill="black")
                elif self.board[i][j] == AI:
                    self.canvas.create_oval(x1+5, y1+5, x2-5, y2-5, fill="white")

        # Draw column letters at the top
        for j in range(GRID_SIZE):
            x_text_col = j * CELL_SIZE + CELL_SIZE // 2
            y_text_col = 15  # Adjusted top spacing
            self.canvas.create_text(x_text_col, y_text_col, text=chr(ord('A') + j), font=("Arial", 10), fill="black", anchor="s")
            
    def click(self, event):
        if self.current_turn != PLAYER:
            return

        col = event.x // CELL_SIZE
        row = event.y // CELL_SIZE

        if 0 <= row < GRID_SIZE and 0 <= col < GRID_SIZE and is_valid_move(self.board, PLAYER, row, col):
            apply_move(self.board, PLAYER, row, col)
            self.current_turn = AI
            self.draw_board()
            self.update_status()
            self.game_window.after(500, self.ai_move)

    def ai_move(self):
        if self.current_turn != AI:
            return

        _, move = minimax(self.board, DEPTH_LIMIT, True, float('-inf'), float('inf'))
        if move:
            apply_move(self.board, AI, move[0], move[1])
        self.current_turn = PLAYER
        self.draw_board()
        self.update_status()

    def update_status(self):
        p_moves = valid_moves(self.board, PLAYER)
        a_moves = valid_moves(self.board, AI)

        if not p_moves and not a_moves:
            self.end_game()
        elif self.current_turn == PLAYER and not p_moves:
            self.current_turn = AI
            self.game_window.after(500, self.ai_move)
        elif self.current_turn == AI and not a_moves:
            self.current_turn = PLAYER

        p_count = sum(row.count(PLAYER) for row in self.board)
        a_count = sum(row.count(AI) for row in self.board)

        self.status.config(text=f"{self.player_name}: {p_count}   |   AI: {a_count}")

    def end_game(self):
        p_score = sum(row.count(PLAYER) for row in self.board)
        a_score = sum(row.count(AI) for row in self.board)
        winner = self.player_name if p_score > a_score else "AI"

        self.result_label.config(text=f"Winner: {winner} (You: {p_score} / AI: {a_score})")
        self.save_score(winner, p_score if winner == self.player_name else a_score)

    def save_score(self, winner, score):
        with open(HIGH_SCORE_FILE, "a") as f:
            f.write(f"{winner}: {score}\n")

# Menu Functions
def start_new_game():
    name_window = tk.Toplevel(root)
    name_window.title("Enter Your Name")
    name_window.geometry("400x300")
    name_window.configure(bg="#e0f7fa")
    name_window.grab_set()

    tk.Label(name_window, text="Enter Your Name", font=("Arial", 18, "bold"), bg="#e0f7fa", fg="#006064").pack(pady=20)
    name_entry = tk.Entry(name_window, font=("Arial", 16))
    name_entry.pack(pady=10)

    feedback = tk.Label(name_window, text="", font=("Arial", 14), bg="#e0f7fa", fg="red")
    feedback.pack()

    def submit_name():
        player_name = name_entry.get().strip()
        if not player_name:
            feedback.config(text="Name cannot be empty!")
        else:
            save_player_name(player_name)
            name_window.destroy()
            ReversiGame(player_name)

    tk.Button(name_window, text="Submit", font=("Arial", 14), bg="#0288d1", fg="white", command=submit_name).pack(pady=20)

def load_previous_game():
    games = list_saved_games()
    if not games:
        return

    load_window = tk.Toplevel(root)
    load_window.title("Load Saved Game")
    load_window.geometry("400x400")
    load_window.configure(bg="#e0f7fa")
    load_window.grab_set()

    tk.Label(load_window, text="Select Saved Game", font=("Arial", 18, "bold"), bg="#e0f7fa").pack(pady=20)

    var = tk.StringVar(load_window)
    var.set(games[0])
    tk.OptionMenu(load_window, var, *games).pack(pady=10)

    def load_selected():
        path = os.path.join(SAVED_GAMES_DIR, var.get())
        player_name, current_turn, board = load_game(path)
        if player_name:
            load_window.destroy()
            ReversiGame(player_name, current_turn, board)

    tk.Button(load_window, text="Load Game", font=("Arial", 14), bg="#0288d1", fg="white", command=load_selected).pack(pady=20)

def view_high_scores():
    if not os.path.exists(HIGH_SCORE_FILE):
        return

    hs_window = tk.Toplevel(root)
    hs_window.title("High Scores")
    hs_window.geometry("400x400")
    hs_window.configure(bg="#e0f7fa")
    hs_window.grab_set()

    with open(HIGH_SCORE_FILE, "r") as f:
        scores = f.readlines()

    tk.Label(hs_window, text="High Scores", font=("Arial", 18, "bold"), bg="#e0f7fa").pack(pady=20)

    for score in scores:
        tk.Label(hs_window, text=score.strip(), font=("Arial", 14), bg="#e0f7fa").pack()

def exit_game():
    root.quit()

# Main Menu UI
root = tk.Tk()
root.title("Reversi Game")
root.state("zoomed")
root.bind("<Escape>", lambda e: root.attributes("-fullscreen", False))

bg_img = Image.open("back.jpg").resize((1920, 1080), Image.Resampling.LANCZOS)
bg_photo = ImageTk.PhotoImage(bg_img)

bg_canvas = tk.Canvas(root, width=1920, height=1080)
bg_canvas.pack(fill="both", expand=True)
bg_canvas.create_image(0, 0, image=bg_photo, anchor="nw")
root.bg_photo = bg_photo

button_style = {'font': ("Arial", 16), 'bg': "#0288d1", 'fg': "white", 'width': 20}

logo_img = Image.open("images.png").resize((150, 150), Image.Resampling.LANCZOS)
logo_photo = ImageTk.PhotoImage(logo_img)
logo_label = tk.Label(root, image=logo_photo, bg="#ffffff")
logo_label.image = logo_photo
logo_label.place(relx=0.5, rely=0.2, anchor='center')

title_label = tk.Label(root, text="Reversi", font=("Cabin Sketch", 30, "bold"), fg="#000000")
title_label.place(relx=0.5, rely=0.35, anchor='center')

tk.Button(root, text="Start New Game", command=start_new_game, **button_style).place(relx=0.5, rely=0.50, anchor='center')
tk.Button(root, text="Load Saved Game", command=load_previous_game, **button_style).place(relx=0.5, rely=0.60, anchor='center')
tk.Button(root, text="View High Scores", command=view_high_scores, **button_style).place(relx=0.5, rely=0.70, anchor='center')
tk.Button(root, text="Exit", command=exit_game, **button_style).place(relx=0.5, rely=0.80, anchor='center')

root.mainloop()
