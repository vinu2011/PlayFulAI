import tkinter as tk
from tkinter import messagebox, scrolledtext
import chess
import chess.engine
import random
import google.generativeai as genai

# Configure Gemini API Key (replace with your actual key)
genai.configure(api_key="AIzaSyBVTH5GZUW3ieg9WZQadpoXVAv0afWkaNs")

# Lc0 engine path
ENGINE_PATH = "/usr/local/bin/lc0"

# Weights paths
WEIGHTS = {
    "aggressive": "lc0-v0.31.2-windows-gpu-nvidia-cuda/791556.pb/aggressive.pb",
    "balanced": "lc0-v0.31.2-windows-gpu-nvidia-cuda/791556.pb/192x15-2022_0418_1738_54_779.pb",
    "defensive": "lc0-v0.31.2-windows-gpu-nvidia-cuda/791556.pb/defensive.pb",
}

# Start LC0 engine
engine = chess.engine.SimpleEngine.popen_uci(ENGINE_PATH)

def analyze_player_moves(player_moves):
    """Analyze the user's first 3 moves to decide if they're aggressive, defensive, or balanced."""
    aggressive_squares = {"e4", "d4", "c4", "f4", "g4"}
    defensive_squares = {"e3", "d3", "g3", "b3", "h3"}
    aggressive_count = sum(1 for move in player_moves if move[2:4] in aggressive_squares)
    defensive_count = sum(1 for move in player_moves if move[2:4] in defensive_squares)
    if aggressive_count >= 2:
        return "aggressive"
    elif defensive_count >= 2:
        return "defensive"
    else:
        return "balanced"

def get_best_move(board, time_limit):
    """Ask LC0 for its best move given a time limit."""
    result = engine.play(board, chess.engine.Limit(time=10))
    return result.move.uci()

def explain_ai_move(fen, move):
    """Generate an explanation for the AI's move using Gemini."""
    prompt = f"Chess board position: {fen}. AI played {move}. Why is this a strong move based on the position?"
    model = genai.GenerativeModel("gemini-1.5-flash")
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Error in explanation: {str(e)}"

def suggest_best_moves(board, last_player_move):
    """Suggest the top 3 moves the user could have played, with explanations from Gemini."""
    analysis = engine.analyse(board, chess.engine.Limit(time=1.0), multipv=3)
    best_moves = [(info["pv"][0].uci(), info["score"].relative.score()) for info in analysis]
    explanations = []
    model = genai.GenerativeModel("gemini-1.5-flash")
    for move, _ in best_moves:
        prompt = (f"Chess position: {board.fen()}. The player moved {last_player_move}, "
                  f"but a stronger move was {move}. Explain in 1 line why {move} is a better choice based on future moves prediction and it should be short and simple for even 8 year old to understand. ")
        try:
            response = model.generate_content(prompt)
            explanation = response.text.strip()
        except Exception as e:
            explanation = f"Error generating explanation: {str(e)}"
        explanations.append((move, explanation))
    return explanations

# Mapping piece symbols (from python-chess) to Unicode
piece_to_unicode = {
    "P": "♙", "R": "♖", "N": "♘", "B": "♗", "Q": "♕", "K": "♔",
    "p": "♟", "r": "♜", "n": "♞", "b": "♝", "q": "♛", "k": "♚"
}
