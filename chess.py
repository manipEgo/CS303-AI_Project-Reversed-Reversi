from cmath import inf
import numpy as np
import random

#from numba import jit

COLOR_BLACK=-1
COLOR_WHITE=1
COLOR_NONE=0
random.seed(0)

directions = ([1,0], [1,1], [0,1], [-1, 1], [-1, 0], [-1, -1], [0, -1], [1, -1])

class AI(object):
        def __init__(self, chessboard_size, color, time_out):
            self.chessboard_size = chessboard_size
            self.color = color
            self.time_out = time_out
            self.candidate_list = []
            self.candidate_set = []
            self.max_weight = -inf
        
        def available_moves(self, chessboard, color):
            move_list = []
            f_rows, f_cols = np.where(chessboard == color)
            for i in range(len(f_rows)):
                for drct in directions:
                    row = f_rows[i] + drct[0]
                    col = f_cols[i] + drct[1]
                    if row < 0 or row >= self.chessboard_size or\
                        col < 0 or col >= self.chessboard_size or\
                        chessboard[row][col] != -color:
                        continue
                    while row >= 0 and row < self.chessboard_size and\
                        col >= 0 and col < self.chessboard_size and\
                        chessboard[row][col] == -color:    
                        row += drct[0]
                        col += drct[1]
                    if row >= 0 and row < self.chessboard_size\
                        and col >= 0 and col < self.chessboard_size\
                        and chessboard[row][col] == COLOR_NONE:
                        move_list.append((row, col))
            return move_list

        # @jit()
        def go(self, chessboard):
            
            # init
            self.candidate_list.clear()
            self.candidate_set.clear()
            self.max_weight = -inf
            
            # all root candidates
            self.candidate_list = self.available_moves(chessboard, self.color)
            self.candidate_set = self.candidate_list.copy()
