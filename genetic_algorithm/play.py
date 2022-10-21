from ..chess import AI
import numpy as np

def play(state_num, count_list, depth_list, board_list, move_list, value_list):
    ai_black = AI(8, -1, 5, state_num[0], count_list[0], depth_list[0], board_list[0], move_list[0], value_list[0])
    ai_white = AI(8, 1, 5, state_num[1], count_list[1], depth_list[1], board_list[1], move_list[1], value_list[1])
    chessboard = np.zeros((8, 8), dtype=int)
    turn = -1
    black_dead = False
    white_dead = False
    step = []

    indices = [(4, 3), (3, 4)]
    for index in indices:
        chessboard[index] = -1
    indices = [(3, 3), (4, 4)]
    for index in indices:
        chessboard[index] = 1
    step.append(chessboard.copy())

    while(not(black_dead and white_dead)):
        if turn == 1:
            ai_white.go(chessboard)
            if len(ai_white.candidate_list) > 0:
                move = ai_white.candidate_list.pop()
                chessboard[move[0]][move[1]] = 1
                white_dead = False
            else:
                white_dead = True
        else:
            ai_black.go(chessboard)
            if len(ai_black.candidate_list) > 0:
                move = ai_black.candidate_list.pop()
                chessboard[move[0]][move[1]] = -1
                black_dead = False
            else:
                black_dead = True
        step.append(chessboard.copy())
        turn = -turn
    
    black_count = chessboard.count(-1)
    white_count = chessboard.count(1)
    
    if black_count > white_count:
        return -1
    elif white_count > black_count:
        return 1
    else:
        return 0