import itertools
import time

iter = itertools.cycle(['.', '..', '...','....','.....'])

while True:
    print(f"\r{next(iter)}", end='', flush=True)
    time.sleep(1)