"""
Tic Tac Toe Player
"""

import math
import copy

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    o = 0
    x = 0
    for player in board:
        for i in range(3):
            if player[i] == X:
                x = x + 1
            elif player[i] == O:
                o = o + 1
    if o >= x:
        return X
    else:
        return O


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    actions = set()
    linha = 0
    for row in board:
        for col in range(3):
            if row[col] == EMPTY:
                actions.add((linha, col))
        linha = linha + 1
    return actions


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    new_board = copy.deepcopy(board)
    player_turn = player(new_board)
    if new_board[action[0]][action[1]] == EMPTY:
        new_board[action[0]][action[1]] = player_turn
    else:
        raise Exception
    return new_board




def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    # Check horizontal
    for i in range(3):
        jogador = board[i][0]
        for j in range(3):
            if board[i][j] != jogador:
                break
            elif j == 2:
                return jogador

    # Check vertical
    for j in range(3):
        jogador = board[0][j]
        for i in range(3):
            if board[i][j] != jogador:
                break
            elif i == 2:
                return jogador

    # Check diagonal

    jogador = board[0][0]
    for i in range(3):
        if board[i][i] != jogador:
            break
        elif i == 2:
            return jogador

    # Check anti-diagonal

    jogador = board[2][0]
    for j in range(3):
        i = 2 - j
        if board[i][j] != jogador:
            break
        elif j == 2:
            return jogador
    # If no winner
    return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    if winner(board) is not None:
        return True

    for i in range(3):
        for j in range(3):
            if board[i][j] == EMPTY:
                return False
    return True


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    jogador = winner(board)
    if jogador == X:
        return 1
    elif jogador == O:
        return -1
    else:
        return 0


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    if terminal(board):
        return None
    elif player(board) == X:
        # Try to maximize
        higher = -100
        for action in actions(board):
            maybe_higher = maxvalue(result(board, action))
            if maybe_higher > higher:
                higher = maybe_higher
                optimal_action = action
        return optimal_action
    elif player(board) == O:
        # Try to minimize
        lower = 100
        for action in actions(board):
            maybe_lower = minvalue(result(board, action))
            if maybe_lower < lower:
                lower = maybe_lower
                optimal_action = action
        return optimal_action


def maxvalue(board):
    if terminal(board):
        return utility(board)
    v = -100000
    for action in actions(board):
        v = max(v, minvalue(result(board, action)))
    return v


def minvalue(board):
    if terminal(board):
        return utility(board)
    v = 100000
    for action in actions(board):
        v = min(v, maxvalue(result(board, action)))
    return v


