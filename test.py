import multiprocessing as mp
import psutil
import time

nums = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10] * 100


def f(x):
    result = 1
    time.sleep(1)
    for i in x:
        result += i
    return result


def f2(x):
    result = 1
    time.sleep(10)
    for i in x:
        result += i
    return result


def spawn():
    procs = list()
    n_cpus = 6 #psutil.cpu_count() - 6 - 7

    print(n_cpus)
    for cpu in range(5):
        affinity = [cpu]
        d = dict(affinity=affinity)
        p = mp.Process(target=run_child2, kwargs=d)
        p.start()
        procs.append(p)
    for cpu in range(20):
        affinity = [cpu]
        d = dict(affinity=affinity)
        p = mp.Process(target=run_child, kwargs=d)
        p.start()
        procs.append(p)
    for p in procs:
        p.join()
        print("joined")


def run_child(affinity):
    proc = psutil.Process()  # get self pid
    print(f"PID: {proc.pid}")
    aff = proc.cpu_affinity()
    print(f"Affinity before: {aff}")
    proc.cpu_affinity(affinity)
    aff = proc.cpu_affinity()
    print(f"Affinity after: {aff}")
    print(f(nums))


def run_child2(affinity):
    proc = psutil.Process()  # get self pid
    print(f"PID: {proc.pid}")
    aff = proc.cpu_affinity()
    print(f"Affinity before: {aff}")
    proc.cpu_affinity(affinity)
    aff = proc.cpu_affinity()
    print(f"Affinity after: {aff}")
    print(f2(nums))


if __name__ == "__main__":
    spawn()
