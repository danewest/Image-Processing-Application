# This file will profile execution time, function call frequency, & function call hierarchy
import time # execution time
import cProfile, pstats # function call frequency
from pyinstrument import Profiler # function call hierarchy
from datetime import datetime
import csv
import os

# arguments to be tested
# notes, this has to run twice so we may want to look at overwriting files if they already exist to be able to run this twice
def run_tests():
    # insert tests

# log generation
def generate_log_summary(run_id, wall_time, cpu_time, cprofile_time, filename="summary.csv"):
    # write header if file does not exist or is empty
    write_header = not os.path.exists(filename) or os.path.getsize(filename) == 0
    with open(filename, "a", newline="") as f:
        writer = csv.writer(f)
        if write_header:
            writer.writerow(["run_id", "wall_clock_time", "active_cpu_time", "cprofile_cumulative_time"])
        writer.writerow([run_id, round(wall_time, 6), round(cpu_time, 6), round(cprofile_time, 6)])

def generate_pyinstrument_log(profiler, run_id, filename="pyinstrument.csv"):
    root_frame = profiler.last_session.root_frame

    def walk(frame, path):
        current_path = path + [frame.function]
        time_s = frame.time
        percent = (time_s / profiler.last_session.duration) * 100
        yield ">".join(current_path), time_s, percent
        for child in frame.children:
            yield from walk(child, current_path)
    
    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["run_id", "function_path", "time_seconds", "time_percent"])
        for func_path, time_s, percent in walk(root_frame, []):
            writer.writerow([run_id, func_path, round(time_s, 6), round(percent, 2)])


def generate_c_log(profile, filename, run_id):
    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        # header
        writer.writerow(["run_id", "function", "num_calls",
                            "parent_time", "avg_per_call", "cumulative_time"])
        
        stats = pstats.Stats(profile) # accesses the raw stats dictionary
        for func, (cc, nc, tt, ct, callers) in stats.stats.items():
            num_calls = nc
            parent_time = tt
            avg_per_call = tt / nc if nc > 0 else 0
            cumulative_time = ct

            func_name = f"{func[0]}:{func[1]}({func[2]})"

            writer.writerow([run_id, func_name, num_calls,
                                parent_time, avg_per_call, cumulative_time])

# main: performs testing
if __name__ == '__main__':
    run_id = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    # run tests for wall clock time, active cpu time, & function call hierarchy
    # run pyinstrument profiler  
    py_profiler = Profiler()
    py_profiler.start()

    clock_start = time.time()
    cpu_start = time.process_time()
    
    run_tests()
    
    clock_end = time.time()
    cpu_end = time.process_time()

    py_profiler.stop()

    # calculate wall clock & cpu times
    wall_clock_time = clock_end - clock_start
    active_cpu_time = cpu_end - cpu_start

    # run tests for function call frequency & time spent in functions
    # run cProfile profiler
    with cProfile.Profile() as c_profile:
        run_tests()
    # calculate cprofile_time
    cprofile_time = sum([ct for _, (_, _, ct, _, _) in pstats.Stats(c_profile).stats.items()])
    
    # write logs
    generate_log_summary(run_id, wall_clock_time, active_cpu_time, cprofile_time)
    generate_pyinstrument_log(py_profiler, run_id)
    generate_c_log(c_profile, f"cprofile_{run_id}.csv", run_id)