from retrying import retry
import random


@retry(wait_fixed=10000)
def do_something_unreliable():
    a = random.randint(0, 10)
    print(a)
    if a > 1:
        raise IOError("Broken sauce, everything is hosed!!!111one")
    else:
        return "Awesome sauce!"

print(do_something_unreliable())