from multiprocessing import Process, Queue, Value
import time
from chess_genetic import AI
import numpy as np

class Game_Parameters(object):
    """Stores all hyper-parameters of an agent"""

    def __init__(self, state, count, depth, board, mobil, cnumb, value, color):
        self.state_tuple = state
        self.count_tuple = count
        self.depth_tuple = depth
        self.board_tuple = board
        self.mobil_tuple = mobil
        self.cnumb_tuple = cnumb
        self.value_tuple = value
        self.color_tuple = color

class Play(Process):
    """Play the game between two agents"""

    def __init__(self, processID, param_queue: Queue, result_queue: Queue, black: Value, white: Value):
        super(Play, self).__init__()
        self.processID = processID
        self.param_queue = param_queue
        self.result_queue = result_queue
        self.state = []
        self.count = []
        self.depth = []
        self.board = []
        self.mobil = []
        self.cnumb = []
        self.value = []
        self.black = Value
        self.white = Value
        self.chessboard = np.zeros((8, 8))
        self.start_time = 0
        self.turn_time = 0
    
    def set_parameters(self):
        """read new parameter set from the queuing sets
        """
        new_params = self.param_queue.get(True)
        self.state = new_params.state_tuple
        self.count = new_params.count_tuple
        self.depth = new_params.depth_tuple
        self.board = new_params.board_tuple
        self.mobil = new_params.mobil_tuple
        self.cnumb = new_params.cnumb_tuple
        self.value = new_params.value_tuple
        self.black = new_params.color_tuple[0]
        self.white = new_params.color_tuple[1]

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
        """Run games till no more queuing agent parameters
        """
        while not self.param_queue.empty():
            self.set_parameters()
            ai_black = AI(8, -1, 5, self.state[0], self.count[0], self.depth[0], self.board[0], self.mobil[0], self.cnumb[0], self.value[0])
            ai_white = AI(8, 1, 5, self.state[1], self.count[1], self.depth[1], self.board[1], self.mobil[1], self.cnumb[1], self.value[1])
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
            
            self.display_board()
            if black_count < white_count:
                self.result_queue.put(self.black)
                print("black wins")
            elif white_count < black_count:
                self.result_queue.put(self.white)
                print("white wins")
            else:
                self.result_queue.put(-1)
                print("draw")
            print()