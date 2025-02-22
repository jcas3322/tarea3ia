from flask import Flask, jsonify, request
from flask_cors import CORS
import numpy as np
import random
from collections import deque

app = Flask(__name__)
CORS(app)  # Habilita CORS en toda la API

def count_inversions(flat_board):
    inv_count = 0
    board_list = [num for num in flat_board if num != 0]
    for i in range(len(board_list)):
        for j in range(i + 1, len(board_list)):
            if board_list[i] > board_list[j]:
                inv_count += 1
    return inv_count

def is_solvable(board):
    flat_board = sum(board, [])
    return count_inversions(flat_board) % 2 == 0

def generate_solvable_puzzle():
    numbers = list(range(9))
    while True:
        random.shuffle(numbers)
        board = [numbers[i:i+3] for i in range(0, 9, 3)]
        if is_solvable(board):
            return board

def find_blank(board):
    for i in range(3):
        for j in range(3):
            if board[i][j] == 0:
                return i, j

def get_neighbors(position):
    row, col = position
    moves = []
    if row > 0: moves.append((-1, 0))
    if row < 2: moves.append((1, 0))
    if col > 0: moves.append((0, -1))
    if col < 2: moves.append((0, 1))
    return moves

def apply_move(board, move):
    new_board = [row[:] for row in board]
    blank_row, blank_col = find_blank(new_board)
    move_row, move_col = move
    new_blank_row, new_blank_col = blank_row + move_row, blank_col + move_col
    new_board[blank_row][blank_col], new_board[new_blank_row][new_blank_col] = new_board[new_blank_row][new_blank_col], new_board[blank_row][blank_col]
    return new_board

def bfs_solve(initial_board):
    goal_state = [[1, 2, 3], [4, 5, 6], [7, 8, 0]]
    queue = deque([(initial_board, [])])
    visited = set()
    while queue:
        board, path = queue.popleft()
        board_tuple = tuple(map(tuple, board))
        if board == goal_state:
            return path
        if board_tuple in visited:
            continue
        visited.add(board_tuple)
        blank_pos = find_blank(board)
        for move in get_neighbors(blank_pos):
            new_board = apply_move(board, move)
            queue.append((new_board, path + [move]))
    return None

initial_board = generate_solvable_puzzle()
solution_path = bfs_solve(initial_board)
current_step = 0

@app.route("/start", methods=["GET"])
def start_game():
    global initial_board, solution_path, current_step
    initial_board = generate_solvable_puzzle()
    solution_path = bfs_solve(initial_board)
    current_step = 0
    return jsonify({"board": initial_board, "finished": False})

@app.route("/next", methods=["GET"])
def next_step():
    global current_step, initial_board
    if current_step >= len(solution_path):
        return jsonify({"board": initial_board, "finished": True})
    initial_board = apply_move(initial_board, solution_path[current_step])
    current_step += 1
    return jsonify({"board": initial_board, "finished": current_step >= len(solution_path)})

if __name__ == "__main__":
    app.run(debug=True)
