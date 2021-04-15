import sys, traceback

if __name__ == "__main__":
    try:
        raise TypeError("oof")
    except TypeError as e:
        traceback_str = ''.join(traceback.format_tb(e.__traceback__))
        print(traceback_str) 
