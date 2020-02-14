from collections import defaultdict
from timeit import Timer
from main import generate

NUM_DIGITS = 6

times = defaultdict(dict)


for digit in range(1, 10):
    aggregated_table = {}
    split_table = defaultdict(dict)

    for i in range(1, NUM_DIGITS + 1):
        timer = Timer('generate(digit, i, aggregated_table, split_table, True, debug=True)', globals={'aggregated_table': aggregated_table, 'split_table': split_table, 'digit': digit, 'i': i, 'generate': generate})
        times[digit][i] = timer.timeit(1)

for digit in times:
    for num_digits in range(1, NUM_DIGITS + 1):
        print(digit, num_digits, times[digit][num_digits])