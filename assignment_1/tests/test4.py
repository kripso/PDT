import random
import time
import threading


class TestClass:
    def __init__(self) -> None:
        self.threads = []
        pass

    def on_call(func):
        def inner(self, _func, _kwargs, last=False):
            if len(self.threads) == 5:
                for t in self.threads:
                    t.join()

                self.threads = []

            func(self, _func, _kwargs, last)

        return inner

    @on_call
    def threaded(self, _func, kwargs, last=False):
        t = threading.Thread(target=_func, kwargs=(kwargs))
        t.start()
        self.threads.append(t)

        if last:
            for t in self.threads:
                t.join()

            self.threads = []

    def do_stuf_1(self, time_sleep):
        print(f"func 1 {time_sleep}")
        time.sleep(time_sleep)

    def do_stuf_2(self, time_sleep):
        print(f"func 2 {time_sleep}")
        time.sleep(time_sleep)

    def do_stuf_3(self, time_sleep):
        print(f"func 3 {time_sleep}")
        time.sleep(time_sleep)


if __name__ == "__main__":

    trying = TestClass()
    start_time = time.time()
    trying.threaded(trying.do_stuf_1, {"time_sleep": 1})
    trying.threaded(trying.do_stuf_1, {"time_sleep": 2})
    trying.threaded(trying.do_stuf_1, {"time_sleep": 5}, last=True)
    print("time to complete", time.time() - start_time)
