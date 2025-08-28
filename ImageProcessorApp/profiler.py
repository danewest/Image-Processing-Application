# This file with profile execution time, funcation call frequency, & function call hierarchy
import time # execution time
import cProfile # function call frequency
import pstats # funtion call frequency
import pyinstrument # function call hierarchy

# insert test arguments
def run_tests():
    # insert tests


if __name__ == '__main__':
    # run tests for wall clock time, active cpu time, & function call hierarchy
    # run pyinstrument profiler  
    py_profiler = Profiler()
    py_profiler.start()

    clock_start = time.time()
    active_start = time.process_time()
    
    run_tests()
    
    clock_end = time.time()
    active_end = time.process_time()

    py_profiler.stop()
    print(py_profiler.out.put_text(unicode=True, color=True))

    # run tests for function call frequency & time spent in functions
    # run cProfile profiler
    with cProfile.Profile() as c_profile:
        run_tests()
    c_results = pstats.Stats(c_profile)
    c_results.sort_stats(pstats.SortKey.TIME)