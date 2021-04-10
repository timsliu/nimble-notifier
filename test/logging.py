import time
import os
import threading
import subprocess

if __name__ == "__main__":
    t1 = threading.Thread(target=lambda: subprocess.run(["python3" ,"-u", "print_repeat.py", " >", "log.txt"]))
    t2 = threading.Thread(target=lambda: subprocess.run(["tail", "-f", "log.txt"]))

    t1.start()
    t2.start()
