# Go Game AI
This project implements an AI to play the game of Go with various strategies for both black and white players. The AI can be customized with different strategies for each player, and it allows you to run multiple games.

# Requirements
- Python 3.x
- Install required packages (if any) by running:
  ```bash
  pip install -r requirements.txt
  ```

# Running the Project
To run the Go Game AI, use the following command in your terminal:
  ```python
  python goGameAI.py <BLACK-STRATEGY> <WHITE-STRATEGY> <NUMBER-OF-GAMES> <DISPLAY-BOARD>
  ```

# Arguments
- **BLACK-STRATEGY**: The strategy for the black player. Choose from:
  - `random`
  - `greedy`
  - `minimax`
  - `alpha_beta` (Minimax with runtime efficiency)
  - `expectimax`
  - `monte_carlo`
  - `qlearn`
    
- **WHITE-STRATEGY**: The strategy for the white player. Choose from:
  - `random`
  - `greedy`
    
- **NUMBER-OF-GAMES**: A positive integer representing how many games you want to simulate.
  
- **DISPLAY-BOARD**: Choose whether to display the game board or not:
  - `display`
  - `not_display`
