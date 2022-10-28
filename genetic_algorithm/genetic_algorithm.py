from multiprocessing import Queue, Value
import os
from random import Random
from time import time_ns
import time
import numpy as np
from statistics import mean
from play import Play, Game_Parameters

# initial parameters
STATE_NUM = 4
COUNT_LIST = [15, 43, 54, 64]
DEPTH_LIST = [5, 4, 3, 10]
BOARD_WEIGHT_LIST = [1, 1, 1, 0]
MOBIL_WEIGHT_LIST = [0, 0, 0, 0]
CNUMB_WEIGHT_LIST = [0, 0, 0, 1]
VALUES = np.array([-5000, 25, -10, -5,
                        45, -1, -1,
                            -3, -2,
                                -1])

# GA parameters
GENETIC_SIZE = 16
GENETIC_DEPTH = 256
GENETIC_REMAIN = 6

COUNT_DRIFT = 0
DEPTH_DRIFT = 0
BOARD_DRIFT = 0
MOBIL_DRIFT = 0
CNUMB_DRIFT = 0
VALUE_DRIFT = 0.002
random = Random(time_ns)

# threading parameters
THREAD_NUM = 8

# ======================================= #
state_nums = []
count_lists = []
depth_lists = []
board_lists = []
mobil_lists = []
cnumb_lists = []
value_lists = []
next_count_lists = []
next_depth_lists = []
next_board_lists = []
next_mobil_lists = []
next_cnumb_lists = []
next_value_lists = []
adaptabilities = []
prepare_params = Queue()
play_results = Queue()
games = []
games_black = []
games_white = []
start_time = 0

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

def display_game(k, depth):
    #print("\033[2J\033[1;1H")
    print("Timing:", str(time.perf_counter() - start_time) + "s")
    print("Processing:",
          str(depth * (GENETIC_SIZE*GENETIC_SIZE - GENETIC_SIZE) + play_results.qsize()) +
          "/" + str((GENETIC_SIZE*GENETIC_SIZE - GENETIC_SIZE) * GENETIC_DEPTH))
    print("Displaying: parameters ", k)
    print("=============================================")
    #print("black:")
    print("counts:", count_lists[k])
    print("depths:", depth_lists[k])
    print("boards:", board_lists[k])
    print("mobils:", mobil_lists[k])
    print("cnumbs:", cnumb_lists[k])
    print("values:", value_lists[k])
    #print("white:")
    #print("counts:", count_lists[white])
    #print("depths:", depth_lists[white])
    #print("boards:", board_lists[white])
    #print("mobils:", mobil_lists[white])
    #print("values:", value_lists[white])
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
    next_count_lists.append(COUNT_LIST)
    for item in range(GENETIC_REMAIN - 1):
        next_count_lists.append(generator(COUNT_LIST, COUNT_DRIFT, True, True))
    next_depth_lists.append(DEPTH_LIST)
    for item in range(GENETIC_REMAIN - 1):
        next_depth_lists.append(generator(DEPTH_LIST, DEPTH_DRIFT, True, True))
    next_board_lists.append(BOARD_WEIGHT_LIST)
    for item in range(GENETIC_REMAIN - 1):
        next_board_lists.append(generator(BOARD_WEIGHT_LIST, BOARD_DRIFT, False, True))
    next_mobil_lists.append(MOBIL_WEIGHT_LIST)
    for item in range(GENETIC_REMAIN - 1):
        next_mobil_lists.append(generator(MOBIL_WEIGHT_LIST, MOBIL_DRIFT, False, True))
    next_cnumb_lists.append(CNUMB_WEIGHT_LIST)
    for item in range(GENETIC_REMAIN - 1):
        next_cnumb_lists.append(generator(CNUMB_WEIGHT_LIST, CNUMB_DRIFT, False, True))
    next_value_lists.append(VALUES)
    for item in range(GENETIC_REMAIN - 1):
        next_value_lists.append(generator(VALUES, VALUE_DRIFT, False, False))

    # steps
    start_time = time.perf_counter()
    for depth in range(GENETIC_DEPTH):
        # step init
        games.clear()
        count_lists.clear()
        depth_lists.clear()
        board_lists.clear()
        mobil_lists.clear()
        cnumb_lists.clear()
        value_lists.clear()
        adaptabilities.clear()
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
            cnumb_lists.append(next_cnumb_lists[item])
        for item in range(GENETIC_REMAIN):
            value_lists.append(next_value_lists[item])
        
        # new random parameters
        for item in range(GENETIC_REMAIN, GENETIC_SIZE):
            count_lists.append(generator(next_count_lists[random.randint(0, GENETIC_REMAIN - 1)], COUNT_DRIFT, True, True))
        for item in range(GENETIC_REMAIN, GENETIC_SIZE):
            depth_lists.append(generator(next_depth_lists[random.randint(0, GENETIC_REMAIN - 1)], DEPTH_DRIFT, True, True))
        for item in range(GENETIC_REMAIN, GENETIC_SIZE):
            board_lists.append(generator(next_board_lists[random.randint(0, GENETIC_REMAIN - 1)], BOARD_DRIFT, False, True))
        for item in range(GENETIC_REMAIN, GENETIC_SIZE):
            mobil_lists.append(generator(next_mobil_lists[random.randint(0, GENETIC_REMAIN - 1)], MOBIL_DRIFT, False, True))
        for item in range(GENETIC_REMAIN, GENETIC_SIZE):
            cnumb_lists.append(generator(next_cnumb_lists[random.randint(0, GENETIC_REMAIN - 1)], CNUMB_DRIFT, False, True))
        for item in range(GENETIC_REMAIN, GENETIC_SIZE):
            value_lists.append(generator(next_value_lists[random.randint(0, GENETIC_REMAIN - 1)], VALUE_DRIFT, False, False))
        
        # push parameters
        for item in range(GENETIC_SIZE):
            for jack in range(GENETIC_SIZE):
                if item == jack:
                    continue
                prepare_params.put(Game_Parameters(
                    (state_nums[item], state_nums[jack]),
                    (count_lists[item], count_lists[jack]),
                    (depth_lists[item], depth_lists[jack]),
                    (board_lists[item], board_lists[jack]),
                    (mobil_lists[item], mobil_lists[jack]),
                    (cnumb_lists[item], cnumb_lists[jack]),
                    (value_lists[item], value_lists[jack]),
                    (item, jack))
                )
        
        # init games
        for item in range(THREAD_NUM):
            black = Value('i', 0)
            white = Value('i', 0)
            games_black.append(black)
            games_white.append(white)
            games.append(Play(item, prepare_params, play_results, black, white))
            games[item].start()
        
        # wait
        k = 0
        all_count = prepare_params.qsize()
        while play_results.qsize() < all_count:
            now_count = play_results.qsize()
            k = (k + 1) % GENETIC_SIZE
            display_game(k, depth)
            start_wait = time.perf_counter()
            while(time.perf_counter() - start_wait < 10):
                pass
        
        # get results
        while not play_results.empty():
            new_result = play_results.get(True)
            if new_result != -1:
                adaptabilities[new_result] += 1
        
        # sorting
        indices = np.argsort(adaptabilities)
        
        # remain the parameters
        for item in range(GENETIC_REMAIN):
            next_count_lists[item] = count_lists[indices[GENETIC_REMAIN - item - 1]]
            next_depth_lists[item] = depth_lists[indices[GENETIC_REMAIN - item - 1]]
            next_board_lists[item] = board_lists[indices[GENETIC_REMAIN - item - 1]]
            next_mobil_lists[item] = mobil_lists[indices[GENETIC_REMAIN - item - 1]]
            next_cnumb_lists[item] = cnumb_lists[indices[GENETIC_REMAIN - item - 1]]
            next_value_lists[item] = value_lists[indices[GENETIC_REMAIN - item - 1]]
        
        # write into files
        with open("results/result_depth_" + str(depth) + ".txt", "w+") as f:
            f.write("adaptabilities:" + os.linesep)
            for item in adaptabilities:
                f.write(str(item) + "\t")
            f.write(os.linesep + "======================================" + os.linesep)
            f.write("remained parameters:" + os.linesep)
            f.write("count lists:" + os.linesep)
            f.write(str(next_count_lists) + os.linesep)
            f.write("depth lists:" + os.linesep)
            f.write(str(next_depth_lists) + os.linesep)
            f.write("board lists:" + os.linesep)
            f.write(str(next_board_lists) + os.linesep)
            f.write("mobil lists:" + os.linesep)
            f.write(str(next_mobil_lists) + os.linesep)
            f.write("cnumb lists:" + os.linesep)
            f.write(str(next_cnumb_lists) + os.linesep)
            f.write("value lists:" + os.linesep)
            f.write(str(next_value_lists) + os.linesep)

    print("counts:", count_lists)
    print("depths:", depth_lists)
    print("boards:", board_lists)
    print("mobils:", mobil_lists)
    print("cnumbs:", cnumb_lists)
    print("values:", value_lists)