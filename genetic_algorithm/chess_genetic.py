from cmath import inf
import time
import numpy as np
import random

#from numba import jit

# CONSTANTS
COLOR_BLACK = -1
COLOR_WHITE = 1
COLOR_NONE = 0
MAX_BIN_CHESS = 1 << 63
LEFT_BOUND = (1) | (1<<8) | (1<<16) | (1<<24) | (1<<32) | (1<<40) | (1<<48) | (1<<56)
RIGHT_BOUND = (1<<7) | (1<<15) | (1<<23) | (1<<31) | (1<<39) | (1<<47) | (1<<55) | (1<<63)
BIN_DIRECT = {"up": 8, "down": 8, "left": 1, "right": 1, "up-left": 9, "up-right": 7, "down-left": 7, "down-right": 9}
POS_VALUES = [9295429630892703873, 4792111478498951490, 2594215222373842980,
              1729382813125312536, 18577348462920192, 10205666933351424,
              6755684016199680, 39582420959232, 26543503441920, 103481868288]
INDEX2BIN = np.array([[1, 2, 4, 8, 16, 32, 64, 128],
                      [256, 512, 1024, 2048, 4096, 8192, 16384, 32768],
                      [65536, 131072, 262144, 524288, 1048576, 2097152, 4194304, 8388608],
                      [16777216, 33554432, 67108864, 134217728, 268435456, 536870912, 1073741824, 2147483648],
                      [4294967296, 8589934592, 17179869184, 34359738368, 68719476736, 137438953472, 274877906944, 549755813888],
                      [1099511627776, 2199023255552, 4398046511104, 8796093022208, 17592186044416, 35184372088832, 70368744177664, 140737488355328],
                      [281474976710656, 562949953421312, 1125899906842624, 2251799813685248, 4503599627370496, 9007199254740992, 18014398509481984, 36028797018963968],
                      [72057594037927936, 144115188075855872, 288230376151711744, 576460752303423488, 1152921504606846976, 2305843009213693952, 4611686018427387904, 9223372036854775808]])
BIN2INDEX = {1: (0, 0), 2: (0, 1), 4: (0, 2), 8: (0, 3), 16: (0, 4), 32: (0, 5), 64: (0, 6), 128: (0, 7),
             256: (1, 0), 512: (1, 1), 1024: (1, 2), 2048: (1, 3), 4096: (1, 4), 8192: (1, 5), 16384: (1, 6), 32768: (1, 7),
             65536: (2, 0), 131072: (2, 1), 262144: (2, 2), 524288: (2, 3), 1048576: (2, 4), 2097152: (2, 5), 4194304: (2, 6), 8388608: (2, 7),
             16777216: (3, 0), 33554432: (3, 1), 67108864: (3, 2), 134217728: (3, 3), 268435456: (3, 4), 536870912: (3, 5), 1073741824: (3, 6), 2147483648: (3, 7),
             4294967296: (4, 0), 8589934592: (4, 1), 17179869184: (4, 2), 34359738368: (4, 3), 68719476736: (4, 4), 137438953472: (4, 5), 274877906944: (4, 6), 549755813888: (4, 7),
             1099511627776: (5, 0), 2199023255552: (5, 1), 4398046511104: (5, 2), 8796093022208: (5, 3), 17592186044416: (5, 4), 35184372088832: (5, 5), 70368744177664: (5, 6), 140737488355328: (5, 7),
             281474976710656: (6, 0), 562949953421312: (6, 1), 1125899906842624: (6, 2), 2251799813685248: (6, 3), 4503599627370496: (6, 4), 9007199254740992: (6, 5), 18014398509481984: (6, 6), 36028797018963968: (6, 7),
             72057594037927936: (7, 0), 144115188075855872: (7, 1), 288230376151711744: (7, 2), 576460752303423488: (7, 3), 1152921504606846976: (7, 4), 2305843009213693952: (7, 5), 4611686018427387904: (7, 6), 9223372036854775808: (7, 7)}

class AI(object):
    """Identical algorithm with ../chess.py, only that the hyper-parameters are passed in with init instead of hard-coding in file"""

    def __init__(self, chessboard_size, color, time_out, state_num, count_list, depth_list, board_list, move_list, cnum_list, value_list):
        self.chessboard_size = chessboard_size
        self.color = color
        self.time_out = time_out
        self.candidate_list = []
        self.candidate_set = []
        self.movable_dict = {}
        self.max_weight = -inf
        self.at_state = 0
        self.start_time = 0.0
        
        # HYPER PARAMETERS
        self.STATE_NUM = state_num
        self.COUNT_LIST = count_list
        self.DEPTH_LIST = depth_list
        self.BOARD_WEIGHT_LIST = board_list
        self.MOVE_WEIGHT_LIST = move_list
        self.CNUMB_WEIGHT_LIST = cnum_list
        self.values = value_list
    
    def bin_to_index(self, bin_pos):
        return BIN2INDEX[bin_pos]
    
    def index_to_bin(self, row, col):
        return (int)(INDEX2BIN[row][col])
    
    def board_to_bin(self, chessboard):
        black_chess = 0
        white_chess = 0
        b_rows, b_cols = np.where(chessboard == COLOR_BLACK)
        w_rows, w_cols = np.where(chessboard == COLOR_WHITE)
        for i in range(len(b_rows)):
            black_chess |= self.index_to_bin(b_rows[i], b_cols[i])
        for i in range(len(w_rows)):
            white_chess |= self.index_to_bin(w_rows[i], w_cols[i])
        return black_chess, white_chess
    
    def bin_available_moves(self, own_chess, opo_chess):
        if (own_chess, opo_chess) in self.movable_dict:
            return self.movable_dict[(own_chess, opo_chess)]
        bin_move_list = []
        current_pos = 1
        check_pos = 0
        while current_pos <= MAX_BIN_CHESS:
            if current_pos & own_chess > 0:
                #1 go up
                check_pos = current_pos >> BIN_DIRECT["up"]
                if check_pos & opo_chess > 0:
                    while check_pos > 0 and check_pos & opo_chess > 0:
                        check_pos >>= BIN_DIRECT["up"]
                    if check_pos > 0 and check_pos & own_chess == 0 and check_pos & opo_chess == 0:
                        bin_move_list.append(check_pos)
                
                #2 go down
                check_pos = current_pos << BIN_DIRECT["down"]
                if check_pos & opo_chess > 0:
                    while check_pos <= MAX_BIN_CHESS and check_pos & opo_chess > 0:
                        check_pos <<= BIN_DIRECT["down"]
                    if check_pos <= MAX_BIN_CHESS and check_pos & own_chess == 0 and check_pos & opo_chess == 0:
                        bin_move_list.append(check_pos)
                
                #3 go left
                if current_pos & LEFT_BOUND == 0:
                    check_pos = current_pos >> BIN_DIRECT["left"]
                    if check_pos & opo_chess > 0:
                        while check_pos > 0 and check_pos & LEFT_BOUND == 0 and check_pos & opo_chess > 0:
                            check_pos >>= BIN_DIRECT["left"]
                        if check_pos > 0 and check_pos & own_chess == 0 and check_pos & opo_chess == 0:
                            bin_move_list.append(check_pos)
                    
                    #4 go up-left
                    check_pos = current_pos >> BIN_DIRECT["up-left"]
                    if check_pos & opo_chess > 0:
                        while check_pos > 0 and check_pos & LEFT_BOUND == 0 and check_pos & opo_chess > 0:
                            check_pos >>= BIN_DIRECT["up-left"]
                        if check_pos > 0 and check_pos & own_chess == 0 and check_pos & opo_chess == 0:
                            bin_move_list.append(check_pos)
                    
                    #5 go down-left
                    check_pos = current_pos << BIN_DIRECT["down-left"]
                    if check_pos & opo_chess > 0:
                        while check_pos <= MAX_BIN_CHESS and check_pos & LEFT_BOUND == 0 and check_pos & opo_chess > 0:
                            check_pos <<= BIN_DIRECT["down-left"]
                        if check_pos <= MAX_BIN_CHESS and check_pos & own_chess == 0 and check_pos & opo_chess == 0:
                            bin_move_list.append(check_pos)
                
                #6 go right
                if current_pos & RIGHT_BOUND == 0:
                    check_pos = current_pos << BIN_DIRECT["right"]
                    if check_pos & opo_chess > 0:
                        while check_pos <= MAX_BIN_CHESS and check_pos & RIGHT_BOUND == 0 and check_pos & opo_chess > 0:
                            check_pos <<= BIN_DIRECT["right"]
                        if check_pos <= MAX_BIN_CHESS and check_pos & own_chess == 0 and check_pos & opo_chess == 0:
                            bin_move_list.append(check_pos)
                    
                    #7 go up-right
                    check_pos = current_pos >> BIN_DIRECT["up-right"]
                    if check_pos & opo_chess > 0:
                        while check_pos > 0 and check_pos & RIGHT_BOUND == 0 and check_pos & opo_chess > 0:
                            check_pos >>= BIN_DIRECT["up-right"]
                        if check_pos > 0 and check_pos & own_chess == 0 and check_pos & opo_chess == 0:
                            bin_move_list.append(check_pos)
                    
                    #8 go down-right
                    check_pos = current_pos << BIN_DIRECT["down-right"]
                    if check_pos & opo_chess > 0:
                        while check_pos <= MAX_BIN_CHESS and check_pos & RIGHT_BOUND == 0 and check_pos & opo_chess > 0:
                            check_pos <<= BIN_DIRECT["down-right"]
                        if check_pos <= MAX_BIN_CHESS and check_pos & own_chess == 0 and check_pos & opo_chess == 0:
                            bin_move_list.append(check_pos)
            current_pos <<= 1
        self.movable_dict[(own_chess, opo_chess)] = bin_move_list
        return bin_move_list
    
    def count_bin_ones(self, num):
        count = 0
        while(num > 0):
            count += 1
            num &= num - 1
        return count
    
    def evaluation(self, own_chess, opo_chess):
        board_sum = 0
        for i in range(10):
            board_sum += self.count_bin_ones(POS_VALUES[i] & own_chess) * self.values[i]
        #move_sum = len(self.bin_available_moves(opo_chess, own_chess)) - len(self.bin_available_moves(own_chess, opo_chess))
        cnum_sum = self.count_bin_ones(opo_chess) - self.count_bin_ones(own_chess)
        return self.BOARD_WEIGHT_LIST[self.at_state] * board_sum + self.CNUMB_WEIGHT_LIST[self.at_state] * cnum_sum# + self.MOVE_WEIGHT_LIST[self.at_state] * move_sum

    def bin_flip(self, own_chess, opo_chess, move):
        result_own = own_chess | move
        result_opo = opo_chess
        #1 go up
        check_pos = move >> BIN_DIRECT["up"]
        if check_pos & opo_chess > 0:
            while check_pos > 0 and check_pos & opo_chess > 0:
                check_pos >>= BIN_DIRECT["up"]
            if check_pos > 0 and check_pos & own_chess > 0:
                check_pos <<= BIN_DIRECT["down"]
                while check_pos != move:
                    result_own |= check_pos
                    result_opo ^= check_pos
                    check_pos <<= BIN_DIRECT["down"]
        
        #2 go down
        check_pos = move << BIN_DIRECT["down"]
        if check_pos & opo_chess > 0:
            while check_pos <= MAX_BIN_CHESS and check_pos & opo_chess > 0:
                check_pos <<= BIN_DIRECT["down"]
            if check_pos <= MAX_BIN_CHESS and check_pos & own_chess > 0:
                check_pos >>= BIN_DIRECT["up"]
                while check_pos != move:
                    result_own |= check_pos
                    result_opo ^= check_pos
                    check_pos >>= BIN_DIRECT["up"]
        
        #3 go left
        if move & LEFT_BOUND == 0:
            check_pos = move >> BIN_DIRECT["left"]
            if check_pos & opo_chess > 0:
                while check_pos > 0 and check_pos & LEFT_BOUND == 0 and check_pos & opo_chess > 0:
                    check_pos >>= BIN_DIRECT["left"]
                if check_pos > 0 and check_pos & own_chess > 0:
                    check_pos <<= BIN_DIRECT["right"]
                    while check_pos != move:
                        result_own |= check_pos
                        result_opo ^= check_pos
                        check_pos <<= BIN_DIRECT["right"]
            
            #4 go up-left
            check_pos = move >> BIN_DIRECT["up-left"]
            if check_pos & opo_chess > 0:
                while check_pos > 0 and check_pos & LEFT_BOUND == 0 and check_pos & opo_chess > 0:
                    check_pos >>= BIN_DIRECT["up-left"]
                if check_pos > 0 and check_pos & own_chess > 0:
                    check_pos <<= BIN_DIRECT["down-right"]
                    while check_pos != move:
                        result_own |= check_pos
                        result_opo ^= check_pos
                        check_pos <<= BIN_DIRECT["down-right"]
            
            #5 go down-left
            check_pos = move << BIN_DIRECT["down-left"]
            if check_pos & opo_chess > 0:
                while check_pos <= MAX_BIN_CHESS and check_pos & LEFT_BOUND == 0 and check_pos & opo_chess > 0:
                    check_pos <<= BIN_DIRECT["down-left"]
                if check_pos <= MAX_BIN_CHESS and check_pos & own_chess > 0:
                    check_pos >>= BIN_DIRECT["up-right"]
                    while check_pos != move:
                        result_own |= check_pos
                        result_opo ^= check_pos
                        check_pos >>= BIN_DIRECT["up-right"]
        
        #6 go right
        if move & RIGHT_BOUND == 0:
            check_pos = move << BIN_DIRECT["right"]
            if check_pos & opo_chess > 0:
                while check_pos <= MAX_BIN_CHESS and check_pos & RIGHT_BOUND == 0 and check_pos & opo_chess > 0:
                    check_pos <<= BIN_DIRECT["right"]
                if check_pos <= MAX_BIN_CHESS and check_pos & own_chess > 0:
                    check_pos >>= BIN_DIRECT["left"]
                    while check_pos != move:
                        result_own |= check_pos
                        result_opo ^= check_pos
                        check_pos >>= BIN_DIRECT["left"]
            
            #7 go up-right
            check_pos = move >> BIN_DIRECT["up-right"]
            if check_pos & opo_chess > 0:
                while check_pos > 0 and check_pos & RIGHT_BOUND == 0 and check_pos & opo_chess > 0:
                    check_pos >>= BIN_DIRECT["up-right"]
                if check_pos > 0 and check_pos & own_chess > 0:
                    check_pos <<= BIN_DIRECT["down-left"]
                    while check_pos != move:
                        result_own |= check_pos
                        result_opo ^= check_pos
                        check_pos <<= BIN_DIRECT["down-left"]
            
            #8 go down-right
            check_pos = move << BIN_DIRECT["down-right"]
            if check_pos & opo_chess > 0:
                while check_pos <= MAX_BIN_CHESS and check_pos & RIGHT_BOUND == 0 and check_pos & opo_chess > 0:
                    check_pos <<= BIN_DIRECT["down-right"]
                if check_pos <= MAX_BIN_CHESS and check_pos & own_chess > 0:
                    check_pos >>= BIN_DIRECT["up-left"]
                    while check_pos != move:
                        result_own |= check_pos
                        result_opo ^= check_pos
                        check_pos >>= BIN_DIRECT["up-left"]
        return result_own, result_opo

    def max_value(self, own_chess, opo_chess, alpha, beta, depth):
        # TODO better time check position
        if depth == self.DEPTH_LIST[self.at_state] or self.time_out - time.process_time() + self.start_time < 0.005:
            return self.evaluation(own_chess, opo_chess), None
        movables = self.bin_available_moves(own_chess, opo_chess)
        if len(movables) == 0:
            return self.min_value(own_chess, opo_chess, alpha, beta, depth+1), None
        
        step_value, step_move = -inf, None
        for move in movables:
            moved_own, moved_opo = self.bin_flip(own_chess, opo_chess, move)
            next_value = self.min_value(moved_own, moved_opo, alpha, beta, depth+1)
            if beta <= next_value:
                return next_value, move
            if step_value < next_value:
                step_value = next_value
                step_move = move
            if alpha < next_value:
                alpha = next_value
        return step_value, step_move
    
    def min_value(self, own_chess, opo_chess, alpha, beta, depth):
        if depth == self.DEPTH_LIST[self.at_state] or self.time_out - time.process_time() + self.start_time < 0.005:
            return self.evaluation(own_chess, opo_chess)
        movables = self.bin_available_moves(opo_chess, own_chess)
        if len(movables) == 0:
            step_value, step_move = self.max_value(own_chess, opo_chess, alpha, beta, depth+1)
            return step_value
        
        step_value = inf
        for move in movables:
            moved_opo, moved_own = self.bin_flip(opo_chess, own_chess, move)
            next_value, _ = self.max_value(moved_own, moved_opo, alpha, beta, depth+1)
            if alpha >= next_value:
                return next_value
            if step_value > next_value:
                step_value = next_value
            if beta > next_value:
                beta = next_value
        return step_value

    # @jit()
    def go(self, chessboard):
        
        # init
        self.start_time = time.process_time()
        self.candidate_list.clear()
        self.candidate_set.clear()
        self.max_weight = -inf
        
        # all root candidates
        if self.color == COLOR_BLACK:
            own_chess, opo_chess = self.board_to_bin(chessboard)
        else:
            opo_chess, own_chess = self.board_to_bin(chessboard)
        self.candidate_set = self.bin_available_moves(own_chess, opo_chess)
        for move in self.candidate_set:
            self.candidate_list.append(self.bin_to_index(move))
        
        # decide depth
        chess_count = self.count_bin_ones(own_chess) + self.count_bin_ones(opo_chess)
        if self.at_state < self.STATE_NUM and chess_count > self.COUNT_LIST[self.at_state]:
            self.at_state += 1
        
        # search
        value, move = self.max_value(own_chess, opo_chess, -inf, inf, 0)
        if move != None:
            self.candidate_list.append(self.bin_to_index(move))