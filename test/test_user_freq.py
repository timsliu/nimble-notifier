import sys
import os

# access everything in parent directory
sys.path.append("..")

import matcher

def test_this_tick(user_dict):
    for i in range(50):
        print("===Tick number: {}===".format(i)) 
        filtered_dict = matcher.users_this_tick(user_dict, i)
        for user in filtered_dict.keys():
            print("User: {}, refresh interval: {}".format(
                user, filtered_dict[user]["refresh_interval"]
            ))


if __name__ == "__main__":
    users = {
        "a": {"refresh_interval": 30, "rand_offset": 8736},
        "b": {"refresh_interval": 30, "rand_offset": 1111},
        "c": {"refresh_interval": 60, "rand_offset": 7482},
        "d": {"refresh_interval": 60, "rand_offset": 1},
        "e": {"refresh_interval": 300, "rand_offset": 89},
        "f": {"refresh_interval": 300, "rand_offset": 10},
        "g": {"refresh_interval": 600, "rand_offset": 2},
        "h": {"refresh_interval": 600, "rand_offset": 511},
        "i": {"refresh_interval": 1200, "rand_offset": 257},
        "j": {"refresh_interval": 1200, "rand_offset": 5109},
    }

    test_this_tick(users)
