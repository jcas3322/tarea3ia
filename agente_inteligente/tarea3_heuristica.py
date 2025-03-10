from flask import Flask, jsonify, request
from flask_cors import CORS
import numpy as np
import random
import heapq

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
    if row > 0: 
        moves.append((-1, 0))  # Arriba
    if row < 2: 
        moves.append((1, 0))   # Abajo
    if col > 0: 
        moves.append((0, -1))  # Izquierda
    if col < 2: 
        moves.append((0, 1))   # Derecha
    return moves

def apply_move(board, move):
    new_board = [row[:] for row in board]  # Copia profunda
    blank_row, blank_col = find_blank(new_board)
    move_row, move_col = move
    new_blank_row, new_blank_col = blank_row + move_row, blank_col + move_col
    # Intercambiar el valor del hueco (0) con la ficha a la que movemos
    new_board[blank_row][blank_col], new_board[new_blank_row][new_blank_col] = \
        new_board[new_blank_row][new_blank_col], new_board[blank_row][blank_col]
    return new_board

def manhattan_distance(board):
    """
    Heurística de distancia Manhattan para el 8-puzzle.
    Suma la distancia de cada ficha a su posición objetivo, ignorando el hueco (0).
    """
    distance = 0
    for i in range(3):
        for j in range(3):
            val = board[i][j]
            if val != 0:
                # Cálculo de la posición objetivo (goal_i, goal_j) para el valor val
                goal_i = (val - 1) // 3
                goal_j = (val - 1) % 3
                distance += abs(goal_i - i) + abs(goal_j - j)
    return distance

def a_star_solve(initial_board):
    """
    Resuelve el 8-puzzle usando A* con distancia Manhattan como heurística.
    Devuelve la secuencia de movimientos (tuplas) para llegar al estado objetivo.
    """
    goal_state = [[1, 2, 3],
                  [4, 5, 6],
                  [7, 8, 0]]

    # Cada entrada de open_list: (f_score, g_score, board, path)
    # f_score = g_score + h (heurística)
    start_h = manhattan_distance(initial_board)
    open_list = [(start_h, 0, initial_board, [])]
    visited = set()

    while open_list:
        f_score, g_score, current_board, path = heapq.heappop(open_list)

        if current_board == goal_state:
            return path  # ¡Encontramos la solución!

        board_tuple = tuple(map(tuple, current_board))
        if board_tuple in visited:
            continue
        visited.add(board_tuple)

        # Expandir vecinos
        blank_pos = find_blank(current_board)
        for move in get_neighbors(blank_pos):
            new_board = apply_move(current_board, move)
            new_g = g_score + 1
            new_h = manhattan_distance(new_board)
            new_f = new_g + new_h
            heapq.heappush(open_list, (new_f, new_g, new_board, path + [move]))

    # Si no se encuentra solución (no debería suceder si el tablero es resoluble)
    return None

# Variables globales para el manejo del juego
initial_board = []
solution_path = []
current_step = 0

@app.route("/start", methods=["GET"])
def start_game():
    """Genera un nuevo tablero solvable y calcula la ruta de solución con A*."""
    global initial_board, solution_path, current_step
    initial_board = generate_solvable_puzzle()
    solution_path = a_star_solve(initial_board)
    current_step = 0
    # Devolvemos el tablero inicial y un indicador de que aún no está terminado
    return jsonify({"board": initial_board, "finished": False})

@app.route("/next", methods=["GET"])
def next_step():
    """
    Aplica el siguiente movimiento de la ruta de solución al tablero actual.
    Si ya no hay más movimientos, indica que el juego está terminado.
    """
    global current_step, initial_board, solution_path
    if current_step >= len(solution_path):
        return jsonify({"board": initial_board, "finished": True})
    
    move = solution_path[current_step]
    initial_board = apply_move(initial_board, move)
    current_step += 1
    
    return jsonify({
        "board": initial_board,
        "finished": current_step >= len(solution_path)
    })

if __name__ == "__main__":
    app.run(debug=True)

