from multiprocessing import  Process
import time
from chess_genetic import AI
import numpy as np

class Play(Process):
    def __init__(self, threadID, state_list, count_list, depth_list, board_list, mobil_list, value_list, black_list, white_list):
        super(Play, self).__init__()
        self.threadID = threadID
        self.task_num = len(state_list)
        self.state_list = state_list
        self.count_list = count_list
        self.depth_list = depth_list
        self.board_list = board_list
        self.mobil_list = mobil_list
        self.value_list = value_list
        self.black_list = black_list
        self.white_list = white_list
        self.state = []
        self.count = []
        self.depth = []
        self.board = []
        self.mobil = []
        self.value = []
        self.black = -1
        self.white = -1
        self.chessboard = np.zeros((8, 8))
        self.start_time = 0
        self.turn_time = 0
        self.finished = 0
        self.game_results = []
    
    def set_parameters(self):
        self.state = self.state_list[self.finished]
        self.count = self.count_list[self.finished]
        self.depth = self.depth_list[self.finished]
        self.board = self.board_list[self.finished]
        self.mobil = self.mobil_list[self.finished]
        self.value = self.value_list[self.finished]
        self.black = self.black_list[self.finished]
        self.white = self.white_list[self.finished]
        self.finished += 1

    def flip(self, move):
        directions = [(1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1)]
        for direction in directions:
            pointer = (move[0] + direction[0], move[1] + direction[1])
            if pointer[0] < 0 or pointer[1] < 0 or pointer[0] > 7 or pointer[1] > 7 or self.chessboard[pointer] != -self.chessboard[move]:
                continue
            while(pointer[0] >= 0 and pointer[1] >= 0 and pointer[0] <= 7 and pointer[1] <= 7 and self.chessboard[pointer] == -self.chessboard[move]):
                pointer = (direction[0] + pointer[0], direction[1] + pointer[1])
            if pointer[0] < 0 or pointer[1] < 0 or pointer[0] > 7 or pointer[1] > 7 or self.chessboard[pointer] != self.chessboard[move]:
                continue
            target = (pointer[0], pointer[1])
            pointer = (move[0] + direction[0], move[1] + direction[1])
            while pointer != target:
                self.chessboard[pointer] = self.chessboard[move]
                pointer = (direction[0] + pointer[0], direction[1] + pointer[1])

    def display_board(self):
        for row in self.chessboard:
            for item in row:
                if item == -1:
                    print('●', end=" ")
                elif item == 1:
                    print('○', end=" ")
                else:
                    print('┼', end=" ")
            print()
        #print("\033[K" + "game time:", str(time.perf_counter() - self.turn_time) +
        #        "/" + str(time.perf_counter() - self.start_time) + "s")

    def run(self):
        while self.finished < self.task_num:
            self.set_parameters()
            ai_black = AI(8, -1, 5, self.state[0], self.count[0], self.depth[0], self.board[0], self.mobil[0], self.value[0])
            ai_white = AI(8, 1, 5, self.state[1], self.count[1], self.depth[1], self.board[1], self.mobil[1], self.value[1])
            self.chessboard = np.zeros((8, 8), dtype=int)
            turn = -1
            black_dead = False
            white_dead = False
            step = []

            self.start_time = time.process_time()

            indices = [(4, 3), (3, 4)]
            for index in indices:
                self.chessboard[index] = -1
            indices = [(3, 3), (4, 4)]
            for index in indices:
                self.chessboard[index] = 1
            step.append(self.chessboard.copy())

            while(not(black_dead and white_dead)):
                self.turn_time = time.process_time()
                if turn == 1:
                    ai_white.go(self.chessboard)
                    if len(ai_white.candidate_list) > 0:
                        move = ai_white.candidate_list.pop()
                        self.chessboard[move[0]][move[1]] = 1
                        self.flip(move)
                        white_dead = False
                    else:
                        white_dead = True
                else:
                    ai_black.go(self.chessboard)
                    if len(ai_black.candidate_list) > 0:
                        move = ai_black.candidate_list.pop()
                        self.chessboard[move[0]][move[1]] = -1
                        self.flip(move)
                        black_dead = False
                    else:
                        black_dead = True
                step.append(self.chessboard.copy())
                turn = -turn
            
            black_count = np.count_nonzero(self.chessboard == -1)
            white_count = np.count_nonzero(self.chessboard == 1)
            
            if black_count > white_count:
                self.game_results.append(self.black)
            elif white_count > black_count:
                self.game_results.append(self.white)
            else:
                self.game_results.append(-1)
            print("\033[2J\033[1;1H")
            print("\033[K" + "Process " + str(self.threadID) + " finished " + str(self.finished) + "/" + str(self.task_num))
            self.display_board()