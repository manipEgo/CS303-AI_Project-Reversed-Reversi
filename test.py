from chess import AI
import numpy as np

ai_black = AI(8, -1, 500)
ai_white = AI(8, 1, 500)
chessboard = np.zeros((8, 8), dtype=int)
turn = 1
black_dead = False
white_dead = False
step = []

indices = [(3, 3), (4, 4)]
for index in indices:
    chessboard[index] = 1
indices = [(4, 3), (3, 4)]
for index in indices:
    chessboard[index] = -1
print(chessboard)
step.append(chessboard.copy())

while(not(black_dead and white_dead)):
    print("step", len(step))
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
    print(chessboard)
    step.append(chessboard.copy())
    turn = -turn
