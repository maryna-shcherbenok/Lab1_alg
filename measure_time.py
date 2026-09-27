from statistics import mean
from time import perf_counter

from hash_words import ChainWordSet


def make_word(number: int, prefix: str = '') -> str:
    chars = []
    value = number
    while True:
        chars.append(chr(97 + value % 26))
        value //= 26
        if value == 0:
            break
    word = prefix + ''.join(reversed(chars))
    return word[-15:]


def build_case(n: int):
    add_count = n // 2
    query_count = n // 5
    remove_count = n // 5
    extra_count = n - add_count - query_count - remove_count

    base = [make_word(i, 'a') for i in range(add_count)]
    missing = [make_word(i, 'z') for i in range(max(query_count, remove_count, extra_count))]

    commands = []
    commands.extend(('+', word) for word in base)
    commands.extend(('?', base[i % len(base)]) for i in range(query_count // 2))
    commands.extend(('?', missing[i]) for i in range(query_count - query_count // 2))
    commands.extend(('-', base[i % len(base)]) for i in range(remove_count // 2))
    commands.extend(('-', missing[i]) for i in range(remove_count - remove_count // 2))
    commands.extend(('+', base[i % len(base)]) for i in range(extra_count))
    return commands[:n]


def one_run(commands):
    table = ChainWordSet()

    start_ops = perf_counter()
    for sign, word in commands:
        if sign == '+':
            table.put_word(word)
        elif sign == '-':
            table.drop_word(word)
        else:
            table.has_word(word)
    ops_time = perf_counter() - start_ops

    start_repeat = perf_counter()
    repeat_total = sum(1 for _ in table.iter_repeats())
    repeat_time = perf_counter() - start_repeat

    return ops_time, repeat_time, repeat_total

def measure_search():
    table = ChainWordSet()

    stored = [make_word(i, 'a') for i in range(500_000)]
    missing = [make_word(i, 'z') for i in range(100_000)]

    for word in stored:
        table.put_word(word)

    successful = stored[:100_000]

    successful_times = []
    unsuccessful_times = []

    for _ in range(5):
        start = perf_counter()

        for word in successful:
            table.has_word(word)

        successful_times.append(perf_counter() - start)

        start = perf_counter()

        for word in missing:
            table.has_word(word)

        unsuccessful_times.append(perf_counter() - start)

    successful_avg = mean(successful_times)
    unsuccessful_avg = mean(unsuccessful_times)

    print()
    print('Search benchmark:')
    print(
        f'100000 successful queries: '
        f'{successful_avg:.6f}s, '
        f'{successful_avg / 100_000 * 1_000_000:.2f} us/query'
    )
    print(
        f'100000 unsuccessful queries: '
        f'{unsuccessful_avg:.6f}s, '
        f'{unsuccessful_avg / 100_000 * 1_000_000:.2f} us/query'
    )

def main():
    for n in (10_000, 100_000, 500_000, 1_000_000):
        commands = build_case(n)  # Generation time is not included in the measurement.
        samples = [one_run(commands) for _ in range(3)]
        ops = mean(x[0] for x in samples)
        repeats = mean(x[1] for x in samples)
        print(
            f'N={n:>9}  operations={ops:.6f}s  '
            f'repeats={repeats:.6f}s  total={ops + repeats:.6f}s'
        )
    measure_search()

if __name__ == '__main__':
    main()
