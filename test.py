import multiprocessing as mp

TEST_SET = {}


def test_function(_TEST_SET, i):
    _TEST_SET[f"{1+i}"] = None
    _TEST_SET[f"{3+i}"] = None


def test_function_2(TEST_SET):
    print(TEST_SET)


def main():

    procs = []
    test_function(TEST_SET, 1)
    _TEST_SET = TEST_SET.copy()
    test_function(_TEST_SET, 2)

    print(TEST_SET)
    p = mp.Process(
        target=test_function_2,
        kwargs={"TEST_SET": TEST_SET},
    )
    p.start()
    procs.append(p)

    for p in procs:
        p.join()


if __name__ == "__main__":
    main()
