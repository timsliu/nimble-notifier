# log_run.py

# wrapper around runner.py that saves the output of a run to a file while
# printing to the terminal the contents of the run

import time
import os
import threading
import subprocess
import datetime

if __name__ == "__main__":
    # path to save the log to 
    start_time = datetime.datetime.now().strftime("%m_%d_%Y_%H_%M_%S")
    log_path = os.path.join("data/logs/", "log_{}.txt".format(start_time))

    f = open(log_path, "w")
    # thread for running Vaccine Notifier
    t1 = threading.Thread(target=lambda: subprocess.run(
    [
        "python3",
        "-u", 
        "runner.py"
    ], stdout=f))
   
    # display output to the terminal
    t2 = threading.Thread(target=lambda: subprocess.run(
    [
        "tail",
        "-f", 
        log_path
    ]))

    t1.start()
    t2.start()
