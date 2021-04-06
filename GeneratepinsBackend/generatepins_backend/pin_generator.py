import random


def gen_digits():
    num_set = random.sample(range(10), 4)
    pin = ''
    for n in num_set:
        pin += str(n)
    return pin
