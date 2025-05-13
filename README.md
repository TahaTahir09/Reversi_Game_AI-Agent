# Reversi_Game_AI-Agent
This project is a full-featured Reversi (Othello) board game implemented in Python using Tkinter for the GUI and a basic AI opponent powered by Minimax with Alpha-Beta Pruning.

**IMPLEMENTATION**

**1. User Interface (Tkinter GUI)**
The board is built using a canvas grid where discs are drawn based on user and AI moves.
The right-side panel includes:
Player info
Score status
Game rules
Save game option

**2. Game Logic**
The game starts with a traditional 4-piece Reversi setup.
Users click on valid cells to place their disc.
Upon placing a disc:
All flippable opponent discs in all 8 directions are flipped.
The turn switches to the AI if possible.

**3. AI Implementation**
The AI uses the Minimax algorithm with Alpha-Beta pruning to calculate the optimal move. The depth of the search is controlled with a depth limit (default: 3). Evaluation is based on disc count difference between player and AI.

**4. Game Saving & Loading**
Games can be saved with a custom filename and later resumed.
All saved games are stored in a saved_games/ directory as text files.

Saved data includes:
Player name
Current turn
Board state

**Rules of Reversi**
Players take turns placing a disc on the board.
A valid move must outflank one or more opponent discs in a straight line.
All outflanked discs are flipped to the current player's color.
If no valid move is available, the player must pass.
The game ends when neither player can move or the board is full.
The player with the most discs wins.

**Getting Started**
Requirements
Python 3.x
Tkinter (usually bundled with Python)
PIL (Pillow) for image support (optional)
Install Pillow (if needed): bash
pip install pillow

**Project Structure**
├── reversi_game.py           # Main game script
├── player_name.txt           # Stores last used player name
├── high_scores.txt           # Optional for tracking scores
├── saved_games/              # Directory for saved games
├── images.png                # Logo image for GUI
**AI Strategy**
Algorithm: Minimax with Alpha-Beta Pruning

Evaluation Function: player_discs - ai_discs
Adjustable depth for performance vs intelligence

**Screenshots**
![image](https://github.com/user-attachments/assets/805b0e0c-8f38-4888-acdd-b8c88f245eb1)
![image](https://github.com/user-attachments/assets/f87e4737-f587-46d8-b099-a20074550fd3)




