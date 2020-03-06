
import resource
import psutil
import os
def limit_memory(max_mem_mb):
    '''
    limit memmory
    '''
    if max_mem_mb != 0:
        new_mem_lim = max_mem_mb * 1024*1024
        (soft,hard)= resource.getrlimit(resource.RLIMIT_AS)
        resource.setrlimit(resource.RLIMIT_AS, (1,hard))
                
def limit_time(time_lim):
    if time_lim:
        (soft,hard)= resource.getrlimit(resource.RLIMIT_CPU)
        resource.setrlimit(resource.RLIMIT_CPU, (time_lim,hard))
def get_cpu_time():
    rusage = resource.getrusage(resource.RUSAGE_SELF)
    return rusage.ru_utime
def get_used_memory():
    sour = psutil.Process(os.getpid())
    ll =sour.memory_info()
    return ll.rss/ 1024. / 1024.

    