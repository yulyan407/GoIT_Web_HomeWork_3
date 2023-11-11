from multiprocessing import Pool, current_process, cpu_count
from time import time


def factorize(*number: int) -> list:
    result = []
    for elem in number:
        elem_result = []
        for i in range(1, elem + 1):
            if elem % i == 0:
                elem_result.append(i)
        result.append(f'assert {elem} == {elem_result}')
    return result


def factorize_process(*number: int) -> None:
    with Pool(cpu_count()) as pool:
        pool.map_async(factorize, number, callback=callback)
        pool.close()
        pool.join()


def callback(result):
    for elem in result:
        print(elem)


if __name__ == '__main__':
    print('Synchronous start:')
    start = time()
    a, b, c, d = (factorize(128, 255, 99999, 10651060))
    print(f'{a}\n{b}\n{c}\n{d}')
    end = time()
    print(f'Function execution time -> {round((end - start), 5)} sec\n')

    print('Asynchronous start:')
    print(f'The number of processor cores -> {cpu_count()}')
    pr_start = time()
    factorize_process(128, 255, 99999, 10651060)
    pr_end = time()
    print(f'Process execution time -> {round((pr_end - pr_start), 5)} sec\n')
