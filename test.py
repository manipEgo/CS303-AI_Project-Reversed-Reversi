from chess import AI
import numpy as np

def display_board(chessboard):
    for row in chessboard:
        for item in row:
            if item == -1:
                print('●', end=" ")
            elif item == 1:
                print('○', end=" ")
            else:
                print('┼', end=" ")
        print()

def flip(chessboard, move):
    directions = [(1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1)]
    for direction in directions:
        pointer = (move[0] + direction[0], move[1] + direction[1])
        if pointer[0] < 0 or pointer[1] < 0 or pointer[0] > 7 or pointer[1] > 7 or chessboard[pointer] != -chessboard[move]:
            continue
        while(pointer[0] >= 0 and pointer[1] >= 0 and pointer[0] <= 7 and pointer[1] <= 7 and chessboard[pointer] == -chessboard[move]):
            pointer = (direction[0] + pointer[0], direction[1] + pointer[1])
        if pointer[0] < 0 or pointer[1] < 0 or pointer[0] > 7 or pointer[1] > 7 or chessboard[pointer] != chessboard[move]:
            continue
        target = (pointer[0], pointer[1])
        pointer = (move[0] + direction[0], move[1] + direction[1])
        while pointer != target:
            chessboard[pointer] = chessboard[move]
            pointer = (direction[0] + pointer[0], direction[1] + pointer[1])

def play():
    ai_black = AI(8, -1, 50)
    ai_white = AI(8, 1, 50)
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
    display_board(chessboard)

    while(not(black_dead and white_dead)):
        print("step:", len(step))
        if turn == 1:
            ai_white.go(chessboard)
            if len(ai_white.candidate_list) > 0:
                move = ai_white.candidate_list.pop()
                chessboard[move[0]][move[1]] = 1
                flip(chessboard, move)
                white_dead = False
            else:
                white_dead = True
        else:
            ai_black.go(chessboard)
            if len(ai_black.candidate_list) > 0:
                move = ai_black.candidate_list.pop()
                chessboard[move[0]][move[1]] = -1
                flip(chessboard, move)
                black_dead = False
            else:
                black_dead = True
        step.append(chessboard.copy())
        
        #print("\033[1A\033[1A\033[1A\033[1A\033[1A\033[1A\033[1A\033[1A\033[1A\033[1A", end="")
        display_board(chessboard)
        turn = -turn
    
    black_count = np.count_nonzero(chessboard == -1)
    white_count = np.count_nonzero(chessboard == 1)
    
    if black_count > white_count:
        return -1
    elif white_count > black_count:
        return 1
    else:
        return 0

play()
