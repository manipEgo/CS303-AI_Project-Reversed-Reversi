from chess import AI
import numpy as np

ai = AI(8, 1, 5000)
chessboard = np.zeros((8, 8), dtype=int)
indices = [(3, 3), (4, 4)]
for index in indices:
    chessboard[index[0]][index[1]] = 1
indices = [(3, 4), (4, 3)]
for index in indices:
    chessboard[index[0]][index[1]] = -1

print(chessboard)
# ai.go(chessboard)
# for item in ai.candidate_list:
#     chessboard[item[0]][item[1]] = 5
# print(chessboard)
print(ai.evaluation(chessboard, 1))