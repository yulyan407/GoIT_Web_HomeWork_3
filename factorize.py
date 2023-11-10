from multiprocessing import Pool, current_process, cpu_count
from time import time


def factorize(*number: int) -> str:
    result = ''
    for elem in number:
        elem_result = []
        for i in range(1, elem + 1):
            if elem % i == 0:
                elem_result.append(i)
        result += f'assert {elem} == {elem_result}\n'
    return result


def factorize_process(*number: int) -> None:
    with Pool(cpu_count()) as pool:
        pool.map_async(factorize, number, callback=callback)
        pool.close()
        pool.join()


def callback(result):
    print(f'With process {result}')


if __name__ == '__main__':
    start = time()
    print(factorize(128, 255, 99999, 10651060))
    end = time()
    print(f'Function execution time -> {round((end - start), 5)} sec\n')

    pr_start = time()
    factorize_process(128, 255, 99999, 10651060)
    pr_end = time()
    print(f'Process execution time -> {round((pr_end - pr_start), 5)} sec\n')
