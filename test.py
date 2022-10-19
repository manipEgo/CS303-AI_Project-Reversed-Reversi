from chess import AI
import numpy as np

ai = AI(8, 1, 5000)
chessboard = np.zeros((8, 8), dtype=int)
print(chessboard.shape)
chessboard[3][3] = chessboard[4][4] = 1
chessboard[3][4] = chessboard[4][3] = -1
print(chessboard)
ai.go(chessboard)
for item in ai.candidate_list:
    chessboard[item[0]][item[1]] = 5
print(chessboard)