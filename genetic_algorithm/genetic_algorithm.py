from random import Random
from time import time_ns
import time
import numpy as np
from statistics import mean
from play import Play

# initial parameters
STATE_NUM = 4
COUNT_LIST = [8, 43, 55, 64]
DEPTH_LIST = [7, 5, 4, 9]
BOARD_WEIGHT_LIST = [1, 1, 1, 1]
MOBIL_WEIGHT_LIST = [1, 3, 4, 1]
VALUES = [-500, 25, -10, -5,
                45, -1, -1,
                    -3, -2,
                        -1]

# GA parameters
GENETIC_SIZE = 3
GENETIC_DEPTH = 2
GENETIC_REMAIN = 1

COUNT_DRIFT = 0
DEPTH_DRIFT = 0.5
BOARD_DRIFT = 0
MOBIL_DRIFT = 10.0
VALUE_DRIFT = 0
random = Random(time_ns)

# threading parameters
THREAD_NUM = 5

# ======================================= #
state_nums = []
count_lists = []
depth_lists = []
board_lists = []
mobil_lists = []
value_lists = []
next_count_lists = []
next_depth_lists = []
next_board_lists = []
next_mobil_lists = []
next_value_lists = []
adaptabilities = []
prepare_params = []
games = []
start_time = 0
finished_num = 0

class Game_Parameters(object):
    def __init__(self):
        self.state_list = []
        self.count_list = []
        self.depth_list = []
        self.board_list = []
        self.mobil_list = []
        self.value_list = []
        self.black_list = []
        self.white_list = []
    
    def append(self, state, count, depth, board, mobil, value, black, white):
        self.state_list.append(state)
        self.count_list.append(count)
        self.depth_list.append(depth)
        self.board_list.append(board)
        self.mobil_list.append(mobil)
        self.value_list.append(value)
        self.black_list.append(black)
        self.white_list.append(white)

# random drift generator
def generator(baseline, percentage, is_int, non_neg):
    dist = abs(mean(baseline) * percentage)
    result = baseline.copy()
    for i in range(len(result)):
        if is_int:
            result[i] = (int)(result[i] + (random.random() * dist * 2.0 - dist))
        else:
            result[i] += random.random() * dist * 2.0 - dist
    if non_neg:
        for i in range(len(result)):
            if result[i] < 0:
                result[i] = 0
    return result

def display_game(k, depth, black, white):
    print("\033[2J\033[1;1H")
    print("Timing:", str(time.perf_counter() - start_time) + "s")
    print("Processing:",
          str((GENETIC_SIZE*GENETIC_SIZE - GENETIC_SIZE) * depth + finished_num) +
          "/" + str((GENETIC_SIZE*GENETIC_SIZE - GENETIC_SIZE) * GENETIC_DEPTH))
    print("Displaying: thread", k)
    print("=============================================")
    print("black:")
    print("counts:", count_lists[black])
    print("depths:", depth_lists[black])
    print("boards:", board_lists[black])
    print("mobils:", mobil_lists[black])
    print("values:", value_lists[black])
    print("white:")
    print("counts:", count_lists[white])
    print("depths:", depth_lists[white])
    print("boards:", board_lists[white])
    print("mobils:", mobil_lists[white])
    print("values:", value_lists[white])
    print("=============================================")
    #display_board(games[k].chessboard, False)

def display_board(chessboard, clear_board):
        if clear_board:
            print("\033[1A\033[1A\033[1A\033[1A\033[1A\033[1A\033[1A\033[1A\033[1A", end="")
        for row in chessboard:
            for item in row:
                if item == -1:
                    print('●', end=" ")
                elif item == 1:
                    print('○', end=" ")
                else:
                    print('┼', end=" ")
            print()
        #print("\033[K" + "game time:", str(time.perf_counter() - turn_time) +
        #        "/" + str(time.perf_counter() - start_time) + "s")

if __name__=="__main__":
    # initial
    for item in range(GENETIC_SIZE):
        state_nums.append(STATE_NUM)
    for item in range(GENETIC_REMAIN):
        next_count_lists.append(generator(COUNT_LIST, COUNT_DRIFT, True, True))
    for item in range(GENETIC_REMAIN):
        next_depth_lists.append(generator(DEPTH_LIST, DEPTH_DRIFT, True, True))
    for item in range(GENETIC_REMAIN):
        next_board_lists.append(generator(BOARD_WEIGHT_LIST, BOARD_DRIFT, False, False))
    for item in range(GENETIC_REMAIN):
        next_mobil_lists.append(generator(MOBIL_WEIGHT_LIST, MOBIL_DRIFT, False, True))
    for item in range(GENETIC_REMAIN):
        next_value_lists.append(generator(VALUES, VALUE_DRIFT, False, False))

    # steps
    start_time = time.perf_counter()
    play_count = 0
    for depth in range(GENETIC_DEPTH):
        # step init
        games.clear()
        count_lists.clear()
        depth_lists.clear()
        board_lists.clear()
        mobil_lists.clear()
        value_lists.clear()
        adaptabilities.clear()
        prepare_params.clear()
        for item in range(THREAD_NUM):
            prepare_params.append(Game_Parameters())
        for item in range(GENETIC_SIZE):
            adaptabilities.append(0)
        
        # remained parameters
        for item in range(GENETIC_REMAIN):
            count_lists.append(next_count_lists[item])
        for item in range(GENETIC_REMAIN):
            depth_lists.append(next_depth_lists[item])
        for item in range(GENETIC_REMAIN):
            board_lists.append(next_board_lists[item])
        for item in range(GENETIC_REMAIN):
            mobil_lists.append(next_mobil_lists[item])
        for item in range(GENETIC_REMAIN):
            value_lists.append(next_value_lists[item])
        
        # new random parameters
        for item in range(GENETIC_REMAIN, GENETIC_SIZE):
            count_lists.append(generator(COUNT_LIST, COUNT_DRIFT, True, True))
        for item in range(GENETIC_REMAIN, GENETIC_SIZE):
            depth_lists.append(generator(DEPTH_LIST, DEPTH_DRIFT, True, True))
        for item in range(GENETIC_REMAIN, GENETIC_SIZE):
            board_lists.append(generator(BOARD_WEIGHT_LIST, BOARD_DRIFT, False, False))
        for item in range(GENETIC_REMAIN, GENETIC_SIZE):
            mobil_lists.append(generator(MOBIL_WEIGHT_LIST, MOBIL_DRIFT, False, True))
        for item in range(GENETIC_REMAIN, GENETIC_SIZE):
            value_lists.append(generator(VALUES, VALUE_DRIFT, False, False))
        
        # push parameters
        k = 0
        for item in range(GENETIC_SIZE):
            for jack in range(GENETIC_SIZE):
                if item == jack:
                    continue
                prepare_params[k].append(
                    (state_nums[item], state_nums[jack]),
                    (count_lists[item], count_lists[jack]),
                    (depth_lists[item], depth_lists[jack]),
                    (board_lists[item], board_lists[jack]),
                    (mobil_lists[item], mobil_lists[jack]),
                    (value_lists[item], value_lists[jack]),
                    item,
                    jack
                )
                k = (k + 1) % THREAD_NUM
        
        # push games
        for item in range(THREAD_NUM):
            games.append(Play(
                item,
                prepare_params[item].state_list,
                prepare_params[item].count_list,
                prepare_params[item].depth_list,
                prepare_params[item].board_list,
                prepare_params[item].mobil_list,
                prepare_params[item].value_list,
                prepare_params[item].black_list,
                prepare_params[item].white_list
            ))
            games[item].start()
        
        # wait
        all_finished = False
        k = 0
        while not all_finished:
            all_finished = True
            finished_num = 0
            for game in games:
                finished_num += game.finished
                if game.finished < game.task_num:
                    all_finished = False
            k = (k + 1) % THREAD_NUM
            display_game(k, depth, games[k].black, games[k].white)
            start_wait = time.perf_counter()
            while(time.perf_counter() - start_wait < 10):
                pass
        
        # get results
        for game in games:
            for result in game.game_results:
                if result != -1:
                    adaptabilities[result] += 1
        
        # sorting
        indices = np.argsort(adaptabilities)
        
        # remain the parameters
        for item in range(GENETIC_REMAIN):
            next_count_lists[item] = count_lists[indices[GENETIC_REMAIN - item - 1]]
            next_depth_lists[item] = depth_lists[indices[GENETIC_REMAIN - item - 1]]
            next_board_lists[item] = board_lists[indices[GENETIC_REMAIN - item - 1]]
            next_mobil_lists[item] = mobil_lists[indices[GENETIC_REMAIN - item - 1]]
            next_value_lists[item] = value_lists[indices[GENETIC_REMAIN - item - 1]]

    print("counts:", count_lists)
    print("depths:", depth_lists)
    print("boards:", board_lists)
    print("mobils:", mobil_lists)
    print("values:", value_lists)