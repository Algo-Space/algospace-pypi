import numpy as np

def random_number(lower, upper):
    out = {
        'result': np.random.randint(lower, upper)
    }
    return out