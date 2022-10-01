import multiprocessing as mp
import psutil

nums = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]*100000000


def f(x):
    result = 1
    for i in x:
        result += i
    return result


def spawn():
    procs = list()
    n_cpus = psutil.cpu_count() - 6 - 8
    print(n_cpus)
    for cpu in range(n_cpus):
        affinity = [cpu]
        d = dict(affinity=affinity)
        p = mp.Process(target=run_child, kwargs=d)
        p.start()
        procs.append(p)
    for p in procs:
        p.join()
        print('joined')


def run_child(affinity):
    proc = psutil.Process()  # get self pid
    print(f'PID: {proc.pid}')
    aff = proc.cpu_affinity()
    print(f'Affinity before: {aff}')
    proc.cpu_affinity(affinity)
    aff = proc.cpu_affinity()
    print(f'Affinity after: {aff}')
    print(f(nums))


if __name__ == '__main__':
    spawn()
