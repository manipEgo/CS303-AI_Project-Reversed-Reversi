from random import Random
import numpy as np
from statistics import mean
from play import play

STATE_NUM = 4
COUNT_LIST = [10, 45, 50, 64]
DEPTH_LIST = [9, 6, 7, 12]
BOARD_WEIGHT_LIST = [1, 1, 1, 1]
MOBIL_WEIGHT_LIST = [1, 3, 4, 1]
VALUES = [-500, 25, -10, -5,
                45, -1, -1,
                    -3, -2,
                        -1]

GENETIC_SIZE = 64
GENETIC_DEPTH = 3
GENETIC_REMAIN = 10

COUNT_DRIFT = 0
DEPTH_DRIFT = 0.5
BOARD_DRIFT = 0
MOBIL_DRIFT = 10.0
VALUE_DRIFT = 0
random = Random(114)

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
        for item in result:
            if item < 0:
                item = 0
    return result

# initial
for i in range(GENETIC_SIZE):
    state_nums.append(STATE_NUM)
for i in range(GENETIC_REMAIN):
    next_count_lists.append(generator(COUNT_LIST, COUNT_DRIFT, True, True))
for i in range(GENETIC_REMAIN):
    next_depth_lists.append(generator(DEPTH_LIST, DEPTH_DRIFT, True, True))
for i in range(GENETIC_REMAIN):
    next_board_lists.append(generator(BOARD_WEIGHT_LIST, BOARD_DRIFT, False, False))
for i in range(GENETIC_REMAIN):
    next_mobil_lists.append(generator(MOBIL_WEIGHT_LIST, MOBIL_DRIFT, False, True))
for i in range(GENETIC_REMAIN):
    next_value_lists.append(generator(VALUES, VALUE_DRIFT, False, False))

# steps
for depth in range(GENETIC_DEPTH):
    # step init
    count_lists.clear()
    depth_lists.clear()
    board_lists.clear()
    mobil_lists.clear()
    value_lists.clear()
    adaptabilities.clear()
    for i in range(GENETIC_SIZE):
        adaptabilities.append(0)
    
    # remained parameters
    for i in range(GENETIC_REMAIN):
        count_lists.append(next_count_lists[i])
    for i in range(GENETIC_REMAIN):
        depth_lists.append(next_depth_lists[i])
    for i in range(GENETIC_REMAIN):
        board_lists.append(next_board_lists[i])
    for i in range(GENETIC_REMAIN):
        mobil_lists.append(next_mobil_lists[i])
    for i in range(GENETIC_REMAIN):
        value_lists.append(next_value_lists[i])
    
    # new random parameters
    for i in range(GENETIC_REMAIN + 1, GENETIC_SIZE):
        count_lists.append(generator(COUNT_LIST, COUNT_DRIFT, True, True))
    for i in range(GENETIC_REMAIN + 1, GENETIC_SIZE):
        depth_lists.append(generator(DEPTH_LIST, DEPTH_DRIFT, True, True))
    for i in range(GENETIC_REMAIN + 1, GENETIC_SIZE):
        board_lists.append(generator(BOARD_WEIGHT_LIST, BOARD_DRIFT, False, False))
    for i in range(GENETIC_REMAIN + 1, GENETIC_SIZE):
        mobil_lists.append(generator(MOBIL_WEIGHT_LIST, MOBIL_DRIFT, False, True))
    for i in range(GENETIC_REMAIN + 1, GENETIC_SIZE):
        value_lists.append(generator(VALUES, VALUE_DRIFT, False, False))
    
    # evaluation
    for i in range(GENETIC_SIZE):
        for j in range(GENETIC_SIZE):
            if i == j:
                continue
            print("=============================================")
            print("playing:", i*j + j, "/", GENETIC_SIZE*GENETIC_SIZE - GENETIC_SIZE, (i*j + j)/(GENETIC_SIZE*GENETIC_SIZE - GENETIC_SIZE)*100, "%")
            print("black:")
            print("counts:", count_lists[i])
            print("depths:", depth_lists[i])
            print("boards:", board_lists[i])
            print("mobils:", mobil_lists[i])
            print("values:", value_lists[i])
            print("white:")
            print("counts:", count_lists[j])
            print("depths:", depth_lists[j])
            print("boards:", board_lists[j])
            print("mobils:", mobil_lists[j])
            print("values:", value_lists[j])
            print("=============================================")
            game_result = play(
                (state_nums[i], state_nums[j]),
                (count_lists[i], count_lists[j]),
                (depth_lists[i], depth_lists[j]),
                (board_lists[i], board_lists[j]),
                (mobil_lists[i], mobil_lists[j]),
                (value_lists[i], value_lists[j])
            )
            print("=============================================")
            if game_result == -1:
                adaptabilities[i] += 1
                print("black wins")
            elif game_result == 1:
                adaptabilities[j] += 1
                print("white wins")
            else:
                print("draw")
    
    # sorting
    indices = np.argsort(-adaptabilities)
    
    # remain the parameters
    for i in range(GENETIC_REMAIN):
        next_count_lists[i] = count_lists[indices[i]]
        next_depth_lists[i] = depth_lists[indices[i]]
        next_board_lists[i] = board_lists[indices[i]]
        next_mobil_lists[i] = mobil_lists[indices[i]]
        next_value_lists[i] = value_lists[indices[i]]

print("counts:", count_lists)
print("depths:", depth_lists)
print("boards:", board_lists)
print("mobils:", mobil_lists)
print("values:", value_lists)
    